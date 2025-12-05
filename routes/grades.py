from flask import Blueprint, render_template, request
from models import StudentSubmission, ExamVersion, Exam, db
from routes.auth import login_required

bp = Blueprint('grades', __name__, url_prefix='/grades')

@bp.route('/')
@login_required
def list_grades():
    from models import Course
    exams = Exam.query.join(ExamVersion).join(StudentSubmission).group_by(Exam.id).order_by(Exam.title).all()
    courses = Course.query.order_by(Course.name).all()
    
    exam_id = request.args.get('exam_id', type=int)
    course_id = request.args.get('course_id', type=int)
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    query = StudentSubmission.query.join(ExamVersion).join(Exam)
    
    if exam_id and exam_id != -1:
        query = query.filter(Exam.id == exam_id)
        
    if course_id:
        query = query.filter(Exam.course_id == course_id)
        
    if start_date:
        from datetime import datetime
        try:
            sd = datetime.strptime(start_date, '%Y-%m-%d')
            query = query.filter(StudentSubmission.submission_date >= sd)
        except ValueError:
            pass
            
    if end_date:
        from datetime import datetime
        from datetime import timedelta
        try:
            # End date inclusive (until end of day)
            ed = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)
            query = query.filter(StudentSubmission.submission_date < ed)
        except ValueError:
            pass

    submissions = query.order_by(Exam.title.asc(), StudentSubmission.submission_date.desc()).all()
    
    return render_template('grades/list.html', 
                           submissions=submissions, 
                           exams=exams, 
                           courses=courses,
                           selected_exam_id=exam_id,
                           selected_course_id=course_id,
                           selected_start_date=start_date,
                           selected_end_date=end_date)

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
    
    score = 0
    total = 0
    
    for eq in exam_questions:
        student_answer = detected_answers.get(str(eq.question_number)) # JSON keys are strings
        is_correct = False
        
        # Get question weight
        q_weight = eq.question.weight if eq.question and eq.question.weight is not None else 1.0
        
        if student_answer and student_answer == eq.correct_option_char:
            score += 1
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
            'resolution': question_resolution,
            'weight': q_weight
        })
        total += 1
        
    return render_template('student/result.html', 
                           exam=exam, 
                           version=version, 
                           score=score, 
                           total=total, 
                           final_grade=submission.score,
                           results=results,
                           submission=submission)

@bp.route('/delete/<int:submission_id>', methods=['POST'])
@login_required
def delete_submission(submission_id):
    submission = StudentSubmission.query.get_or_404(submission_id)
    
    # Optional: Delete the image file if desired, but keeping it might be safer for audit.
    # For now, we just delete the database record as requested to allow re-upload.
    
    exam_id = submission.version.exam.id
    
    db.session.delete(submission)
    db.session.commit()
    
    from flask import flash, redirect, url_for
    flash('Nota deletada com sucesso. O aluno pode enviar o gabarito novamente.', 'success')
    return redirect(url_for('grades.list_grades', exam_id=exam_id))

@bp.route('/export_csv/<int:exam_id>')
@login_required
def export_csv(exam_id):
    import csv
    import io
    from flask import Response
    
    exam = Exam.query.get_or_404(exam_id)
    submissions = StudentSubmission.query.join(ExamVersion).filter(ExamVersion.exam_id == exam.id).all()
    
    # Create CSV in memory
    output = io.StringIO()
    output.write(u'\ufeff') # Add BOM for Excel
    # Force quotes for all fields to prevent delimiter issues
    writer = csv.writer(output, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
    
    # Header
    writer.writerow(['Nome do Aluno', 'Curso', 'Versão da Prova', 'Nota Final'])
    
    # Data
    for sub in submissions:
        writer.writerow([
            sub.student_name,
            sub.student_course,
            sub.version.label,
            sub.score if sub.score is not None else 0.0
        ])
        
    output.seek(0)
    
    return Response(
        output,
        mimetype="text/csv",
        headers={"Content-Disposition": f"attachment;filename=notas_{exam.title.replace(' ', '_')}.csv"}
    )
