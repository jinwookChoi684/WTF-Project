# ✅ contextual_info.py
import os
from openai import OpenAI
from typing import Optional
from .weather import get_weather_data
from .utils import get_today_datetime_info, extract_city_from_message
from langchain.memory import ConversationBufferMemory


client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def should_trigger_contextual_info(user_input: str, info_type: str) -> bool:
    if info_type == "날씨":
        examples = (
            '- "예": 유저가 지금 정보를 요청하는 경우 (예: "오늘 날씨 어때?")\n'
            '- "아니오": 단순 언급이거나 과거/비유적인 표현 (예: "어제 날씨 진짜 별로였지")'
        )
    elif info_type == "시간":
        examples = (
            '- "예": 유저가 지금 시각/날짜를 알고 싶어하는 경우 (예: "지금 몇 시야?")\n'
            '- "아니오": 단순 감상이나 비유 (예: "시간이 너무 빨리 가")'
        )
    else:
        return False

    prompt = f"""
사용자의 발화가 아래와 같을 때, {info_type} 정보를 실제로 제공해야 하는지 판단해줘.
{examples}

반드시 "예" 또는 "아니오"로만 대답해줘.

발화: "{user_input}"
"""
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "너는 의도를 명확하게 분류하는 전문가야. 반드시 '예' 또는 '아니오'로만 답해."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.0
        )
        return "예" in response.choices[0].message.content.strip()
    except Exception as e:
        print(f"[GPT 판단 오류: {e}]")
        return False


async def get_contextual_info_reply(user_input: str, system_prompt: str, memory: ConversationBufferMemory) -> Optional[str]:
    info_type = None
    if should_trigger_contextual_info(user_input, "날씨"):
        info_type = "날씨"
    elif should_trigger_contextual_info(user_input, "시간"):
        info_type = "시간"
    else:
        return None

    chat_history = memory.chat_memory.messages
    messages = [{"role": "system", "content": system_prompt}]
    for msg in chat_history:
        if msg.type == "human":
            messages.append({"role": "user", "content": msg.content})
        elif msg.type == "ai":
            messages.append({"role": "assistant", "content": msg.content})
    messages.append({"role": "user", "content": user_input})

    if info_type == "날씨":
        city = extract_city_from_message(user_input)
        weather_data = get_weather_data(city)
        if not weather_data:
            return f"'{city}'에 대한 날씨 정보를 찾을 수 없어요."
        info_str = f"{weather_data['city']}의 현재 날씨는 {weather_data['condition']}이고, 기온은 {weather_data['temperature']}°C야."
    else:
        time_data = get_today_datetime_info()
        info_str = f"오늘은 {time_data['date']} {time_data['weekday']}이고, 현재 시각은 {time_data['time']}이야."

    messages.append({
        "role": "system",
        "content": f"아래 정보를 참고해서 유저의 스타일에 맞춰 자연스럽게 대답해줘:\n{info_str}"
    })

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            temperature=0.7
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"[GPT contextual info reply error: {e}]")
        return None
