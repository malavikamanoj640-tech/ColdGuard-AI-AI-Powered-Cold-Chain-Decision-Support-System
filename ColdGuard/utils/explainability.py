def explain(a):
    fs=a.get('factors',[])
    if a['risk_level'] in ('HIGH','CRITICAL'):
        summary=f"The model estimates a {a['risk_probability']:.0f}% overall supply risk. The strongest drivers are {fs[0]['name'].lower()} and {fs[1]['name'].lower() if len(fs)>1 else 'current operating conditions'}."
    elif a['risk_level']=='MODERATE': summary=f"The shipment is in a watch zone at {a['risk_probability']:.0f}% overall risk; conditions should be monitored as the journey continues."
    else: summary=f"The shipment currently shows a low estimated risk of {a['risk_probability']:.0f}%, with no dominant adverse driver detected."
    return {'summary':summary,'drivers':fs,'recommendations':[x[0] for x in []]}
