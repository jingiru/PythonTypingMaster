from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# 메인 페이지 라우트
@app.route('/')
def index():
    return render_template('index.html')

# 코드 비교 API
@app.route('/compare', methods=['POST'])
def compare():
    data = request.json
    user_code = data.get('user_code', '').strip()
    correct_code = data.get('correct_code', '').strip()

    # 공백 제거된 코드 비교
    if user_code.replace(' ', '') == correct_code.replace(' ', ''):
        return jsonify({"is_correct": True, "method": "whitespace_comparison"})

    # Python 코드 실행 결과 비교
    try:
        user_result = eval(user_code)  # eval은 간단한 테스트용, 보안 강화 필요
        correct_result = eval(correct_code)
        is_correct = user_result == correct_result
        return jsonify({"is_correct": is_correct, "method": "execution_comparison"})
    except Exception as e:
        return jsonify({"is_correct": False, "error": str(e)})

# Flask 실행
if __name__ == '__main__':
    app.run(debug=True)
