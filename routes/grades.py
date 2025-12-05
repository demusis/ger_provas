from flask import Blueprint, render_template, request
from models import StudentSubmission, ExamVersion, Exam
from routes.auth import login_required

bp = Blueprint('grades', __name__, url_prefix='/grades')

@bp.route('/')
@login_required
def list_grades():
    exams = Exam.query.join(ExamVersion).join(StudentSubmission).group_by(Exam.id).order_by(Exam.title).all()
    exam_id = request.args.get('exam_id', type=int)
    
    submissions = []
    if exam_id:
        query = StudentSubmission.query.join(ExamVersion).join(Exam)
        if exam_id != -1:
            query = query.filter(Exam.id == exam_id)
        submissions = query.order_by(Exam.title.asc(), StudentSubmission.submission_date.desc()).all()
    
    return render_template('grades/list.html', submissions=submissions, exams=exams, selected_exam_id=exam_id)

@bp.route('/<int:submission_id>')
@login_required
def view_submission(submission_id):
    submission = StudentSubmission.query.get_or_404(submission_id)
    version = submission.version
    exam = version.exam
    
    import json
    detected_answers = json.loads(submission.answers)
    
    results = []
    # Get questions ordered by number
    exam_questions = sorted(version.questions, key=lambda x: x.question_number)
    
    for eq in exam_questions:
        student_answer = detected_answers.get(str(eq.question_number)) # JSON keys are strings
        is_correct = False
        if student_answer and student_answer == eq.correct_option_char:
            is_correct = True
        
        question_statement = "QUESTÃO DELETADA"
        question_resolution = "N/A"
        
        if eq.question:
            question_statement = eq.question.statement
            question_resolution = eq.question.resolution
            
        results.append({
            'number': eq.question_number,
            'statement': question_statement,
            'student_answer': student_answer if student_answer else "N/A",
            'correct_answer': eq.correct_option_char,
            'is_correct': is_correct,
            'resolution': question_resolution
        })
        
    return render_template('student/result.html', 
                           exam=exam, 
                           version=version, 
                           score=submission.score / 10 * submission.total_questions, # Reconstruct raw score
                           total=submission.total_questions, 
                           final_grade=submission.score,
                           results=results,
                           submission=submission)
