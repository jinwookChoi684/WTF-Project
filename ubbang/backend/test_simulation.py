# ✅ test_simulation.py
import asyncio
from app.BasePrompt_builder import BasePromptBuilder
from app.openai_helper import get_user_memory, get_chatbot_response, detect_query_type
from app.contextual_info import get_contextual_info_reply
from app.naver_helper import get_external_info

test_messages = [
    "나 오늘 진짜 너무 힘들었어",
    "백악기 공룡에 대해서 알려줘",
    "서울 날씨 어때?",
    "나 몇살이게?",
    "나 요즘 금붕어가 키우고 싶어. 금붕어 키우기에 대해 알려줘",
    "이미 점심시간이 지났는데.. 점심 몇시에 먹는게 좋을까?",
    "어제는 날씨가 안 좋아서 별로였는데.. 오늘은 좋네!",
    "우울해서 아무것도 하기 싫어",
    "과장님이 날 혼낼 때 마다 자존감이 떨어져서 너무 속상해.",
    "이 챗봇 사용법을 잘 모르겠어.",
    "지금까지 내가 너와 나눈 대화 요약해서 말해봐"

]

# 테스트 유저 정보
pk = "test-pk"
userId = "test-user"
gender = "female"
mode = "banmal"
age = 23
tf = "T"

# prompt & memory 준비
prompt_builder = BasePromptBuilder(gender=gender, mode=mode, age=age, tf=tf)
system_prompt = prompt_builder.build()
memory = get_user_memory(pk)

# ✅ 테스트 실행 함수
async def run_test():
    for i, msg in enumerate(test_messages):
        print(f"\n📨 [{i+1}] 유저 입력: {msg}")

        # 날씨/시간 자동응답 시도
        contextual_reply = await get_contextual_info_reply(msg, system_prompt, memory)
        if contextual_reply:
            print(f"🌤️ 자동 응답: {contextual_reply}")
            memory.chat_memory.add_user_message(msg)
            memory.chat_memory.add_ai_message(contextual_reply)
            continue

        # 쿼리 유형 분류
        query_type = detect_query_type(msg)
        print(f"🔍 쿼리 유형: {query_type}")

        if query_type == "외부정보검색":
            reply = get_external_info(msg, system_prompt, memory)
        else:
            reply = await get_chatbot_response(user_input=msg, system_prompt=system_prompt, memory=memory)

        memory.chat_memory.add_user_message(msg)
        memory.chat_memory.add_ai_message(reply)

        print(f"🤖 챗봇 응답: {reply}")


# 🧪 실행
if __name__ == "__main__":
    asyncio.run(run_test())
