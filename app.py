from flask import Flask, render_template, request, jsonify
import ast
import re

app = Flask(__name__)

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
    
    # 5. 콜론 앞의 공백 제거
    code = re.sub(r'\s*:', ':', code)
    
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
    if code.strip() in ['for', 'if', 'while', 'print', 'input', 'def', 'class', 'return']:
        return True
        
    try:
        # if 문의 경우 실행 가능한 형태로 만들어 검사
        if code.strip().startswith('if'):
            code = f"{code}\n    pass"
            
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
        "normalized_correct": normalize_code(correct_code)
    })

if __name__ == '__main__':
    app.run(debug=True)