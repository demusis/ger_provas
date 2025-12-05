from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file, make_response
from models import db, Category, Exam, Course
from services.exam_service import create_exam_logic
from services.latex_service import generate_exam_latex
from routes.auth import login_required
import io

import random

bp = Blueprint('exams', __name__, url_prefix='/exams')

@bp.route('/')
@login_required
def list_exams():
    course_id = request.args.get('course_id', type=int)
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    courses = Course.query.order_by(Course.name).all()
    
    query = Exam.query
    
    if course_id:
        query = query.filter_by(course_id=course_id)
        
    if start_date:
        # Date in Exam is stored as string 'dd/mm/yyyy'.
        # Since it's a string, range filtering is tricky if we don't convert.
        # However, database is probably SQLite where dates are strings.
        # But Exam.date is stored as '09/12/2025' (DD/MM/YYYY) which doesn't sort well as string.
        # We need to fetch and filter in python OR rely on consistent format if stored as YYYY-MM-DD.
        # Looking at create_exam, it takes date from form (typically YYYY-MM-DD) but let's check.
        # `create_exam_logic` takes date. 
        # If stored as 'DD/MM/YYYY' (as seen in list.html: {{ exam.date }}), SQL string comparison fails.
        # We might need to filter manually in Python if the dataset is small, or fix data storage.
        # For now, let's filter in Python to be safe given the existing data format ambiguity.
        pass

    # Re-reading: The Exam model has `date = db.Column(db.String(20), nullable=False)`.
    # And create_exam uses `request.form.get('date')`. HTML date input sends 'YYYY-MM-DD'.
    # But list.html screenshot shows '09/12/2025'.
    # If the user input is YYYY-MM-DD, we should filter by that.
    # Let's assume standard YYYY-MM-DD for storage for robust filtering, 
    # BUT if specific format used is DD/MM/YYYY we have a problem.
    # Let's try to filter assuming YYYY-MM-DD first, or handle the filter in python.
    
    exams = query.order_by(Exam.id.desc()).all()
    
    if start_date or end_date:
        filtered_exams = []
        from datetime import datetime
        
        sd = datetime.strptime(start_date, '%Y-%m-%d') if start_date else None
        ed = datetime.strptime(end_date, '%Y-%m-%d') if end_date else None
        
        for exam in exams:
            try:
                # Try parsing exam date. It could be YYYY-MM-DD or DD/MM/YYYY
                if '-' in exam.date:
                    e_date = datetime.strptime(exam.date, '%Y-%m-%d')
                else:
                    e_date = datetime.strptime(exam.date, '%d/%m/%Y')
                
                if sd and e_date < sd: continue
                if ed and e_date > ed: continue
                
                filtered_exams.append(exam)
            except:
                # If date parsing fails, include it or exclude it? Let's include to be safe? Or exclude.
                pass
                
        exams = filtered_exams

    return render_template('exams/list.html', exams=exams, courses=courses, selected_course_id=course_id, selected_start_date=start_date, selected_end_date=end_date)

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
        # Parse distribution
        distribution = {}
        total_questions = 0
        for cat in categories:
            # We now support Min/Max
            # If explicit 'cat_{id}' exists (legacy/shim), use it.
            # Otherwise look for min/max.
            
            # The UI now sends cat_{id}_min and cat_{id}_max
            min_q = request.form.get(f'cat_{cat.id}_min')
            max_q = request.form.get(f'cat_{cat.id}_max')
            
            if min_q and max_q:
                try:
                    mn = int(min_q)
                    mx = int(max_q)
                    if mx >= mn and mx > 0:
                        distribution[cat.id] = {'min': mn, 'max': mx}
                        # We don't know the exact count here anymore, but create_exam_logic handles it.
                        # total_questions is technically variable, but we pass 0 or an estimate.
                        total_questions += mn 
                except ValueError:
                    pass
            
            # Check for legacy single input just in case
            legacy_count = request.form.get(f'cat_{cat.id}')
            if legacy_count:
                try:
                    lc = int(legacy_count)
                    if lc > 0:
                        distribution[cat.id] = lc # Backward compatibility (fixed count)
                        total_questions += lc
                except:
                    pass
        
        # Parse difficulty distribution
        difficulty_config = {
            'easy': int(request.form.get('pct_easy', 30)),
            'medium': int(request.form.get('pct_medium', 50)),
            'hard': int(request.form.get('pct_hard', 20))
        }
        
        try:
            show_resolution = 'show_resolution' in request.form
            max_grade = float(request.form.get('max_grade', 10.0))
            create_exam_logic(title, date, course.name, course.id, total_questions, distribution, num_versions, show_resolution, max_grade, difficulty_config)
            flash('Prova gerada com sucesso!')
            return redirect(url_for('exams.list_exams'))
        except Exception as e:
            # Log the full error for debugging (print to console which appears in server logs)
            import traceback
            traceback.print_exc()
            flash(f"Erro ao gerar prova: {str(e)}", 'error')
            
    return render_template('exams/create.html', categories=categories, courses=courses)

