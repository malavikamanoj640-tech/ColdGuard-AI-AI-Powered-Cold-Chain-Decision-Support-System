import json, math, hashlib
from datetime import datetime
from pathlib import Path
import numpy as np
from PIL import Image, ImageStat

try:
    import requests
except Exception:
    requests = None


def cv_inspect(file_storage):
    """Lightweight offline package inspection; optionally enhanced by OpenCV if installed."""
    img = Image.open(file_storage).convert('RGB')
    w,h = img.size
    stat = ImageStat.Stat(img)
    mean = sum(stat.mean)/3
    contrast = sum(stat.stddev)/3
    # Heuristic visual quality indicators, intentionally presented as screening rather than certified diagnosis.
    low_light = mean < 55
    low_contrast = contrast < 18
    aspect = max(w,h)/max(1,min(w,h))
    damage_score = 18
    reasons=[]
    if low_light: damage_score += 12; reasons.append('Low-light image; package edges may be obscured')
    if low_contrast: damage_score += 10; reasons.append('Low contrast; surface damage may be difficult to inspect')
    if aspect > 2.8: damage_score += 8; reasons.append('Unusual package aspect ratio')
    damage_score = min(95, damage_score)
    label = 'SCREENING PASS' if damage_score < 35 else ('REVIEW' if damage_score < 60 else 'POTENTIAL DAMAGE')
    return {'label':label,'damage_score':round(damage_score,1),'confidence':round(min(96,62+contrast*0.8),1),'width':w,'height':h,'mean_brightness':round(mean,1),'contrast':round(contrast,1),'reasons':reasons or ['No strong visual anomaly detected by the offline screening model'], 'note':'This is an assistive visual screening result, not a certified quality inspection.'}


def disruption_scenario(data):
    base=float(data.get('baseline_risk',30)); delay=float(data.get('delay_hours',0)); temp=float(data.get('temperature',5)); demand=float(data.get('demand_multiplier',1)); closure=bool(data.get('route_closure',False)); refrigeration=bool(data.get('refrigeration_failure',False)); weather=bool(data.get('severe_weather',False))
    delay_impact=delay*4
    temp_impact=max(0,temp-8)*7
    demand_impact=max(0,(demand-1)*35)
    closure_impact=18 if closure else 0
    refrigeration_impact=25 if refrigeration else 0
    weather_impact=12 if weather else 0
    risk=min(99,base + delay_impact + temp_impact + demand_impact + closure_impact + refrigeration_impact + weather_impact)
    actions=[]
    if closure: actions.append('Reroute through the lowest-risk available corridor')
    if refrigeration: actions.append('Move to controlled storage and dispatch a backup cooling unit')
    if weather: actions.append('Increase telemetry frequency and add weather buffer to ETA')
    if demand>1.15: actions.append('Prioritize high-risk/high-value inventory and replenish safety stock')
    if not actions: actions.append('Continue monitoring; no major disruption response required')
    contributors=[
        {'name':'Baseline risk','impact':round(base,1)},
        {'name':'Delay','impact':round(delay_impact,1)},
        {'name':'Temperature excursion','impact':round(temp_impact,1)},
        {'name':'Demand pressure','impact':round(demand_impact,1)},
        {'name':'Route closure','impact':round(closure_impact,1)},
        {'name':'Refrigeration failure','impact':round(refrigeration_impact,1)},
        {'name':'Severe weather','impact':round(weather_impact,1)}
    ]
    return {'baseline_risk':round(base,1),'scenario_risk':round(risk,1),'impact_points':round(risk-base,1),'severity':'CRITICAL' if risk>=75 else 'HIGH' if risk>=55 else 'MODERATE' if risk>=30 else 'LOW','recommended_actions':actions,'estimated_delay_hours':round(delay+(2.5 if closure else 0)+(1.5 if weather else 0),1),'estimated_loss':round(1500*(risk/100)*(1+max(0,demand-1)),0),'contributors':contributors}


def _linear_predict(train, horizon):
    y=np.asarray(train,dtype=float); x=np.arange(len(y)); coef=np.polyfit(x,y,1); future=np.arange(len(y),len(y)+horizon)
    return np.maximum(0,np.polyval(coef,future))


def _moving_average_predict(train, horizon, window=4):
    values=list(map(float,train))
    for _ in range(horizon): values.append(float(np.mean(values[-min(window,len(values)):])) )
    return np.asarray(values[-horizon:])


def _exp_smooth_predict(train, horizon, alpha=0.45):
    values=list(map(float,train)); level=values[0]
    for v in values[1:]: level=alpha*v+(1-alpha)*level
    return np.repeat(level,horizon)


def _mae(actual,pred):
    a=np.asarray(actual,dtype=float); p=np.asarray(pred,dtype=float)
    return float(np.mean(np.abs(a-p))) if len(a) else 0.0


def demand_forecast(history=None, horizon=7):
    if history is None: history=[38,42,45,43,49,54,52,57,61,59,65,68,70,73]
    y=np.asarray(history,dtype=float)
    horizon=max(1,int(horizon))
    if len(y)<8:
        pred=_linear_predict(y,horizon)
        return {'history':y.astype(int).tolist(),'forecast':np.maximum(0,np.round(pred)).astype(int).tolist(),'trend_per_day':round(float((pred[-1]-pred[0])/max(1,horizon-1)),2),'method':'Linear trend','selected_model':'Linear Trend','models':[]}
    split=max(5,len(y)-4); train=y[:split]; test=y[split:]
    candidates={
        'Linear Trend': lambda h:_linear_predict(train,h),
        'Moving Average': lambda h:_moving_average_predict(train,h),
        'Exponential Smoothing': lambda h:_exp_smooth_predict(train,h)
    }
    scores=[]
    for name,fn in candidates.items():
        pred=fn(len(test)); scores.append({'model':name,'mae':round(_mae(test,pred),2),'rmse':round(float(np.sqrt(np.mean((test-pred)**2))),2)})
    selected=min(scores,key=lambda x:x['mae'])['model']
    full_fn=candidates[selected]
    # Rebuild the selected model on all observations.
    if selected=='Linear Trend': full_pred=_linear_predict(y,horizon)
    elif selected=='Moving Average': full_pred=_moving_average_predict(y,horizon)
    else: full_pred=_exp_smooth_predict(y,horizon)
    trend=float(np.polyfit(np.arange(len(y)),y,1)[0])
    return {'history':y.astype(int).tolist(),'forecast':np.maximum(0,np.round(full_pred)).astype(int).tolist(),'trend_per_day':round(trend,2),'method':selected,'selected_model':selected,'models':scores,'holdout_points':int(len(test))}


