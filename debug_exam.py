from app import create_app
from models import db, ExamVersion, ExamQuestion

app = create_app()

with app.app_context():
    versions = ExamVersion.query.all()
    print(f"Total versions found: {len(versions)}")
    
    for v in versions:
        print(f"Version ID: {v.id}, Label: {v.label}, Exam: {v.exam.title}, Unique Code: {v.unique_code}")
        questions = v.questions
        print(f"  Questions count: {len(questions)}")
        for q in questions:
            print(f"    Q{q.question_number}: {q.question.statement[:20]}... (Correct: {q.correct_option_char})")
