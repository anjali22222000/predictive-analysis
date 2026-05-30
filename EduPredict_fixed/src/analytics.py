"""
analytics.py
Computes all aggregated statistics for the Flask dashboard API.
"""
import os
import pandas as pd

BASE_DIR  = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, 'data', 'student_dataset.csv')


def get_grade(score: float) -> str:
    if score >= 90: return 'A+'
    if score >= 80: return 'A'
    if score >= 70: return 'B'
    if score >= 60: return 'C'
    if score >= 50: return 'D'
    return 'F'


def get_risk_level(score: float) -> str:
    if score >= 70: return 'Low'
    if score >= 55: return 'Medium'
    return 'High'


def run_analytics(df: pd.DataFrame = None) -> dict:
    if df is None:
        df = pd.read_csv(DATA_PATH)
    df = df.copy()
    df['Grade'] = df['Exam_Score'].apply(get_grade)

    month_order = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
    monthly_raw = df.groupby('Month')['Exam_Score'].mean().round(2).to_dict()
    monthly_avg = {m: float(monthly_raw.get(m, 0)) for m in month_order if m in monthly_raw}

    top5 = (df.groupby('Student_ID')['Exam_Score']
              .mean().sort_values(ascending=False)
              .head(5).round(2))
    top5_dict = {str(int(k)): float(v) for k, v in top5.items()}

    student_avgs = df.groupby('Student_ID')['Exam_Score'].mean()
    at_risk = int((student_avgs < 55).sum())

    df['hrs_bin'] = pd.cut(df['Hours_Studied'], bins=[0, 10, 20, 30, 40],
                           labels=['0-10', '10-20', '20-30', '30-40'])
    hrs_vs = df.groupby('hrs_bin', observed=True)['Exam_Score'].mean().round(2)
    hrs_vs_dict = {str(k): float(v) for k, v in hrs_vs.items()}

    return {
        'grade_distribution':  {k: int(v) for k, v in df['Grade'].value_counts().items()},
        'monthly_avg_scores':  monthly_avg,
        'top_students':        top5_dict,
        'metrics': {
            'avg_attendance':    round(float(df['Attendance'].mean()), 1),
            'avg_hours_studied': round(float(df['Hours_Studied'].mean()), 1),
            'avg_exam_score':    round(float(df['Exam_Score'].mean()), 1),
            'avg_test_score':    round(float(df['Test_Score'].mean()), 1),
            'total_students':    int(df['Student_ID'].nunique()),
            'total_records':     int(len(df)),
            'at_risk_students':  at_risk,
            'pass_rate':         round(float((df['Exam_Score'] >= 50).mean() * 100), 1),
        },
        'participation_dist':  {k: int(v) for k, v in df['Participation'].value_counts().items()},
        'submission_dist':     {k: int(v) for k, v in df['Submission_Timeliness'].value_counts().items()},
        'extra_c_dist':        {k: int(v) for k, v in df['Extra_C'].value_counts().items()},
        'score_ranges': {
            '90-100': int((df['Exam_Score'] >= 90).sum()),
            '80-89':  int(((df['Exam_Score'] >= 80) & (df['Exam_Score'] < 90)).sum()),
            '70-79':  int(((df['Exam_Score'] >= 70) & (df['Exam_Score'] < 80)).sum()),
            '60-69':  int(((df['Exam_Score'] >= 60) & (df['Exam_Score'] < 70)).sum()),
            '<60':    int((df['Exam_Score'] < 60).sum()),
        },
        'hours_vs_score': hrs_vs_dict,
    }


if __name__ == '__main__':
    r = run_analytics()
    for k, v in r.items():
        print(f"\n{k}: {v}")
