from flask import Flask, render_template, request, jsonify, send_file
from datetime import datetime
from pathlib import Path
import pandas as pd, numpy as np, json, os
from config import DATASET_PATH, DB_PATH, OLLAMA_URL, OLLAMA_HOST, OLLAMA_MODEL, OLLAMA_TIMEOUT
from database.db import init_db, init_phase7, init_ops8, upsert_shipment, add_telemetry, add_alert, add_simulation, add_audit, save_passport, rows, connect, add_event, add_notification
from utils.risk_engine import assess, recommendation
from utils.explainability import explain
from utils.report import make_report
from utils.advanced_ai import cv_inspect, disruption_scenario, demand_forecast, inventory_plan, route_options, multi_agent_answer, ollama_chat
from utils.live_tracking import build_live_shipments, live_summary
from utils.decision_center import build_decisions, summary as decision_summary
from utils.phase7 import anomaly_detection, forecast_risk, intervention_optimizer, counterfactual, root_cause
from utils.recovery_engine import excursion_index, recommended_actions, rank_resources, rank_resources_from_coords, simulate_intervention

app=Flask(__name__); app.secret_key='supplyshield-local'
init_db(); init_phase7(); init_ops8()


def dataset_latest():
    df=pd.read_csv(DATASET_PATH); df=df.drop(columns=['Unnamed: 0'],errors='ignore'); df['date']=pd.to_datetime(df['date'],dayfirst=True,errors='coerce')
    df=df.sort_values(['batch_id','date']); return df.groupby('batch_id',as_index=False).tail(1)


def enhanced_analytics():
    """Prepare presentation-ready analytics from the richer demo dataset.
    Proxy labels are explicitly treated as demonstration labels, not audited loss events.
    """
    p=Path(DATASET_PATH).parent/'enhanced_supply_chain.csv'
    if not p.exists():
        return {}
    df=pd.read_csv(p)
    df['date']=pd.to_datetime(df['date'],errors='coerce')
    df['month']=df['date'].dt.to_period('M').astype(str)
    # Executive aggregates
    monthly=(df.groupby('month',as_index=False)
        .agg(avg_risk=('risk_score','mean'),shipments=('batch_id','nunique'),
             compliance=('cold_chain_compliance_pct','mean'),delay=('delay_hours','mean')))
    regional=(df.groupby('state',as_index=False).agg(
        avg_risk=('risk_score','mean'),shipments=('batch_id','nunique'),
        compliance=('cold_chain_compliance_pct','mean')).sort_values('avg_risk',ascending=False).head(8))
    mode=(df.groupby('transport_mode',as_index=False).agg(
        avg_risk=('risk_score','mean'),shipments=('batch_id','nunique'),
        delay=('delay_hours','mean')).sort_values('avg_risk',ascending=False))
    levels=df['risk_level'].value_counts().reindex(['LOW','MODERATE','HIGH','CRITICAL']).fillna(0)
    outcomes=df['quality_event_proxy'].value_counts().reindex([0,1]).fillna(0)
    # compact sample for scatter: distance vs risk, one point per selected row
    sample=df[['route_distance_km','risk_score','delay_hours','cold_chain_compliance_pct']].dropna()
    if len(sample)>180:
        sample=sample.sample(180,random_state=42)
    return {
        'records':int(len(df)),
        'batches':int(df['batch_id'].nunique()),
        'avg_risk':round(float(df['risk_score'].mean()),1),
        'compliance':round(float(df['cold_chain_compliance_pct'].mean()),1),
        'on_time':round(float(df['on_time_delivery'].mean()*100),1),
        'proxy_events':int(df['quality_event_proxy'].sum()),
        'interventions':int((df['intervention_required']=='YES').sum()),
        'levels':{k:int(v) for k,v in levels.items()},
        'monthly':[
            {'month':r['month'],'risk':round(float(r['avg_risk']),1),'shipments':int(r['shipments']),
             'compliance':round(float(r['compliance']),1),'delay':round(float(r['delay']),1)}
            for _,r in monthly.iterrows()],
        'regional':[{'state':r['state'],'risk':round(float(r['avg_risk']),1),'shipments':int(r['shipments']),
                     'compliance':round(float(r['compliance']),1)} for _,r in regional.iterrows()],
        'modes':[{'mode':r['transport_mode'],'risk':round(float(r['avg_risk']),1),'delay':round(float(r['delay']),1),
                  'shipments':int(r['shipments'])} for _,r in mode.iterrows()],
        'scatter':[{'distance':round(float(r['route_distance_km']),1),'risk':round(float(r['risk_score']),1),
                    'delay':round(float(r['delay_hours']),1),'compliance':round(float(r['cold_chain_compliance_pct']),1)}
                   for _,r in sample.iterrows()],
        'proxy_events_split':{'No event':int(outcomes.get(0,0)),'Proxy event':int(outcomes.get(1,0))}
    }

