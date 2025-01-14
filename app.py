import streamlit as st
import pandas as pd
from datetime import datetime
import os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.units import inch
from io import BytesIO
import google.generativeai as genai
from openai import OpenAI
from anthropic import Anthropic

# 스트림릿 페이지 설정
st.set_page_config(
    page_title="AI 입시 컨설팅",
    page_icon="🎓",
    layout="wide"
)

# 사이드바에 API 키 입력 섹션
with st.sidebar:
    st.header("API 설정")
    openai_api_key = st.text_input("OpenAI API 키", type="password")
    google_api_key = st.text_input("Google API 키", type="password")
    anthropic_api_key = st.text_input("Anthropic API 키", type="password")
    
    st.markdown("---")
    st.markdown("""
    ### API 키 발급 방법
    1. OpenAI API 키: [OpenAI 웹사이트](https://platform.openai.com/account/api-keys)
    2. Google API 키: [Google Cloud Console](https://console.cloud.google.com/)
    3. Anthropic API 키: [Anthropic Console](https://console.anthropic.com/)
    """)

# 메인 페이지
st.title("AI 입시 컨설팅 시스템")
st.markdown("---")

# 설문 폼 생성
with st.form("consultation_form"):
    st.header("📝 입시 상담 설문")
    
    # 기본 정보
    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("이름")
        email = st.text_input("이메일 주소")
        gender = st.selectbox("성별", ["남자", "여자"])
        birth_date = st.date_input("생년월일")
    
    with col2:
        school = st.text_input("현재 학교명")
        grade = st.selectbox("학년", ["고1", "고2", "고3"])
        desired_university = st.text_input("희망 대학 또는 학과")
        admission_type = st.text_input("목표 대학의 전형 (예: 정시/수시/특기자 전형 등)")
    
    st.markdown("---")
    
    # 진로 및 학업 정보
    col3, col4 = st.columns(2)
    with col3:
        career_path = st.text_input("희망하는 진로 또는 직업")
        discussed_with_parents = st.radio("희망 진로에 대해 부모님과 논의해 보셨나요?", ["예", "아니오"])
        grades = st.text_input("최근 3년간 주요 과목 내신 평균 등급")
        mock_exam_scores = st.text_input("모의고사(또는 모의평가) 성적 평균")
    
    with col4:
        best_subject = st.text_area("현재 가장 자신 있는 과목과 이유")
        worst_subject = st.text_area("가장 어려움을 느끼는 과목과 이유")
        study_hours = st.number_input("하루 평균 공부 시간 (시간)", min_value=0, max_value=24)
        study_methods = st.multiselect("주로 사용하는 학습 방법", 
            ["독학", "학원", "온라인 강의", "과외", "학교 수업"])
    
    st.markdown("---")
    
    # 입시 준비 상황
    activities = st.text_area("입시 준비를 위해 따로 준비하고 있는 활동 (예: 동아리, 봉사활동, 공모전, 자격증 등)")
    has_written_statement = st.radio("자기소개서 작성을 해본 적 있나요?", ["예", "아니오"])
    comprehensive_activities = st.text_area("학생부 종합전형 대비를 위해 준비한 활동(또는 경험)")
    interview_preparation = st.text_input("목표 대학의 면접 전형이 있다면 준비 상황")
    
    # 상담 요청 사항
    consultation_needs = st.text_area("상담을 통해 가장 알고 싶은 점")
    concerns = st.text_area("입시에 있어 가장 큰 고민 또는 걱정거리")
    parents_opinion = st.text_area("부모님께서 본인의 진학 목표에 대해 어떻게 생각하시는지")
    additional_comments = st.text_area("추가로 전달하고 싶은 내용이나 질문")
    
    # AI 모델 선택
    ai_model = st.selectbox("AI 컨설팅 모델 선택", 
        ["GPT-4o", "Gemini 1.5 Flash", "Claude 3.5 Sonnet"])
    
    submit_button = st.form_submit_button("상담 신청하기")