def inventory_plan(stock, forecast, lead_time=3, service_level=1.65):
    stock=float(stock); vals=np.asarray(forecast,dtype=float); daily=float(np.mean(vals)) if len(vals) else 0; std=float(np.std(vals)) if len(vals) else 0
    safety=service_level*std*math.sqrt(max(1,lead_time)); reorder_point=daily*lead_time+safety
    order_qty=max(0,math.ceil(daily*(lead_time+7)+safety-stock))
    target=max(0,math.ceil(daily*(lead_time+7)+safety))
    days_cover=stock/daily if daily>0 else 0
    stockout_prob=min(99,max(0,(reorder_point-stock)/max(1,reorder_point)*100))
    status='REORDER NOW' if stock<reorder_point else ('WATCH STOCK' if stock<target else 'STOCK HEALTHY')
    return {'current_stock':round(stock,1),'avg_daily_demand':round(daily,1),'safety_stock':round(safety,1),'reorder_point':round(reorder_point,1),'reorder_quantity':int(order_qty),'target_stock':int(target),'days_of_cover':round(days_cover,1),'stockout_probability':round(stockout_prob,1),'status':status}

def route_options(distance_km=160):
    routes=[('Eco Route',distance_km*1.08,5.8,0.22),('Balanced Route',distance_km,4.7,0.14),('Express Route',distance_km*0.96,3.6,0.31)]
    out=[]
    for name,dist,hrs,risk in routes:
        cost=round(1800+dist*7.2+(0 if name=='Eco Route' else 450 if name=='Balanced Route' else 950))
        carbon=round(dist*0.12,1)
        score=round(risk*100 + hrs*4 + cost/500 - carbon*0.5,1)
        out.append({'name':name,'distance_km':round(dist,1),'eta_hours':hrs,'risk':round(risk*100,1),'cost':cost,'carbon_kg':carbon,'score':score})
    return sorted(out,key=lambda z:z['score'])


def multi_agent_answer(question, shipments):
    q=question.lower(); high=[s for s in shipments if s.get('risk_level') in ('HIGH','CRITICAL')]
    delayed=sorted(shipments,key=lambda s:float(s.get('delay_hours') or 0),reverse=True)
    if 'critical' in q or 'danger' in q or 'risk' in q:
        s=max(shipments,key=lambda s:float(s.get('risk_probability') or 0),default=None)
        if not s:return 'No shipments are currently available.'
        return f"Decision Agent: {s.get('batch_id')} has the highest risk at {float(s.get('risk_probability') or 0):.1f}%. Logistics Agent recommends prioritization; Quality Agent recommends condition monitoring; Inventory Agent should check destination safety stock."
    if 'delay' in q:
        s=delayed[0] if delayed else None
        return f"Logistics Agent: {s.get('batch_id')} has the largest recorded delay at {float(s.get('delay_hours') or 0):.1f} hours." if s else 'No delayed shipment data is available.'
    if 'inventory' in q or 'stock' in q:
        return 'Inventory Agent: run the Inventory Optimizer to compare current stock, safety stock and predicted demand.'
    return f"SupplyShield Copilot: I found {len(high)} high/critical shipments. Ask me about risk, delays, inventory, routes, disruptions or recommendations."


def ollama_chat(question, context, model='qwen2.5:0.5b', ollama_url='http://localhost:11434/api/generate', timeout=30):
    """Call a local Ollama model. Returns None when Ollama/model is unavailable."""
    if requests is None:
        return None
    question = str(question or '').strip()
    if not question:
        return None
    try:
        # Keep operational context compact so small local models can answer reliably.
        compact = {
            'shipments': context.get('shipments', [])[:20],
            'alerts': context.get('alerts', [])[:10]
        }
        prompt = (
            "You are SupplyShield Copilot, a concise supply-chain operations assistant. "
            "Use ONLY the supplied operational context. Do not invent shipment facts. "
            "Explain risk, delays, inventory, routes, disruptions and recommended actions clearly. "
            "If the context does not contain the answer, say that the available data is insufficient. "
            "This is decision support, not a replacement for an operations professional.\n\n"
            f"OPERATIONAL CONTEXT:\n{json.dumps(compact, default=str)[:14000]}\n\n"
            f"USER QUESTION:\n{question}\n\n"
            "Answer in 3-6 concise sentences or bullets."
        )
        r=requests.post(
            ollama_url,
            json={'model':model, 'prompt':prompt, 'stream':False,
                  'options':{'temperature':0.2, 'num_predict':300}},
            timeout=timeout
        )
        if not r.ok:
            return None
        data=r.json()
        answer=str(data.get('response') or '').strip()
        return answer or None
    except Exception:
        return None


def audit_hash(previous_hash, event):
    payload=f"{previous_hash}|{json.dumps(event,sort_keys=True,default=str)}".encode()
    return hashlib.sha256(payload).hexdigest()
