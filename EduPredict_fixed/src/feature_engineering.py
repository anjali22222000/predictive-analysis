"""
feature_engineering.py
Converts raw student CSV into ML-ready featured CSV.
Run: python src/feature_engineering.py
"""
import pandas as pd
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def feature_engineering(input_path: str, output_path: str) -> pd.DataFrame:
    print("Starting Feature Engineering...")
    df = pd.read_csv(input_path)
    print(f"Dataset Loaded! Shape: {df.shape}")

    # Categorical to Numeric
    sub_map = {'on time': 10, 'late': 0, 'no submission': -10}
    df['Submission_Timeliness'] = (df['Submission_Timeliness']
                                   .str.strip().str.lower()
                                   .map(sub_map).fillna(0).round(2))

    df['Participation'] = df['Participation'].map(
        {'High': 10, 'Medium': 5, 'Low': 0}).fillna(0).round(2)

    df['Extra_C'] = df['Extra_C'].map(
        {'Highly Active': 10, 'Active': 5, 'Inactive': 0}).fillna(0).round(2)

    df.fillna(df.mean(numeric_only=True), inplace=True)

    # Scaled helpers
    df['Hours_Studied_scaled']   = (df['Hours_Studied'] / 40 * 10).clip(0, 10).round(2)
    df['Attendance_scaled']      = (df['Attendance'] / 10).clip(0, 10).round(2)
    df['Previous_Scores_scaled'] = (df['Previous_Scores'] / 10).clip(0, 10).round(2)
    df['Backlogs_scaled']        = (df['Backlogs'] / 5 * 10).clip(0, 10).round(2)

    # 4 Smart composite features
    df['engagement_feature']  = ((df['Attendance_scaled'] + df['Participation']) / 2).round(2)
    df['risk_feature']        = (df['Backlogs_scaled'] - df['Previous_Scores_scaled']).round(2)
    df['balance_feature']     = ((df['Hours_Studied_scaled'] + df['Submission_Timeliness']) / 2).round(2)
    df['activeness_feature']  = ((df['Participation'] + df['Extra_C']) / 2).round(2)

    final_cols = [
        'Student_ID', 'Month',
        'Hours_Studied', 'Attendance', 'Previous_Scores', 'Test_Score',
        'Project_Marks', 'Submission_Timeliness', 'Participation',
        'Extra_C', 'Backlogs', 'Exam_Score',
        'engagement_feature', 'risk_feature', 'balance_feature', 'activeness_feature'
    ]
    df_final = df[final_cols]
    df_final.to_csv(output_path, index=False)
    print(f"Feature Engineering done. Saved: {output_path}")
    return df_final


if __name__ == '__main__':
    inp = os.path.join(BASE_DIR, 'data', 'student_dataset.csv')
    out = os.path.join(BASE_DIR, 'data', 'student_dataset_featured.csv')
    feature_engineering(inp, out)
