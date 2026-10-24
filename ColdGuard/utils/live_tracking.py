from datetime import datetime
import math, hashlib

# Demo-only moving shipment simulator. No real GPS is claimed here.
ROUTES = [
    ((18.5204, 73.8567), (19.0760, 72.8777)), # Pune -> Mumbai
    ((12.9716, 77.5946), (13.0827, 80.2707)), # Bengaluru -> Chennai
    ((17.3850, 78.4867), (16.5062, 80.6480)), # Hyderabad -> Vijayawada
    ((28.6139, 77.2090), (27.1767, 78.0081)), # Delhi -> Agra
    ((22.5726, 88.3639), (23.0225, 72.5714)), # Kolkata -> Ahmedabad
    ((19.0760, 72.8777), (21.1458, 79.0882)), # Mumbai -> Nagpur
]
CITIES = ["Pune", "Bengaluru", "Hyderabad", "Delhi", "Kolkata", "Mumbai"]


def _route_for(batch_id, idx):
    h = int(hashlib.sha256(str(batch_id).encode()).hexdigest()[:8], 16)
    return ROUTES[(h + idx) % len(ROUTES)]


def _lerp(a, b, t):
    return a + (b-a)*t


def _haversine(a, b):
    lat1, lon1 = map(math.radians, a); lat2, lon2 = map(math.radians, b)
    dlat, dlon = lat2-lat1, lon2-lon1
    x = math.sin(dlat/2)**2 + math.cos(lat1)*math.cos(lat2)*math.sin(dlon/2)**2
    return 6371 * 2 * math.asin(math.sqrt(x))


def _risk_level(r):
    return 'LOW' if r < 30 else 'MODERATE' if r < 60 else 'HIGH' if r < 80 else 'CRITICAL'


def build_live_shipments(rows, now=None):
    now = now or datetime.now()
    out=[]
    source = rows[:18]
    # Fall back to demo shipments when DB is empty.
    if not source:
        source=[{'batch_id':f'SS-{1042+i}','risk_probability':25+i*4,'thermal_temp':4.5+i%4,'humidity':58+i%7,'delay_hours':i%4,'expiry_hours':48+i*6,'risk_level':_risk_level(25+i*4)} for i in range(10)]
    for idx, s in enumerate(source):
        batch=str(s.get('batch_id') or f'SS-{1000+idx}')
        start,end=_route_for(batch,idx)
        # Each shipment moves at a different phase, changing smoothly with wall clock time.
        phase=((now.timestamp()/45.0)+(idx*1.37))%12/12
        lat=_lerp(start[0],end[0],phase); lon=_lerp(start[1],end[1],phase)
        base=float(s.get('risk_probability') or 25)
        temp=float(s.get('thermal_temp') or 4.5)
        humidity=float(s.get('humidity') or 60)
        delay=float(s.get('delay_hours') or 0)
        expiry=float(s.get('expiry_hours') or 48)
        wave=math.sin(now.timestamp()/28.0+idx)*0.65
        live_temp=max(1.0,temp+wave+(0.7 if idx%7==0 else 0))
        live_delay=max(0,delay+((now.minute+idx)%11)/12.0)
        weather_risk=8+((idx*7)%16)
        thermal_risk=max(0,(live_temp-6)*8)
        delay_risk=min(25,live_delay*5)
        shelf_left=max(2,expiry-(now.timestamp()%3600)/3600-(idx%5)*1.2)
        live_risk=max(0,min(99,base*0.62+thermal_risk+delay_risk+weather_risk+(10 if shelf_left<18 else 0)))
        speed=32+(idx*9)%42
        eta=max(8,round((_haversine((lat,lon),end)/speed)*60,0))
        status='CRITICAL' if live_risk>=80 else 'HIGH' if live_risk>=60 else 'WARNING' if live_risk>=40 else 'NORMAL'
        action=(
            'Activate backup refrigeration + prioritize unloading' if live_risk>=80 or live_temp>=8.5 else
            'Reroute and increase telemetry frequency' if live_risk>=60 else
            'Monitor temperature and ETA' if live_risk>=40 else
            'Continue normal monitoring'
        )
        out.append({
            'batch_id':batch,'lat':round(lat,5),'lon':round(lon,5),'speed_kmh':speed,
            'temperature':round(live_temp,1),'humidity':round(humidity+wave*3,1),'delay_hours':round(live_delay,1),
            'risk':round(live_risk,1),'risk_level':_risk_level(live_risk),'status':status,
            'eta_min':int(eta),'shelf_life_hours':round(shelf_left,1),'weather_risk':weather_risk,
            'origin':s.get('origin') or CITIES[idx%len(CITIES)],'destination':s.get('destination') or CITIES[(idx+1)%len(CITIES)],
            'action':action,'updated_at':now.isoformat(timespec='seconds')
        })
    return sorted(out,key=lambda x:x['risk'],reverse=True)


def live_summary(shipments):
    n=len(shipments)
    high=sum(x['risk']>=60 for x in shipments)
    critical=sum(x['risk']>=80 for x in shipments)
    temp_alerts=sum(x['temperature']>=8 for x in shipments)
    avg=round(sum(x['risk'] for x in shipments)/n,1) if n else 0
    return {'shipments':n,'high_risk':high,'critical':critical,'temperature_alerts':temp_alerts,'avg_risk':avg,'updated_at':datetime.now().isoformat(timespec='seconds')}
