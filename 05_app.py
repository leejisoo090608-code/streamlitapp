import streamlit as st
import pandas as pd
import random
import os

# 1. 페이지 기본 설정
st.set_page_config(page_title="마음 기대기 ☁️", page_icon="☁️", layout="centered")

# ---------------------------------------------------------
# [사이드바] 파일 업로드, 세대 선택 & 안전 가이드
# ---------------------------------------------------------
st.sidebar.title("⚙️ 설정 및 데이터 관리")

# 📂 1. CSV 파일 업로드 기능 추가
uploaded_file = st.sidebar.file_uploader("📂 상담 데이터(CSV) 업로드", type=["csv"])

persona = st.sidebar.selectbox(
    "상담사 말투 선택:",
    ("친한 친구 (MZ세대)", "따뜻한 멘토 (X세대)", "푸근한 어르신 (시니어)")
)

st.sidebar.markdown("---")
st.sidebar.warning(
    "🆘 **24시간 긴급 전문 상담전화**\n\n"
    "혼자 감당하기 힘든 고통이 있다면 전문가의 도움을 받으세요.\n\n"
    "* **자살예방 상담전화:** ☎️ **109**\n"
    "* **청소년 상담전화:** ☎️ **1388**\n"
    "* **정신건강 상담전화:** ☎️ **1577-0199**"
)

# ---------------------------------------------------------
# [데이터 로드] 업로드된 파일 우선 사용 -> 없으면기존 data.csv 검색
# ---------------------------------------------------------
@st.cache_data
def load_data(file_source):
    if file_source is not None:
        for enc in ['utf-8', 'cp949', 'euc-kr', 'utf-8-sig']:
            try:
                # 업로드된 파일 객체이거나 파일 경로일 때 분기 처리
                if isinstance(file_source, str):
                    return pd.read_csv(file_source, encoding=enc)
                else:
                    file_source.seek(0)
                    return pd.read_csv(file_source, encoding=enc)
            except (UnicodeDecodeError, Exception):
                continue
    return None

# 업로드한 파일이 있으면 그것을 쓰고, 없으면 로컬/깃허브의 data.csv를 찾음
if uploaded_file is not None:
    df = load_data(uploaded_file)
    st.sidebar.success("✅ CSV 데이터가 업로드되었습니다!")
elif os.path.exists("data.csv"):
    df = load_data("data.csv")
else:
    df = None

# 세션 상태 초기화
if "messages" not in st.session_state:
    st.session_state.messages = []
if "emotion_selected" not in st.session_state:
    st.session_state.emotion_selected = False

# 메인 헤더
st.title("마음 기대기 ☁️")
st.caption("공공데이터 기반 세대별 맞춤 마음상담")
st.info("🔒 이곳에서의 대화는 어디에도 저장되지 않는 안전한 공간입니다.")
st.write("---")

# 위기 키워드 감지
CRISIS_KEYWORDS = ["자살", "죽고 싶", "죽고싶", "살기 싫", "살기싫", "자해", "극단적 선택", "죽는 법"]

def check_crisis(text):
    return any(keyword in text for keyword in CRISIS_KEYWORDS)

# ---------------------------------------------------------
# [데이터 기반 답변 찾기 함수]
# ---------------------------------------------------------
def get_custom_response(user_text, selected_persona, target_emotion=None):
    if df is None:
        return "⚠️ 데이터가 연결되지 않았습니다. 왼쪽 사이드바에서 CSV 파일을 업로드해 주세요!"
    
    # 필수 열 확인
    required_cols = ['generation', 'emotion', 'response']
    if not all(col in df.columns for col in required_cols):
        return "⚠️ CSV 파일의 열 이름(generation, emotion, response)을 확인해 주세요."
    
    # 1. 선택한 세대에 해당하는 데이터 필터링
    filtered_df = df[df['generation'] == selected_persona]
    if filtered_df.empty:
        filtered_df = df  # 데이터가 없으면 전체에서 찾기
        
    # 2. 감정 버튼 클릭 시 조건 필터링
    if target_emotion:
        emotion_match = filtered_df[filtered_df['emotion'] == target_emotion]
        if not emotion_match.empty:
            return random.choice(emotion_match['response'].dropna().tolist())

    # 3. 직접 입력 시 키워드 매칭 검색
    if 'question_keyword' in filtered_df.columns:
        for index, row in filtered_df.iterrows():
            keywords = str(row.get('question_keyword', '')).split(',')
            for kw in keywords:
                kw = kw.strip()
                if kw and kw in user_text:
                    return row['response']
                
    # 4. 일치하는 키워드가 없을 때 기본 답변
    default_responses = filtered_df['response'].dropna().tolist()
    if default_responses:
        return random.choice(default_responses)
    else:
        return "당신의 이야기를 들려주셔서 고마워요. 마음이 조금이라도 편안해지셨으면 좋겠어요."

# ---------------------------------------------------------
# [1단계] 초기 감정 선택 버튼
# ---------------------------------------------------------
if not st.session_state.emotion_selected and len(st.session_state.messages) == 0:
    st.subheader("오늘 마음 상태는 어떠신가요?")
    st.write("아래 마음 상태 중 하나를 눌러 편하게 시작해 보세요.")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("😫 답답해요"):
            reply = get_custom_response("", persona, target_emotion="답답함")
            st.session_state.messages.append({"role": "user", "content": "오늘 너무 답답하고 억울해."})
            st.session_state.messages.append({"role": "assistant", "content": reply})
            st.session_state.emotion_selected = True
            st.rerun()
            
    with col2:
        if st.button("😰 불안해요"):
            reply = get_custom_response("", persona, target_emotion="불안함")
            st.session_state.messages.append({"role": "user", "content": "요즘 마음이 불안하고 걱정이 많아."})
            st.session_state.messages.append({"role": "assistant", "content": reply})
            st.session_state.emotion_selected = True
            st.rerun()
            
    with col3:
        if st.button("🌧️ 슬퍼요"):
            reply = get_custom_response("", persona, target_emotion="슬픔")
            st.session_state.messages.append({"role": "user", "content": "마음이 외롭고 슬퍼."})
            st.session_state.messages.append({"role": "assistant", "content": reply})
            st.session_state.emotion_selected = True
            st.rerun()

# ---------------------------------------------------------
# [2단계] 대화창 표시 및 메시지 입력 처리
# ---------------------------------------------------------
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

if user_input := st.chat_input("메시지를 입력하세요..."):
    # 사용자 메시지 표시
    with st.chat_message("user"):
        st.write(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})

    # 위기 상황 감지 시 경고 표시
    if check_crisis(user_input):
        st.error(
            "🚨 **도움이 필요한 당신에게**\n\n"
            "혼자 감당하기 힘든 고통이 있다면 24시간 전문 상담사가 기다리고 있습니다.\n\n"
            "📞 **자살예방 상담전화:** 109 (24시간 무료)\n"
            "📞 **청소년 전화:** 1388 (24시간 상담)"
        )

    # 데이터셋에서 답변 가져오기
    bot_reply = get_custom_response(user_input, persona)
    
    with st.chat_message("assistant"):
        st.write(bot_reply)
    st.session_state.messages.append({"role": "assistant", "content": bot_reply})
