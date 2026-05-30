"""
suggestion.py
Generates actionable improvement tips based on student data and predicted score.
"""


def get_grade(score: float) -> str:
    if score >= 90: return 'A+'
    if score >= 80: return 'A'
    if score >= 70: return 'B'
    if score >= 60: return 'C'
    if score >= 50: return 'D'
    return 'F'


def generate_suggestions(student_data: dict, predicted_score: float) -> list:
    tips = []
    att  = float(student_data.get('Attendance', 100))
    hrs  = float(student_data.get('Hours_Studied', 0))
    sub  = student_data.get('Submission_Timeliness', '')
    par  = student_data.get('Participation', '')
    ext  = student_data.get('Extra_C', '')
    bck  = int(student_data.get('Backlogs', 0))
    tst  = float(student_data.get('Test_Score', 30))
    prj  = float(student_data.get('Project_Marks', 40))

    if att < 60:
        tips.append({"icon": "🚨", "category": "Critical",
                     "text": f"Attendance critically low ({att:.0f}%). Risk of being barred from exams."})
    elif att < 75:
        tips.append({"icon": "⚠️", "category": "Warning",
                     "text": f"Attendance {att:.0f}% is below the 75% threshold. Attend all remaining classes."})

    if hrs < 10:
        tips.append({"icon": "📚", "category": "Critical",
                     "text": f"Only {hrs:.0f} hrs/week of study is insufficient. Target at least 25 hours."})
    elif hrs < 20:
        tips.append({"icon": "📖", "category": "Improvement",
                     "text": f"Increase study time from {hrs:.0f} to 25+ hrs/week for better results."})

    if sub == 'No Submission':
        tips.append({"icon": "❌", "category": "Critical",
                     "text": "No submissions detected. Missing work directly costs marks."})
    elif sub == 'Late':
        tips.append({"icon": "⏰", "category": "Warning",
                     "text": "Late submissions hurt your grade. Use a planner to track deadlines."})

    if par == 'Low':
        tips.append({"icon": "🙋", "category": "Improvement",
                     "text": "Low participation. Active learners score 10-15% higher consistently."})

    if bck >= 4:
        tips.append({"icon": "🆘", "category": "Critical",
                     "text": f"{bck} backlogs are a serious risk. Dedicate daily revision blocks to clear them."})
    elif bck >= 2:
        tips.append({"icon": "📌", "category": "Warning",
                     "text": f"{bck} backlogs found. Create a clearing schedule this week."})

    if ext == 'Inactive':
        tips.append({"icon": "🏅", "category": "Growth",
                     "text": "No co-curricular activity. Even one club improves discipline significantly."})

    if tst < 15:
        tips.append({"icon": "📝", "category": "Academic",
                     "text": f"Test score {tst:.0f}/30 is low. Solve 5 past papers per week."})

    if prj < 20:
        tips.append({"icon": "💡", "category": "Academic",
                     "text": f"Project score {prj:.0f}/40 needs work. Meet your supervisor for guidance."})

    grade = get_grade(predicted_score)
    verdict_map = {
        'A+': {"icon": "🏆", "category": "Excellent",    "text": "Outstanding! You are among the top performers. Keep it up."},
        'A':  {"icon": "🌟", "category": "Great",        "text": "Excellent work! Push into A+ with consistency."},
        'B':  {"icon": "✅", "category": "Good",         "text": "Solid performance. One focused month can push you to A."},
        'C':  {"icon": "📈", "category": "Average",      "text": "Average result. Build a structured daily study plan."},
        'D':  {"icon": "⚠️", "category": "Below Avg",   "text": "Below average. Seek academic support immediately."},
        'F':  {"icon": "🆘", "category": "At Risk",      "text": "High risk of failing. Attend every class and request tutoring now."},
    }
    tips.append(verdict_map[grade])

    if not tips:
        tips.append({"icon": "🎯", "category": "Perfect",
                     "text": "All metrics look great! Maintain your momentum."})
    return tips


if __name__ == '__main__':
    sample = {
        "Hours_Studied": 8, "Attendance": 62,
        "Submission_Timeliness": "No Submission", "Participation": "Low",
        "Extra_C": "Inactive", "Previous_Scores": 48,
        "Test_Score": 11, "Project_Marks": 15, "Backlogs": 4
    }
    for tip in generate_suggestions(sample, 38.5):
        print(f"[{tip['category']}] {tip['icon']} {tip['text']}")
