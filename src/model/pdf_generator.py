from fpdf import FPDF
import os

def create_name_report(name_data, output_path):
    pdf = FPDF()
    pdf.add_page()
    
    # Set font
    pdf.set_font("Arial", "B", 16)
    
    # Title
    pdf.cell(0, 10, "이름 분석 리포트", ln=True, align="C")
    
    # Set font for content
    pdf.set_font("Arial", "", 12)
    
    # Basic Information
    pdf.cell(0, 10, f"생성된 이름: {name_data['name']}", ln=True)
    pdf.cell(0, 10, f"성별: {name_data['gender']}", ln=True)
    pdf.cell(0, 10, f"생년월일: {name_data['birth_date']}", ln=True)
    
    # Fortune Score
    pdf.ln(10)
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "운세 점수", ln=True)
    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 10, f"총운: {name_data['fortune_score']}", ln=True)
    
    # Name Analysis
    pdf.ln(10)
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "이름 분석", ln=True)
    pdf.set_font("Arial", "", 12)
    pdf.multi_cell(0, 10, name_data['analysis'])
    
    # Save the PDF
    pdf.output(output_path) 