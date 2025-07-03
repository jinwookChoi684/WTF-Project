# app/inference_helper.py

from openai import OpenAI
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def analyze_user_from_chat_history(history: list[str]) -> str:
    """
    최근 대화 내용(history)을 기반으로 유저의 감정 상태, 주요 관심사, 프롬프트 보강 문장을 추론해 반환
    """
    prompt = f"""
다음은 유저와의 최근 대화입니다:

{chr(10).join(history[-10:])}

이 대화를 기반으로, 챗봇 응답을 보완하기 위해 아래 세 가지 정보를 추론해주세요:

1. 유저의 감정 상태 (예: 무기력, 외로움, 분노, 불안, 안정감 등)
2. 유저가 자주 언급하는 주제 또는 고민 (예: 연애, 취업, 인간관계, 가족, 진로, 스트레스 등)
3. system_prompt에 추가할 수 있는 문장 3~4개 (문장만 출력, 분석은 하지 마세요)

<출력 형식 예시>
감정 상태: 무기력, 외로움
주요 주제: 연애, 인간관계
프롬프트 추가 문장:
- 요즘 외로움을 자주 표현하니, 말투에 따뜻함과 지지를 담아줘.
- 유저가 연애와 인간관계에 대해 많이 이야기하니 공감과 위로를 자주 표현해줘.
- 판단하지 말고 유저 입장에서 이야기를 들어주는 태도를 유지해줘.
- 말투는 조금 더 부드럽고 다정하게 유지해줘.
""".strip()

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.4,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"[ERROR] 유저 추론 실패: {e}")
        return ""
