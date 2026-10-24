import os, joblib, math
import pandas as pd, numpy as np
from datetime import datetime
from config import MODEL_DIR

FEATURES=["thermal_shipper_temp_reading","room_temp_reading","room_humidity_reading","item_expiry_hours","ultra_low_temperature_freezer_hours","out_of_bound_temperature_hours","refrigeration_temperature_hours","location","current_hop","external_storage","hour","day_of_week"]
NUMERIC=FEATURES[:7]+FEATURES[10:]
MODEL=None

def load_model():
    global MODEL
    if MODEL is None: MODEL=joblib.load(os.path.join(MODEL_DIR,'quality_risk_model.pkl'))
    return MODEL

def clean_num(v,default=0):
    try:
        x=float(v)
        return default if math.isnan(x) else x
    except: return default

def prepare(d):
    # Normalize the date to a value that behaves consistently across
    # Python datetime, pandas Timestamp, strings and invalid/missing input.
    now=datetime.now(); date=d.get('date')
    if date:
        try:
            parsed=pd.to_datetime(date, errors='coerce')
            dt=now if pd.isna(parsed) else parsed
        except (TypeError, ValueError, OverflowError):
            dt=now
    else:
        dt=now
    row={
      'thermal_shipper_temp_reading':clean_num(d.get('thermal_temp'),4), 'room_temp_reading':clean_num(d.get('room_temperature'),22),
      'room_humidity_reading':clean_num(d.get('humidity'),60), 'item_expiry_hours':clean_num(d.get('expiry_hours'),120),
      'ultra_low_temperature_freezer_hours':clean_num(d.get('freezer_hours'),0), 'out_of_bound_temperature_hours':clean_num(d.get('oob_hours'),0),
      'refrigeration_temperature_hours':clean_num(d.get('refrigeration_hours'),0), 'location':str(d.get('location') or 'Unknown'),
      'current_hop':str(d.get('current_hop') or 'transit_stage'), 'external_storage':str(d.get('external_storage') or 'No'),
      'hour':int(dt.hour),'day_of_week':int(dt.weekday())}
    return pd.DataFrame([row])[FEATURES]

def label(p):
    return 'LOW' if p<30 else 'MODERATE' if p<60 else 'HIGH' if p<80 else 'CRITICAL'

def assess(d):
    X=prepare(d); p=float(load_model().predict_proba(X)[0][1])*100
    temp=clean_num(d.get('thermal_temp'),4); room=clean_num(d.get('room_temperature'),22); hum=clean_num(d.get('humidity'),60)
    expiry=max(0,clean_num(d.get('expiry_hours'),120)); oob=max(0,clean_num(d.get('oob_hours'),0)); delay=max(0,clean_num(d.get('delay_hours'),0))
    quality=min(100, 0.58*p + min(25,oob*8) + (18 if expiry<24 else 10 if expiry<48 else 0))
    env=min(100, (abs(temp-5)*9) + (max(0,abs(hum-60)-10)*1.3) + min(40,oob*8))
    delay_r=min(100, delay*9 + (18 if expiry<24 else 8 if expiry<48 else 0))
    operational=min(100, delay*6 + (15 if str(d.get('external_storage','No')).lower()=='yes' else 0) + (10 if str(d.get('logistics_stage','')).lower() in ['last_mile','hub','external_storage'] else 0))
    overall=min(100, round(0.55*p+0.20*env+0.15*delay_r+0.10*operational,2))
    factors=[]
    candidates=[('Temperature stability',max(0,abs(temp-5)*9)),('Expiry pressure',18 if expiry<24 else 10 if expiry<48 else 0),('Out-of-range exposure',min(25,oob*8)),('Transit delay',min(25,delay*9)),('Humidity variance',min(15,max(0,abs(hum-60)-10)*1.3))]
    for n,v in sorted(candidates,key=lambda x:x[1],reverse=True):
        if v>0: factors.append({'name':n,'impact':round(min(100,v),1)})
    if not factors: factors=[{'name':'Stable operating conditions','impact':5}]
    outcome='CRITICAL_RISK' if overall>=80 else 'QUALITY_RISK' if quality>=60 else 'DELAY_RISK' if delay_r>=55 else 'MONITOR'
    return {'risk_probability':round(overall,2),'risk_level':label(overall),'quality_risk':round(quality,2),'delay_risk':round(delay_r,2),'environment_risk':round(env,2),'operational_risk':round(operational,2),'predicted_outcome':outcome,'factors':factors}

def recommendation(a):
    out=[]
    if a['quality_risk']>=60: out.append(('Stabilize environmental conditions','Reduce further temperature exposure before the next logistics stage.'))
    if a['delay_risk']>=55: out.append(('Prioritize dispatch','Reduce queue and transit time because the shipment is time-sensitive.'))
    if a['environment_risk']>=55: out.append(('Move to controlled storage','Use a monitored environment until conditions normalize.'))
    if a['operational_risk']>=50: out.append(('Minimize handling','Avoid unnecessary transfers and external-storage exposure.'))
    if not out: out.append(('Continue monitored flow','Current conditions do not indicate an urgent intervention.'))
    return out[:4]