def row_to_input(x):
    return {'batch_id':str(x.get('batch_id','')), 'product':'Temperature-sensitive goods', 'location':str(x.get('location','')), 'logistics_stage':str(x.get('current_hop','')), 'thermal_temp':x.get('thermal_shipper_temp_reading',4), 'room_temperature':x.get('room_temp_reading',22), 'humidity':x.get('room_humidity_reading',60), 'expiry_hours':x.get('item_expiry_hours',120), 'oob_hours':x.get('out_of_bound_temperature_hours',0), 'freezer_hours':x.get('ultra_low_temperature_freezer_hours',0), 'refrigeration_hours':x.get('refrigeration_temperature_hours',0), 'external_storage':str(x.get('external_storage','No'))}

def enrich(r):
    a=assess(r); r.update(a); r['recommendations']=[x[0]+' — '+x[1] for x in recommendation(a)]; r['explanation']=explain(a); return r

@app.route('/')
def home(): return render_template('index.html')
@app.route('/dashboard')
def dashboard():
    latest=dataset_latest(); assessments=[]
    for _,x in latest.iterrows(): assessments.append(enrich(row_to_input(x)))
    n=len(assessments); high=sum(x['risk_level'] in ['HIGH','CRITICAL'] for x in assessments)
    avg=round(sum(x['risk_probability'] for x in assessments)/n,1) if n else 0
    recent=rows('SELECT * FROM shipments ORDER BY updated_at DESC LIMIT 8')
    analytics=enhanced_analytics()
    return render_template('dashboard.html',kpis={'shipments':analytics.get('batches',n),'high':analytics.get('levels',{}).get('HIGH',0)+analytics.get('levels',{}).get('CRITICAL',0),
        'avg':analytics.get('avg_risk',avg),'preventable':analytics.get('interventions',round(high*0.68))},
        recent=recent,analytics=analytics)
@app.route('/risk-intelligence')
def intelligence(): return render_template('intelligence.html')
@app.route('/digital-twin')
def twin(): return render_template('digital_twin.html',shipments=rows('SELECT * FROM shipments ORDER BY updated_at DESC'))
@app.route('/simulator')
def simulator(): return render_template('simulator.html',shipments=rows('SELECT * FROM shipments ORDER BY updated_at DESC'))
@app.route('/analytics')
def analytics():
    data=enhanced_analytics()
    if not data:
        data={'records':0,'batches':0,'avg_risk':0,'compliance':0,'on_time':0,'proxy_events':0,'interventions':0,
              'levels':{'LOW':0,'MODERATE':0,'HIGH':0,'CRITICAL':0},'monthly':[],'regional':[],'modes':[],'scatter':[],'proxy_events_split':{}}
    return render_template('analytics.html',data=data)
@app.get('/api/analytics')
def api_analytics():
    return jsonify(enhanced_analytics())
@app.route('/alerts')
def alerts():
    items=rows('SELECT * FROM alerts ORDER BY created_at DESC LIMIT 60')
    stats={'open':sum(str(x.get('status') or 'OPEN')!='RESOLVED' for x in items),'critical':sum(str(x.get('severity') or '').upper()=='CRITICAL' for x in items),'resolved':sum(str(x.get('status') or '')=='RESOLVED' for x in items)}
    return render_template('alerts.html',alerts=items,stats=stats)
@app.route('/shipments')
def shipments(): return render_template('shipments.html',shipments=rows('SELECT * FROM shipments ORDER BY updated_at DESC'))

