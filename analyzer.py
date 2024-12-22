# analyzer.py
import torch
from transformers import AutoModel, AutoTokenizer
from sklearn.metrics.pairwise import cosine_similarity
from db import get_keywords_from_db

model = None
tokenizer = None

def init_model():
    """
    Windows 환경에서 멀티프로세싱 에러를 피하기 위해,
    전역이 아니라 __main__에서만 호출되는 구조를 권장.
    """
    global model, tokenizer
    # 실제로 사용 가능한 모델(또는 로컬 경로)로 교체
    model = AutoModel.from_pretrained("bert-base-multilingual-cased")
    tokenizer = AutoTokenizer.from_pretrained("bert-base-multilingual-cased")
    print("[DEBUG] Model and tokenizer initialized.")

def get_whole_embedding(text: str):
    """
    문장(또는 짧은 텍스트)을 입력받아,
    BERT 출력(last_hidden_state)을 평균 풀링하여 임베딩 벡터를 반환
    """
    inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True, max_length=512)
    with torch.no_grad():
        outputs = model(**inputs)
    # [batch=1, seq_len, hidden_dim] -> [1, hidden_dim] -> numpy
    emb = outputs.last_hidden_state.mean(dim=1).numpy()
    return emb

def analyze_text_vs_db_titles(text: str, threshold: float = 0.77):
    """
    B안:
      1) 전체 'text'를 임베딩 (get_whole_embedding)
      2) DB에서 (id, title)을 가져온 뒤, 각 title도 임베딩
      3) cosine_similarity( text_emb, title_emb )를 계산
      4) 높은 순으로 정렬해 상위 5개 (또는 threshold 이상)만 리턴

    최종 반환 형태 (예):
      [
        {"id": 1, "keyword": "가맹점수수료"},
        {"id": 2, "keyword": "가용자본"},
        ...
      ]
    """
    if model is None or tokenizer is None:
        raise ValueError("Model/tokenizer are not initialized. Call init_model() first.")

    # (1) DB 아이템
    db_items = get_keywords_from_db()
    print(f"[DEBUG] Received text: {text}")
    print(f"[DEBUG] DB items count: {len(db_items)}")

    # (2) 문장 전체 임베딩
    text_emb = get_whole_embedding(text)
    print("[DEBUG] Text embedding shape:", text_emb.shape)

    # (3) DB title 임베딩 + 유사도 계산
    results = []
    for item in db_items:
        title_emb = get_whole_embedding(item["title"])
        sim = cosine_similarity(text_emb, title_emb)[0][0]
        results.append((sim, item["id"], item["title"],item["content"]))

    # (4) 내림차순 정렬
    results.sort(key=lambda x: x[0], reverse=True)

    print("\n[DEBUG] Similarities (top 10 shown):")
    for i, (sim, _id, _title, _content) in enumerate(results[:10], start=1):
        print(f"  {i}. sim={sim:.4f}, id={_id}, title='{_title}',content='{_content}'")

    # (5) 상위 5개 중 threshold 이상만
    top_5 = results[:5]
    final_list = []
    for (sim, _id, _title) in top_5:
        if sim >= threshold:
            final_list.append({"id": _id, "title": _title,"content":_content})

    print("\n[DEBUG] Final top 5 with threshold check:")
    for item in top_5:
        print(f"  sim={item[0]:.4f}, id={item[1]}, title='{item[2]}', content='{item[3]}' - "
              f"{'PASS' if item[0] >= threshold else 'FAIL'}")

    print("\n[DEBUG] Final matched list:", final_list)
    return final_list


