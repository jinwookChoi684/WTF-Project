
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
from langchain.chains import LLMChain
from langchain_core.prompts import ChatPromptTemplate
# noinspection PyUnresolvedReferences
from app.BasePrompt_builder import BasePromptBuilder

# --------------------------------------------------------------------------------

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.7)

# -------------------------------------------------------------------------------


# 🎯 LangChain 기반 응답 memory (유저별로 분리)
user_memory_store = {}
def get_user_memory(pk: str) -> ConversationBufferMemory:
    if pk not in user_memory_store:
        user_memory_store[pk] = ConversationBufferMemory(return_messages=True)
    return user_memory_store[pk]



# --------------------------------------------------------------------------------
# (유저 인풋+시스템프롬프트+버퍼메모리)를 기반으로 응답생성하는 함수
# ✅ 메인 응답 함수 (LangChain Memory + FAISS context 통합)
async def get_chatbot_response(
        pk: str,
        user_input: str,
        system_prompt: str,
        memory: ConversationBufferMemory,
        faiss_context: str = None
):
    try:
        # ✅ FAISS context가 있으면 system_prompt에 포함
        if faiss_context:
            system_prompt += f"\n\n# 추가 정보:\n다음은 이전에 유저가 남긴 중요한 내용이야. 참고해서 대답해줘:\n{faiss_context}"

        # ✅ LangChain prompt 구성
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            *memory.chat_memory.messages,
            ("human", "{input}"),
        ])

        chain = LLMChain(
            llm=llm,
            prompt=prompt,
            memory=memory,
            verbose=False,
        )

        result = await chain.arun(input=user_input)
        return result
    except Exception as e:
        print(f"[Chatbot 응답 실패] {e}")
        return "⚠️ 답변 생성 중 오류가 발생했어요."

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
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "너는 입력된 문장을 적절한 응답 방식으로 분류하는 분류기야."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.0,
    )
    return response.choices[0].message.content.strip()


# ✅ FAISS 기반 개인기록 검색 + GPT 응답 생성 함수
from .faiss_helper import search_from_faiss


async def get_rag_response(
    user_input: str,
    memory: ConversationBufferMemory,
    pk: str,
    gender: str,
    mode: str,
    age: int,
    tf: str
) -> str:
    # 1. 검색
    retrieved_chunks = search_from_faiss(pk, user_input, k=10)
    if not retrieved_chunks:
        return "🧠 과거 대화 중 관련된 내용을 찾지 못했어. 다시 한번 말해줄 수 있을까?"

    # 2. context 요약
    context_summary = "\n".join([f"- {chunk}" for chunk in retrieved_chunks])

    # 3. 프롬프트 생성
    prompt_builder = BasePromptBuilder(gender=gender, mode=mode, age=age, tf=tf)
    base_prompt = prompt_builder.build()

    system_prompt = f"""{base_prompt}

지금부터는 아래 과거 대화 내용을 참고해서 유저의 현재 질문에 더 풍부하고 자연스럽게 반응해줘:

{context_summary}
"""

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_input}
    ]

    # 4. 응답 생성
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            temperature=0.7
        )
        reply = response.choices[0].message.content.strip()

        memory.chat_memory.add_user_message(user_input)
        memory.chat_memory.add_ai_message(reply)

        return reply

    except Exception as e:
        print(f"[RAG 응답 실패] {e}")
        return "⚠️ 답변 생성 중 오류가 발생했어요. 잠시 후 다시 시도해줘!"
    
# ✅ 벡터 검색 필요 여부 판단 (vector vs memory)
def should_use_vector_search(user_input: str) -> bool:
    try:
        prompt = f"""
다음 사용자의 질문이 과거 대화 기록을 기반으로 검색해야 할 내용인지 판단해줘.

질문: "{user_input}"

답변 형식은 반드시 다음 중 하나로 해줘:
- vector → 과거 대화 검색 필요
- memory → 현재 대화 흐름에 응답

정답:
"""

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0,
        )
        answer = response.choices[0].message.content.strip().lower()
        return "vector" in answer or "과거" in answer

    except Exception as e:
        print(f"[쿼리 분류 실패] {e}")
        return False