@app.route('/shipment/<batch_id>')
def shipment_detail(batch_id):
    found=rows('SELECT * FROM shipments WHERE batch_id=?',(batch_id,))
    if not found: return 'Shipment not found',404
    live=build_live_shipments(found)
    return render_template('shipment_detail.html',shipment=found[0],live=(live[0] if live else {}),telemetry=rows('SELECT * FROM telemetry WHERE batch_id=? ORDER BY recorded_at DESC LIMIT 40',(batch_id,)),alerts=rows('SELECT * FROM alerts WHERE batch_id=? ORDER BY created_at DESC LIMIT 20',(batch_id,)),events=rows('SELECT * FROM shipment_events WHERE batch_id=? ORDER BY created_at DESC LIMIT 40',(batch_id,)),actions=rows('SELECT * FROM alert_actions WHERE batch_id=? ORDER BY created_at DESC LIMIT 30',(batch_id,)),twin=rows('SELECT * FROM twin_states WHERE batch_id=? ORDER BY created_at DESC LIMIT 10',(batch_id,)))

@app.route('/system-health')
def system_health():
    health={'database':'CONNECTED','db_path':str(DB_PATH),'shipments':rows('SELECT COUNT(*) n FROM shipments')[0]['n'],'telemetry':rows('SELECT COUNT(*) n FROM telemetry')[0]['n'],'open_alerts':rows("SELECT COUNT(*) n FROM alerts WHERE COALESCE(status,'OPEN')!='RESOLVED'")[0]['n'],'devices':rows("SELECT COUNT(*) n FROM devices WHERE status='Connected'")[0]['n']}
    return render_template('system_health.html',health=health)

@app.get('/api/notifications')
def api_notifications():
    return jsonify({'unread':rows('SELECT COUNT(*) n FROM notifications WHERE read_flag=0')[0]['n'],'items':rows('SELECT * FROM notifications ORDER BY created_at DESC LIMIT 20')})

@app.post('/api/notifications/<int:nid>/read')
def read_notification(nid):
    with connect() as c:c.execute('UPDATE notifications SET read_flag=1 WHERE id=?',(nid,));c.commit()
    return jsonify({'ok':True})
@app.route('/reports')
def reports(): return render_template('reports.html')
@app.route('/live-tracking')
def live_tracking():
    live=build_live_shipments(rows('SELECT * FROM shipments ORDER BY risk_probability DESC'))
    return render_template('live_tracking.html', live=live, summary=live_summary(live))

@app.route('/control-tower')
def control_tower():
    ships=rows('SELECT * FROM shipments ORDER BY risk_probability DESC')
    return render_template('control_tower.html',shipments=ships,alerts=rows('SELECT * FROM alerts ORDER BY created_at DESC LIMIT 12'))
@app.route('/ai-lab')
def ai_lab(): return render_template('ai_lab.html')


@app.route('/ai-7')
def phase7_lab(): return render_template('phase7.html')

@app.route('/governance')
def governance():
    return render_template('governance.html',devices=rows('SELECT * FROM devices ORDER BY device_id'),outcomes=rows('SELECT * FROM intervention_outcomes ORDER BY id DESC LIMIT 50'))

@app.post('/api/phase7/analyze')
def phase7_analyze():
    data=request.get_json(silent=True) or {}
    assessment=enrich(dict(data))
    history=rows('SELECT * FROM telemetry WHERE batch_id=? ORDER BY recorded_at DESC LIMIT 20',(data.get('batch_id',''),))
    result={'assessment':assessment,'forecast':forecast_risk(data,assess,6),'anomaly':anomaly_detection(history),
            'optimizer':intervention_optimizer(data,assess),'counterfactual':counterfactual(data,assess,30),
            'root_cause':root_cause(data,assessment),'explanation':assessment.get('explanation')}
    add_audit('AI7_DECISION',data.get('batch_id','DEMO'),{'risk':assessment['risk_probability'],'recommended':result['optimizer']['recommended']})
    return jsonify(result)

@app.post('/api/intervention-outcome')
def intervention_outcome():
    d=request.get_json(silent=True) or {}; now=datetime.now().isoformat(timespec='seconds')
    with connect() as c:
        c.execute('INSERT INTO intervention_outcomes(batch_id,action,baseline_risk,predicted_risk,actual_risk,status,user_email,created_at) VALUES(?,?,?,?,?,?,?,?)',
                  (d.get('batch_id'),d.get('action'),d.get('baseline_risk'),d.get('predicted_risk'),d.get('actual_risk'),d.get('status','RECORDED'),d.get('user_email','demo@supplyshield.local'),now)); c.commit()
    add_audit('INTERVENTION_OUTCOME',d.get('batch_id',''),d); return jsonify({'ok':True})

