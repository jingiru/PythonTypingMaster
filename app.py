from flask import Flask, render_template, request, jsonify, session, redirect, url_for, send_file
import ast
import sys
import os
import re
import csv
import random
import subprocess
import uuid
import pandas as pd
import psycopg2
from datetime import datetime, timedelta, timezone

app = Flask(__name__)

application = app
SCORES_FILE = 'scores.csv'
XLSX_FILE = 'scores.xlsx'
DATABASE_URL = os.environ.get("DATABASE_URL")


def get_db_connection():
    return psycopg2.connect(DATABASE_URL, sslmode="require")


def init_db():
    if not DATABASE_URL:
        return

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS exam_sessions (
                    code TEXT PRIMARY KEY,
                    school TEXT NOT NULL DEFAULT '',
                    class_name TEXT NOT NULL DEFAULT '',
                    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
                );
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS scores (
                    exam_code TEXT NOT NULL DEFAULT '000000',
                    student_id TEXT NOT NULL,
                    name TEXT NOT NULL DEFAULT '',
                    level TEXT,
                    average_score INTEGER,
                    high_score INTEGER,
                    submitted_at TIMESTAMP,
                    UNIQUE (exam_code, student_id)
                );
            """)
            cur.execute("ALTER TABLE scores ADD COLUMN IF NOT EXISTS exam_code TEXT NOT NULL DEFAULT '000000';")
            cur.execute("ALTER TABLE scores DROP CONSTRAINT IF EXISTS scores_pkey;")
            cur.execute("""
                DO $$
                BEGIN
                    IF NOT EXISTS (
                        SELECT 1
                        FROM pg_constraint
                        WHERE conname = 'scores_exam_code_student_id_key'
                    ) THEN
                        ALTER TABLE scores ADD CONSTRAINT scores_exam_code_student_id_key UNIQUE (exam_code, student_id);
                    END IF;
                END $$;
            """)
            cur.execute("""
                INSERT INTO exam_sessions (code, school, class_name)
                VALUES ('000000', '기존 데이터', '')
                ON CONFLICT (code) DO NOTHING;
            """)


def is_valid_exam_code_format(code):
    return bool(re.fullmatch(r"\d{6}", code or ""))


def make_download_filename(exam):
    code = exam.get("code", "")
    parts = [exam.get("school", ""), exam.get("class_name", ""), code, "수행평가결과"]
    filename = "_".join([part.strip() for part in parts if part and part.strip()])
    filename = re.sub(r'[\\/:*?"<>|]+', "_", filename)
    return f"{filename or 'scores'}.xlsx"


def generate_exam_code(cur=None):
    for _ in range(100):
        code = f"{random.randint(0, 999999):06d}"
        if DATABASE_URL:
            cur.execute("SELECT 1 FROM exam_sessions WHERE code = %s;", (code,))
            if not cur.fetchone():
                return code
        else:
            if code not in load_local_sessions():
                return code
    raise RuntimeError("수행평가 코드를 발급할 수 없습니다. 다시 시도해 주세요.")


def load_local_sessions():
    sessions = {}
    if os.path.exists("exam_sessions.csv"):
        with open("exam_sessions.csv", newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            for row in reader:
                if len(row) >= 4:
                    sessions[row[0]] = {
                        "code": row[0],
                        "school": row[1],
                        "class_name": row[2],
                        "created_at": row[3]
                    }

    if "000000" not in sessions:
        sessions["000000"] = {
            "code": "000000",
            "school": "기존 데이터",
            "class_name": "",
            "created_at": ""
        }

    return sessions


def save_local_session(code, school, class_name):
    sessions = load_local_sessions()
    KST = timezone(timedelta(hours=9))
    created_at = datetime.now(KST).strftime("%Y-%m-%d %H:%M:%S")
    sessions[code] = {
        "code": code,
        "school": school,
        "class_name": class_name,
        "created_at": created_at
    }

    with open("exam_sessions.csv", 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        for session_data in sessions.values():
            writer.writerow([
                session_data["code"],
                session_data["school"],
                session_data["class_name"],
                session_data["created_at"]
            ])


def local_exam_exists(code):
    return code in load_local_sessions()


def local_score_row(row):
    if len(row) == 6:
        return ["000000"] + row
    return row

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
    exam_code = request.args.get("code", "").strip()
    return render_template('exam.html', exam_code=exam_code)


@app.route('/validate_exam_code/<exam_code>')
def validate_exam_code(exam_code):
    if not is_valid_exam_code_format(exam_code):
        return jsonify({"valid": False}), 400

    if DATABASE_URL:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT code, school, class_name
                    FROM exam_sessions
                    WHERE code = %s;
                """, (exam_code,))
                row = cur.fetchone()

        if not row:
            return jsonify({"valid": False}), 404

        return jsonify({
            "valid": True,
            "exam": {
                "code": row[0],
                "school": row[1],
                "class_name": row[2]
            }
        })

    sessions = load_local_sessions()
    if exam_code not in sessions:
        return jsonify({"valid": False}), 404

    return jsonify({"valid": True, "exam": sessions[exam_code]})