@bp.route('/download/<int:exam_id>')
@login_required
def download_latex(exam_id):
    latex_content = generate_exam_latex(exam_id)
    
    response = make_response(latex_content)
    response.headers['Content-Type'] = 'application/x-latex'
    response.headers['Content-Disposition'] = f'attachment; filename=prova_{exam_id}.tex'
    return response

@bp.route('/download_pdf/<int:exam_id>')
@login_required
def download_pdf(exam_id):
    import subprocess
    import tempfile
    import os
    
    latex_content = generate_exam_latex(exam_id)
    
    with tempfile.TemporaryDirectory() as temp_dir:
        tex_file_path = os.path.join(temp_dir, 'exam.tex')
        with open(tex_file_path, 'w', encoding='utf-8') as f:
            f.write(latex_content)
            
        # Run pdflatex twice to resolve references
        try:
            for _ in range(2):
                result = subprocess.run(
                    ['pdflatex', '-interaction=nonstopmode', 'exam.tex'],
                    cwd=temp_dir,
                    capture_output=True,
                    text=True
                )
                if result.returncode != 0:
                    raise Exception(f"PDFLaTeX failed: {result.stderr}")
            
            pdf_file_path = os.path.join(temp_dir, 'exam.pdf')
            
            if os.path.exists(pdf_file_path):
                with open(pdf_file_path, 'rb') as f:
                    pdf_content = f.read()
                    
                response = make_response(pdf_content)
                response.headers['Content-Type'] = 'application/pdf'
                response.headers['Content-Disposition'] = f'attachment; filename=prova_{exam_id}.pdf'
                return response
            else:
                flash('Erro: O arquivo PDF não foi gerado.', 'error')
                return redirect(url_for('exams.list_exams'))
                
        except Exception as e:
            flash(f'Erro ao gerar PDF: {str(e)}', 'error')
            return redirect(url_for('exams.list_exams'))

@bp.route('/toggle_resolution/<int:exam_id>')
@login_required
def toggle_resolution(exam_id):
    exam = Exam.query.get_or_404(exam_id)
    exam.show_resolution = not exam.show_resolution
    db.session.commit()
    flash(f'Visibilidade do gabarito da prova "{exam.title}" alterada para {"Visível" if exam.show_resolution else "Oculto"}.')
    return redirect(url_for('exams.list_exams'))

@bp.route('/delete/<int:exam_id>', methods=['POST'])
@login_required
def delete_exam(exam_id):
    exam = Exam.query.get_or_404(exam_id)
    
    # Check for submissions
    from models import StudentSubmission, ExamVersion, ExamQuestion
    
    has_submissions = StudentSubmission.query.join(ExamVersion).filter(ExamVersion.exam_id == exam.id).first()
    
    if has_submissions:
        flash(f'Não é possível excluir a prova "{exam.title}" pois já existem notas associadas.', 'error')
        return redirect(url_for('exams.list_exams'))
        
    try:
        # Delete related records (if cascade not set up in DB)
        # Delete ExamQuestions
        for version in exam.versions:
            ExamQuestion.query.filter_by(version_id=version.id).delete()
            
        # Delete ExamVersions
        ExamVersion.query.filter_by(exam_id=exam.id).delete()
        
        # Delete Exam
        db.session.delete(exam)
        db.session.commit()
        flash(f'Prova "{exam.title}" excluída com sucesso.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao excluir prova: {str(e)}', 'error')
        
    return redirect(url_for('exams.list_exams'))