@app.post('/api/alerts/<int:alert_id>/action')
def alert_action(alert_id):
    d=request.get_json(silent=True) or {}; action=str(d.get('action','ACKNOWLEDGED')).upper(); now=datetime.now().isoformat(timespec='seconds')
    found=rows('SELECT * FROM alerts WHERE id=?',(alert_id,)); batch=found[0]['batch_id'] if found else ''
    status={'ACKNOWLEDGED':'ACKNOWLEDGED','INVESTIGATE':'INVESTIGATING','TAKE_ACTION':'ACTION_TAKEN','ESCALATE':'ESCALATED','RESOLVE':'RESOLVED'}.get(action,action)
    with connect() as c:
        c.execute('UPDATE alerts SET acknowledged=?,status=?,assigned_to=?,resolved_at=? WHERE id=?',(1 if action!='ESCALATE' else 0,status,d.get('user_email','demo@supplyshield.local'),now if action=='RESOLVE' else None,alert_id))
        c.execute('INSERT INTO alert_actions(alert_id,batch_id,action,user_email,note,created_at) VALUES(?,?,?,?,?,?)',(alert_id,batch,action,d.get('user_email','demo@supplyshield.local'),d.get('note',''),now)); c.commit()
    add_event(batch,'ALERT_ACTION',f'Alert {status.replace("_"," ").title()}',d.get('note',''), 'INFO' if action=='RESOLVE' else 'HIGH')
    add_notification(batch,f'Alert {status.replace("_"," ").title()}',d.get('note') or f'Alert #{alert_id} updated','INFO',f'/shipment/{batch}')
    add_audit('ALERT_'+action,batch,{'alert_id':alert_id,'status':status}); return jsonify({'ok':True,'action':action,'status':status})

@app.post('/api/twin/<batch_id>/simulate')
def twin_simulate(batch_id):
    found=rows('SELECT * FROM shipments WHERE batch_id=?',(batch_id,))
    if not found:return jsonify({'error':'Shipment not found'}),404
    d=request.get_json(silent=True) or {}; base=dict(found[0]); base_input={'batch_id':batch_id,'thermal_temp':base.get('thermal_temp') or 4,'room_temperature':base.get('room_temperature') or 22,'humidity':base.get('humidity') or 60,'expiry_hours':base.get('expiry_hours') or 48,'oob_hours':base.get('oob_hours') or 0,'freezer_hours':base.get('freezer_hours') or 0,'refrigeration_hours':base.get('refrigeration_hours') or 0,'delay_hours':base.get('delay_hours') or 0,'external_storage':'No'}
    baseline=enrich(dict(base_input)); sim=dict(base_input)
    sim['thermal_temp']=float(d.get('temperature',sim['thermal_temp'])); sim['delay_hours']=float(d.get('delay_hours',sim['delay_hours']))
    if d.get('cooling'): sim['thermal_temp']=max(2.0,sim['thermal_temp']-3.0)
    result=enrich(sim); action=d.get('action') or ('Emergency cooling' if d.get('cooling') else 'Scenario simulation')
    now=datetime.now().isoformat(timespec='seconds')
    with connect() as c:c.execute('INSERT INTO twin_states(batch_id,scenario,baseline_risk,simulated_risk,temperature,delay_hours,action,created_at) VALUES(?,?,?,?,?,?,?,?)',(batch_id,d.get('scenario','WHAT_IF'),baseline['risk_probability'],result['risk_probability'],sim['thermal_temp'],sim['delay_hours'],action,now));c.commit()
    add_event(batch_id,'DIGITAL_TWIN','Digital twin simulation completed',f"{baseline['risk_probability']:.1f}% → {result['risk_probability']:.1f}% using {action}")
    return jsonify({'baseline':baseline,'simulated':result,'action':action,'risk_reduction':round(baseline['risk_probability']-result['risk_probability'],1)})


@app.route('/support-center')
def support_center():
    ships=rows('SELECT * FROM shipments ORDER BY risk_probability DESC')
    return render_template('support_center.html',shipments=ships)

