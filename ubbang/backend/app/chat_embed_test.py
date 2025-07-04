import os
import faiss
import numpy as np
from dotenv import load_dotenv
from openai import OpenAI
from langchain.memory import ConversationBufferMemory
from langchain.schema import HumanMessage

# ✅ 환경변수 로드 + OpenAI 설정
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ✅ 초기화
index = faiss.IndexFlatL2(1536)
metadata = []
memory = ConversationBufferMemory(return_messages=True)


# ✅ 텍스트 임베딩 함수
def embed_text(text: str) -> list:
    res = client.embeddings.create(
        model="text-embedding-3-small",
        input=[text]
    )
    return res.data[0].embedding


# ✅ 유사도 검색 함수 (자기 자신 제외 + 거리 출력)
def search_similar(query: str, top_k: int = 5, max_distance: float = 8) -> list:
    query_vec = embed_text(query)
    query_np = np.array([query_vec], dtype="float32")
    D, I = index.search(query_np, top_k)

    print("\n📏 유사도 거리 결과:")
    results = []
    for dist, i in zip(D[0], I[0]):
        if i < len(metadata):
            text = metadata[i]["text"].strip()
            print(f"🔍 거리: {dist:.4f} | 문장: {text}")
            if dist < max_distance and text != query.strip():
                results.append(text)
    return results



# ✅ 프롬프트 구성 함수
def build_prompt(user_input: str, similar_texts: list) -> str:
    if not similar_texts:
        return f"(참고할 과거 문장이 없어요)\n\n질문: {user_input}"

    deduped = list({s.strip() for s in similar_texts if s.strip() != user_input.strip()})
    prompt = "\n".join([f"참고: {s}" for s in deduped])
    return f"{prompt}\n\n질문: {user_input}"


# ✅ GPT 응답 생성 함수
def get_response(prompt: str) -> str:
    res = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "유저 감정에 공감하며 자연스럽게 반응해줘."},
            {"role": "user", "content": prompt}
        ]
    )
    return res.choices[0].message.content.strip()


