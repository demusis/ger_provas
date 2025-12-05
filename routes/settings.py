from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file, make_response
from models import db, Category, Question
from routes.auth import login_required
import json
import io
from datetime import datetime

bp = Blueprint('settings', __name__, url_prefix='/settings')

@bp.route('/')
@login_required
def index():
    return render_template('settings/index.html')

@bp.route('/download_db')
@login_required
def download_db():
    categories = Category.query.all()
    questions = Question.query.all()
    
    data = {
        'categories': [],
        'questions': []
    }
    
    for cat in categories:
        data['categories'].append({
            'id': cat.id,
            'name': cat.name,
            'description': cat.description
        })
        
    for q in questions:
        data['questions'].append({
            'id': q.id,
            'category_id': q.category_id,
            'statement': q.statement,
            'alt_a': q.alt_a,
            'alt_b': q.alt_b,
            'alt_c': q.alt_c,
            'alt_d': q.alt_d,
            'alt_e': q.alt_e,
            'num_alternatives': q.num_alternatives,
            'correct': q.correct,
            'resolution': q.resolution,
            'comment': q.comment
        })
        
    json_str = json.dumps(data, indent=4, ensure_ascii=False)
    
    mem = io.BytesIO()
    mem.write(json_str.encode('utf-8'))
    mem.seek(0)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"banco_questoes_{timestamp}.json"
    
    return send_file(
        mem,
        as_attachment=True,
        download_name=filename,
        mimetype='application/json'
    )

@bp.route('/upload_db', methods=['POST'])
@login_required
def upload_db():
    if 'db_file' not in request.files:
        flash('Nenhum arquivo selecionado.', 'error')
        return redirect(url_for('settings.index'))
        
    file = request.files['db_file']
    if file.filename == '':
        flash('Nenhum arquivo selecionado.', 'error')
        return redirect(url_for('settings.index'))
        
    if file:
        try:
            data = json.load(file)
            
            # Basic validation
            if 'categories' not in data or 'questions' not in data:
                flash('Formato de arquivo inválido.', 'error')
                return redirect(url_for('settings.index'))
            
            # Clear existing data
            # WARNING: This might fail if there are foreign key constraints from Exams
            # We will try to catch integrity errors
            # Check restore mode
            restore_mode = request.form.get('restore_mode', 'replace')
            
            try:
                if restore_mode == 'replace':
                    # We need to delete questions first, then categories
                    # But if exams exist, they reference questions.
                    # If we delete questions, exams might break or prevent deletion.
                    
                    # Let's try to delete all questions
                    num_deleted_q = Question.query.delete()
                    num_deleted_c = Category.query.delete()
                    
                    # Flush to check for errors
                    db.session.flush()
                    
                    # Insert Categories
                    for cat_data in data['categories']:
                        cat = Category(
                            id=cat_data['id'],
                            name=cat_data['name'],
                            description=cat_data.get('description')
                        )
                        db.session.add(cat)
                    
                    # Insert Questions
                    for q_data in data['questions']:
                        q = Question(
                            id=q_data['id'],
                            category_id=q_data['category_id'],
                            statement=q_data['statement'],
                            alt_a=q_data['alt_a'],
                            alt_b=q_data['alt_b'],
                            alt_c=q_data['alt_c'],
                            alt_d=q_data['alt_d'],
                            alt_e=q_data.get('alt_e'),
                            num_alternatives=q_data['num_alternatives'],
                            correct=q_data['correct'],
                            resolution=q_data.get('resolution'),
                            comment=q_data.get('comment')
                        )
                        db.session.add(q)
                        
                elif restore_mode == 'append':
                    # Map old category IDs (from JSON) to new category IDs (in DB)
                    category_map = {}
                    
                    # Process Categories
                    for cat_data in data['categories']:
                        # Check if category exists by name
                        existing_cat = Category.query.filter_by(name=cat_data['name']).first()
                        
                        if existing_cat:
                            category_map[cat_data['id']] = existing_cat.id
                        else:
                            # Create new category
                            new_cat = Category(
                                name=cat_data['name'],
                                description=cat_data.get('description')
                            )
                            db.session.add(new_cat)
                            db.session.flush() # Get ID
                            category_map[cat_data['id']] = new_cat.id
                            
                    # Process Questions
                    for q_data in data['questions']:
                        # Get new category ID
                        new_cat_id = category_map.get(q_data['category_id'])
                        
                        if new_cat_id:
                            q = Question(
                                category_id=new_cat_id, # Use mapped ID
                                statement=q_data['statement'],
                                alt_a=q_data['alt_a'],
                                alt_b=q_data['alt_b'],
                                alt_c=q_data['alt_c'],
                                alt_d=q_data['alt_d'],
                                alt_e=q_data.get('alt_e'),
                                num_alternatives=q_data['num_alternatives'],
                                correct=q_data['correct'],
                                resolution=q_data.get('resolution'),
                                comment=q_data.get('comment')
                                # Note: We do NOT set 'id', let DB auto-increment to avoid conflicts
                            )
                            db.session.add(q)
                
                db.session.commit()
                flash('Banco de dados atualizado com sucesso!', 'success')
                
            except Exception as e:
                db.session.rollback()
                flash(f'Erro ao atualizar banco de dados: {str(e)}. Verifique se existem provas criadas que impedem a exclusão das questões.', 'error')
                
        except json.JSONDecodeError:
            flash('Arquivo JSON inválido.', 'error')
        except Exception as e:
            flash(f'Erro inesperado: {str(e)}', 'error')
            
    return redirect(url_for('settings.index'))

