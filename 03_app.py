import streamlit as st
import streamlit.components.v1 as components

# 스트림릿 페이지 기본 설정
st.set_page_config(page_title="마음 기대기 ☁️", layout="centered")

# HTML/CSS/JS 코드를 파이썬 문자열로 감싸기
html_code = """
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>세대 공감 심리상담 챗봇</title>
    <style>
        :root {
            --primary-color: #4CAF50;
            --bg-color: #f4f7f6;
            --chat-bg: #ffffff;
        }
        body {
            font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, system-ui, Roboto, 'Helvetica Neue', 'Segoe UI', 'Apple SD Gothic Neo', 'Noto Sans KR', 'Malgun Gothic', sans-serif;
            background-color: var(--bg-color);
            margin: 0;
            padding: 0;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh; /* 여기서 났던 에러가 해결됩니다 */
        }
        .app-container {
            width: 100%;
            max-width: 400px;
            height: 100vh;
            max-height: 750px;
            background-color: var(--chat-bg);
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            display: flex;
            flex-direction: column;
            border-radius: 10px;
            overflow: hidden;
        }
        .header {
            background-color: var(--primary-color);
            color: white;
            padding: 15px 20px;
            text-align: center;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .header h1 {
            margin: 0;
            font-size: 1.2rem;
        }
        .settings {
            background-color: #e8f5e9;
            padding: 10px 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 0.9rem;
        }
        .settings select {
            padding: 5px;
            border-radius: 5px;
            border: 1px solid #ccc;
        }
        .chat-box {
            flex: 1;
            padding: 20px;
            overflow-y: auto;
            display: flex;
            flex-direction: column;
            gap: 10px;
        }
        .message {
            max-width: 80%;
            padding: 10px 15px;
            border-radius: 15px;
            line-height: 1.4;
            font-size: 0.95rem;
            word-wrap: break-word;
        }
        .user-message {
            align-self: flex-end;
            background-color: #dcf8c6;
            border-bottom-right-radius: 0;
        }
        .bot-message {
            align-self: flex-start;
            background-color: #f1f0f0;
            border-bottom-left-radius: 0;
        }
        .input-area {
            display: flex;
            padding: 15px;
            background-color: #fff;
            border-top: 1px solid #eee;
        }
        .input-area input {
            flex: 1;
            padding: 10px 15px;
            border: 1px solid #ccc;
            border-radius: 20px;
            outline: none;
            font-size: 0.95rem;
        }
        .input-area button {
            background-color: var(--primary-color);
            color: white;
            border: none;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            margin-left: 10px;
            cursor: pointer;
            font-weight: bold;
        }
    </style>
</head>
<body>

<div class="app-container">
    <div class="header">
        <h1>마음 기대기 ☁️</h1>
    </div>
    
    <div class="settings">
        <span>상담사 말투 선택:</span>
        <select id="persona-select">
            <option value="mz">친한 친구 (MZ세대)</option>
            <option value="x">따뜻한 멘토 (X세대)</option>
            <option value="senior">푸근한 어르신 (시니어)</option>
        </select>
    </div>

    <div class="chat-box" id="chat-box">
        <div class="message bot-message">안녕하세요! 오늘 하루는 어떠셨나요? 편하게 마음을 이야기해 주세요.</div>
    </div>

    <div class="input-area">
        <input type="text" id="user-input" placeholder="메시지를 입력하세요..." onkeypress="handleKeyPress(event)">
        <button onclick="sendMessage()">전송</button>
    </div>
</div>

<script>
    const botResponses = {
        mz: [
            "헐, 진짜 힘들었겠다 ㅠㅠ 완전 공감해요. 너무 무리하지 말고 오늘은 맛있는 거 먹고 푹 쉬어요!",
            "그럴 땐 진짜 스트레스받죠! 그래도 님은 충분히 잘하고 있으니까 기죽지 마요. 파이팅! 🔥",
            "요즘 많이 지친 것 같은데, 언제든 여기 와서 다 털어놔요. 제가 다 들어줄게요!"
        ],
        x: [
            "오늘 하루도 정말 고생 많으셨습니다. 가끔은 모든 걸 잠시 내려놓고 온전히 본인만의 시간을 가지는 것도 필요해요.",
            "그런 고민을 안고 계셨군요. 누구나 겪을 수 있는 일이지만 혼자 앓으면 더 힘듭니다. 천천히 해결해 나가면 될 거예요.",
            "충분히 잘해오고 계십니다. 스스로에게 너무 엄격해지지 마시고, 조금은 여유를 가져보시길 바랍니다."
        ],
        senior: [
            "아이고, 마음고생이 참 많았겠네. 다 지나가는 비일 테니 너무 깊게 상심하지 말게나.",
            "힘든 일이 있어도 밥은 든든하게 잘 챙겨 먹어야 해. 건강이 최고지. 다 잘 될 거니까 걱정 내려놓고 푹 쉬어.",
            "살다 보면 별의별 일이 다 있는 법이지요. 그만큼 마음이 더 단단해질 테니, 내가 여기서 묵묵히 응원해 주겠네."
        ]
    };

    function handleKeyPress(event) {
        if (event.key === 'Enter') {
            sendMessage();
        }
    }

    function sendMessage() {
        const inputField = document.getElementById('user-input');
        const messageText = inputField.value.trim();
        if (messageText === '') return;

        appendMessage(messageText, 'user-message');
        inputField.value = '';

        setTimeout(() => {
            const persona = document.getElementById('persona-select').value;
            const responses = botResponses[persona];
            const randomResponse = responses[Math.floor(Math.random() * responses.length)];
            appendMessage(randomResponse, 'bot-message');
        }, 500);
    }

    function appendMessage(text, className) {
        const chatBox = document.getElementById('chat-box');
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${className}`;
        messageDiv.textContent = text;
        
        chatBox.appendChild(messageDiv);
        chatBox.scrollTop = chatBox.scrollHeight;
    }
</script>

</body>
</html>
"""

# 스트림릿 컴포넌트를 사용하여 HTML 렌더링 (높이를 800px로 넉넉하게 잡음)
components.html(html_code, height=800)
