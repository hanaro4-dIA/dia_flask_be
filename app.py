# app.py
from flask import Flask, request, jsonify
from analyzer import init_model, analyze_text_vs_db_titles

app = Flask(__name__)

@app.route('/extract_keywords', methods=['POST'])
def extract_keywords():
    """
    Spring에서 { "text": "..." }를 받으면,
    analyze_full_text_and_db_match 로직으로 분석하고,
    { "id": ..., "title": ...} 리스트를 JSON 배열로 반환
    """
    req_data = request.get_json()
    text_input = req_data.get("text", "")

    print("받은 텍스트:", text_input)

    # 분석 수행
    results = analyze_text_vs_db_titles(text_input, threshold=0.66)
    
    # 리스트를 jsonify하면 JSON 배열로 응답
    return jsonify({"responseKeywordDTOList": results})

if __name__ == "__main__":
    # Windows 멀티프로세싱 오류 방지: 여기서 모델 초기화
    init_model()
    # Flask 서버 실행
    app.run(host="0.0.0.0", port=5000)