@app.get('/api/support/<batch_id>')
def api_support(batch_id):
    found=rows('SELECT * FROM shipments WHERE batch_id=?',(batch_id,))
    if not found:return jsonify({'error':'Shipment not found'}),404
    live=build_live_shipments(found); current=live[0] if live else {}
    origin=(current.get('lat'),current.get('lon')) if current.get('lat') is not None else None
    resources=rows('SELECT * FROM recovery_resources WHERE active=1')
    ranked=rank_resources_from_coords(origin,dict(found[0]),resources)
    return jsonify({'shipment':found[0],'current':current,'resources':ranked,'mode':'SIMULATION','note':'Shipment GPS movement is simulated for academic demonstration. Resource records are demo/partner-style records and availability must be verified in production.'})

@app.post('/api/support/<batch_id>/route')
def start_support_route(batch_id):
    d=request.get_json(silent=True) or {}; code=d.get('resource_code')
    found=rows('SELECT * FROM shipments WHERE batch_id=?',(batch_id,)); rr=rows('SELECT * FROM recovery_resources WHERE resource_code=? AND active=1',(code,))
    if not found or not rr:return jsonify({'error':'Shipment or support resource not found'}),404
    live=build_live_shipments(found); cur=live[0] if live else {}; start=(cur.get('lat'),cur.get('lon')); dest=(float(rr[0]['latitude']),float(rr[0]['longitude']))
    from utils.recovery_engine import haversine_km
    dist=haversine_km(start,dest) if start[0] is not None else None; eta=max(1,round((dist or 1)/35*60)); now=datetime.now().isoformat(timespec='seconds')
    with connect() as c:
        c.execute("UPDATE support_routes SET status='CANCELLED' WHERE batch_id=? AND status='IN_PROGRESS'",(batch_id,))
        c.execute('INSERT INTO support_routes(batch_id,resource_code,start_lat,start_lon,dest_lat,dest_lon,distance_km,eta_min,status,progress,started_at,created_by) VALUES(?,?,?,?,?,?,?,?,?,?,?,?)',(batch_id,code,start[0],start[1],dest[0],dest[1],dist,eta,'IN_PROGRESS',0,now,d.get('user_email','demo@supplyshield.local'))); c.commit()
        route_id=c.execute('SELECT LAST_INSERT_ID() id').fetchone()['id']
    add_event(batch_id,'SUPPORT_ROUTE','Recovery destination assigned',f"Routing to {rr[0]['name']} · {round(dist or 0,1)} km · ETA {eta} min",'HIGH')
    add_audit('SUPPORT_ROUTE_ASSIGNED',batch_id,{'resource_code':code,'distance_km':dist,'eta_min':eta})
    return jsonify({'ok':True,'route_id':route_id,'resource':rr[0],'distance_km':round(dist or 0,1),'eta_min':eta})

@app.get('/api/support-route/<int:route_id>')
def support_route_status(route_id):
    r=rows('SELECT * FROM support_routes WHERE id=?',(route_id,))
    if not r:return jsonify({'error':'Route not found'}),404
    x=dict(r[0]); started=datetime.fromisoformat(x['started_at']); elapsed=max(0,(datetime.now()-started).total_seconds())
    # Accelerated demo: full journey in 90 seconds; replace with GPS/MQTT in production.
    progress=min(1.0,elapsed/90.0); lat=float(x['start_lat'])+(float(x['dest_lat'])-float(x['start_lat']))*progress; lon=float(x['start_lon'])+(float(x['dest_lon'])-float(x['start_lon']))*progress
    status='ARRIVED' if progress>=1 else 'IN_PROGRESS'; remaining=max(0,round(float(x['eta_min'])*(1-progress)))
    if status=='ARRIVED' and x['status']!='ARRIVED':
        now=datetime.now().isoformat(timespec='seconds')
        with connect() as c:c.execute("UPDATE support_routes SET status='ARRIVED',progress=100,arrived_at=? WHERE id=?",(now,route_id));c.commit()
        add_event(x['batch_id'],'SUPPORT_ARRIVAL','Shipment reached recovery support destination',f"Route #{route_id} completed",'INFO')
    return jsonify({'route_id':route_id,'batch_id':x['batch_id'],'resource_code':x['resource_code'],'lat':round(lat,6),'lon':round(lon,6),'dest_lat':x['dest_lat'],'dest_lon':x['dest_lon'],'progress':round(progress*100,1),'status':status,'eta_remaining_min':remaining,'mode':'SIMULATION'})

@app.route('/recovery-intelligence')
def recovery_intelligence():
    ships=rows('SELECT * FROM shipments ORDER BY risk_probability DESC')
    return render_template('recovery_intelligence.html',shipments=ships)

