# 🎓 EduPredict — ML Student Performance Analyser

A full-stack Machine Learning project that predicts student exam scores using
Linear Regression, Decision Tree, Random Forest, and Gradient Boosting —
complete with a live dashboard, cybersecurity features, and detailed analytics.

---

## 📁 Project Structure

```
EduPredict/
├── run.py                          ← Master launcher (run this!)
├── requirements.txt
├── README.md
│
├── data/
│   ├── Data.py                     ← Dataset generator (original)
│   ├── misssing_data.py            ← Missing-data generator (original)
│   ├── student_dataset.csv         ← Main dataset (1000 students × 6 months)
│   ├── student_dataset_missing.csv ← Dataset with injected missing values
│   ├── student_dataset_cleaned.csv ← After preprocessing
│   ├── student_dataset_featured.csv← After feature engineering (ML-ready)
│   └── students_summary.json       ← Pre-computed per-student stats (for API)
│
├── models/
│   ├── trained_model.pkl           ← Best model (Linear Regression, R²=0.913)
│   ├── trained_model0.pkl          ← Original model 0
│   ├── trained_model2.pkl          ← Original model 2
│   └── trained_model3.pkl          ← Original model 3
│
├── src/
│   ├── data_preprocessing.py       ← Cleans missing values per student
│   ├── feature_engineering.py      ← Encodes categoricals + 4 smart features
│   ├── train_model.py              ← Trains 4 models, saves best (R² comparison)
│   ├── evaluate_model.py           ← Full evaluation metrics + residual plot
│   ├── predict.py                  ← ML inference function
│   ├── analytics.py                ← Dashboard aggregations
│   ├── suggestion.py               ← Smart improvement tips engine
│   └── security.py                 ← 🔐 Cybersecurity layer
│
├── app/
│   ├── app.py                      ← Flask backend (12 REST endpoints)
│   └── static/
│       └── index.html              ← Full dashboard UI (6 tabs, all working)
│
├── notebooks/
│   ├── EDA.ipynb                   ← Exploratory Data Analysis
│   └── model_training.ipynb        ← Model training notebook
│
└── outputs/
    ├── model_comparison.json       ← R², MAE, RMSE for all 4 models
    ├── graphs/
    │   └── evaluation_plot.png     ← Actual vs Predicted + Residual plot
    └── reports/
```

---

## 🚀 Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run everything (auto trains if needed)
python run.py

# 3. Open browser
http://localhost:5000
```

---

## 🤖 ML Pipeline

| Step | Script | Description |
|------|--------|-------------|
| 1 | `data/misssing_data.py` | Generates raw dataset with missing values |
| 2 | `src/data_preprocessing.py` | Fills missing values per student |
| 3 | `src/feature_engineering.py` | Encodes + creates 4 smart features |
| 4 | `src/train_model.py` | Trains 4 models, saves best by R² |
| 5 | `src/evaluate_model.py` | Evaluation metrics + plots |
| 6 | `src/predict.py` | Single-student prediction function |

### Feature Engineering
- **Submission_Timeliness** → `{On time: 10, Late: 0, No Submission: -10}`
- **Participation** → `{High: 10, Medium: 5, Low: 0}`
- **Extra_C** → `{Highly Active: 10, Active: 5, Inactive: 0}`
- **engagement_feature** = `(Attendance_scaled + Participation) / 2`
- **risk_feature** = `Backlogs_scaled − Previous_Scores_scaled`
- **balance_feature** = `(Hours_Studied_scaled + Submission_Timeliness) / 2`
- **activeness_feature** = `(Participation + Extra_C) / 2`

### Model Results (trained on 6000 records, 80/20 split)

| Model | R² | MAE | RMSE |
|-------|----|-----|------|
| **Linear Regression** ⭐ | **0.913** | **3.067** | **3.536** |
| Gradient Boosting | 0.900 | 3.215 | 3.810 |
| Random Forest | 0.878 | 3.476 | 4.195 |
| Decision Tree | 0.715 | 5.222 | 6.415 |

---

## 🌐 API Endpoints

| Method | Route | Description |
|--------|-------|-------------|
| `POST` | `/api/login` | Get HMAC auth token |
| `GET` | `/api/analytics` | Dashboard statistics |
| `POST` | `/api/predict` | Predict student score |
| `GET` | `/api/students` | List all students (search/filter/sort/page) |
| `GET` | `/api/student/<id>` | Single student profile + monthly records |
| `GET` | `/api/model-info` | Model comparison results |
| `GET` | `/api/security` | Security event log |
| `GET` | `/api/health` | Health check |

---

## 🔐 Cybersecurity Features

| Feature | Implementation |
|---------|----------------|
| Rate Limiting | 60 req/min per IP — blocks flood/brute-force |
| XSS Protection | Regex pattern matching — blocks `<script>`, `onerror`, `eval()` |
| SQL Injection Guard | Detects `SELECT`, `UNION`, `DROP`, `--`, `#` patterns |
| HMAC Token Auth | SHA-256 signed tokens, 8-hour expiry, tamper-proof |
| Audit Logging | All events logged with IP + timestamp to `outputs/audit.log` |
| Input Validation | Allowlist-based categorical validation + numeric range clamping |

Demo credentials:
- `teacher` / `teacher123`
- `admin` / `admin2024`
- `viewer` / `view123`

---

## 📊 Dashboard Tabs

1. **Dashboard** — Stat cards, monthly trend, score distribution, grade doughnut, top 5
2. **Predict Score** — Form with sliders → ML prediction → score ring + breakdown + tips
3. **Students** — 1000 students, search/filter/sort/paginate, click → full profile modal
4. **Analytics** — Submission, extra-curricular, hours vs score, area trend charts
5. **ML Model** — Model comparison bars, pipeline visualization, feature importance
6. **Security** — Live event feed, threat level, HMAC demo, XSS/rate-limit simulation

---

## 👥 Team

Built with ❤️ using Python, Flask, Scikit-learn, Chart.js
