import math, json, statistics
from datetime import datetime, timedelta
import numpy as np

FEATURES=['thermal_temp','room_temperature','humidity','expiry_hours','oob_hours','delay_hours','refrigeration_hours','freezer_hours']

def anomaly_detection(history):
    """Robust z-score anomaly detection over telemetry; safe with short histories."""
    if not history: return {'anomaly':False,'score':0,'reasons':[]}
    reasons=[]; score=0.0
    for field,label in [('temperature','Temperature'),('humidity','Humidity')]:
        vals=[float(x.get(field) or 0) for x in history if x.get(field) is not None]
        if len(vals)>=4:
            med=statistics.median(vals); mad=statistics.median([abs(v-med) for v in vals]) or .25
            z=abs(vals[0]-med)/(1.4826*mad)
            if z>3: reasons.append(f'{label} telemetry deviates sharply from recent baseline'); score=max(score,min(100,z*18))
    if len(history)>=2:
        jump=abs(float(history[0].get('temperature') or 0)-float(history[1].get('temperature') or 0))
        if jump>=4: reasons.append(f'Rapid temperature change of {jump:.1f}°C detected'); score=max(score,min(100,jump*12))
    return {'anomaly':bool(reasons),'score':round(score,1),'reasons':reasons or ['Telemetry is within recent operating pattern']}

def forecast_risk(data, assess_fn, hours=6):
    """Scenario forecast based on current thermal trend and delay exposure."""
    temp=float(data.get('thermal_temp',4) or 4); room=float(data.get('room_temperature',22) or 22)
    delay=float(data.get('delay_hours',0) or 0); oob=float(data.get('oob_hours',0) or 0)
    refrigeration=float(data.get('refrigeration_hours',0) or 0)
    warming=max(0.15,min(1.15,(room-temp)*0.035 + delay*0.06 - refrigeration*0.004))
    points=[]; violation=None
    for h in range(0,hours+1):
        d=dict(data); d['thermal_temp']=round(temp+warming*h,2); d['delay_hours']=delay+h
        d['oob_hours']=oob+max(0,h-1) if d['thermal_temp']>8 else oob
        a=assess_fn(d); points.append({'hour':h,'temperature':d['thermal_temp'],'risk':round(float(a['risk_probability']),1),'level':a['risk_level']})
        if violation is None and (d['thermal_temp']>8 or a['risk_probability']>=70): violation=h
    return {'points':points,'violation_hour':violation,'message':('No critical violation predicted in forecast window' if violation is None else f'Potential cold-chain violation in approximately {violation} hour(s)')}

def intervention_optimizer(data, assess_fn):
    base=assess_fn(data); actions=[
      ('Continue current route',{},0,0,0.3),
      ('Emergency active cooling',{'thermal_temp':max(2,float(data.get('thermal_temp',4))-4),'oob_hours':max(0,float(data.get('oob_hours',0))-1)},2200,.5,1.6),
      ('Reroute to faster corridor',{'delay_hours':max(0,float(data.get('delay_hours',0))-2)},3100,1.0,2.2),
      ('Transfer to nearby cold storage',{'thermal_temp':4,'oob_hours':0,'refrigeration_hours':float(data.get('refrigeration_hours',0))+4,'delay_hours':max(0,float(data.get('delay_hours',0))-.5)},1800,1.1,.8),
      ('Priority dispatch + cooling',{'thermal_temp':5,'delay_hours':max(0,float(data.get('delay_hours',0))-2),'oob_hours':max(0,float(data.get('oob_hours',0))-.5)},2700,.6,1.8)
    ]
    out=[]
    for name,changes,cost,delay,carbon in actions:
        d=dict(data); d.update(changes); a=assess_fn(d); risk=float(a['risk_probability'])
        benefit=float(base['risk_probability'])-risk
        utility=benefit*1.2-cost/250-delay*5-carbon*2
        out.append({'action':name,'risk':round(risk,1),'risk_reduction':round(benefit,1),'cost_inr':cost,'delay_hours':delay,'carbon_index':carbon,'utility':round(utility,1),'changes':changes})
    out.sort(key=lambda x:x['utility'],reverse=True)
    for i,x in enumerate(out): x['recommended']=(i==0)
    return {'baseline_risk':round(float(base['risk_probability']),1),'options':out,'recommended':out[0]}

def counterfactual(data, assess_fn, target=30):
    base=float(assess_fn(data)['risk_probability']); candidates=[]
    for temp in np.arange(min(float(data.get('thermal_temp',4)),8),1.9,-.5):
        d=dict(data); d['thermal_temp']=round(float(temp),1); a=assess_fn(d)
        if a['risk_probability']<=target: candidates.append(('thermal_temp',d['thermal_temp'],a['risk_probability'])); break
    for delay in np.arange(max(0,float(data.get('delay_hours',0))),-0.1,-.5):
        d=dict(data); d['delay_hours']=round(float(delay),1); a=assess_fn(d)
        if a['risk_probability']<=target: candidates.append(('delay_hours',d['delay_hours'],a['risk_probability'])); break
    d=dict(data); d.update({'thermal_temp':4,'oob_hours':0,'delay_hours':max(0,float(data.get('delay_hours',0))-2)})
    combined=assess_fn(d)
    return {'baseline_risk':round(base,1),'target_risk':target,'single_changes':[{'feature':a,'value':b,'resulting_risk':round(float(c),1)} for a,b,c in candidates], 'recommended_changes':{'thermal_temp':4,'oob_hours':0,'delay_hours':d['delay_hours']},'resulting_risk':round(float(combined['risk_probability']),1)}

def root_cause(data, assessment):
    factors=[]
    rules=[('Temperature excursion',max(0,float(data.get('thermal_temp',4))-8)*9),('Out-of-bound exposure',float(data.get('oob_hours',0))*12),('Transport delay',float(data.get('delay_hours',0))*7),('Humidity stress',max(0,float(data.get('humidity',60))-75)*1.2),('Low remaining shelf life',max(0,48-float(data.get('expiry_hours',120)))*.7)]
    for n,s in rules:
        if s>0: factors.append({'cause':n,'impact':round(min(100,s),1)})
    factors.sort(key=lambda x:x['impact'],reverse=True)
    return {'incident':assessment.get('risk_level')+' supply-chain risk','primary_cause':factors[0]['cause'] if factors else 'No dominant excursion','factors':factors[:4],'generated_at':datetime.now().isoformat(timespec='seconds')}
