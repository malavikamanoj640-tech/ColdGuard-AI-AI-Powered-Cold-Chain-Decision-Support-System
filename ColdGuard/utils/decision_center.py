from datetime import datetime


def _level(r):
    return 'CRITICAL' if r >= 80 else 'HIGH' if r >= 60 else 'MODERATE' if r >= 40 else 'LOW'


def build_decisions(shipments):
    decisions=[]
    for s in shipments:
        risk=float(s.get('risk', s.get('risk_probability', 0)) or 0)
        temp=float(s.get('temperature', s.get('thermal_temp', 4)) or 4)
        delay=float(s.get('delay_hours', 0) or 0)
        shelf=float(s.get('shelf_life_hours', s.get('expiry_hours', 48)) or 48)
        weather=float(s.get('weather_risk', 0) or 0)
        score=risk + (12 if temp >= 8 else 7 if temp >= 6 else 0) + (8 if delay >= 2 else 4 if delay >= 1 else 0) + (7 if shelf < 18 else 3 if shelf < 30 else 0)
        if temp >= 8.5 or risk >= 80:
            action='Activate backup refrigeration and prioritize unloading'
            category='COLD-CHAIN'
            impact='High risk reduction'
        elif risk >= 60 or shelf < 18:
            action='Reroute via lowest-risk route and increase telemetry frequency'
            category='ROUTE'
            impact='Reduce delay and exposure'
        elif delay >= 1.5 or weather >= 18:
            action='Monitor ETA and prepare contingency route'
            category='ETA'
            impact='Prevent escalation'
        else:
            action='Continue normal monitoring'
            category='MONITOR'
            impact='Maintain service level'
        decisions.append({
            'batch_id':s.get('batch_id','Unknown'),'risk':round(risk,1),'priority_score':round(min(99,score),1),
            'risk_level':_level(risk),'temperature':round(temp,1),'delay_hours':round(delay,1),
            'shelf_life_hours':round(shelf,1),'weather_risk':round(weather,1),
            'action':action,'category':category,'impact':impact,
            'origin':s.get('origin',''), 'destination':s.get('destination',''),
        })
    return sorted(decisions,key=lambda x:(x['priority_score'],x['risk']),reverse=True)


def summary(decisions):
    n=len(decisions)
    return {
        'critical':sum(x['risk']>=80 for x in decisions),
        'high':sum(60<=x['risk']<80 for x in decisions),
        'temperature':sum(x['temperature']>=8 for x in decisions),
        'short_shelf':sum(x['shelf_life_hours']<18 for x in decisions),
        'avg_risk':round(sum(x['risk'] for x in decisions)/n,1) if n else 0,
        'actions':min(5,n), 'updated_at':datetime.now().isoformat(timespec='seconds')
    }
