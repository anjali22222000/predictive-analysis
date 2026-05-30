"""
evaluate_model.py
Evaluate multiple trained models and find the best one
Run: python src/evaluate_model.py
"""

import os
import pandas as pd
import numpy as np
import joblib

from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

FEATURE_COLS = [
    'Hours_Studied', 'Attendance', 'Previous_Scores', 'Test_Score',
    'Project_Marks', 'Submission_Timeliness', 'Participation',
    'Extra_C', 'Backlogs',
    'engagement_feature', 'risk_feature', 'balance_feature', 'activeness_feature'
]


def evaluate_all_models():

    # 🔹 Models list (ensure these files exist in /models folder)
    models = {
        "Linear Regression": os.path.join(BASE_DIR, 'models', 'trained_model_linear.pkl'),
        "Decision Tree": os.path.join(BASE_DIR, 'models', 'trained_model_decision.pkl'),
        "Random Forest": os.path.join(BASE_DIR, 'models', 'trained_model_random.pkl'),
        "Gradient Boosting": os.path.join(BASE_DIR, 'models', 'trained_model_gradient.pkl')
    }

    data_path = os.path.join(BASE_DIR, 'data', 'student_dataset_featured.csv')

    if not os.path.exists(data_path):
        raise FileNotFoundError(f"Data not found: {data_path}")

    df = pd.read_csv(data_path)

    X = df[FEATURE_COLS]
    y = df['Exam_Score']

    # same test set for all models
    _, X_test, _, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    results = []

    print("\n" + "=" * 50)
    print("     MODEL COMPARISON RESULTS")
    print("=" * 50)

    for name, path in models.items():

        if not os.path.exists(path):
            print(f"\n❌ {name} model not found at {path}")
            continue

        model = joblib.load(path)

        y_pred = np.clip(model.predict(X_test), 0, 100)

        mae = mean_absolute_error(y_test, y_pred)
        rmse = mean_squared_error(y_test, y_pred) ** 0.5
        r2 = r2_score(y_test, y_pred)

        print(f"\n🔹 {name}")
        print(f"   MAE  : {mae:.4f}")
        print(f"   RMSE : {rmse:.4f}")
        print(f"   R2   : {r2:.4f}")

        results.append({
            "name": name,
            "MAE": mae,
            "RMSE": rmse,
            "R2": r2
        })

    # 🔥 Find Best Model (based on highest R2)
    if results:
        best_model = max(results, key=lambda x: x["R2"])

        print("\n" + "=" * 50)
        print("🏆 BEST MODEL")
        print("=" * 50)
        print(f"{best_model['name']} is the best performing model")
        print(f"R2 Score : {best_model['R2']:.4f}")
        print(f"RMSE     : {best_model['RMSE']:.4f}")
        print(f"MAE      : {best_model['MAE']:.4f}")
        print("=" * 50)

    else:
        print("\n⚠️ No models evaluated. Check file paths.")


if __name__ == "__main__":
    evaluate_all_models()