@bp.route('/change_password', methods=['POST'])
@login_required
def change_password():
    current_password = request.form.get('current_password')
    new_password = request.form.get('new_password')
    confirm_password = request.form.get('confirm_password')
    
    if new_password != confirm_password:
        flash('As novas senhas não conferem.', 'error')
        return redirect(url_for('settings.index'))
        
    from models import User
    from werkzeug.security import check_password_hash, generate_password_hash
    
    # Assume single admin user
    user = User.query.filter_by(username='admin').first()
    
    if not user or not check_password_hash(user.password_hash, current_password):
        flash('Senha atual incorreta.', 'error')
        return redirect(url_for('settings.index'))
        
    user.password_hash = generate_password_hash(new_password)
    db.session.commit()
    
    flash('Senha alterada com sucesso!', 'success')
    return redirect(url_for('settings.index'))

@bp.route('/reset_db', methods=['POST'])
@login_required
def reset_db():
    password = request.form.get('password')
    
    from models import User, StudentSubmission, ExamQuestion, ExamVersion, Exam, Question, Category, Course
    from werkzeug.security import check_password_hash
    import os
    import shutil
    
    # Verify password
    user = User.query.filter_by(username='admin').first()
    if not user or not check_password_hash(user.password_hash, password):
        flash('Senha incorreta. Ação cancelada.', 'error')
        return redirect(url_for('settings.index'))
        
    try:
        # Delete data in correct order to respect Foreign Keys
        StudentSubmission.query.delete()
        ExamQuestion.query.delete()
        ExamVersion.query.delete()
        Exam.query.delete()
        Question.query.delete()
        Category.query.delete()
        Course.query.delete()
        
        # We do NOT delete the User table to allow login
        
        db.session.commit()
        
        # Delete uploaded files
        upload_folder = os.path.join('static', 'uploads')
        if os.path.exists(upload_folder):
            # Remove all files in the folder but keep the folder
            for filename in os.listdir(upload_folder):
                file_path = os.path.join(upload_folder, filename)
                try:
                    if os.path.isfile(file_path) or os.path.islink(file_path):
                        os.unlink(file_path)
                    elif os.path.isdir(file_path):
                        shutil.rmtree(file_path)
                except Exception as e:
                    print(f'Failed to delete {file_path}. Reason: {e}')
                    
        flash('Banco de dados e arquivos reiniciados com sucesso.', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao reiniciar banco de dados: {str(e)}', 'error')
        
    return redirect(url_for('settings.index'))