def generate_ai_consultation(student_info, model_name):
    """AI 모델을 사용하여 입시 컨설팅 생성"""
    
    prompt = f"""
    당신은 20년 경력의 입시 전문 컨설턴트입니다. 
    다음 학생의 정보를 바탕으로 전문적이고 구체적인 입시 컨설팅을 제공해주세요.
    
    ### 학생 정보
    - 이름: {student_info['name']}
    - 학년: {student_info['grade']}
    - 성별: {student_info['gender']}
    - 학교: {student_info['school']}
    - 희망대학/학과: {student_info['desired_university']}
    - 전형: {student_info['admission_type']}
    
    ### 학업 현황
    - 내신등급: {student_info['grades']}
    - 모의고사 성적: {student_info['mock_exam_scores']}
    - 자신 있는 과목: {student_info['best_subject']}
    - 취약 과목: {student_info['worst_subject']}
    - 공부시간: {student_info['study_hours']}시간
    - 학습 방법: {', '.join(student_info['study_methods'])}
    
    ### 진로 및 준비사항
    - 희망진로: {student_info['career_path']}
    - 부모님과 논의: {student_info['discussed_with_parents']}
    - 준비 활동: {student_info['activities']}
    - 자기소개서 경험: {student_info['has_written_statement']}
    - 종합전형 준비: {student_info['comprehensive_activities']}
    - 면접 준비: {student_info['interview_preparation']}
    
    ### 상담 요청사항
    - 주요 고민: {student_info['concerns']}
    - 상담 희망사항: {student_info['consultation_needs']}
    - 부모님 의견: {student_info['parents_opinion']}
    - 추가 질문: {student_info['additional_comments']}
    
    다음 항목들을 포함하여 전문적이고 구체적인 컨설팅을 제공해주세요:
    1. 현재 상황 분석 (강점과 약점)
    2. 목표 대학 진학 가능성 평가
    3. 맞춤형 입시 전략 수립
    4. 학습 계획 및 시간 관리 조언
    5. 비교과 활동 추천
    6. 전형별 준비 전략
    7. 개선이 필요한 부분과 구체적인 실천 방안
    8. 향후 일정 및 중요 체크포인트
    
    각 항목에 대해 구체적이고 실천 가능한 조언을 제공해주세요.
    """
    
    try:
        if model_name == "GPT-4o" and openai_api_key:
            client = OpenAI(api_key=openai_api_key)
            response = client.chat.completions.create(
                model="gpt-4-0613",  # GPT-4o의 올바른 엔드포인트
                messages=[{
                    "role": "system",
                    "content": "당신은 20년 경력의 입시 전문 컨설턴트입니다. 전문적이고 구체적인 조언을 제공합니다. 학생의 상황을 깊이 있게 분석하고 실현 가능한 목표와 전략을 제시합니다."
                },
                {
                    "role": "user", 
                    "content": prompt
                }],
                temperature=0.7,
                max_tokens=4000,
                top_p=0.95,
                presence_penalty=0.1,
                frequency_penalty=0.1
            )
            return response.choices[0].message.content
            
        elif model_name == "Gemini 1.5 Flash" and google_api_key:
            genai.configure(api_key=google_api_key)
            model = genai.GenerativeModel('gemini-1.5-pro-latest')
            
            # 생성 설정
            generation_config = genai.types.GenerationConfig(
                temperature=0.7,
                top_p=0.95,
                top_k=40,
                max_output_tokens=4000,
                candidate_count=1
            )
            
            chat = model.start_chat(history=[])
            response = chat.send_message(
                prompt,
                generation_config=generation_config
            )
            
            if response and response.text:
                return response.text
            else:
                return "AI 컨설팅 생성에 실패했습니다. 다시 시도해주세요."
            
        elif model_name == "Claude 3.5 Sonnet" and anthropic_api_key:
            client = Anthropic(api_key=anthropic_api_key)
            message = client.messages.create(
                model="claude-3.5-sonnet",  # 올바른 Claude 3.5 Sonnet 엔드포인트
                max_tokens=4000,
                temperature=0.7,
                system="당신은 20년 경력의 입시 전문 컨설턴트입니다. 전문적이고 구체적인 조언을 제공합니다. 학생의 상황을 깊이 있게 분석하고 실현 가능한 목표와 전략을 제시합니다.",
                messages=[{
                    "role": "user",
                    "content": prompt
                }],
                metadata={
                    "type": "educational_consulting",
                    "format": "detailed_analysis"
                }
            )
            return message.content
            
        else:
            return "선택한 AI 모델의 API 키가 설정되지 않았습니다. API 키를 확인해주세요."
            
    except Exception as e:
        return f"AI 컨설팅 생성 중 오류가 발생했습니다: {str(e)}"

