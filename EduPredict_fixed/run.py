"""
run.py - EduPredict Master Launcher
=====================================
Just run: python run.py
Then open: http://127.0.0.1:5000
"""
import os, sys, json, argparse

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(ROOT, 'src'))

FEATURED  = os.path.join(ROOT, 'data', 'student_dataset_featured.csv')
MODEL_PKL = os.path.join(ROOT, 'models', 'trained_model.pkl')
SUMMARY   = os.path.join(ROOT, 'data', 'students_summary.json')
RAW_CSV   = os.path.join(ROOT, 'data', 'student_dataset.csv')

parser = argparse.ArgumentParser()
parser.add_argument('--retrain', action='store_true', help='Force retrain model')
parser.add_argument('--port', type=int, default=5000, help='Port number (default 5000)')
args = parser.parse_args()

print()
print("=" * 46)
print("   EduPredict  -  ML Student Analyser")
print("=" * 46)
print()

# Step 1: Feature Engineering
if not os.path.exists(FEATURED):
    print("[1/4] Running feature engineering...")
    from feature_engineering import feature_engineering
    feature_engineering(RAW_CSV, FEATURED)
else:
    print("[1/4] Featured dataset already exists")

# Step 2: Train model
if not os.path.exists(MODEL_PKL) or args.retrain:
    print("[2/4] Training ML models...")
    from train_model import train
    train()
else:
    print("[2/4] Trained model already exists  (use --retrain to force)")

# Step 3: Student summary JSON
if not os.path.exists(SUMMARY):
    print("[3/4] Pre-computing student summaries...")
    import pandas as pd
    from analytics import get_grade, get_risk_level

    df = pd.read_csv(RAW_CSV)
    students = df.groupby('Student_ID').agg(
        avg_score      =('Exam_Score',     'mean'),
        avg_attendance =('Attendance',     'mean'),
        avg_hours      =('Hours_Studied',  'mean'),
        avg_test       =('Test_Score',     'mean'),
        avg_project    =('Project_Marks',  'mean'),
        backlogs       =('Backlogs',       'first'),
        prev_scores    =('Previous_Scores','first'),
        records        =('Month',          'count'),
    ).reset_index().round(2)

    monthly = (df.pivot_table(index='Student_ID', columns='Month',
                               values='Exam_Score', aggfunc='mean')
                 .fillna(0).round(2))

    out = []
    for _, r in students.iterrows():
        sid  = int(r['Student_ID'])
        mrow = {}
        for m in ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']:
            if m in monthly.columns:
                v = monthly[monthly.index == sid][m].values
                mrow[m] = round(float(v[0]), 2) if len(v) else 0.0
        out.append({
            'id':             sid,
            'avg_score':      round(float(r['avg_score']),      2),
            'avg_attendance': round(float(r['avg_attendance']), 1),
            'avg_hours':      round(float(r['avg_hours']),      1),
            'avg_test':       round(float(r['avg_test']),       1),
            'avg_project':    round(float(r['avg_project']),    1),
            'backlogs':       int(r['backlogs']),
            'prev_scores':    int(r['prev_scores']),
            'records':        int(r['records']),
            'grade':          get_grade(float(r['avg_score'])),
            'risk':           get_risk_level(float(r['avg_score'])),
            'monthly':        mrow,
        })

    with open(SUMMARY, 'w') as f:
        json.dump(sorted(out, key=lambda x: -x['avg_score']), f, indent=2)
    print(f"   Saved {len(out)} student profiles")
else:
    print("[3/4] Student summaries already exist")

# Step 4: Launch Flask
print(f"[4/4] Starting Flask server...")
print()
print("  +-----------------------------------------+")
print(f"  |  Open browser: http://127.0.0.1:{args.port}      |")
print("  |  Press Ctrl+C to stop                  |")
print("  +-----------------------------------------+")
print()

os.chdir(os.path.join(ROOT, 'app'))
sys.path.insert(0, os.path.join(ROOT, 'src'))

from app.app import app
app.run(debug=False, port=args.port, host='127.0.0.1')
