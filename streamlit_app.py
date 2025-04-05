import streamlit as st
from openai import OpenAI

# Show title and description.
st.title("💬 와인 소믈리에 포도송이")
st.write(
    "저는 상황에 따른 와인 추천을 하는 와인 소믈리에 포도송이입니다. "    
)

# Ask user for their OpenAI API key via `st.text_input`.
# Alternatively, you can store the API key in `./.streamlit/secrets.toml` and access it
# via `st.secrets`, see https://docs.streamlit.io/develop/concepts/connections/secrets-management
openai_api_key = st.text_input("OpenAI API Key", type="password")
if not openai_api_key:
    st.info("OpenAI API key를 입력하세요.", icon="🗝️")
else:

    # Create an OpenAI client.
    client = OpenAI(api_key=openai_api_key)

    # 세션 상태 변수에 채팅 메시지를 저장 (다시 실행해도 메시지가 유지되도록 설정)
if "messages" not in st.session_state:
    st.session_state.messages = []

# 기존 채팅 메시지 표시
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 사용자 입력 필드 생성
if prompt := st.chat_input("음식, 와인 스타일, 예산에 대해 알려주세요!"):
    
    # 사용자 입력 저장 및 표시
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # OpenAI API를 사용하여 응답 생성
    # 이전 대화 메시지를 포함하여 컨텍스트를 유지
    system_prompt = (
        "당신은 와인 전문가입니다. "
        "사용자가 먹을 음식, 선호하는 와인 스타일, 예산 금액을 입력하면 "
        "이를 기반으로 적합한 와인을 추천해주세요. "
        "와인 이름, 가격대, 그리고 왜 추천하는지 간단히 설명해주세요."
    )
    
    # 시스템 메시지 추가
    if len(st.session_state.messages) == 1:  # 첫 번째 메시지라면 시스템 프롬프트 추가
        st.session_state.messages.insert(0, {"role": "system", "content": system_prompt})

    # OpenAI API 호출 및 스트리밍 응답 처리
    stream = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": m["role"], "content": m["content"]}
            for m in st.session_state.messages
        ],
        stream=True,
    )

    # 응답을 스트리밍하며 표시하고 세션 상태에 저장
    with st.chat_message("assistant"):
        response = st.write_stream(stream)
    st.session_state.messages.append({"role": "assistant", "content": response})
