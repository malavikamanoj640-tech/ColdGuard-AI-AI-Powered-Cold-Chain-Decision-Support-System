"""SupplyShield AI 9.0 prescriptive recovery intelligence.

Scores recovery resources and simulates intervention effects. The bundled resources are
DEMO records for academic use; production deployments should replace them with verified
partner/IoT/provider data.
"""
import math

CITY_COORDS={
 'mumbai':(19.0760,72.8777),'mumbai airport':(19.0896,72.8656),'pune':(18.5204,73.8567),
 'delhi':(28.6139,77.2090),'delhi airport':(28.5562,77.1000),'nashik':(19.9975,73.7898),
 'nagpur':(21.1458,79.0882),'hyderabad':(17.3850,78.4867),'bengaluru':(12.9716,77.5946),
 'bangalore':(12.9716,77.5946),'chennai':(13.0827,80.2707),'kolkata':(22.5726,88.3639)
}

def num(v,default=0.0):
    try:return float(v)
    except (TypeError,ValueError):return default

def coords(location):
    s=str(location or '').strip().lower().replace('_',' ')
    for key,value in CITY_COORDS.items():
        if key in s:return value
    return None

def haversine_km(a,b):
    if not a or not b:return None
    lat1,lon1=a;lat2,lon2=b;r=6371.0
    p1,p2=math.radians(lat1),math.radians(lat2);dp=math.radians(lat2-lat1);dl=math.radians(lon2-lon1)
    x=math.sin(dp/2)**2+math.cos(p1)*math.cos(p2)*math.sin(dl/2)**2
    return 2*r*math.asin(min(1,math.sqrt(x)))

def excursion_index(shipment):
    """0-100 severity index: deviation magnitude × exposure duration + sensitivity + shelf pressure."""
    t=num(shipment.get('thermal_temp'),5);oob=max(0,num(shipment.get('oob_hours')));expiry=max(0,num(shipment.get('expiry_hours'),120))
    product=str(shipment.get('product') or '').lower()
    sensitivity=1.25 if any(x in product for x in ('vaccine','biologic','insulin','pharma')) else 1.1 if any(x in product for x in ('food','dairy','frozen')) else 1.0
    deviation=max(0,t-8)+max(0,2-t)*1.2
    magnitude=min(45,deviation*12*sensitivity)
    duration=min(35,oob*10*sensitivity)
    shelf=20 if expiry<=12 else 14 if expiry<=24 else 8 if expiry<=48 else 0
    score=round(min(100,magnitude+duration+shelf),1)
    level='CRITICAL' if score>=75 else 'HIGH' if score>=50 else 'MODERATE' if score>=25 else 'LOW'
    return {'score':score,'level':level,'temperature_deviation':round(deviation,2),'sensitivity_factor':sensitivity}

def recommended_actions(shipment):
    ex=excursion_index(shipment);risk=num(shipment.get('risk_probability'));t=num(shipment.get('thermal_temp'),5);delay=num(shipment.get('delay_hours'))
    actions=[]
    if ex['level']=='CRITICAL' or risk>=80: actions.append({'code':'HOLD_ASSESS','title':'Hold for controlled assessment','reason':'Prevent normal transit until conditions are stabilized and checked.','effect':0.34})
    if t>8 or t<2: actions.append({'code':'CONTROLLED_STORAGE','title':'Move to controlled storage','reason':'Reduce further environmental exposure.','effect':0.30})
    if t>8 or delay>=2: actions.append({'code':'REEFER','title':'Dispatch refrigerated transport','reason':'Protect the recovery leg and reduce exposure.','effect':0.24})
    if delay>=1: actions.append({'code':'PRIORITY','title':'Prioritize dispatch','reason':'Reduce queue and transit delay.','effect':0.18})
    actions.append({'code':'MONITOR','title':'Increase telemetry frequency','reason':'Confirm that conditions stabilize after intervention.','effect':0.08})
    return actions[:4]

