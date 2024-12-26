from flask import Flask, request, jsonify
from analyzer import init_model, analyze_text_vs_db_titles

app = Flask(__name__)

# Flask 애플리케이션 초기화 시 모델도 초기화
init_model()

@app.route('/extract_keywords', methods=['POST'])
def extract_keywords():
    req_data = request.get_json()
    text_input = req_data.get("text", "")
    results = analyze_text_vs_db_titles(text_input, threshold=0.66)
    return jsonify({"responseKeywordDTOList": results})

