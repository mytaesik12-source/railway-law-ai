import streamlit as st
import google.generativeai as genai
from pypdf import PdfReader
import os

# 1. 구글 Gemini 설정 (API 키 입력)
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

# 사용 가능한 모델 자동 찾기
available_model = "gemini-1.5-flash"
try:
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            available_model = m.name
            break
except Exception as e:
    pass

model = genai.GenerativeModel(available_model)

st.set_page_config(page_title="철도안전법 3단 AI 가이드", page_icon="🚉")
st.title("🚉 철도안전법 3단 가이드 전문가")
st.markdown("법률, 시행령, 시행규칙을 한 번에 종합해서 분석해 드립니다!")
st.markdown("---")

# 2. 여러 개의 PDF를 한 번에 읽는 함수로 업그레이드!
@st.cache_data 
def read_all_pdfs(file_list):
    text = ""
    for file_path in file_list:
        if os.path.exists(file_path):
            reader = PdfReader(file_path)
            text += f"\n\n--- [{file_path} 내용] ---\n\n" # 어떤 파일인지 구분표시
            for page in reader.pages:
                text += page.extract_text()
    return text

# 🔥 3. 여기에 다운받은 3개 파일의 '정확한 이름'을 모두 적어주세요!
law_files = [
    "철도안전법(법률)(제21188호)(20260303).pdf",
    "철도안전법 시행령(대통령령)(제34919호)(20240927).pdf",  # <-- 실제 파일명으로 꼭 수정하세요!
    "철도안전법 시행규칙(국토교통부령)(제01569호)(20260312).pdf"   # <-- 실제 파일명으로 꼭 수정하세요!
]

# 파일이 전부 폴더에 잘 있는지 검사
missing_files = [f for f in law_files if not os.path.exists(f)]

if missing_files:
    st.error("❌ 다음 파일을 찾을 수 없습니다. 파일명과 폴더 위치를 확인해주세요!")
    for mf in missing_files:
        st.write(f"- {mf}")
else:
    # 3개 파일을 모두 읽어서 하나의 거대한 지식으로 만듭니다.
    law_content = read_all_pdfs(law_files)
    st.success(f"✅ 철도안전법 3단(법·령·규칙) 학습 완료! (선택된 AI: {available_model})")
    
    query = st.text_input("질문을 입력하세요", placeholder="예: 철도차량 정비기술자의 자격 기준과 교육 이수 시간은?")

    if query:
        with st.spinner("법률, 시행령, 시행규칙을 교차 검증하는 중..."):
            try:
                # AI에게 '3단으로 대답해!' 라고 프롬프트(지시사항)를 강력하게 줍니다.
                prompt = f"""
                너는 대한민국 철도안전법 전문가야. 
                아래 제공된 [철도안전법], [시행령], [시행규칙] 텍스트를 종합적으로 분석해서 답변해.
                
                [답변 규칙]
                1. 하나의 질문에 대해 법률, 시행령, 시행규칙이 어떻게 연결되는지 입체적으로 설명할 것.
                2. 반드시 구체적인 조항(예: 법 제26조, 시행령 제n조, 시행규칙 제n조)을 명시할 것.
                3. 현장 작업자가 이해하기 쉽게 풀어서 설명할 것.
                
                [법령 전문]
                {law_content[:150000]} 
                
                [질문]
                {query}
                """
                response = model.generate_content(prompt)
                
                st.markdown("### 🤖 3단 입체 분석 결과")
                st.info(response.text)
                
            except Exception as e:
                st.error("❌ AI 답변 생성 중 문제가 발생했습니다.")
                st.write(f"상세 원인: {e}")