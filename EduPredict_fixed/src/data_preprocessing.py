"""
data_preprocessing.py
Loads the raw/missing student dataset, fills missing values
per student, and saves cleaned CSV.
Run: python src/data_preprocessing.py
"""
import pandas as pd
import numpy as np
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def find_file(filename, search_path):
    for root, dirs, files in os.walk(search_path):
        if filename in files:
            return os.path.join(root, filename)
    return None


def preprocess(input_path=None, output_path=None):
    if input_path is None:
        input_path = find_file('student_dataset_missing.csv', BASE_DIR)
        if input_path is None:
            input_path = os.path.join(BASE_DIR, 'data', 'student_dataset.csv')
    if output_path is None:
        output_path = os.path.join(BASE_DIR, 'data', 'student_dataset_cleaned.csv')

    print(f"Loading: {input_path}")
    df = pd.read_csv(input_path)
    print(f"Initial shape: {df.shape}")

    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
    students = df['Student_ID'].unique()
    all_comb = pd.MultiIndex.from_product(
        [students, months], names=['Student_ID', 'Month']
    ).to_frame(index=False)
    df_full = pd.merge(all_comb, df, on=['Student_ID', 'Month'], how='left')
    print(f"After expansion: {df_full.shape}")

    numeric_cols = df_full.select_dtypes(include=[np.number]).columns.tolist()
    cat_cols = [c for c in df_full.select_dtypes(include=['object']).columns
                if c not in ['Student_ID', 'Month']]

    for col in numeric_cols:
        df_full[col] = pd.to_numeric(df_full[col], errors='coerce')

    def fill_group(group):
        for col in numeric_cols:
            if group[col].isnull().any():
                group[col] = group[col].fillna(group[col].mean()).round(2)
        for col in cat_cols:
            if group[col].isnull().any():
                mode = group[col].mode()
                group[col] = group[col].fillna(mode[0] if not mode.empty else 'Unknown')
        return group

    df_cleaned = (df_full
                  .groupby('Student_ID', group_keys=False)
                  .apply(fill_group)
                  .reset_index(drop=True))

    df_cleaned.to_csv(output_path, index=False)
    print(f"Cleaned dataset saved: {output_path}")
    print(f"Final shape: {df_cleaned.shape}")
    return df_cleaned


if __name__ == '__main__':
    preprocess()