# ✅ 예시 문장
example_sentences = [
    "담배를 많이 폈어",
    "목이 칼칼하고 아파서 병원 가야 할까 고민돼",
    "맛있는거 먹었어",
    "기침이 나고 목이 간질간질해",
    "오늘은 기분이 좋아",
    "감기 기운이 있는 것 같아",
    "놀이공원 다녀왔어",
    "요즘 잠을 잘 못 자",
    "속이 울렁거리고 입맛이 없어",
    "하루 종일 멍해",
    "회사 일이 너무 스트레스야",
    "친구랑 놀고왔어",
    "가슴이 답답하고 숨이 잘 안 쉬어져",
    "눈물이 자꾸 나",
    "요즘 이유 없이 불안해",
    "몸이 무거워서 아무것도 하기 싫어",
    "상사한테 칭찬받았어",
    "불면증 때문에 새벽까지 깨어 있어",
    "오늘 월급받았어",
    "나 좀 위로해줘",
    "주말이 너무 빨리 끝났어",
    "아무에게도 연락하고 싶지 않아",
    "너무 외롭고 쓸쓸해",
    "왠지 모르게 울컥했어",
    "시험 망친 것 같아",
    "집에 있기만 해도 답답해",
    "날씨가 좋아서 산책했어",
    "처음으로 혼밥했어",
    "약속이 취소돼서 허탈해",
    "감정 기복이 심해진 것 같아",
    "오늘은 왠지 텐션이 높아",
    "아침에 일어나는 게 너무 힘들어",
    "쓸데없는 생각이 너무 많아",
    "이불 밖은 위험해",
    "오늘은 별일 없이 무난했어",
    "배가 너무 고픈데 뭘 먹어야 할지 모르겠어",
    "전화 한 통이 간절했어",
    "다 괜찮은 척하는 것도 지쳐",
    "친구가 먼저 연락 안 하면 서운해",
    "누가 나 좀 안아줬으면 좋겠어",
    "한숨이 자꾸 나와",
    "의욕이 1도 없어",
    "오늘따라 혼자 있는 게 싫어",
    "스트레칭하고 좀 나아졌어",
    "방 청소하니까 기분이 상쾌해",
    "드라이브 다녀왔어",
    "반려동물이 너무 귀여워서 행복했어",
    "요즘 시간 가는 줄 모르겠어",
    "꿈자리가 뒤숭숭했어",
    "운동하니까 기분이 좀 나아졌어",
    "자존감이 떨어지는 것 같아",
    "별일 아닌데 눈물이 났어",
    "너무 배고픈데 귀찮아서 안 먹었어",
    "조용한 음악 들으면서 누워 있었어",
    "오랜만에 사람들 만나서 좋았어",
    "혼자 카페 가는 게 익숙해졌어",
    "생각이 많아서 잠이 안 와",
    "왜 이렇게 마음이 허전하지",
    "나는 왜 이렇게 못났을까",
    "괜찮다고 말하면서 울고 있었어",
    "누가 내 맘 좀 알아줬으면",
    "오늘따라 세상이 밝아 보여",
    "작은 일에 감동받았어",
    "친구랑 싸워서 마음이 불편해",
    "모든 게 귀찮고 싫어",
    "기대했던 일이 무산돼서 속상해",
    "오랜만에 웃었어",
    "요즘 거울 보기 싫어",
    "억지로 웃고 있는 느낌이야",
    "계속 누워만 있고 싶어",
    "할 일이 너무 많아서 머리가 아파",
    "대화가 잘 안 통해서 외로웠어",
    "예전에 좋았던 시절이 생각나",
    "의미 없는 하루가 반복되는 기분",
    "아무것도 안 했는데 피곤해",
    "너무 소란스러운 공간에 있으면 불안해져",
    "좋아하는 사람한테 연락이 안 와서 불안해",
    "밤에 혼자 있으면 생각이 많아져",
    "마음이 너무 복잡해",
    "나도 사랑받고 싶어",
    "사람들 눈치 보느라 지쳐",
    "요즘 내가 누군지도 모르겠어",
    "이상하게 울고 싶어지는 밤이야",
    "기억이 흐릿해지는 게 무서워",
    "말 한마디에 상처받았어",
    "그냥 다 내려놓고 싶어",
    "나를 아껴주는 사람이 있을까",
    "하루만이라도 푹 자고 싶어",
    "어디론가 멀리 떠나고 싶어",
    "마음의 여유가 필요한 것 같아",
    "혼자라는 걸 느낄 때가 제일 슬퍼",
    "나는 왜 이렇게 부족할까",
    "괜히 눈치 보게 돼",
    "시간이 너무 빨리 지나가",
    "모두가 나보다 나은 것 같아",
    "내가 뭘 하고 싶은지도 모르겠어",
    "다들 행복해 보이는데 나만 아닌 것 같아",
    "한 번쯤은 누가 내 얘기 들어줬으면",
    "내가 없어도 되는 존재인 것 같아",
    "하루를 어떻게 보내야 할지 모르겠어",
    "마음이 너무 공허해",
    "다시 예전처럼 웃고 싶어"
]


# ✅ 예시 임베딩 및 저장
print("📌 예시 문장 임베딩 중...")
for s in example_sentences:
    vec = embed_text(s)
    index.add(np.array([vec], dtype="float32"))
    metadata.append({"text": s})
print("✅ 예시 저장 완료!\n")

# ✅ 유저 입력
user_input = "개빡친다"

# ✅ 유사도 검색
similar_texts = search_similar(user_input)

# ✅ 이후에 저장
embedding = embed_text(user_input)
index.add(np.array([embedding], dtype="float32"))
metadata.append({"text": user_input})
memory.chat_memory.add_message(HumanMessage(content=user_input))

# ✅ 유사 문장 출력
print("\n🔍 유사한 과거 문장:")
if similar_texts:
    for i, t in enumerate(similar_texts):
        print(f"{i + 1}. {t}")
else:
    print("❌ 유사한 문장을 찾지 못했어요.")

# ✅ GPT 프롬프트 및 응답
prompt = build_prompt(user_input, similar_texts)
reply = get_response(prompt)

print("\n📤 GPT 프롬프트:\n", prompt)
print("\n🤖 GPT 응답:\n", reply)