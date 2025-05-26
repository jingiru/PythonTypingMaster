from flask import Flask, render_template, request, jsonify, session, redirect, url_for, send_file
import ast
import os
import re
import csv
import pandas as pd
from datetime import datetime

app = Flask(__name__)

application = app
SCORES_FILE = 'scores.csv'
XLSX_FILE = 'scores.xlsx'

def normalize_code(code):
    """코드 정규화: Python 코드의 공백을 일관되게 처리"""
    # 1. 여러 공백을 하나로 통일
    code = ' '.join(code.split())
    
    # 2. 연산자 주변 공백 정규화
    code = re.sub(r'\s*([<>+=\-*/])\s*', r'\1', code)
    
    # 3. 괄호 주변 공백 제거
    code = re.sub(r'\s*\(\s*', '(', code)  # 여는 괄호
    code = re.sub(r'\s*\)\s*', ')', code)  # 닫는 괄호
    
    # 4. 쉼표 다음에만 공백 유지
    code = re.sub(r'\s*,\s*', ', ', code)
    
    # 5. 콜론 앞뒤의 공백 제거 (release 250118 11:25)
    code = re.sub(r'\s*:\s*', ':', code)
    
    # 6. 대괄호 주변 공백 제거
    code = re.sub(r'\s*\[\s*', '[', code)
    code = re.sub(r'\s*\]\s*', ']', code)
    
    # 7. 중괄호 주변 공백 제거
    code = re.sub(r'\s*{\s*', '{', code)
    code = re.sub(r'\s*}\s*', '}', code)
    
    return code

def is_valid_python_syntax(code):
    """Python 코드의 문법이 유효한지 검사"""
    # 단순 키워드나 식별자인 경우
    if code.strip() in ['for', 'if', 'else', 'while', 'print', 'input', 'def', 'class', 'return']:
        return True

    try:
        # 문맥이 필요한 키워드 처리
        single_keywords = ['else:', 'elif:', 'except:', 'finally:']
        if code.strip() in single_keywords:
            # 기본 문맥을 추가하여 검사
            code = f"if True:\n    pass\n{code}\n    pass"
        elif code.strip().startswith('if '):
            # if 문의 경우 실행 가능한 형태로 만들어 검사
            code = f"{code}\n    pass"
        elif code.strip().startswith('elif '):
            # elif 문도 if 문맥 추가
            code = f"if True:\n    pass\n{code}\n    pass"
        elif code.strip().startswith('for '):
            # for 루프의 경우 실행 가능한 블록 추가
            code = f"{code}\n    pass"
        elif code.strip().startswith('try:'):
            # try 구문의 경우 except 블록 추가
            code = f"{code}\n    pass\nexcept Exception:\n    pass"
        elif code.strip().startswith('def ') and 'try:' in code:
            # 함수 정의와 try 결합 처리
            code = f"{code}\n    pass\n    except Exception:\n        pass"
        elif code.strip().startswith('while '):
            # while 루프의 경우 실행 가능한 블록 추가
            code = f"{code}\n    pass"
        elif code.strip().startswith('def '):
            # 모든 함수 정의에 대한 처리
            code = f"{code}\n    pass"

        # AST를 통해 문법 검사
        ast.parse(code)
        return True
    except Exception:
        return False




def calculate_char_accuracy(user_input, correct_code):
    """문자 단위 정확도 계산"""
    # 공백을 제거한 상태로 비교
    user_chars = list(user_input.replace(' ', ''))
    correct_chars = list(correct_code.replace(' ', ''))
    correct_count = 0
    total_length = len(correct_chars)
    
    for i in range(min(len(user_chars), len(correct_chars))):
        if user_chars[i] == correct_chars[i]:
            correct_count += 1
            
    return round((correct_count / total_length) * 100)

def are_codes_equivalent(code1, code2):
    """두 코드가 의미적으로 동일한지 검사"""
    normalized1 = normalize_code(code1)
    normalized2 = normalize_code(code2)
    return normalized1 == normalized2

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/compare', methods=['POST'])
def compare():
    data = request.json
    user_code = data.get('user_code', '').strip()
    correct_code = data.get('correct_code', '').strip()
    
    # 문법 검사
    is_syntax_valid = is_valid_python_syntax(user_code)
    
    # 문자 단위 정확도 계산
    char_accuracy = calculate_char_accuracy(user_code, correct_code)
    
    # 코드 동등성 검사 (문법이 유효한 경우만)
    is_equivalent = are_codes_equivalent(user_code, correct_code) if is_syntax_valid else False
    
    return jsonify({
    "is_correct": is_equivalent and is_syntax_valid,
    "is_syntax_valid": is_syntax_valid,
    "accuracy": char_accuracy,
    "normalized_user": normalize_code(user_code),
    "normalized_correct": normalize_code(correct_code),
    "debug": {
        "user_code": user_code,
        "correct_code": correct_code,
        "normalized_user": normalize_code(user_code),
        "normalized_correct": normalize_code(correct_code)
    }
})


# --- 수행평가 영역 --- #


@app.route('/exam')
def typing_test():
    return render_template('exam.html')

SCORES_FILE = 'scores.csv'

@app.route('/submit', methods=['POST'])
def submit_score():
    data = request.json
    student_id = data.get('student_id')
    name = data.get('name')
    level = data.get('level')  
    average_score = data.get('average_score')
    high_score = data.get('high_score')
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 기존 데이터를 모두 읽기
    rows = []
    if os.path.exists(SCORES_FILE):
        with open(SCORES_FILE, newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            rows = [row for row in reader if row[0] != student_id]

    # 새로운 데이터 추가
    rows.append([student_id, name, level, average_score, high_score, timestamp])

    # 덮어쓰기
    with open(SCORES_FILE, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerows(rows)

    return jsonify({"status": "success"})




# --- admin 영역 --- #

@app.route('/admin')
def admin():
    scores = []
    if os.path.exists(SCORES_FILE):
        with open(SCORES_FILE, newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            scores = list(reader)
    return render_template('admin.html', scores=scores)


@app.route('/download')
def download_scores():
    if not os.path.exists(SCORES_FILE):
        return "제출된 데이터가 없습니다.", 404

    df = pd.read_csv(SCORES_FILE, header=None,
                     names=["학번", "이름", "최고 점수", "평균 점수", "제출 시간"])
    df.to_excel(XLSX_FILE, index=False, sheet_name="수행평가 결과")

    return send_file(XLSX_FILE, as_attachment=True)


@app.route('/reset', methods=['POST'])
def reset_scores():
    open(SCORES_FILE, 'w', encoding='utf-8').close()  # 내용 비우기
    return redirect(url_for('admin'))





if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))  # 환경 변수 PORT를 가져오고, 기본값으로 5000 사용
    app.run(host="0.0.0.0", port=port, debug=True)  # 모든 IP에서 접속 가능하도록 host="0.0.0.0" 설정