@app.route('/submit', methods=['POST'])
def submit_score():
    data = request.json
    exam_code = data.get('exam_code', '').strip()
    student_id = data.get('student_id')
    name = data.get('name')
    level = data.get('level')
    average_score = data.get('average_score')
    high_score = data.get('high_score')
    KST = timezone(timedelta(hours=9))
    now = datetime.now(KST).replace(tzinfo=None)
    timestamp = now.strftime("%Y-%m-%d %H:%M:%S")

    if not is_valid_exam_code_format(exam_code):
        return jsonify({"status": "error", "message": "유효한 수행평가 코드가 필요합니다."}), 400

    if DATABASE_URL:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1 FROM exam_sessions WHERE code = %s;", (exam_code,))
                if not cur.fetchone():
                    return jsonify({"status": "error", "message": "존재하지 않는 수행평가 코드입니다."}), 404

                cur.execute("""
                    INSERT INTO scores
                        (exam_code, student_id, name, level, average_score, high_score, submitted_at)
                    VALUES
                        (%s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (exam_code, student_id)
                    DO UPDATE SET
                        name = EXCLUDED.name,
                        level = EXCLUDED.level,
                        average_score = EXCLUDED.average_score,
                        high_score = EXCLUDED.high_score,
                        submitted_at = EXCLUDED.submitted_at;
                """, (exam_code, student_id, name, level, average_score, high_score, now))

        return jsonify({"status": "success"})

    if not local_exam_exists(exam_code):
        return jsonify({"status": "error", "message": "존재하지 않는 수행평가 코드입니다."}), 404

    updated = False
    rows = []

    if os.path.exists(SCORES_FILE):
        with open(SCORES_FILE, newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            for row in reader:
                normalized_row = local_score_row(row)
                if normalized_row[0] == exam_code and normalized_row[1] == student_id:
                    # 해당 학번이 이미 존재하면 갱신
                    rows.append([exam_code, student_id, name, level, average_score, high_score, timestamp])
                    updated = True
                else:
                    rows.append(normalized_row)

    if not updated:
        # 기존에 학번이 없으면 새로 추가
        rows.append([exam_code, student_id, name, level, average_score, high_score, timestamp])

    with open(SCORES_FILE, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerows(rows)

    return jsonify({"status": "success"})





# --- admin 영역 --- #

@app.route('/admin')
def admin():
    if DATABASE_URL:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT
                        e.code,
                        e.school,
                        e.class_name,
                        to_char(e.created_at, 'YYYY-MM-DD HH24:MI:SS'),
                        COUNT(s.student_id)
                    FROM exam_sessions e
                    LEFT JOIN scores s ON s.exam_code = e.code
                    GROUP BY e.code, e.school, e.class_name, e.created_at
                    ORDER BY e.created_at DESC;
                """)
                sessions = cur.fetchall()

        return render_template('admin.html', scores=[], sessions=sessions, selected_exam=None)

    sessions = []
    for session_data in load_local_sessions().values():
        sessions.append((
            session_data["code"],
            session_data["school"],
            session_data["class_name"],
            session_data["created_at"],
            0
        ))
    return render_template('admin.html', scores=[], sessions=sessions, selected_exam=None)


@app.route('/admin/exams', methods=['POST'])
def create_exam():
    school = request.form.get("school", "").strip()
    class_name = request.form.get("class_name", "").strip()

    if DATABASE_URL:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                code = generate_exam_code(cur)
                cur.execute("""
                    INSERT INTO exam_sessions (code, school, class_name)
                    VALUES (%s, %s, %s);
                """, (code, school, class_name))

        return redirect(url_for('admin_exam', exam_code=code))

    code = generate_exam_code()
    save_local_session(code, school, class_name)
    return redirect(url_for('admin_exam', exam_code=code))


@app.route('/admin/exams/<exam_code>')
def admin_exam(exam_code):
    if not is_valid_exam_code_format(exam_code):
        return redirect(url_for('admin'))

    if DATABASE_URL:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT code, school, class_name, to_char(created_at, 'YYYY-MM-DD HH24:MI:SS')
                    FROM exam_sessions
                    WHERE code = %s;
                """, (exam_code,))
                selected_exam = cur.fetchone()

                if not selected_exam:
                    return redirect(url_for('admin'))

                cur.execute("""
                    SELECT
                        student_id,
                        name,
                        COALESCE(level, ''),
                        COALESCE(average_score::text, ''),
                        COALESCE(high_score::text, ''),
                        COALESCE(to_char(submitted_at, 'YYYY-MM-DD HH24:MI:SS'), '')
                    FROM scores
                    WHERE exam_code = %s
                    ORDER BY student_id;
                """, (exam_code,))
                scores = cur.fetchall()

        return render_template('admin.html', scores=scores, sessions=[], selected_exam=selected_exam)

    scores = []
    selected_exam = load_local_sessions().get(exam_code)
    if not selected_exam:
        return redirect(url_for('admin'))

    if os.path.exists(SCORES_FILE):
        with open(SCORES_FILE, newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            scores = [local_score_row(row)[1:] for row in reader if local_score_row(row)[0] == exam_code]
    return render_template(
        'admin.html',
        scores=scores,
        sessions=[],
        selected_exam=(
            selected_exam["code"],
            selected_exam["school"],
            selected_exam["class_name"],
            selected_exam["created_at"]
        )
    )


@app.route('/download')
def download_scores():
    exam_code = request.args.get("code", "").strip()
    if not is_valid_exam_code_format(exam_code):
        return "수행평가 코드가 필요합니다.", 400

    if DATABASE_URL:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT code, school, class_name
                    FROM exam_sessions
                    WHERE code = %s;
                """, (exam_code,))
                exam_row = cur.fetchone()

                if not exam_row:
                    return "존재하지 않는 수행평가 코드입니다.", 404

                cur.execute("""
                    SELECT
                        student_id AS "학번",
                        name AS "이름",
                        COALESCE(level, '') AS "레벨",
                        average_score AS "평균 점수",
                        high_score AS "최고 점수",
                        to_char(submitted_at, 'YYYY-MM-DD HH24:MI:SS') AS "제출 시간"
                    FROM scores
                    WHERE exam_code = %s
                    ORDER BY student_id;
                """, (exam_code,))
                rows = cur.fetchall()
                columns = [desc[0] for desc in cur.description]

        if not rows:
            return "제출된 데이터가 없습니다.", 404

        df = pd.DataFrame(rows, columns=columns)
        df.to_excel(XLSX_FILE, index=False, sheet_name="수행평가 결과")

        filename = make_download_filename({
            "code": exam_row[0],
            "school": exam_row[1],
            "class_name": exam_row[2]
        })
        return send_file(XLSX_FILE, as_attachment=True, download_name=filename)

    if not os.path.exists(SCORES_FILE):
        return "제출된 데이터가 없습니다.", 404

    rows = []
    with open(SCORES_FILE, newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        rows = [local_score_row(row)[1:] for row in reader if local_score_row(row)[0] == exam_code]

    if not rows:
        return "제출된 데이터가 없습니다.", 404

    df = pd.DataFrame(rows, columns=["학번", "이름", "레벨", "평균 점수", "최고 점수", "제출 시간"])
    df.to_excel(XLSX_FILE, index=False, sheet_name="수행평가 결과")

    session_data = load_local_sessions().get(exam_code, {"code": exam_code, "school": "", "class_name": ""})
    return send_file(XLSX_FILE, as_attachment=True, download_name=make_download_filename(session_data))


@app.route('/reset', methods=['POST'])
def reset_scores():
    exam_code = request.form.get("code", "").strip()
    if not is_valid_exam_code_format(exam_code):
        return redirect(url_for('admin'))

    if DATABASE_URL:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    UPDATE scores
                    SET level = NULL,
                        average_score = NULL,
                        high_score = NULL,
                        submitted_at = NULL;
                    WHERE exam_code = %s;
                """, (exam_code,))

        return redirect(url_for('admin_exam', exam_code=exam_code))

    if os.path.exists(SCORES_FILE):
        with open(SCORES_FILE, newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            rows = []
            for row in reader:
                normalized_row = local_score_row(row)
                if normalized_row[0] == exam_code:
                    rows.append([normalized_row[0], normalized_row[1], normalized_row[2], '', '', '', ''])
                else:
                    rows.append(normalized_row)

        with open(SCORES_FILE, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerows(rows)

    return redirect(url_for('admin_exam', exam_code=exam_code))



@app.route('/preset_ids', methods=['POST'])
def preset_ids():
    data = request.json
    exam_code = data.get('exam_code', '').strip()
    start_id = int(data['start_id'])
    end_id = int(data['end_id'])

    if not is_valid_exam_code_format(exam_code):
        return jsonify({"status": "error", "message": "수행평가 코드가 필요합니다."}), 400

    if not DATABASE_URL and not local_exam_exists(exam_code):
        return jsonify({"status": "error", "message": "존재하지 않는 수행평가 코드입니다."}), 404

    if DATABASE_URL:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                for student_id in range(start_id, end_id + 1):
                    cur.execute("""
                        INSERT INTO scores
                            (exam_code, student_id, name, level, average_score, high_score, submitted_at)
                        VALUES
                            (%s, %s, '', NULL, NULL, NULL, NULL)
                        ON CONFLICT (exam_code, student_id) DO NOTHING;
                    """, (exam_code, str(student_id)))

        return jsonify({"status": "preset_done"})

    new_rows = []
    if os.path.exists(SCORES_FILE):
        with open(SCORES_FILE, newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            existing_rows = {}
            for row in reader:
                normalized_row = local_score_row(row)
                existing_rows[(normalized_row[0], normalized_row[1])] = normalized_row
    else:
        existing_rows = {}

    for student_id in range(start_id, end_id + 1):
        sid = str(student_id)
        if (exam_code, sid) not in existing_rows:
            new_rows.append([exam_code, sid, "", "", "", "", ""])

    with open(SCORES_FILE, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerows(new_rows)

    return jsonify({"status": "preset_done"})


@app.route('/clear_all', methods=['POST'])
def clear_all():
    data = request.get_json(silent=True) or {}
    exam_code = data.get("exam_code", "").strip()
    if not is_valid_exam_code_format(exam_code):
        return jsonify({"status": "error", "message": "수행평가 코드가 필요합니다."}), 400

    if DATABASE_URL:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM scores WHERE exam_code = %s;", (exam_code,))

        return jsonify({"status": "cleared_all"})

    if os.path.exists(SCORES_FILE):
        with open(SCORES_FILE, newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            rows = [local_score_row(row) for row in reader if local_score_row(row)[0] != exam_code]

        with open(SCORES_FILE, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerows(rows)
    return jsonify({"status": "cleared_all"})


init_db()


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))  # 환경 변수 PORT를 가져오고, 기본값으로 5000 사용
    app.run(host="0.0.0.0", port=port, debug=True)  # 모든 IP에서 접속 가능하도록 host="0.0.0.0" 설정