def rank_resources(shipment,resources,limit=6):
    origin=coords(shipment.get('location') or shipment.get('origin')); ex=excursion_index(shipment); ranked=[]
    for r in resources:
        if str(r.get('active',1)) in ('0','False','false'):continue
        rc=(num(r.get('latitude')),num(r.get('longitude'))) if r.get('latitude') is not None and r.get('longitude') is not None else None
        d=haversine_km(origin,rc) if origin and rc else None
        capability=0
        capability+=30 if r.get('cooling') else 0; capability+=18 if r.get('reefer') else 0
        capability+=15 if r.get('quality_lab') and ex['level'] in ('HIGH','CRITICAL') else 0
        cap=str(r.get('capacity_status') or '').lower(); capability+=8 if cap in ('available','high','open') else 2 if cap else 0
        distance_score=18 if d is None else max(0,25-min(25,d*1.4))
        urgency=12 if ex['level']=='CRITICAL' else 8 if ex['level']=='HIGH' else 4
        score=round(min(100,capability+distance_score+urgency),1)
        eta=None if d is None else max(1,round(d/35*60))
        x=dict(r);x.update({'distance_km':None if d is None else round(d,1),'eta_min':eta,'intervention_score':score});ranked.append(x)
    ranked.sort(key=lambda x:(-x['intervention_score'],99999 if x['distance_km'] is None else x['distance_km']))
    for i,x in enumerate(ranked[:limit],1):x['rank']=i;x['recommendation']='BEST MATCH' if i==1 else 'ASSESSMENT OPTION' if x.get('quality_lab') else 'ALTERNATIVE'
    return ranked[:limit]

def simulate_intervention(shipment,action_code,assess_fn):
    before=assess_fn(dict(shipment));sim=dict(shipment);code=str(action_code or 'MONITOR').upper()
    if code=='CONTROLLED_STORAGE':sim['thermal_temp']=min(6,max(3,num(sim.get('thermal_temp'),5)-3));sim['oob_hours']=max(0,num(sim.get('oob_hours'))-1.5);sim['external_storage']='No'
    elif code=='REEFER':sim['thermal_temp']=min(6,max(3,num(sim.get('thermal_temp'),5)-2));sim['delay_hours']=max(0,num(sim.get('delay_hours'))-.75);sim['refrigeration_hours']=num(sim.get('refrigeration_hours'))+2
    elif code=='PRIORITY':sim['delay_hours']=max(0,num(sim.get('delay_hours'))-2);sim['expiry_hours']=num(sim.get('expiry_hours'),48)+2
    elif code=='HOLD_ASSESS':sim['thermal_temp']=min(6,max(3,num(sim.get('thermal_temp'),5)-3.5));sim['oob_hours']=max(0,num(sim.get('oob_hours'))-1);sim['delay_hours']=num(sim.get('delay_hours'))+.5
    after=assess_fn(sim);reduction=round(max(0,before['risk_probability']-after['risk_probability']),1)
    status='RECOVERED' if after['risk_probability']<40 else 'STABILIZED' if reduction>=15 else 'MONITOR' if reduction>0 else 'STILL CRITICAL'
    return {'before':before,'after':after,'simulated_inputs':sim,'risk_reduction':reduction,'improvement_pct':round((reduction/max(1,before['risk_probability']))*100,1),'predicted_status':status}

def rank_resources_from_coords(origin, shipment, resources, limit=8):
    """Rank support resources from a real/current coordinate when available."""
    ex=excursion_index(shipment); ranked=[]
    for r in resources:
        if str(r.get('active',1)) in ('0','False','false'): continue
        rc=(num(r.get('latitude')),num(r.get('longitude'))) if r.get('latitude') is not None and r.get('longitude') is not None else None
        d=haversine_km(origin,rc) if origin and rc else None
        capability=(30 if r.get('cooling') else 0)+(18 if r.get('reefer') else 0)+(15 if r.get('quality_lab') and ex['level'] in ('HIGH','CRITICAL') else 0)
        cap=str(r.get('capacity_status') or '').lower(); capability += 8 if cap in ('available','high','open') else 2 if cap else 0
        distance_score=18 if d is None else max(0,25-min(25,d*1.4)); urgency=12 if ex['level']=='CRITICAL' else 8 if ex['level']=='HIGH' else 4
        score=round(min(100,capability+distance_score+urgency),1); eta=None if d is None else max(1,round(d/35*60))
        x=dict(r); x.update({'distance_km':None if d is None else round(d,1),'eta_min':eta,'intervention_score':score}); ranked.append(x)
    ranked.sort(key=lambda x:(-x['intervention_score'],99999 if x['distance_km'] is None else x['distance_km']))
    for i,x in enumerate(ranked[:limit],1): x['rank']=i; x['recommendation']='BEST MATCH' if i==1 else 'ASSESSMENT OPTION' if x.get('quality_lab') else 'ALTERNATIVE'
    return ranked[:limit]
