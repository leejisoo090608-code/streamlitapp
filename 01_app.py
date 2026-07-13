import streamlit as st
from openai import OpenAI
import json
import os

# ==========================
# OpenAI API KEY 입력
# ==========================
API_KEY = "여기에_본인의_OpenAI_API_KEY"

client = OpenAI(api_key=API_KEY)

# ==========================
# 페이지 설정
# ==========================
st.set_page_config(
    page_title="💙 마음친구 AI 심리상담",
    page_icon="💙",
    layout="wide"
)

st.title("💙 마음친구 AI 심리상담")
st.write("언제 어디서나 편하게 고민을 이야기해보세요.")

# ==========================
# 세대별 말투
# ==========================
generation = st.selectbox(
    "세대를 선택하세요",
    [
        "어린이",
        "청소년",
        "20~30대",
        "40~50대",
        "60대 이상"
    ]
)

tone_prompt = {
    "어린이": "친절한 선생님처럼 쉽고 따뜻하게 이야기한다.",
    "청소년": "친구처럼 편안하고 공감하는 말투를 사용한다.",
    "20~30대": "차분하고 현실적인 상담사처럼 이야기한다.",
    "40~50대": "존중하며 따뜻하게 상담한다.",
    "60대 이상": "정중하고 편안한 말투를 사용한다."
}

# ==========================
# 오늘의 기분
# ==========================
emotion = st.radio(
    "오늘 기분은 어떤가요?",
    ["😊", "😐", "😢", "😡", "😭"],
    horizontal=True
)

# ==========================
# 채팅 기록
# ==========================
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# ==========================
# 사용자 입력
# ==========================
user_input = st.chat_input("마음을 편하게 이야기해주세요.")

danger_words = [
    "죽고싶",
    "자살",
    "끝내고싶",
    "살기싫",
    "사라지고싶"
]

if user_input:

    st.session_state.messages.append(
        {
            "role": "user",
            "content": user_input
        }
    )

    with st.chat_message("user"):
        st.write(user_input)

    # ==========================
    # 위기 표현 감지
    # ==========================
    if any(word in user_input for word in danger_words):

        answer = """
현재 말씀해주신 내용을 보면 많이 힘드신 것 같습니다.

혼자 견디려고 하지 마시고,
가족이나 믿을 수 있는 사람에게 지금 상황을 알려주세요.

가까운 정신건강복지센터나 응급의료기관 등 전문적인 도움을 받는 것도 중요합니다.

저는 계속 이야기를 들어드릴 수 있지만,
긴급한 상황에서는 전문가의 직접적인 도움이 가장 중요합니다.
"""

    else:

        system_prompt = f"""
당신은 전문 심리상담 AI입니다.

규칙

{tone_prompt[generation]}

- 사용자의 감정을 먼저 공감한다.
- 비난하지 않는다.
- 의학적 진단은 하지 않는다.
- 따뜻하고 자연스럽게 대화한다.
"""

        response = client.chat.completions.create(
            model="gpt-4.1",
            messages=[
                {
                    "role": "system",
                    "content": system_prompt
                }
            ] + st.session_state.messages
        )

        answer = response.choices[0].message.content

    with st.chat_message("assistant"):
        st.write(answer)

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": answer
        }
    )

    with open("chat_history.json", "w", encoding="utf-8") as f:
        json.dump(
            st.session_state.messages,
            f,
            ensure_ascii=False,
            indent=4
        )
