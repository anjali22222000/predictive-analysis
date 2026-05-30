"""
app.py - EduPredict Flask Backend
==================================
All routes:
  POST /api/login          - get auth token
  GET  /api/analytics      - dashboard stats
  POST /api/predict        - ML prediction
  GET  /api/students       - student list (search/filter/sort/page)
  GET  /api/student/<id>   - single student detail
  GET  /api/model-info     - model comparison results
  GET  /api/security       - security event log
  GET  /api/health         - health check
"""
import os, sys, json
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

# Fix paths so imports work from any working directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_DIR  = os.path.join(BASE_DIR, 'src')
sys.path.insert(0, SRC_DIR)

from predict    import predict_exam_score
from analytics  import run_analytics, get_grade, get_risk_level
from suggestion import generate_suggestions
from security   import (audit, rate_limit, validate_predict_input,
                        generate_token, verify_token, get_security_stats)

import pandas as pd

STATIC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')
DATA_DIR   = os.path.join(BASE_DIR, 'data')
RAW_CSV    = os.path.join(DATA_DIR, 'student_dataset.csv')
MODEL_JSON = os.path.join(BASE_DIR, 'outputs', 'model_comparison.json')

app = Flask(__name__, static_folder=STATIC_DIR, static_url_path='')
CORS(app, origins='*')

# ── Load CSV once ──────────────────────────────────────────────────────────────
df_raw = pd.read_csv(RAW_CSV)
print(f"[INFO] Loaded CSV: {len(df_raw)} records, "
      f"{df_raw['Student_ID'].nunique()} unique students")


# ── Build STUDENTS list directly from CSV (no stale JSON file) ─────────────────
def _grade(score):
    if score >= 90: return 'A+'
    if score >= 80: return 'A'
    if score >= 70: return 'B'
    if score >= 60: return 'C'
    if score >= 50: return 'D'
    return 'F'

def _risk(score):
    if score >= 70: return 'Low'
    if score >= 50: return 'Medium'
    return 'High'

def build_students(df):
    students = []
    for sid, grp in df.groupby('Student_ID'):
        avg_score = round(float(grp['Exam_Score'].mean()), 2)

        # Monthly scores
        monthly = {}
        if 'Month' in grp.columns:
            monthly = (
                grp.groupby('Month')['Exam_Score']
                   .mean()
                   .round(2)
                   .to_dict()
            )

        students.append({
            'id':             int(sid),
            'avg_score':      avg_score,
            'avg_attendance': round(float(grp['Attendance'].mean()), 1),
            'avg_hours':      round(float(grp['Hours_Studied'].mean()), 1),
            'avg_test':       round(float(grp['Test_Score'].mean()), 1),
            'avg_project':    round(float(grp['Project_Marks'].mean()), 1),
            'backlogs':       int(grp['Backlogs'].max()),
            'prev_scores':    int(grp['Previous_Scores'].iloc[0]),
            'records':        int(len(grp)),
            'grade':          _grade(avg_score),
            'risk':           _risk(avg_score),
            'monthly':        monthly,
        })

    print(f"[INFO] Built STUDENTS list: {len(students)} students")
    return students

STUDENTS = build_students(df_raw)


# ── Analytics cache ────────────────────────────────────────────────────────────
ANALYTICS_CACHE = None

def get_analytics():
    global ANALYTICS_CACHE
    if ANALYTICS_CACHE is None:
        ANALYTICS_CACHE = run_analytics(df_raw)

    data = dict(ANALYTICS_CACHE)

    month_order = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
    data['monthly_avg_scores'] = {
        m: data['monthly_avg_scores'].get(m)
        for m in month_order
        if m in data['monthly_avg_scores']
    }
    return data


# ── Demo users ─────────────────────────────────────────────────────────────────
DEMO_USERS = {
    'teacher': ('teacher123', 'teacher'),
    'admin':   ('admin2024',  'admin'),
    'viewer':  ('view123',    'viewer'),
}


# ══════════════════════════════════════════════════════════════════════════════
#  ROUTES
# ══════════════════════════════════════════════════════════════════════════════

@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')


@app.route('/api/login', methods=['POST'])
@rate_limit
def login():
    data     = request.get_json() or {}
    username = str(data.get('username', '')).strip()
    password = str(data.get('password', '')).strip()
    ip       = request.remote_addr
    if username in DEMO_USERS and DEMO_USERS[username][0] == password:
        role  = DEMO_USERS[username][1]
        token = generate_token(username, role)
        audit('LOGIN_SUCCESS', f'user={username}', 'INFO', ip)
        return jsonify({'token': token, 'user': username, 'role': role})
    audit('LOGIN_FAIL', f'user={username}', 'WARNING', ip)
    return jsonify({'error': 'Invalid credentials'}), 401


