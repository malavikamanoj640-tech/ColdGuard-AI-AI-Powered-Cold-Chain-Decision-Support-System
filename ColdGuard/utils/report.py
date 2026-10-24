from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from pathlib import Path

def make_report(path,r,a):
    doc=SimpleDocTemplate(str(path),pagesize=A4,rightMargin=42,leftMargin=42,topMargin=42,bottomMargin=42)
    s=getSampleStyleSheet(); story=[]
    story.append(Paragraph('SUPPLYSHIELD AI',ParagraphStyle('title',parent=s['Title'],fontSize=24,textColor=colors.HexColor('#123B5D'),alignment=TA_CENTER)))
    story.append(Paragraph('Explainable Predictive Supply Risk Assessment',ParagraphStyle('sub',parent=s['Normal'],alignment=TA_CENTER,textColor=colors.HexColor('#5B7083')))); story.append(Spacer(1,18))
    data=[['Shipment','Value'],['Batch ID',r.get('batch_id','—')],['Product',r.get('product','—')],['Route',f"{r.get('origin','—')} → {r.get('destination','—')}"],['Overall Risk',f"{a['risk_probability']:.1f}% ({a['risk_level']})"],['Quality Risk',f"{a['quality_risk']:.1f}%"],['Delay Risk',f"{a['delay_risk']:.1f}%"],['Environment Risk',f"{a['environment_risk']:.1f}%"]]
    t=Table(data,colWidths=[150,330]); t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#123B5D')),('TEXTCOLOR',(0,0),(-1,0),colors.white),('GRID',(0,0),(-1,-1),.4,colors.HexColor('#D7E2EA')),('PADDING',(0,0),(-1,-1),8)])); story.append(t); story.append(Spacer(1,18))
    story.append(Paragraph('Key risk drivers',s['Heading2']))
    for f in a['factors']: story.append(Paragraph(f"• {f['name']} — impact score {f['impact']:.1f}",s['BodyText']))
    story.append(Spacer(1,10)); story.append(Paragraph('Recommended actions',s['Heading2']))
    for x in r.get('recommendations',[]): story.append(Paragraph(f"• {x}",s['BodyText']))
    story.append(Spacer(1,16)); story.append(Paragraph('Decision-support note: this report contains model-estimated risk, not a confirmation of physical product spoilage or loss.',s['BodyText']))
    doc.build(story)
