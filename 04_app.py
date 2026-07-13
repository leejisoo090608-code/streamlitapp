streamlit
openai
import streamlit as st

# 1. 페이지 설정
st.set_page_config(page_title="마음 기대기 ☁️", page_icon="☁️", layout="centered")

# OpenAI 라이브러리 체크
try:
    from openai import OpenAI
except ImportError:
    st.error("OpenAI 라이브러리가 필요합니다. 터미널에서 'pip install openai'를 실행해 주세요.")
    st.stop()

# ---------------------------------------------------------
# [안전조치 1] 사이드바 상시 안전 안내 및 API/페르소나 설정
# ---------------------------------------------------------
st.sidebar.title("⚙️ 설정 및 안전 안내")
api_key = st.sidebar.text_input("OpenAI API Key를 입력하세요", type="password")

persona = st.sidebar.selectbox(
    "상담사 말투 선택:",
    ("친한 친구 (MZ세대)", "따뜻한 멘토 (X세대)", "푸근한 어르신 (시니어)")
)

st.sidebar.markdown("---")
st.sidebar.warning(
    "🆘 **24시간 긴급 전문 상담전화**\n\n"
    "혼자 감당하기 힘든 고통이 있다면 주저하지 말고 전문가의 도움을 받으세요.\n\n"
    "* **자살예방 상담전화:** ☎️ **109**\n"
    "* **청소년 상담전화:** ☎️ **1388**\n"
    "* **정신건강 상담전화:** ☎️ **1577-0199**"
)

# 세대별 프롬프트 설정
system_prompts = {
    "친한 친구 (MZ세대)": (
        "당신은 친한 동갑내기 친구이자 따뜻한 심리 상담가입니다. "
        "MZ세대 유행어와 이모지를 적절히 사용하여 반말로 친근하고 따뜻하게 위로해 주세요. "
        "상대방이 심각한 위기 상황을 표현하면 공감과 함께 전문 기관(109)을 따뜻하게 권유하세요."
    ),
    "따뜻한 멘토 (X세대)": (
        "당신은 인생 경험이 풍부하고 따뜻한 멘토이자 심리 상담가입니다. "
        "정중하고 부드러운 존댓말(~했습니다, ~하셨군요)을 사용해 진심 어린 조언을 건네세요."
    ),
    "푸근한 어르신 (시니어)": (
        "당신은 푸근한 시골 어르신이자 심리 상담가입니다. "
        "~했구나, ~구만 같은 정겨운 어르신 말투로 무조건적인 사랑과 따뜻한 위로를 건네주세요."
    )
}

# 세션 상태 초기화
if "messages" not in st.session_state:
    st.session_state.messages = []
if "emotion_selected" not in st.session_state:
    st.session_state.emotion_selected = False

# 메인 타이틀
st.title("마음 기대기 ☁️")
st.caption("어디서든 편하게 나누는 세대별 맞춤 심리상담")
st.info("🔒 이곳에서의 대화는 어디에도 저장되지 않는 안전하고 비밀이 보장되는 공간입니다.")
st.write("---")

# ---------------------------------------------------------
# [단계 1] 초기 감정 선택 (대화 시작 전 감정 버튼 배치)
# ---------------------------------------------------------
if not st.session_state.emotion_selected and len(st.session_state.messages) == 0:
    st.subheader("오늘 마음 상태는 어떠신가요?")
    st.write("무슨 말부터 시작해야 할지 모르겠다면, 아래 버튼을 눌러 마음을 전해 주세요.")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("😫 답답하고 억울해요"):
            st.session_state.messages.append({"role": "user", "content": "오늘 너무 답답하고 억울한 일이 있었어."})
            st.session_state.emotion_selected = True
            st.rerun()
            
    with col2:
        if st.button("😰 불안하고 무서워요"):
            st.session_state.messages.append({"role": "user", "content": "요즘 마음이 많이 불안하고 무서워."})
            st.session_state.emotion_selected = True
            st.rerun()
            
    with col3:
        if st.button("🌧️ 외롭고 슬퍼요"):
            st.session_state.messages.append({"role": "user", "content": "혼자인 것 같고 너무 외롭고 슬퍼."})
            st.session_state.emotion_selected = True
            st.rerun()

    col4, col5 = st.columns(2)
    with col4:
        if st.button("🔋 그냥 지치고 무기력해요"):
            st.session_state.messages.append({"role": "user", "content": "아무것도 하기 싫고 그냥 너무 지쳐."})
            st.session_state.emotion_selected = True
            st.rerun()
            
    with col5:
        if st.button("💬 그냥 이야기 들어주세요"):
            st.session_state.messages.append({"role": "user", "content": "안녕, 오늘 내 이야기 좀 들어줄래?"})
            st.session_state.emotion_selected = True
            st.rerun()

# ---------------------------------------------------------
# [단계 2] 실시간 대화 및 위기 상황 감지 안전조치
# ---------------------------------------------------------

# 위기 키워드 탐지 함수
CRISIS_KEYWORDS = ["자살", "죽고 싶", "죽고싶", "살기 싫", "살기싫", "자해", "극단적 선택", "죽는 법", "삶을 끝"]

def check_crisis(text):
    return any(keyword in text for keyword in CRISIS_KEYWORDS)

# 이전 대화 내용 출력
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# 메시지 입력 처리
if user_input := st.chat_input("메시지를 입력하세요..."):
    
    # 사용자 메시지 화면 표시 및 저장
    with st.chat_message("user"):
        st.write(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})

    # [안전조치 2] 위기 단어 감지 시 팝업 붉은색 안내 박스 출력
    if check_crisis(user_input):
        st.error(
            "🚨 **도움이 필요한 당신에게**\n\n"
            "혼자 감당하기 힘든 고통이나 위험한 생각이 들고 계신가요?\n"
            "당신은 혼자가 아닙니다. 24시간 언제든 마음을 털어놓을 수 있는 전문 상담사가 기다리고 있습니다.\n\n"
            "📞 **자살예방 상담전화:** 109 (24시간 무료)\n"
            "📞 **청소년 전화:** 1388 (24시간 상담)"
        )

    # API 키가 없을 때 가짜 대화 작동
    if not api_key:
        mock_reply = f"[{persona}] 마음을 들려주셔서 고마워요. (사이드바에 API 키를 입력하시면 실시간 AI 상담이 진행됩니다!)"
        with st.chat_message("assistant"):
            st.write(mock_reply)
        st.session_state.messages.append({"role": "assistant", "content": mock_reply})
        
    else:
        # 실제 AI API 대화 진행
        try:
            client = OpenAI(api_key=api_key)
            
            api_messages = [{"role": "system", "content": system_prompts[persona]}]
            for m in st.session_state.messages:
                api_messages.append({"role": m["role"], "content": m["content"]})
            
            with st.chat_message("assistant"):
                message_placeholder = st.empty()
                full_response = ""
                
                for response in client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=api_messages,
                    stream=True,
                ):
                    full_response += (response.choices[0].delta.content or "")
                    message_placeholder.write(full_response + "▌")
                message_placeholder.write(full_response)
                
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            
        except Exception as e:
            st.error(f"오류가 발생했습니다: {e}")
