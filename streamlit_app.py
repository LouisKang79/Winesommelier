import streamlit as st
from openai import OpenAI

# 세션 상태 초기화 (필요한 변수들 설정)
if "stage" not in st.session_state:
    st.session_state.stage = "api_key"  # 단계: api_key, question_1, question_2, question_3, recommendation
if "wine_preferences" not in st.session_state:
    st.session_state.wine_preferences = {
        "food": "",
        "style": "",
        "budget": ""
    }
if "messages" not in st.session_state:
    st.session_state.messages = []

# 제목 및 설명 표시
st.title("💬 와인 소믈리에 포도송이")
st.write(
    "저는 상황에 따른 와인 추천을 하는 와인 소믈리에 포도송이입니다. "    
)

# API 키 입력 단계
if st.session_state.stage == "api_key":
    openai_api_key = st.text_input("OpenAI API Key", type="password")
    if not openai_api_key:
        st.info("OpenAI API key를 입력하세요.", icon="🗝️")
    else:
        st.session_state.openai_api_key = openai_api_key
        st.session_state.stage = "question_1"
        st.rerun()  # experimental_rerun() -> rerun()으로 변경

# 음식 선택 단계
elif st.session_state.stage == "question_1":
    st.subheader("어떤 음식과 함께 와인을 즐기실 계획인가요?")
    
    food_options = [
        "소고기/스테이크", 
        "해산물/생선", 
        "치즈/파스타", 
        "닭고기 요리", 
        "돼지고기 요리", 
        "디저트/달콤한 음식", 
        "식사 없이 와인만",
        "기타 (직접 입력)"
    ]
    
    food_choice = st.radio("음식 선택", food_options, index=0)
    
    if food_choice == "기타 (직접 입력)":
        custom_food = st.text_input("드실 음식을 입력해주세요")
        if custom_food:
            st.session_state.wine_preferences["food"] = custom_food
    else:
        st.session_state.wine_preferences["food"] = food_choice
    
    if st.button("다음 단계로", key="next_1"):
        st.session_state.stage = "question_2"
        st.rerun()  # experimental_rerun() -> rerun()으로 변경

# 와인 스타일 선택 단계
elif st.session_state.stage == "question_2":
    st.subheader("어떤 스타일의 와인을 선호하시나요?")
    
    style_options = [
        "풀바디 레드 와인 (진하고 풍부한 맛)",
        "미디엄바디 레드 와인 (균형 잡힌 맛)",
        "라이트바디 레드 와인 (가볍고 과일향이 강한)",
        "드라이한 화이트 와인 (산뜻하고 깔끔한)",
        "스위트한 화이트 와인 (달콤한)",
        "스파클링 와인 (탄산이 있는)",
        "로제 와인 (분홍빛 와인)",
        "상관없음 (소믈리에 추천)"
    ]
    
    style_choice = st.radio("와인 스타일 선택", style_options, index=7)
    st.session_state.wine_preferences["style"] = style_choice
    
    if st.button("다음 단계로", key="next_2"):
        st.session_state.stage = "question_3"
        st.rerun()  # experimental_rerun() -> rerun()으로 변경

# 예산 선택 단계
elif st.session_state.stage == "question_3":
    st.subheader("예산은 어느 정도로 생각하고 계신가요?")
    
    budget_options = [
        "3만원 이하",
        "3만원 ~ 5만원",
        "5만원 ~ 10만원",
        "10만원 이상",
        "가격 상관없이 최고의 와인"
    ]
    
    budget_choice = st.radio("예산 선택", budget_options, index=1)
    st.session_state.wine_preferences["budget"] = budget_choice
    
    if st.button("와인 추천 받기", key="get_recommendation"):
        # 시스템 메시지 추가
        system_prompt = (
            "당신은 와인 전문가입니다. "
            "다음 정보를 기반으로 적합한 와인을 추천해주세요:\n"
            f"- 음식: {st.session_state.wine_preferences['food']}\n"
            f"- 선호하는 와인 스타일: {st.session_state.wine_preferences['style']}\n"
            f"- 예산: {st.session_state.wine_preferences['budget']}\n\n"
            "와인 이름, 가격대, 그리고 왜 추천하는지 간단히 설명해주세요. "
            "또한 해당 와인과 어울리는 추가 음식이나 디저트도 제안해주세요."
        )
        
        # 메시지 초기화 및 시스템 메시지 추가
        st.session_state.messages = []
        st.session_state.messages.append({"role": "system", "content": system_prompt})
        st.session_state.messages.append({"role": "user", "content": f"음식: {st.session_state.wine_preferences['food']}, 와인 스타일: {st.session_state.wine_preferences['style']}, 예산: {st.session_state.wine_preferences['budget']}"})
        
        # 추천 받기 단계로 이동
        st.session_state.stage = "recommendation"
        st.rerun()  # experimental_rerun() -> rerun()으로 변경

# 추천 결과 단계
elif st.session_state.stage == "recommendation":
    st.subheader("당신의 취향에 맞는 와인 추천")
    
    # 선택한 정보 표시
    st.write("**선택하신 정보:**")
    st.write(f"- 음식: {st.session_state.wine_preferences['food']}")
    st.write(f"- 와인 스타일: {st.session_state.wine_preferences['style']}")
    st.write(f"- 예산: {st.session_state.wine_preferences['budget']}")
    
    # OpenAI API를 사용하여 응답 생성
    try:
        client = OpenAI(api_key=st.session_state.openai_api_key)
        
        with st.spinner("와인 소믈리에가 추천 중입니다..."):
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
            
    except Exception as e:
        st.error(f"오류가 발생했습니다: {str(e)}")
    
    # 다시 추천받기 버튼
    if st.button("다른 와인 추천받기"):
        st.session_state.stage = "question_1"
        st.rerun()  # experimental_rerun() -> rerun()으로 변경

# 이전 대화 내용 표시 (recommendation 단계가 아닐 때만)
if st.session_state.stage != "recommendation":
    for message in st.session_state.messages:
        if message["role"] != "system":  # 시스템 메시지는 표시하지 않음
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
