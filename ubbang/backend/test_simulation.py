import asyncio
from app.BasePrompt_builder import BasePromptBuilder
from app.openai_helper import (
    get_user_memory,
    get_chatbot_response,
    detect_query_type,
    get_rag_response,
    should_use_vector_search
)
from app.contextual_info import get_contextual_info_reply
from app.naver_helper import get_external_info
from app.faiss_helper import save_to_faiss

# 테스트용 대화 메시지
TEST_MESSAGES = [
    "안녕 우빵아~",
    "나랑 지난번에 했던 대화들 기억 나??",
    "나는 최근에 공룡에 대해 관심이 많아졌어. 공룡박물관 한국에 갈 만한 곳 추천해줄 수 있어?",
    "아하 너는 어떤 공룡을 젤 좋아해?",
    "너는 어느시대 공룡들이 젤 멋진거같애?",
    "난 그 목이긴 초식공룡이 그냥 귀여운거같애",
    "아 맞다 나는 요즘 내 방이 청소를 아무리해도 더러워져서 고민이야",
    "나는 치운다고 치우는데 엄마가 자꾸 더럽다고 뭐라해",
    "너는 너의 방을 깨끗하게 쓰고 있니?",
    "사실은 아무리 어지러워 보여도 나만의 규칙대로 물건들이 있는 거거든..",
    #-----------10개------------------------------------------------------------
    "내가 뭐에 대해 궁금하다고 했었지?",
    "친구와 싸웠어. 내 욕을 하고 다녔대.",
    "다른 친구를 통해서 듣게 되었고.. 손절할거야.",
    "그래도 속상한건 어쩔 수 가 없네."
    "오늘 점심 떄를 놓쳤는데, 몇시에 먹는게 좋을까?",
    "그냥 점심 먹지 말고 저녁을 먹을까...",
    "갑자기 너무 피곤하다.",
    "어제 업무가 너무 많아서 제대로 잠을 못 잤어.",
    "과장님께서 날 자주 혼내시는데, 혼날 떄 마다 자존감이 너무 떨어져.",
    "다른 입사동기들 보다 잘하고 싶은데..ㅠ",
    # --------20개 -------------------------------------------------------------
    "휴일에 업무관련 책들도 많이 읽는데, 그래도 여전히 어려워.",
    "하.. 그리고 어제는 남자친구랑도 싸운거 있지.",
    "뭐랄까... 너무 이기적이라고 느껴져. 나한테 배려도 너무 부족한 것 같고.",
    "싸움이 잦아지니까 더 지치는 것 같아.",
    "안 그래도 신경쓰이고 스트레스 받는 일이 많은데 남자친구까지 그러니까 기댈 곳이 없는 기분이야.",
    "지금까지 내가 너와 나눈 대화 요약해서 말해봐"
]

# 테스트용 유저 정보
pk = "test-pk"
user_id = "test-user"
gender = "female"
mode = "banmal"
age = 23
tf = "T"

# 프롬프트 및 메모리 생성
prompt_builder = BasePromptBuilder(gender=gender, mode=mode, age=age, tf=tf)
system_prompt = prompt_builder.build()
memory = get_user_memory(pk)

# ✅ 테스트 실행 함수
async def run_test():
    message_history = []  # FAISS 저장용

    for i, msg in enumerate(TEST_MESSAGES):
        print(f"\n📨 [{i+1}] 유저 입력: {msg}")

        # 날씨/시간 자동응답 시도
        contextual_reply = await get_contextual_info_reply(msg, system_prompt, memory)
        if contextual_reply:
            print(f"🌤️ 자동 응답: {contextual_reply}")
            memory.chat_memory.add_user_message(msg)
            memory.chat_memory.add_ai_message(contextual_reply)
            message_history.extend([
                {"role": "user", "content": msg},
                {"role": "assistant", "content": contextual_reply}
            ])
            continue

        # 쿼리 유형 감지
        query_type = detect_query_type(msg)
        print(f"🔍 쿼리 유형: {query_type}")

        if query_type == "외부정보검색":
            reply = get_external_info(msg, mode, memory)

        elif should_use_vector_search(msg):
            reply = await get_rag_response(msg, system_prompt, memory, pk)

        else:
            reply = await get_chatbot_response(user_input=msg, system_prompt=system_prompt, memory=memory)

        memory.chat_memory.add_user_message(msg)
        memory.chat_memory.add_ai_message(reply)

        message_history.extend([
            {"role": "user", "content": msg},
            {"role": "assistant", "content": reply}
        ])

        print(f"🤖 챗봇 응답: {reply}")

        # 매 10턴마다 FAISS 저장
        if (i + 1) % 10 == 0:
            save_to_faiss(pk=pk, messages=message_history)
            message_history.clear()

    # 테스트 끝나면 FAISS 저장
    if message_history:
        save_to_faiss(pk=pk, messages=message_history)


# 🧪 실행
if __name__ == "__main__":
    asyncio.run(run_test())
