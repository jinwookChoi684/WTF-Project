



## ****** 본질적으로 "응답생성(completion)"에 집중하는 py파일 입니다 *****
## GPT 응답생성






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

## 챗봇 응답에 관한 응답함수들을 이 파일로 다 빼놓음
# 시스템 프롬프트, 메모리 기반 응답, 쿼리 타입 감지 포함

from openai import OpenAI
import os
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains import LLMChain
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder


load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
llm = ChatOpenAI(model="gpt-4o")




# 🎯 LangChain 기반 응답 memory (유저별로 분리)
user_memory_store = {}


def get_user_memory(pk: str) -> ConversationBufferMemory:
    if pk not in user_memory_store:
        user_memory_store[pk] = ConversationBufferMemory(return_messages=True)
    return user_memory_store[pk]


async def get_chatbot_response(pk: str, user_input: str, system_prompt: str, memory) -> str:
    try:
        memory = get_user_memory(pk)

        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            MessagesPlaceholder(variable_name="history"),
            ("human", "{input}")
        ])

        chain = LLMChain(llm=llm, memory=memory, prompt=prompt)
        result = chain.run({"input": user_input})
        return result

    except Exception as e:
        print(f"[ERROR] get_chatbot_response 실패: {e}")
        return "⚠️ 챗봇 응답 생성 중 문제가 발생했어."


# 🎯 쿼리 타입 감지 (개인기록 / 외부정보 / 일반대화)
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

# ✅ 문맥에 따라 날씨/시간 응답이 필요한지 판단하는 함수
def should_trigger_contextual_info(user_input: str, info_type: str) -> bool:
    """
    GPT에게 현재 발화에서 실제 정보 호출이 필요한지 판단하게 함
    info_type: "날씨" or "시간"
    """
    question = f"""
사용자의 발화가 아래와 같을 때, {info_type} 정보를 실제로 제공해야 하는지 판단해줘.
- "예": 유저가 지금 정보를 요청하는 경우 (예: "오늘 날씨 어때?")
- "아니오": 단순 언급이거나 과거/비유적인 표현 (예: "어제 날씨 진짜 별로였지")

반드시 "예" 또는 "아니오"만 대답해줘.

발화: "{user_input}"
"""
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": question}],
            temperature=0.0
        )
        answer = response.choices[0].message.content.strip()
        return "예" in answer
    except Exception as e:
        print(f"[GPT 판단 실패: {e}]")
        return False