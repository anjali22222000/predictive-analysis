from faker import Faker
import random
import csv
import os

fake = Faker()

NUM_STUDENTS = 30000
START_ID = int(input("Enter starting student ID: "))

levels = ['Low', 'Medium', 'High']
yes_no = ['On time', 'Late', 'No Submission']
Active_inactive = ['Highly Active', 'Active', 'Inactive']
months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']

# Get the folder where this script (data.py) is located
script_folder = os.path.dirname(os.path.abspath(__file__))

# CSV file path in the same folder
file_path = os.path.join(script_folder, 'student_dataset.csv')

# Check if file already exists
file_exists = os.path.isfile(file_path)

# Function to calculate exam score
def calculate_exam_score(hours, attendance, prev_score, test_score, project_marks, submission, participation, extra_c, backlogs):
    score = (
        (hours * 2) +
        (attendance * 0.3) +
        (prev_score * 0.2) +
        (test_score * 1.5) +
        (project_marks * 1)
    )
    if submission == 'On time':
        score += 10
    elif submission == 'Late':
        score += 0
    elif submission == 'No Submission':
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
    score = score + random.uniform(-5, 15)
    return max(0, min(100, round(((score / 245) * 100), 2)))

# Open file in write mode
with open(file_path, mode='a', newline='') as file:
    writer = csv.writer(file)

    if not file_exists:
        writer.writerow([
            'Student_ID',
            'Month',
            'Hours_Studied',
            'Attendance',
            'Submission_Timeliness',
            'Participation',
            'Extra_C',
            'Previous_Scores',
            'Test_Score',
            'Project_Marks',
            'Backlogs',
            'Exam_Score'
        ])

    student_id = START_ID

    for _ in range(NUM_STUDENTS):
        prev_score = random.randint(40, 100)
        backlogs = random.randint(0, 5)
        project_marks = random.randint(10, 40)

        for month in months:
            hours = random.randint(5, 40)
            attendance = random.randint(50, 100)
            submission = random.choice(yes_no)
            participation = random.choice(levels)
            extra_c = random.choice(Active_inactive)
            test_score = random.randint(10, 30)

            exam_score = calculate_exam_score(
                hours, attendance, prev_score,
                test_score, project_marks, submission,
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
                project_marks,
                backlogs,
                exam_score
            ])

        student_id += 1

print(f"✅ Data saved successfully at {file_path}")