from flask import Blueprint, render_template, request, redirect, url_for, flash
from models import db, Course, Exam
from routes.auth import login_required

bp = Blueprint('courses', __name__, url_prefix='/courses')

@bp.route('/')
@login_required
def list_courses():
    courses = Course.query.order_by(Course.name).all()
    return render_template('courses/list.html', courses=courses)

@bp.route('/create', methods=['POST'])
@login_required
def create_course():
    name = request.form.get('name')
    if name:
        if Course.query.filter_by(name=name).first():
            flash('Disciplina já existe.', 'error')
        else:
            course = Course(name=name)
            db.session.add(course)
            db.session.commit()
            flash('Disciplina criada com sucesso!', 'success')
    else:
        flash('Nome da disciplina é obrigatório.', 'error')
    return redirect(url_for('courses.list_courses'))

@bp.route('/edit/<int:id>', methods=['POST'])
@login_required
def edit_course(id):
    course = Course.query.get_or_404(id)
    new_name = request.form.get('name')
    
    if new_name:
        existing = Course.query.filter_by(name=new_name).first()
        if existing and existing.id != id:
            flash('Já existe uma disciplina com esse nome.', 'error')
        else:
            course.name = new_name
            db.session.commit()
            flash('Disciplina atualizada!', 'success')
    return redirect(url_for('courses.list_courses'))

@bp.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete_course(id):
    course = Course.query.get_or_404(id)
    
    # Check if used in exams
    if Exam.query.filter_by(course_id=id).first():
        flash('Não é possível excluir esta disciplina pois existem provas vinculadas a ela.', 'error')
    else:
        db.session.delete(course)
        db.session.commit()
        flash('Disciplina removida!', 'success')
        
    return redirect(url_for('courses.list_courses'))
