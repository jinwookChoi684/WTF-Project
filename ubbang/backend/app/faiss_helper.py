import os
import uuid
from typing import List, Dict, Optional
from dotenv import load_dotenv
from langchain.schema import Document
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.docstore.in_memory import InMemoryDocstore
from langchain.text_splitter import RecursiveCharacterTextSplitter

# 환경변수 로드 및 임베딩 모델 초기화
load_dotenv()
embedding_model = OpenAIEmbeddings(openai_api_key=os.getenv("OPENAI_API_KEY"))

# 텍스트 분할 설정
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=300,
    chunk_overlap=30
)

# ✅ 1. FAISS 저장 함수 (pk별로 저장)
def save_to_faiss(pk: str, messages: List[Dict[str, str]]):
    """
    주어진 메시지 리스트를 FAISS에 저장.
    각 메시지는 {"role": "user"/"assistant", "content": "..."} 형태
    """
    texts = []
    metadatas = []

    for msg in messages:
        role_prefix = "[유저]" if msg["role"] == "user" else "[우빵]"
        text = f"{role_prefix} {msg['content']}"
        # print(f"🧩 원본 텍스트: {text!r}")  # 디버그 로그
        chunks = text_splitter.split_text(text)
        # print(f"🧩 분할된 조각 개수: {len(chunks)}")  # 디버그 로그

        for chunk in chunks:
            texts.append(chunk)
            metadatas.append({
                "pk": pk,
                "message_id": str(uuid.uuid4()),
                "role": msg["role"]
            })
    if not texts:
        print(f"⚠️ 저장할 유효 텍스트 없음. FAISS 저장 생략 (pk: {pk})")
        return

    faiss_path = f"vectorstore/faiss_index/{pk}"
    os.makedirs(faiss_path, exist_ok=True)

    if os.path.exists(os.path.join(faiss_path, "index.faiss")):
        db = FAISS.load_local(faiss_path, embedding_model, allow_dangerous_deserialization=True)
        db.add_texts(texts, metadatas=metadatas)
    else:
        db = FAISS.from_texts(texts, embedding_model, metadatas=metadatas)

    db.save_local(faiss_path)
    print(f"✅ FAISS 저장 완료 ({pk}): {len(texts)}개 조각")


# ✅ 2. FAISS 유사도 검색 함수
def search_from_faiss(pk: str, query: str, k: int = 3) -> List[str]:
    """
    유저 쿼리에 대해 FAISS에서 유사한 메시지 top-k 검색
    """
    faiss_path = f"vectorstore/faiss_index/{pk}"
    if not os.path.exists(os.path.join(faiss_path, "index.faiss")):
        print(f"❗FAISS 인덱스 없음: {faiss_path}")
        return []

    db = FAISS.load_local(faiss_path, embedding_model, allow_dangerous_deserialization=True)
    docs = db.similarity_search(query, k=k)
    return [doc.page_content for doc in docs]


# ✅ 3. FAISS 로드 함수 (옵션)
def load_faiss_index(pk: str) -> Optional[FAISS]:
    """
    FAISS 인덱스를 로드. 없으면 None 반환
    """
    try:
        faiss_path = f"vectorstore/faiss_index/{pk}"
        if not os.path.exists(os.path.join(faiss_path, "index.faiss")):
            return None
        return FAISS.load_local(faiss_path, embedding_model, allow_dangerous_deserialization=True)
    except Exception as e:
        print(f"[FAISS 로드 실패] {e}")
        return None