@app.get('/api/recovery/<batch_id>')
def api_recovery(batch_id):
    found=rows('SELECT * FROM shipments WHERE batch_id=?',(batch_id,))
    if not found:return jsonify({'error':'Shipment not found'}),404
    ship=dict(found[0]); resources=rows('SELECT * FROM recovery_resources WHERE active=1')
    return jsonify({'shipment':ship,'excursion':excursion_index(ship),'actions':recommended_actions(ship),'resources':rank_resources(ship,resources),'note':'Bundled recovery resources are demonstration records. Verify real-world availability before dispatch.'})

@app.post('/api/recovery/<batch_id>/simulate')
def api_recovery_simulate(batch_id):
    found=rows('SELECT * FROM shipments WHERE batch_id=?',(batch_id,))
    if not found:return jsonify({'error':'Shipment not found'}),404
    d=request.get_json(silent=True) or {}; result=simulate_intervention(dict(found[0]),d.get('action_code'),assess)
    result['action_code']=str(d.get('action_code') or 'MONITOR').upper(); result['resource_code']=d.get('resource_code')
    return jsonify(result)

@app.post('/api/recovery/<batch_id>/plan')
def api_recovery_plan(batch_id):
    found=rows('SELECT * FROM shipments WHERE batch_id=?',(batch_id,))
    if not found:return jsonify({'error':'Shipment not found'}),404
    d=request.get_json(silent=True) or {}; action=str(d.get('action_code') or 'MONITOR').upper(); sim=simulate_intervention(dict(found[0]),action,assess); now=datetime.now().isoformat(timespec='seconds')
    status='APPROVED' if d.get('approve') else 'PROPOSED'
    with connect() as c:
        c.execute('INSERT INTO recovery_plans(batch_id,action_code,resource_code,baseline_risk,predicted_risk,risk_reduction,predicted_status,status,approved_by,created_at,updated_at) VALUES(?,?,?,?,?,?,?,?,?,?,?)',(batch_id,action,d.get('resource_code'),sim['before']['risk_probability'],sim['after']['risk_probability'],sim['risk_reduction'],sim['predicted_status'],status,d.get('approved_by','demo@supplyshield.local') if status=='APPROVED' else None,now,now));c.commit()
    add_event(batch_id,'RECOVERY_PLAN',f'Recovery plan {status.lower()}',f"{action}: {sim['before']['risk_probability']:.1f}% → {sim['after']['risk_probability']:.1f}%",'INFO')
    add_audit('RECOVERY_PLAN_'+status,batch_id,{'action':action,'resource_code':d.get('resource_code'),'risk_reduction':sim['risk_reduction']})
    return jsonify({'ok':True,'status':status,'simulation':sim})

@app.route('/decision-center')
def decision_center():
    live=build_live_shipments(rows('SELECT * FROM shipments ORDER BY risk_probability DESC'))
    decisions=build_decisions(live)
    return render_template('decision_center.html', decisions=decisions, summary=decision_summary(decisions))
@app.route('/passport/<batch_id>')
def passport(batch_id):
    found=rows('SELECT * FROM product_passports WHERE batch_id=?',(batch_id,))
    return jsonify(json.loads(found[0]['passport_json'])) if found else (jsonify({'error':'Passport not found'}),404)

@app.post('/api/assess')
def api_assess():
    data=request.get_json(silent=True) or {}; data=enrich(data); return jsonify(data)
@app.post('/api/register')
def api_register():
    data=request.get_json(silent=True) or {}; data=enrich(data); upsert_shipment(data); add_telemetry(data)
    if data['risk_level'] in ('HIGH','CRITICAL'):
        add_alert(data['batch_id'],data['risk_level'],'Elevated supply risk',f"Overall risk is {data['risk_probability']:.1f}%.")
        add_notification(data['batch_id'],'Elevated supply risk',f"AI risk reached {data['risk_probability']:.1f}%",data['risk_level'])
    add_event(data['batch_id'],'SHIPMENT_UPDATE','Shipment assessment updated',f"Risk {data['risk_probability']:.1f}% · {data['risk_level']}",data['risk_level'])
    return jsonify({'ok':True,'shipment':data})
