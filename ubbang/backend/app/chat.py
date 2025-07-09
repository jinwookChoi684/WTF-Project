
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import os, uuid, time, asyncio
from dotenv import load_dotenv
import boto3
from boto3.dynamodb.conditions import Key

from .BasePrompt_builder import BasePromptBuilder

from .openai_helper import (
    get_chatbot_response,
    get_user_memory,
    detect_query_type,
    get_rag_response,
    should_use_vector_search)

from .weather import get_weather_data
from .utils import extract_city_from_message, get_today_datetime_info
from .contextual_info import get_contextual_info_reply, should_trigger_contextual_info
from .naver_helper import get_external_info

from .faiss_helper import save_to_faiss, search_from_faiss
from datetime import datetime

from .dynamo_utils import get_recent_messages_from_dynamo

# -------------------------------------------------------------------------------

load_dotenv()
router = APIRouter()
dynamodb = boto3.resource("dynamodb", region_name="ap-northeast-2")
table = dynamodb.Table(os.getenv("DYNAMO_TABLE_NAME", "ChatMessages"))

# -------------------------------------------------------------------------------

# 유저 활동 시간 업데이트 함수 (4시간 무응답 감지용)
def update_last_active_time(pk: str):
    try:
        table.update_item(
            Key={"pk": pk, "timestamp": 0},  # 유휴 추적용 dummy row
            UpdateExpression="SET last_active_time = :t",
            ExpressionAttributeValues={":t": int(time.time())}
        )
    except Exception as e:
        print(f"[ERROR] last_active_time 업데이트 실패: {e}")


# 메시지 저장
def save_message_to_dynamo(pk: str, userId: str,  role: str, content: str, gender: str, tf: str):
    try:
        table.put_item(
            Item={
                "pk": str(pk),                  # 파티션 키
                "timestamp": int(time.time()),  # 정렬 키
                "userId": str(userId),          # 참고용
                "gender": gender,
                "tf": str(tf),
                "role": role,
                "content": content,
                "message_id": str(uuid.uuid4())
            }
        )
    except Exception as e:
        print(f"[ERROR] 메시지 저장 실패: {e}")


# WebSocket 엔드포인트
@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()

    # ✅ 쿼리에서 유저 정보 수신
    pk = str(websocket.query_params.get("pk"))
    userId = websocket.query_params.get("userId", f"guest-{str(uuid.uuid4())}")
    gender = websocket.query_params.get("gender", "female")
    mode = websocket.query_params.get("mode", "banmal")
    age = int(websocket.query_params.get("age", "25"))
    tf = websocket.query_params.get("tf", "F")  # T or F

    print(f"📥 WebSocket 요청 들어옴: pk={pk}, user_id={userId}, mode={mode}, gender={gender}, age={age}, tf={tf}")

    # ✅ system prompt 생성
    prompt_builder = BasePromptBuilder(gender=gender, mode=mode, age=age, tf=tf)
    system_prompt = prompt_builder.build()

    # ✅ 메모리 복원 (LangChain)
    memory = get_user_memory(pk)

    embedding_counter = 0
    buffered_messages = []
    

    try:
        while True:
            user_msg = await websocket.receive_text()
            print(f"👤 유저 메시지: {user_msg}")

            # ✅ 1. 메시지 저장 (user) + 활동 시간 갱신
            save_message_to_dynamo(pk, userId, "user", user_msg, gender, tf)
            update_last_active_time(pk)

            # ✅ 2. 날씨/시간 판단 → 자동응답
            contextual_reply = await get_contextual_info_reply(user_input=user_msg, system_prompt=system_prompt,memory=memory)
            if contextual_reply:
                save_message_to_dynamo(pk, userId, "assistant", contextual_reply, gender, tf)
                memory.chat_memory.add_user_message(user_msg)
                memory.chat_memory.add_ai_message(contextual_reply)
                await websocket.send_text(contextual_reply)
                continue  # GPT 호출 생략

            # ✅ 3. 질의 유형 분기 (개인기록/RAG/일반대화)
            query_type = detect_query_type(user_msg)
            print(f"🔍 쿼리 유형 감지: {query_type}")

            if query_type == "외부정보검색":
                reply = get_external_info(user_msg, mode, memory)

            else:
                retrieved_chunks = search_from_faiss(pk, user_msg) if should_use_vector_search(user_msg) else []

                reply = await get_chatbot_response(
                    pk=pk,
                    user_input=user_msg,
                    system_prompt=system_prompt,
                    memory=memory,
                    faiss_context="\n".join(retrieved_chunks) if retrieved_chunks else None
                )

            # ✅ 4. 응답 저장 및 전송 + 활동 시간 갱신
            save_message_to_dynamo(pk, userId, "assistant", reply, gender, tf)
            update_last_active_time(pk)
            memory.chat_memory.add_user_message(user_msg)
            memory.chat_memory.add_ai_message(reply)
            await websocket.send_text(reply)

            # ✅ 5. FAISS 업데이트 (10턴 마다 저장)
            buffered_messages.append({"role": "user", "content": user_msg})
            buffered_messages.append({"role": "assistant", "content": reply})
            embedding_counter += 1

            if embedding_counter >= 10:
                save_to_faiss(pk, buffered_messages)
                embedding_counter = 0
                buffered_messages = []


    except WebSocketDisconnect:
        print("❌ WebSocket 연결 끊김")
    except Exception as e:
        print(f"❌ 예외 발생: {e}")
        await websocket.send_text("⚠️ 오류가 발생했어요. 잠시 후 다시 시도해주세요.")
    finally:
        if buffered_messages:
            print("📦 WebSocket 종료 시점 FAISS 저장 실행")
            save_to_faiss(pk, buffered_messages)    