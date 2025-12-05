from flask import Blueprint, render_template, request, redirect, url_for, flash
from models import db, Question, Category, ExamQuestion
from routes.auth import login_required

bp = Blueprint('questions', __name__, url_prefix='/questions')

@bp.route('/')
@login_required
def list_questions():
    category_id = request.args.get('category_id', type=int)
    categories = Category.query.all()
    
    if category_id:
        questions = Question.query.filter_by(category_id=category_id).all()
    else:
        questions = Question.query.all()
        
    return render_template('questions/list.html', questions=questions, categories=categories, selected_category_id=category_id)

@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_question():
    categories = Category.query.all()
    if request.method == 'POST':
        category_id = request.form.get('category_id')
        new_category_name = request.form.get('new_category_name')
        
        if new_category_name:
            category = Category(name=new_category_name)
            db.session.add(category)
            db.session.commit()
            category_id = category.id
            
        num_alternatives = int(request.form.get('num_alternatives', 4))
        
        question = Question(
            category_id=category_id,
            statement=request.form.get('statement'),
            alt_a=request.form.get('alt_a'),
            alt_b=request.form.get('alt_b'),
            alt_c=request.form.get('alt_c') if num_alternatives >= 3 else '',
            alt_d=request.form.get('alt_d') if num_alternatives >= 4 else '',
            alt_e=request.form.get('alt_e') if num_alternatives >= 5 else '',
            num_alternatives=num_alternatives,
            correct=request.form.get('correct'),
            resolution=request.form.get('resolution'),
            comment=request.form.get('comment')
        )
        db.session.add(question)
        db.session.commit()
        flash('Questão criada com sucesso!')
        return redirect(url_for('questions.list_questions'))
        
    return render_template('questions/create.html', categories=categories)

@bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_question(id):
    question = Question.query.get_or_404(id)
    categories = Category.query.all()
    
    if request.method == 'POST':
        question.category_id = request.form.get('category_id')
        question.statement = request.form.get('statement')
        question.num_alternatives = int(request.form.get('num_alternatives', 4))
        question.alt_a = request.form.get('alt_a')
        question.alt_b = request.form.get('alt_b')
        question.alt_c = request.form.get('alt_c') if question.num_alternatives >= 3 else ''
        question.alt_d = request.form.get('alt_d') if question.num_alternatives >= 4 else ''
        question.alt_e = request.form.get('alt_e') if question.num_alternatives >= 5 else ''
        question.correct = request.form.get('correct')
        question.resolution = request.form.get('resolution')
        question.comment = request.form.get('comment')
        
        db.session.commit()
        flash('Questão atualizada!')
        return redirect(url_for('questions.list_questions'))
        
    return render_template('questions/edit.html', question=question, categories=categories)

@bp.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete_question(id):
    question = Question.query.get_or_404(id)
    
    # Check if question is used in any exam
    usage_count = ExamQuestion.query.filter_by(question_id=id).count()
    if usage_count > 0:
        flash('Não é possível excluir esta questão pois ela está sendo utilizada em uma ou mais provas.', 'error')
        return redirect(url_for('questions.list_questions'))
        
    db.session.delete(question)
    db.session.commit()
    flash('Questão removida!')
    return redirect(url_for('questions.list_questions'))

@bp.route('/get/<int:id>')
@login_required
def get_question(id):
    question = Question.query.get_or_404(id)
    return {
        'id': question.id,
        'category': question.category.name,
        'statement': question.statement,
        'alt_a': question.alt_a,
        'alt_b': question.alt_b,
        'alt_c': question.alt_c,
        'alt_d': question.alt_d,
        'alt_e': question.alt_e,
        'correct': question.correct,
        'resolution': question.resolution,
        'comment': question.comment
    }