def generate_pdf_report(student_info, consultation_text):
    """PDF 보고서 생성"""
    buffer = BytesIO()
    
    # D2Coding 폰트 설정
    pdfmetrics.registerFont(TTFont('D2Coding', 'D2Coding-Ver1.3.2-20180524.ttf'))
    
    # PDF 문서 생성
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=inch,
        leftMargin=inch,
        topMargin=inch,
        bottomMargin=inch
    )
    
    # 스타일 설정
    styles = getSampleStyleSheet()
    
    # 모든 스타일에 D2Coding 폰트 적용
    styles['Title'].fontName = 'D2Coding'
    styles['Title'].fontSize = 20
    styles['Title'].leading = 24
    
    styles['Heading1'].fontName = 'D2Coding'
    styles['Heading1'].fontSize = 16
    styles['Heading1'].leading = 20
    
    styles.add(ParagraphStyle(
        name='Korean',
        fontName='D2Coding',
        fontSize=10,
        leading=14
    ))
    
    # 문서 내용 구성
    content = []
    
    # 제목
    title = Paragraph(f"AI 입시 컨설팅 보고서 - {student_info['name']}", styles['Title'])
    content.append(title)
    content.append(Paragraph("<br/><br/>", styles['Title']))  # 제목 아래 여백 추가
    
    # 기본 정보
    content.append(Paragraph("학생 기본 정보", styles['Heading1']))
    content.append(Paragraph("<br/>", styles['Korean']))  # 헤더 아래 여백 추가
    info_text = f"""
    이름: {student_info['name']}
    학년: {student_info['grade']}
    학교: {student_info['school']}
    희망대학/학과: {student_info['desired_university']}
    """
    content.append(Paragraph(info_text, styles['Korean']))
    
    # 컨설팅 내용
    content.append(Paragraph("컨설팅 내용", styles['Heading1']))
    for paragraph in consultation_text.split('\n'):
        if paragraph.strip():
            content.append(Paragraph(paragraph, styles['Korean']))
    
    # PDF 생성
    doc.build(content)
    buffer.seek(0)
    return buffer

# 폼 제출 처리
if submit_button:
    if not name or not email:
        st.error("이름과 이메일은 필수 입력 항목입니다.")
    else:
        # 학생 정보 딕셔너리 생성
        student_info = {
            'name': name,
            'email': email,
            'gender': gender,
            'birth_date': birth_date,
            'school': school,
            'grade': grade,
            'desired_university': desired_university,
            'admission_type': admission_type,
            'career_path': career_path,
            'discussed_with_parents': discussed_with_parents,
            'grades': grades,
            'mock_exam_scores': mock_exam_scores,
            'best_subject': best_subject,
            'worst_subject': worst_subject,
            'study_hours': study_hours,
            'study_methods': study_methods,
            'activities': activities,
            'has_written_statement': has_written_statement,
            'comprehensive_activities': comprehensive_activities,
            'interview_preparation': interview_preparation,
            'consultation_needs': consultation_needs,
            'concerns': concerns,
            'parents_opinion': parents_opinion,
            'additional_comments': additional_comments
        }
        
        with st.spinner("AI 컨설팅 생성 중..."):
            # AI 컨설팅 생성
            consultation_result = generate_ai_consultation(student_info, ai_model)
            
            if "오류" not in consultation_result:
                st.success("AI 컨설팅이 생성되었습니다!")
                
                # 컨설팅 결과 표시
                st.markdown("### 📋 컨설팅 결과")
                st.markdown(consultation_result)
                
                # PDF 생성 및 다운로드 버튼
                with st.spinner("PDF 생성 중..."):
                    try:
                        pdf_buffer = generate_pdf_report(student_info, consultation_result)
                        
                        st.download_button(
                            label="📄 상담 결과 PDF 다운로드",
                            data=pdf_buffer,
                            file_name=f"{name}_입시상담결과.pdf",
                            mime="application/pdf"
                        )
                    except Exception as e:
                        st.error(f"PDF 생성 중 오류가 발생했습니다: {str(e)}")
            else:
                st.error(consultation_result) 