# 유저가 채팅할 때마다 last_active_time 갱신됨
# idle_checker.py가 30분마다 모든 유저 스캔해서
# 4시간 이상 유휴 유저 찾음
# 해당 유저의 최근 30개 메시지를 get_recent_messages로 가져와
# save_to_faiss()로 저장됨

# get_recent_messages() 함수는 idle_checker.py에서
# 유저 pk를 받아 해당 유저의 최근 메시지들을 DynamoDB에서 불러오는 역할이야.



# app/dynamo_utils.py

import os
import time
import boto3
from boto3.dynamodb.conditions import Key
from typing import List, Dict
from dotenv import load_dotenv

load_dotenv()
dynamodb = boto3.resource("dynamodb", region_name="ap-northeast-2")
table = dynamodb.Table(os.getenv("DYNAMO_TABLE_NAME", "ChatMessages"))

# ✅ 최근 메시지 불러오는 함수 (기본 30개)
def get_recent_messages_from_dynamo(pk: str, limit: int = 10) -> List[Dict[str, str]]:
    try:
        response = table.query(
            KeyConditionExpression=Key("pk").eq(pk),
            ScanIndexForward=False,  # 최신순 정렬
            Limit=limit
        )
        items = response.get("Items", [])
        items.reverse()  # 오래된 순서로 정렬
        messages = [{"role": item["role"], "content": item["content"]} for item in items if "role" in item and "content" in item]
        return messages
    except Exception as e:
        print(f"[ERROR] get_recent_messages 실패: {e}")
        return []
