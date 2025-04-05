import streamlit as st
import requests
from bs4 import BeautifulSoup
import re
from openai import OpenAI
import time

# 와인 가격 정보 크롤링 함수
def get_wine_price(wine_name):
    try:
        # 검색 쿼리 준비
        search_query = wine_name.replace(" ", "+")
        url = f"https://www.wine-searcher.com/find/{search_query}"
        
        # User-Agent 설정 (크롤링 탐지 방지)
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        # 요청 보내기
        response = requests.get(url, headers=headers)
        
        if response.status_code != 200:
            return "가격 정보를 찾을 수 없습니다."
        
        # HTML 파싱
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 가격 정보 찾기 (첫 번째 결과)
        price_element = soup.select_one('.offer-wine .offer-price .offer-price__num')
        avg_price_element = soup.select_one('.priceRating .adBanner div span:nth-child(3)')
        
        price_info = ""
        
        if price_element:
            price = price_element.text.strip()
            price_info += f"현재 판매가: {price}\n"
        
        if avg_price_element:
            avg_price = avg_price_element.text.strip()
            price_info += f"평균 가격: {avg_price}\n"
        
        if not price_info:
            price_info = "정확한 가격 정보를 찾을 수 없습니다."
            
        return price_info
    
    except Exception as e:
        return f"가격 정보를 가져오는 중 오류가 발생했습니다: {str(e)}"

# Streamlit 앱 설정
st.set_page_config(page_title="포도송이 와인 소믈리에", page_icon="🍷")

# 제목과 설명
st.title("🍷 와인 소믈리에 포도송이")
st.write("저는 상황에 맞는 와인을 추천해주는 소믈리에 포도송이입니다. 간단한 질문에 답해주시면 최적의 와인을 추천해드립니다.")

# OpenAI API 키 입력
openai_api_key = st.text_input("OpenAI API Key", type="password")

# 세션 상태 초기화
if "step" not in st.session_state:
    st.session_state.step = 0
    
if "answers" not in st.session_state:
    st.session_state.answers = {
        "음식": "",
        "와인 스타일": "",
        "예산": "",
        "특별한 요구사항": ""
    }
    
if "messages" not in st.session_state:
    st.session_state.messages = []
    
if "wine_recommendations" not in st.session_state:
    st.session_state.wine_recommendations = []
    
if "show_restart" not in st.session_state:
    st.session_state.show_restart = False

# 질문 목록 정의
questions = [
    "어떤 음식과 함께 와인을 드실 예정인가요? (예: 스테이크, 해산물, 파스타 등)",
    "선호하는 와인 스타일이 있으신가요? (예: 드라이, 스위트, 바디감 있는, 가벼운 등)",
    "와인 예산은 어느 정도로 생각하고 계신가요? (예: 3만원 이하, 5-10만원 등)",
    "기타 특별한 요구사항이 있으신가요? (예: 유기농, 빈티지, 특정 국가 등)"
]

# 챗봇 시작/재시작 함수
def restart_chat():
    st.session_state.step = 0
    st.session_state.answers = {
        "음식": "",
        "와인 스타일": "",
        "예산": "",
        "특별한 요구사항": ""
    }
    st.session_state.messages = []
    st.session_state.wine_recommendations = []
    st.session_state.show_restart = False

