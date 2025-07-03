
## GPT 응답생성
## 시스템 프롬프트, 메모리 기반 응답, 쿼리 타입 감지 포함


## 챗봇 응답에 관한 응답함수들을 이 파일로 다 뺴놓을거임
## 그래야 프롬프트 수정에 있어서 용이하기땜시
## 시스템 프롬프트, 메모리 기반 응답, 쿼리 타입 감지 포함

# ---------------------------------------------------------------------
# 6/30 업데이트 사항
# BufferMemory 관련 코드 수정
# get_cahtbot_response()를 memory기반으로 재작성
# chat.py도 변경
# memory_store.py 새로 생성 : LangChain 초기화 및 memory 저장용 딕셔너리
# get_chatbot_response() 함수가 history 대신 memory를 받아서 응답 생성
# LangChain의 ConversationChain 사용
# ------------------------------------------------------------------------


# app/openai_helper.py
from openai import OpenAI
import os
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains import LLMChain
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

# --------------------------------------------------------------------------------

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
llm = ChatOpenAI(model="gpt-4o")

# -------------------------------------------------------------------------------


# 🎯 LangChain 기반 응답 memory (유저별로 분리)
user_memory_store = {}


def get_user_memory(pk: str) -> ConversationBufferMemory:
    if pk not in user_memory_store:
        user_memory_store[pk] = ConversationBufferMemory(return_messages=True)
    return user_memory_store[pk]



# --------------------------------------------------------------------------------
# (유저 인풋+시스템프롬프트+버퍼메모리)를 기반으로 응답생성하는 함수
async def get_chatbot_response(
    user_input: str,
    system_prompt: str,
    memory: ConversationBufferMemory) -> str:


    # LangChain message 리스트 구성
    # 1. 대화 이력 정리
    chat_history = memory.chat_memory.messages
    messages = [{"role": "system", "content": system_prompt}]

    for msg in chat_history:
        if msg.type == "human":
            messages.append({"role": "user", "content": msg.content})
        elif msg.type == "ai":
            messages.append({"role": "assistant", "content": msg.content})
    
    # 2. 최신 유저 입력 추가
    messages.append({"role": "user", "content": user_input})
    
    # 3. 지피티 응답 생성
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            temperature=0.7
        )
        return response.choices[0].message.content.strip()

    except Exception as e:
        print(f"[GPT 응답 실패] {e}")
        return "⚠️ 답변 생성 중 오류가 발생했어요. 잠시 후 다시 시도해줘!"

# ---------------------------------------------------------------------------------

# 쿼리 타입 감지 (개인기록 / 외부정보 / 일반대화)
def detect_query_type(message: str) -> str:
    prompt = f"""
    다음 유저의 발화를 읽고, 어떤 응답 방식이 적절한지 하나만 골라줘.
    - 개인기록검색
    - 외부정보검색
    - 일반대화

    유저 발화: "{message}"
    적절한 방식:"""

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.0,
    )
    return response.choices[0].message.content.strip()

