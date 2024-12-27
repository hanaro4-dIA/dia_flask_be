from flask import Flask, request, jsonify
from analyzer import init_model, analyze_text_vs_db_titles

app = Flask(__name__)


# Flask 애플리케이션 초기화 시 모델도 초기화
init_model()


@app.route('/extract_keywords', methods=['POST'])
def extract_keywords():
    """
    키워드 추출 및 DB 저장
    """
    req_data = request.get_json()
    text_input = req_data.get("text", "")
    journal_id = req_data.get("journal_id")  # 추가
    customer_id = req_data.get("customer_id")  # 추가

    print("받은 텍스트:", text_input)
    print("저널 ID:", journal_id)
    print("고객 ID:", customer_id)

    # 분석 수행 및 저장
    results = analyze_text_vs_db_titles(text_input, threshold=0.66, journal_id=journal_id, customer_id=customer_id)
    
     # 즉시 응답
    return jsonify({"status": "OK"})

