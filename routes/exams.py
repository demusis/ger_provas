from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file, make_response
from models import db, Category, Exam, Course
from services.exam_service import create_exam_logic
from services.latex_service import generate_exam_latex
from routes.auth import login_required
import io

bp = Blueprint('exams', __name__, url_prefix='/exams')

@bp.route('/')
@login_required
def list_exams():
    course_id = request.args.get('course_id', type=int)
    courses = Course.query.order_by(Course.name).all()
    
    if course_id:
        exams = Exam.query.filter_by(course_id=course_id).order_by(Exam.id.desc()).all()
    else:
        exams = Exam.query.order_by(Exam.id.desc()).all()
        
    return render_template('exams/list.html', exams=exams, courses=courses, selected_course_id=course_id)

@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_exam():
    categories = Category.query.all()
    courses = Course.query.order_by(Course.name).all()
    
    if request.method == 'POST':
        title = request.form.get('title')
        date = request.form.get('date')
        course_id = request.form.get('course_id')
        num_versions = int(request.form.get('num_versions'))
        
        course = Course.query.get(course_id)
        if not course:
            flash('Disciplina inválida.', 'error')
            return redirect(url_for('exams.create_exam'))
        
        # Parse distribution
        distribution = {}
        total_questions = 0
        for cat in categories:
            count = request.form.get(f'cat_{cat.id}')
            if count and int(count) > 0:
                distribution[cat.id] = int(count)
                total_questions += int(count)
        
        try:
            show_resolution = 'show_resolution' in request.form
            create_exam_logic(title, date, course.name, course.id, total_questions, distribution, num_versions, show_resolution)
            flash('Prova gerada com sucesso!')
            return redirect(url_for('exams.list_exams'))
        except ValueError as e:
            flash(str(e), 'error')
            
    return render_template('exams/create.html', categories=categories, courses=courses)

@bp.route('/download/<int:exam_id>')
@login_required
def download_latex(exam_id):
    latex_content = generate_exam_latex(exam_id)
    
    response = make_response(latex_content)
    response.headers['Content-Type'] = 'application/x-latex'
    response.headers['Content-Disposition'] = f'attachment; filename=prova_{exam_id}.tex'
    return response

@bp.route('/toggle_resolution/<int:exam_id>')
@login_required
def toggle_resolution(exam_id):
    exam = Exam.query.get_or_404(exam_id)
    exam.show_resolution = not exam.show_resolution
    db.session.commit()
    flash(f'Visibilidade do gabarito da prova "{exam.title}" alterada para {"Visível" if exam.show_resolution else "Oculto"}.')
    return redirect(url_for('exams.list_exams'))
