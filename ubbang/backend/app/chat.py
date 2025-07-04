
# 6/30 업데이트 -----------------------------------------------
# history 리스트 제거, 대신 get_chatbot_response(pk, message) 호출
# query_params에서 pk도 함께 받도록 수정

# 7/1 업데이트 -------------------------------------------------
# 반말/존댓말 모드 + RAG/GPT 분기 + 외부검색 통합
# 비회원 유저만 DynamoDB에 유저/챗봇 쌍으로 저장 + 성별 포함

# ✅ chat.py
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import os, uuid, time, asyncio
from dotenv import load_dotenv
import boto3
from boto3.dynamodb.conditions import Key

from .openai_helper import (
    build_system_prompt, get_chatbot_response,
    get_user_memory, detect_query_type,should_trigger_contextual_info
)
from .weather import get_weather
from .utils import extract_city_from_message, get_today_date
from .retrieval_helper import get_rag_response
from .naver_helper import get_external_info
print("✅ chat.py WebSocket 라우터 로드됨")
load_dotenv()
router = APIRouter()
dynamodb = boto3.resource("dynamodb", region_name="ap-northeast-2")
table = dynamodb.Table(os.getenv("DYNAMO_TABLE_NAME", "ChatMessages"))

def save_message_to_dynamo(pk: int, userId: str,  role: str, content: str, gender: str):
    try:
        table.put_item(
            Item={
                "pk": int(pk),                  # 파티션 키
                "timestamp": int(time.time()),  # 정렬 키
                "userId": str(userId),        # 참고용
                "gender": gender,
                "role": role,
                "content": content,
                "message_id": str(uuid.uuid4())
            }
        )
    except Exception as e:
        print(f"[ERROR] 메시지 저장 실패: {e}")


def get_chat_history(pk: int, limit: int = 200) -> list[dict]:  # ✅ limit 증가
    try:
        response = table.query(
            KeyConditionExpression=Key("pk").eq(pk),
            ScanIndexForward=False,
            Limit=limit,
        )
        items = response.get("Items", [])
        return sorted(items, key=lambda x: x.get("timestamp", 0))
    except Exception as e:
        print(f"[ERROR] 채팅 기록 조회 실패: {e}")
        return []

# ✅ LangChain memory 복원
def restore_memory_from_dynamo(pk: int):
    history = get_chat_history(pk, limit=200)
    memory = get_user_memory(pk)
    memory.chat_memory.messages.clear()

    for item in history:
        role = item.get("role")
        content = item.get("content")
        if role == "user":
            memory.chat_memory.add_user_message(content)
        elif role == "assistant":
            memory.chat_memory.add_ai_message(content)

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()

    pk = int(websocket.query_params.get("pk"))
    userId = websocket.query_params.get("userId", f"guest-{str(uuid.uuid4())}")
    gender = websocket.query_params.get("gender", "female")
    mode = websocket.query_params.get("mode", "banmal")

    print(f"📥 WebSocket 요청 들어옴: pk={pk}, user_id={userId}, mode={mode}, gender={gender}")

    memory = get_user_memory(pk)
    restore_memory_from_dynamo(pk)  # ✅ 이전 대화 복원
    system_prompt = build_system_prompt(gender, mode)
    # 기존 코드의 history 대신 save_message_to_dynamo로 변경
    # history = [{"role": "system", "content": system_prompt}]

    try:
        while True:
            msg = await websocket.receive_text()
            save_message_to_dynamo(pk, userId,"user", msg, gender)

            response_parts = []
            if "날씨" in msg and should_trigger_contextual_info(msg, "날씨"):
                city = extract_city_from_message(msg)
                response_parts.append(get_weather(city))

            if "몇시" in msg and should_trigger_contextual_info(msg, "시간"):
                response_parts.append(get_today_date())

            if response_parts:
                reply = " ".join(response_parts)
            else:
                query_type = await asyncio.to_thread(detect_query_type, msg)

                if query_type == "개인기록검색":
                    reply = await asyncio.to_thread(get_rag_response, msg, pk, system_prompt, memory)
                elif query_type == "외부정보검색":
                    reply = await asyncio.to_thread(get_external_info, msg, system_prompt, memory)

                else:
                    reply = await get_chatbot_response(pk, msg, system_prompt, memory)

            save_message_to_dynamo(pk, userId,"assistant", reply, gender)
            memory.chat_memory.add_user_message(msg)
            memory.chat_memory.add_ai_message(reply)

            try:
                await websocket.send_text(reply)
            except Exception:
                await websocket.send_text("⚠️ 응답 전송 중 오류 발생!")

    except Exception as e:
        print(f"[FATAL ERROR] WebSocket 처리 중 예외 발생: {e}")
        await websocket.close()