# 사용자가 API 키를 입력했을 때만 실행
if openai_api_key:
    try:
        # OpenAI 클라이언트 생성
        client = OpenAI(api_key=openai_api_key)
        
        # 처음 시작할 때 환영 메시지 추가
        if len(st.session_state.messages) == 0:
            welcome_msg = "안녕하세요! 포도송이 와인 소믈리에입니다. 몇 가지 질문에 답해주시면 최적의 와인을 추천해드리겠습니다."
            st.session_state.messages.append({"role": "assistant", "content": welcome_msg})
        
        # 이전 메시지 표시
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
        
        # 사용자에게 단계별 질문하기
        if st.session_state.step < len(questions):
            question_idx = st.session_state.step
            question_key = list(st.session_state.answers.keys())[question_idx]
            
            # 현재 질문 표시
            if len(st.session_state.messages) == 0 or st.session_state.messages[-1]["content"] != questions[question_idx]:
                with st.chat_message("assistant"):
                    st.markdown(questions[question_idx])
                st.session_state.messages.append({"role": "assistant", "content": questions[question_idx]})
            
            # 사용자 입력 받기
            user_answer = st.chat_input(f"{question_key}에 대해 답변해주세요...")
            
            if user_answer:
                # 사용자 답변 표시 및 저장
                with st.chat_message("user"):
                    st.markdown(user_answer)
                st.session_state.messages.append({"role": "user", "content": user_answer})
                
                # 답변 저장
                st.session_state.answers[question_key] = user_answer
                
                # 다음 단계로 이동
                st.session_state.step += 1
                
                # 페이지 리프레시
                st.rerun()
        
        # 모든 질문에 답변한 경우 와인 추천 생성
        elif st.session_state.step == len(questions) and not st.session_state.wine_recommendations:
            with st.chat_message("assistant"):
                message = "감사합니다! 정보를 바탕으로 와인을 추천해드리겠습니다. 잠시만 기다려주세요..."
                st.markdown(message)
            
            st.session_state.messages.append({"role": "assistant", "content": message})
            
            # 사용자 정보를 바탕으로 프롬프트 생성
            user_info = f"""
            음식: {st.session_state.answers['음식']}
            선호하는 와인 스타일: {st.session_state.answers['와인 스타일']}
            예산: {st.session_state.answers['예산']}
            특별 요구사항: {st.session_state.answers['특별한 요구사항']}
            """
            
            system_prompt = """
            당신은 와인 소믈리에입니다. 사용자의 정보를 바탕으로 3가지 와인을 추천해주세요.
            각 와인에 대해 다음 정보를 포함해 주세요:
            1. 와인 이름 (영어와 한글)
            2. 생산 국가 및 지역
            3. 포도 품종
            4. 맛 프로필 (간단히)
            5. 왜 사용자에게 이 와인이 적합한지 설명
            
            와인 이름은 정확하고 구체적으로 작성하세요. 
            예시: "Château Margaux 2015", "Cloudy Bay Sauvignon Blanc 2021"
            
            결과는 구조화된 형식으로 제공하고, 각 와인을 명확하게 구분해주세요.
            """
            
            # OpenAI API 호출
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_info}
                ]
            )
            
            # 추천 결과 저장
            recommendations_text = response.choices[0].message.content
            
            # 추천 와인 정보 추출 (정규표현식으로 와인 이름 추출)
            wine_pattern = r'(?:[\d]+\.\s)?([\w\s\'\-\.]+\d{4}|[\w\s\'\-\.]+)(?:\s\(|\s-|\s–|:)'
            wines = re.findall(wine_pattern, recommendations_text)
            
            # 추출된 와인이 없으면 다른 방식으로 추출 시도
            if not wines:
                wine_pattern = r'[\d]+\.\s([\w\s\'\-\.]+)'
                wines = re.findall(wine_pattern, recommendations_text)
            
            # 추천 와인 목록 저장
            st.session_state.wine_recommendations = wines[:3] if wines else []
            
            # 추천 결과 표시
            with st.chat_message("assistant"):
                st.markdown(recommendations_text)
            
            st.session_state.messages.append({"role": "assistant", "content": recommendations_text})
            
            # 재시작 버튼 표시 활성화
            st.session_state.show_restart = True
            
            # 가격 정보 크롤링 및 표시
            if st.session_state.wine_recommendations:
                with st.chat_message("assistant"):
                    st.markdown("추천 와인의 가격 정보를 찾고 있습니다...")
                
                price_info = "### 추천 와인 가격 정보\n\n"
                
                for wine in st.session_state.wine_recommendations:
                    price_info += f"#### {wine}\n"
                    wine_price = get_wine_price(wine)
                    price_info += f"{wine_price}\n\n"
                    # 너무 빠른 요청으로 차단되지 않도록 약간의 딜레이 추가
                    time.sleep(1)
                
                with st.chat_message("assistant"):
                    st.markdown(price_info)
                
                st.session_state.messages.append({"role": "assistant", "content": price_info})
            
            # 사용자 만족도 피드백 메시지
            with st.chat_message("assistant"):
                feedback_msg = "추천해 드린 와인이 마음에 드셨나요? 다른 추천이 필요하시면 아래 버튼을 눌러 새로운 추천을 받으실 수 있습니다."
                st.markdown(feedback_msg)
            
            st.session_state.messages.append({"role": "assistant", "content": feedback_msg})
        
        # 추천 완료 후 재시작 버튼 표시
        if st.session_state.show_restart:
            if st.button("새로운 와인 추천 받기"):
                restart_chat()
                st.rerun()
        
    except Exception as e:
        st.error(f"오류가 발생했습니다: {str(e)}")
else:
    st.info("OpenAI API key를 입력하세요.", icon="🔑")

# 푸터
st.markdown("---")
st.markdown("© 2023 포도송이 와인 소믈리에 | 와인 가격 정보 출처: wine-searcher.com")
