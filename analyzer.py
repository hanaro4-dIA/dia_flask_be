# analyzer.py
import torch
from transformers import AutoModel, AutoTokenizer
from sklearn.metrics.pairwise import cosine_similarity
from db import get_keywords_from_db, save_journal_keywords

model = None
tokenizer = None

def init_model():
    """
    모델과 토크나이저 초기화
    """
    global model, tokenizer
    model = AutoModel.from_pretrained("bert-base-multilingual-cased")
    tokenizer = AutoTokenizer.from_pretrained("bert-base-multilingual-cased")
    print("[DEBUG] Model and tokenizer initialized.")

def get_whole_embedding(text: str):
    """
    텍스트를 임베딩 벡터로 변환
    """
    inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True, max_length=512)
    with torch.no_grad():
        outputs = model(**inputs)
    emb = outputs.last_hidden_state.mean(dim=1).numpy()
    return emb

def analyze_text_vs_db_titles(text: str, threshold: float = 0.66, journal_id: int = None, customer_id: int = None):
    """
    키워드 추출 후 DB 저장
    """
    if model is None or tokenizer is None:
        raise ValueError("Model/tokenizer are not initialized. Call init_model() first.")

    # (1) DB 아이템 가져오기
    db_items = get_keywords_from_db()
    print(f"[DEBUG] Received text: {text}")
    print(f"[DEBUG] DB items count: {len(db_items)}")

    # (2) 텍스트 임베딩
    text_emb = get_whole_embedding(text)
    print("[DEBUG] Text embedding shape:", text_emb.shape)

    # (3) DB title 임베딩 + 유사도 계산
    results = []
    for item in db_items:
        title_emb = get_whole_embedding(item["title"])
        sim = cosine_similarity(text_emb, title_emb)[0][0]
        results.append((sim, item["id"], item["title"], item["content"]))

    # (4) 내림차순 정렬
    results.sort(key=lambda x: x[0], reverse=True)

    # (5) 상위 5개 중 threshold 이상만
    final_list = []
    for (sim, _id, _title, _content) in results[:5]:
        if sim >= threshold:
            final_list.append({"id": _id, "title": _title, "content": _content})

    # (6) 저장 로직 추가
    if journal_id and customer_id:
        save_journal_keywords(final_list, journal_id, customer_id)

    print("[DEBUG] Final matched list:", final_list)
    return final_list