@app.post('/api/simulate')
def api_simulate():
    data=request.get_json(silent=True) or {}; base=enrich(data); sim_inputs=dict(data); sim=enrich(sim_inputs); sim['simulated_from']=base['risk_probability']; add_simulation(data.get('batch_id','SIMULATION'),base['risk_probability'],sim['risk_probability'],sim_inputs); return jsonify({'baseline':base,'simulated':sim,'reduction':round(base['risk_probability']-sim['risk_probability'],2)})
@app.get('/api/shipment/<batch_id>')
def api_shipment(batch_id):
    found=rows('SELECT * FROM shipments WHERE batch_id=?',(batch_id,));
    if not found: return jsonify({'error':'Shipment not found'}),404
    return jsonify(found[0])
@app.get('/api/history/<batch_id>')
def api_history(batch_id): return jsonify(rows('SELECT * FROM telemetry WHERE batch_id=? ORDER BY recorded_at DESC LIMIT 30',(batch_id,)))
@app.post('/api/report')
def api_report():
    data=request.get_json(silent=True) or {}; data=enrich(data); out=Path('reports')/f"SupplyShield_{data.get('batch_id','assessment')}.pdf"; out.parent.mkdir(exist_ok=True); make_report(out,data,data); return jsonify({'url':'/download-report/'+out.name})
@app.get('/download-report/<name>')
def download(name):
    p=Path('reports')/name
    if not p.exists(): return 'Report not found',404
    return send_file(p,as_attachment=True,download_name=p.name)

@app.get('/api/live-tracking')
def api_live_tracking():
    live=build_live_shipments(rows('SELECT * FROM shipments ORDER BY risk_probability DESC'))
    return jsonify({'summary':live_summary(live),'shipments':live,'mode':'SIMULATION','note':'GPS positions, telemetry and weather risk are simulated for demonstration. Connect a GPS/MQTT source for production telemetry.'})

@app.get('/api/live-tracking/<batch_id>')
def api_live_tracking_one(batch_id):
    live=build_live_shipments(rows('SELECT * FROM shipments ORDER BY risk_probability DESC'))
    found=[x for x in live if x['batch_id']==batch_id]
    return jsonify(found[0]) if found else (jsonify({'error':'Shipment not found'}),404)

@app.get('/api/decision-center')
def api_decision_center():
    live=build_live_shipments(rows('SELECT * FROM shipments ORDER BY risk_probability DESC'))
    decisions=build_decisions(live)
    return jsonify({'summary':decision_summary(decisions),'decisions':decisions,'mode':'SIMULATION'})

@app.post('/api/decision-agent')
def api_decision_agent():
    data=request.get_json(silent=True) or {}
    question=str(data.get('question','What should we do right now?')).strip()
    live=build_live_shipments(rows('SELECT * FROM shipments ORDER BY risk_probability DESC'))
    decisions=build_decisions(live)
    context={'top_decisions':decisions[:5],'summary':decision_summary(decisions)}
    model=str(data.get('model') or OLLAMA_MODEL)
    answer=ollama_chat(question,context,model=model,ollama_url=OLLAMA_URL,timeout=OLLAMA_TIMEOUT)
    if not answer:
        top=decisions[0] if decisions else None
        answer=(f"Prioritize {top['batch_id']}: {top['action']}. Risk is {top['risk']}% with {top['temperature']}°C temperature and {top['shelf_life_hours']}h shelf life." if top else 'No active shipments require intervention.')
    return jsonify({'answer':answer,'provider':'Qwen via Ollama' if answer and 'Prioritize' not in answer else 'SupplyShield Local Fallback','top':decisions[:3]})

@app.get('/api/control-tower')
def api_control_tower():
    ships=rows('SELECT * FROM shipments ORDER BY risk_probability DESC')
    return jsonify({'shipments':ships,'alerts':rows('SELECT * FROM alerts WHERE acknowledged=0 ORDER BY created_at DESC LIMIT 20')})

@app.post('/api/copilot')
def api_copilot():
    data=request.get_json(silent=True) or {}
    q=str(data.get('question','')).strip()
    if not q:
        return jsonify({'answer':'Please enter a question about shipments, risk, delays, inventory or recommendations.',
                        'provider':'local'}), 400
    ships=rows('SELECT * FROM shipments ORDER BY risk_probability DESC LIMIT 30')
    context={'shipments':ships,'alerts':rows('SELECT * FROM alerts ORDER BY created_at DESC LIMIT 10')}
    model=str(data.get('model') or OLLAMA_MODEL)
    ollama_answer=ollama_chat(q,context,model=model,ollama_url=OLLAMA_URL, timeout=OLLAMA_TIMEOUT)
    answer=ollama_answer or multi_agent_answer(q,ships)
    return jsonify({'answer':answer,
                    'provider':'Qwen via Ollama' if ollama_answer else 'SupplyShield Local Fallback',
                    'model':model if ollama_answer else None})

