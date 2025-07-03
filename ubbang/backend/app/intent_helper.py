

# ***** 날씨/시간 판단, 추론 기반 intent 분류



import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def should_trigger_contextual_info(user_input: str, info_type: str) -> bool:
    """
    사용자의 발화에서 실제 날씨/시간 정보를 제공해야 하는지 GPT에게 판단하게 함
    info_type: "날씨" or "시간"
    """
    if info_type == "날씨":
        examples = (
            '- "예": 유저가 지금 정보를 요청하는 경우 (예: "오늘 날씨 어때?")\n'
            '- "아니오": 단순 언급이거나 과거/비유적인 표현 (예: "어제 날씨 진짜 별로였지")'
        )
    elif info_type == "시간":
        examples = (
            '- "예": 유저가 지금 시각/날짜를 알고 싶어하는 경우 (예: "지금 몇 시야?", "오늘 며칠이야?")\n'
            '- "아니오": 단순 감상이나 비유 (예: "시간이 너무 빨리 가", "그땐 시간이 참 많았는데")'
        )
    else:
        return False

    question = f"""
사용자의 발화가 아래와 같을 때, {info_type} 정보를 실제로 제공해야 하는지 판단해줘.
{examples}

반드시 \"예\" 또는 \"아니오\"만 대답해줘.

발화: "{user_input}"
""".strip()

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "너는 사용자의 의도를 정확히 판별하는 판단 전문가야. 반드시 '예' 또는 '아니오'로만 대답해."},
                {"role": "user", "content": question}
            ],
            temperature=0.0
        )
        answer = response.choices[0].message.content.strip().replace(" ", "").lower()
        return "예" in answer
    except Exception as e:
        print(f"[GPT 판단 실패: {e}")
        return False

def extract_city_from_message(user_input: str) -> str:
    """
    사용자의 메시지에서 도시명을 추출함 (단순 키워드 매칭 기반)
    실서비스에서는 NER 기반 또는 GPT 기반으로 확장 가능
    """
    known_cities = ["서울", "부산", "대구", "인천", "광주", "대전", "울산", "제주", "수원", "춘천"]
    for city in known_cities:
        if city in user_input:
            return city
    return "서울"  # 기본값