from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, Image
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
import pandas as pd

# Load data
vendors = pd.read_csv("../outputs/vendor_risk_scores.csv")

# PDF setup
doc = SimpleDocTemplate("../outputs/Risk_Assessment_Report.pdf", pagesize=A4)
styles = getSampleStyleSheet()
elements = []

# Title
elements.append(Paragraph("AI-Driven Risk Assessment Report", styles['Title']))
elements.append(Spacer(1, 12))

# Overview
overview = """
This report presents the results of risk scoring and analysis 
for third-party cloud vendors. The scoring combines rule-based 
attributes with anomaly detection (optional).
"""
elements.append(Paragraph(overview, styles['Normal']))
elements.append(Spacer(1, 12))

# Table of vendors
table_data = [vendors.columns.to_list()] + vendors.values.tolist()
table = Table(table_data)
table.setStyle([('BACKGROUND', (0,0), (-1,0), colors.grey),
                ('TEXTCOLOR',(0,0),(-1,0),colors.whitesmoke),
                ('ALIGN',(0,0),(-1,-1),'CENTER'),
                ('GRID', (0,0), (-1,-1), 1, colors.black)])
elements.append(table)
elements.append(Spacer(1, 20))

# Charts
elements.append(Paragraph("Visualizations", styles['Heading2']))
elements.append(Spacer(1, 12))

elements.append(Image("../outputs/vendor_risk_scores_bar.png", width=400, height=250))
elements.append(Spacer(1, 12))
elements.append(Image("../outputs/risk_level_counts.png", width=300, height=300))

# Build PDF
doc.build(elements)

print("✅ Report generated: ../outputs/Risk_Assessment_Report.pdf")
