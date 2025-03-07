from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
import os
from datetime import datetime

# 한글 폰트 등록
def register_fonts():
    """한글 폰트를 등록합니다."""
    font_path = os.path.join('static', 'fonts', 'NotoSansKR-Regular.ttf')
    pdfmetrics.registerFont(TTFont('NotoSansKR', font_path))

def create_name_report(name_data, name_id):
    """이름 분석 보고서를 생성합니다."""
    # 보고서 저장 경로
    report_dir = os.path.join('static', 'reports')
    os.makedirs(report_dir, exist_ok=True)
    report_path = os.path.join(report_dir, f'name_report_{name_id}.pdf')
    
    # PDF 문서 생성
    doc = SimpleDocTemplate(
        report_path,
        pagesize=A4,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=72
    )
    
    # 스토리 리스트 (PDF 요소들을 담을 리스트)
    story = []
    
    # 한글 폰트 등록
    register_fonts()
    
    # 스타일시트 가져오기
    styles = getSampleStyleSheet()
    
    # 제목
    title_style = styles['Title']
    title_style.fontName = 'NotoSansKR'
    title = Paragraph(f"이름 분석 보고서 - {name_data['name']}", title_style)
    story.append(title)
    story.append(Spacer(1, 20))
    
    # 기본 정보
    basic_info = [
        ["이름", name_data['name']],
        ["한자", name_data['hanja']],
        ["의미", name_data['meaning']],
        ["생성일", datetime.now().strftime('%Y-%m-%d')]
    ]
    
    basic_table = Table(basic_info, colWidths=[2*inch, 4*inch])
    basic_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'NotoSansKR'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'NotoSansKR'),
        ('FONTSIZE', (0, 1), (-1, -1), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    story.append(basic_table)
    story.append(Spacer(1, 20))
    
    # 분석 정보
    analysis_info = [
        ["분석 항목", "내용"],
        ["음양", name_data['analysis']['yinyang']],
        ["오행", name_data['analysis']['elements']],
        ["획수", f"{name_data['analysis']['strokes']}획"],
        ["종합 점수", f"{name_data['score']:.1f}점"]
    ]
    
    analysis_table = Table(analysis_info, colWidths=[2*inch, 4*inch])
    analysis_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'NotoSansKR'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'NotoSansKR'),
        ('FONTSIZE', (0, 1), (-1, -1), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    story.append(analysis_table)
    story.append(Spacer(1, 20))
    
    # 상세 설명
    explanation_style = styles['Normal']
    explanation_style.fontName = 'NotoSansKR'
    
    explanations = [
        "이름 분석 상세 설명",
        "",
        "1. 음양 분석",
        f"- 현재 이름의 음양 조화: {name_data['analysis']['yinyang']}",
        "- 음양의 조화는 이름의 균형과 안정성을 나타냅니다.",
        "",
        "2. 오행 분석",
        f"- 현재 이름의 오행: {name_data['analysis']['elements']}",
        "- 오행의 조화는 이름의 생명력과 발전성을 나타냅니다.",
        "",
        "3. 획수 분석",
        f"- 현재 이름의 총 획수: {name_data['analysis']['strokes']}획",
        "- 획수는 이름의 길흉과 운세를 나타냅니다.",
        "",
        "4. 종합 평가",
        f"- 현재 이름의 종합 점수: {name_data['score']:.1f}점",
        "- 종합 점수는 이름의 전반적인 길흉을 나타냅니다."
    ]
    
    for text in explanations:
        story.append(Paragraph(text, explanation_style))
        story.append(Spacer(1, 6))
    
    # PDF 생성
    doc.build(story)
    
    return report_path 