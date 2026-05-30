from faker import Faker
import random
import csv
import os

fake = Faker()

NUM_STUDENTS = 29000
START_ID = int(input("Enter starting student ID: "))

levels = ['Low', 'Medium', 'High']
yes_no = ['On time', 'Late', 'No Submmission']
Active_inactive = ['Highly Active', 'Active', 'Inactive']
months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']

# 🔹 Auto path (script ke location ke hisaab se)
# 🔹 Detect current folder name
base_dir = os.path.dirname(os.path.abspath(__file__))
current_folder = os.path.basename(base_dir)

if current_folder == "data":
    # Already inside data folder
    file_path = os.path.join(base_dir, 'student_dataset_missing.csv')
else:
    # Create/use data folder
    data_dir = os.path.join(base_dir, 'data')
    os.makedirs(data_dir, exist_ok=True)
    file_path = os.path.join(data_dir, 'student_dataset_missing.csv')

file_exists = os.path.isfile(file_path)

MISSING_PROB = 0.15
ROW_DROP_PROB = 0.05

def make_missing(value):
    if random.random() < MISSING_PROB:
        return random.choice([None, "", "NaN"])
    return value

def calculate_exam_score(hours, attendance, prev_score, test_score, project_marks, submission, participation, extra_c, backlogs):
    
    hours = hours if isinstance(hours, (int, float)) else 0
    attendance = attendance if isinstance(attendance, (int, float)) else 0
    test_score = test_score if isinstance(test_score, (int, float)) else 0
    project_marks = project_marks if isinstance(project_marks, (int, float)) else 0

    score = (
        (hours * 2) +
        (attendance * 0.3) +
        (prev_score * 0.2) +
        (test_score * 1.5) +
        (project_marks * 1)
    )

    if submission == 'On time':
        score += 10
    elif submission == 'No Submmission':
        score -= 10

    if participation == 'High':
        score += 10
    elif participation == 'Medium':
        score += 5

    if extra_c == 'Highly Active':
        score += 10
    elif extra_c == 'Active':
        score += 5

    score -= (backlogs * 5)
    score = score + random.uniform(-15, 15)

    return max(0, min(100, round(((score / 245) * 100), 2)))


with open(file_path, mode='a', newline='') as file:
    writer = csv.writer(file)

    if not file_exists:
        writer.writerow([
            'Student_ID','Month','Hours_Studied','Attendance',
            'Submission_Timeliness','Participation','Extra_C',
            'Previous_Scores','Test_Score','Project_Marks',
            'Backlogs','Exam_Score'
        ])

    student_id = START_ID

    for _ in range(NUM_STUDENTS):

        # ❗ Clean (NO dirty)
        prev_score = random.randint(40, 100)
        backlogs = random.randint(0, 5)
        project_marks = random.randint(10, 40)

        for month in months:

            if month != 'Jun' and random.random() < ROW_DROP_PROB:
                continue

            # ✅ Dirty allowed
            hours = make_missing(random.randint(5, 40))
            attendance = make_missing(random.randint(50, 100))
            submission = make_missing(random.choice(yes_no))
            participation = make_missing(random.choice(levels))
            extra_c = make_missing(random.choice(Active_inactive))
            test_score = make_missing(random.randint(10, 30))
            project_marks_m = make_missing(project_marks)

            exam_score = calculate_exam_score(
                hours, attendance, prev_score,
                test_score, project_marks_m, submission,
                participation, extra_c, backlogs
            )

            writer.writerow([
                student_id,
                month,
                hours,
                attendance,
                submission,
                participation,
                extra_c,
                prev_score,
                test_score,
                project_marks_m,
                backlogs,
                exam_score
            ])

        student_id += 1

print(f"✅ Dataset generated at: {file_path}")