@app.route('/api/analytics')
@rate_limit
def api_analytics():
    audit('ANALYTICS_VIEW', 'fetched', 'INFO', request.remote_addr)
    return jsonify(get_analytics())


@app.route('/api/predict', methods=['POST'])
@rate_limit
def api_predict():
    raw_data = request.get_json() or {}
    clean, errors = validate_predict_input(raw_data)
    if errors:
        audit('INVALID_INPUT', '; '.join(errors), 'WARNING', request.remote_addr)
        return jsonify({'error': 'Validation failed', 'details': errors}), 400

    score = predict_exam_score(clean)
    grade = get_grade(score)
    risk  = get_risk_level(score)
    tips  = generate_suggestions(clean, score)

    sub_n = {'On time': 10, 'Late': 5, 'No Submission': 0}.get(clean['Submission_Timeliness'], 5)
    par_n = {'High': 10, 'Medium': 5, 'Low': 0}.get(clean['Participation'], 5)
    ext_n = {'Highly Active': 10, 'Active': 5, 'Inactive': 0}.get(clean['Extra_C'], 5)

    # Academic score: weighted composite, normalized so max inputs (100+30+40) → 100
    # raw = Previous_Scores(40-100) + Test_Score(10-30)*2 + Project_Marks(10-40)
    # min_raw = 40 + 20 + 10 = 70,  max_raw = 100 + 60 + 40 = 200
    raw_academic = float(clean['Previous_Scores']) + float(clean['Test_Score']) * 2 + float(clean['Project_Marks'])
    academic_score = round((raw_academic - 70) / (200 - 70) * 100, 1)

    attendance_val = float(clean['Attendance'])

    # Low attendance override: below 50% → force FAIL grade
    low_attendance = attendance_val < 50

    breakdown = {
        'Academic':        academic_score,
        'Attendance':      round(attendance_val / 10, 1),
        'Study Habit':     round(float(clean['Hours_Studied']) / 4, 1),
        'Discipline':      round(sub_n, 1),
        'Participation':   round(par_n, 1),
        'Extracurricular': round(ext_n, 1),
    }

    # Low attendance override — below 50% → automatic FAIL, not eligible
    if low_attendance:
        grade = 'F'
        risk  = 'High'

    audit('PREDICT', f'score={score} grade={grade}', 'INFO', request.remote_addr)
    return jsonify({
        'predicted_score': score,
        'grade':           grade,
        'risk_level':      risk,
        'suggestions':     tips,
        'breakdown':       breakdown,
        'low_attendance':  low_attendance,
    })


@app.route('/api/students')
@rate_limit
def api_students():
    q        = request.args.get('q', '').strip()
    grade_f  = request.args.get('grade', '').strip()
    risk_f   = request.args.get('risk', '').strip()
    sort_by  = request.args.get('sort', 'avg_score')
    order    = request.args.get('order', 'desc')
    page     = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 20))

    results = STUDENTS
    if q:       results = [s for s in results if q in str(s['id'])]
    if grade_f: results = [s for s in results if s['grade'] == grade_f]
    if risk_f:  results = [s for s in results if s['risk']  == risk_f]

    reverse = (order == 'desc')
    valid_sorts = {'avg_score', 'avg_attendance', 'avg_hours', 'backlogs', 'id'}
    if sort_by in valid_sorts:
        results = sorted(results, key=lambda x: x.get(sort_by, 0), reverse=reverse)

    total = len(results)
    start = (page - 1) * per_page
    paged = results[start:start + per_page]

    audit('STUDENTS_LIST', f'q={q} count={total}', 'INFO', request.remote_addr)
    return jsonify({
        'students': paged,
        'total':    total,
        'page':     page,
        'pages':    (total + per_page - 1) // per_page,
    })


@app.route('/api/student/<int:student_id>')
@rate_limit
def api_student(student_id):
    student = next((s for s in STUDENTS if s['id'] == student_id), None)
    if not student:
        return jsonify({'error': 'Student not found'}), 404
    rows = df_raw[df_raw['Student_ID'] == student_id].to_dict(orient='records')
    audit('STUDENT_DETAIL', f'id={student_id}', 'INFO', request.remote_addr)
    return jsonify({**student, 'monthly_records': rows})


@app.route('/api/model-info')
def api_model_info():
    if os.path.exists(MODEL_JSON):
        with open(MODEL_JSON) as f:
            return jsonify(json.load(f))
    return jsonify({'error': 'Run train_model.py first'}), 404


@app.route('/api/security')
@rate_limit
def api_security():
    return jsonify(get_security_stats())


@app.route('/api/health')
def health():
    return jsonify({
        'status':   'ok',
        'students': len(STUDENTS),
        'records':  len(df_raw),
    })


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