@app.get('/api/ollama-status')
def api_ollama_status():
    import requests
    try:
        r=requests.get(OLLAMA_HOST.rstrip('/')+'/api/tags',timeout=3)
        if not r.ok:
            return jsonify({'online':False,'model':OLLAMA_MODEL,'message':'Ollama is not responding normally.'})
        models=[m.get('name','') for m in r.json().get('models',[])]
        installed=OLLAMA_MODEL in models or any(x.startswith(OLLAMA_MODEL.split(':')[0]+':') for x in models)
        return jsonify({'online':True,'model':OLLAMA_MODEL,'installed':installed,'models':models})
    except Exception as e:
        return jsonify({'online':False,'model':OLLAMA_MODEL,'installed':False,'models':[],'message':'Start Ollama to enable Qwen Copilot.'})

@app.post('/api/cv-inspect')
def api_cv_inspect():
    f=request.files.get('image'); batch=request.form.get('batch_id','CV-DEMO')
    if not f:return jsonify({'error':'Upload an image'}),400
    result=cv_inspect(f); rows_before=rows('SELECT * FROM cv_inspections WHERE batch_id=? ORDER BY id DESC LIMIT 1',(batch,))
    from database.db import connect
    with connect() as c:c.execute("INSERT INTO cv_inspections(batch_id,result_json,created_at) VALUES(?,?,datetime('now'))",(batch,json.dumps(result)));c.commit()
    add_audit('CV_INSPECTION',batch,result); return jsonify(result)

@app.post('/api/disruption')
def api_disruption():
    data=request.get_json(silent=True) or {}; result=disruption_scenario(data); add_audit('DISRUPTION_SIMULATION',data.get('batch_id','SCENARIO'),result); return jsonify(result)

@app.get('/api/forecast')
def api_forecast():
    raw=request.args.get('history',''); history=[float(x) for x in raw.split(',') if x.strip()] if raw else None; return jsonify(demand_forecast(history))

@app.post('/api/inventory-optimize')
def api_inventory():
    data=request.get_json(silent=True) or {}; f=data.get('forecast') or demand_forecast()['forecast']; result=inventory_plan(data.get('stock',0),f,data.get('lead_time',3)); return jsonify(result)

@app.get('/api/routes')
def api_routes(): return jsonify({'routes':route_options(float(request.args.get('distance',160)))})

@app.post('/api/passport')
def api_passport():
    data=request.get_json(silent=True) or {}; batch=data.get('batch_id','')
    found=rows('SELECT * FROM shipments WHERE batch_id=?',(batch,))
    if not found:return jsonify({'error':'Shipment not found'}),404
    history=rows('SELECT * FROM telemetry WHERE batch_id=? ORDER BY recorded_at',(batch,))
    events=rows('SELECT event_type,payload,event_hash,created_at FROM audit_log WHERE batch_id=? ORDER BY id',(batch,))
    payload={'passport_id':f'SSP-{batch}','batch_id':batch,'shipment':found[0],'telemetry_history':history,'audit_events':events,'generated_at':datetime.now().isoformat(timespec='seconds')}
    save_passport(batch,payload); add_audit('PASSPORT_UPDATED',batch,{'passport_id':payload['passport_id']}); return jsonify(payload)

@app.get('/api/audit/verify')
def api_audit_verify():
    events=rows('SELECT * FROM audit_log ORDER BY id'); prev='GENESIS'; valid=True
    import hashlib
    for e in events:
        expected=hashlib.sha256(f"{prev}|{e['event_type']}|{e['batch_id']}|{e['payload']}".encode()).hexdigest()
        if expected!=e['event_hash'] or e['previous_hash']!=prev: valid=False; break
        prev=e['event_hash']
    return jsonify({'valid':valid,'events':len(events),'verified_until':prev})




if __name__=='__main__':
    app.run(debug=True,host='127.0.0.1',port=5000)
