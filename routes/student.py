from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from models import db, ExamVersion, ExamQuestion, StudentSubmission
import os
import json
from werkzeug.utils import secure_filename

from services.omr_service import process_exam_image

bp = Blueprint('student', __name__, url_prefix='/student')

@bp.route('/<unique_code>', methods=['GET', 'POST'])
def upload_answers(unique_code):
    version = ExamVersion.query.filter_by(unique_code=unique_code).first_or_404()
    exam = version.exam
    
    detected_answers = {}
    
    # Check if submission already exists
    existing_submission = StudentSubmission.query.filter_by(exam_version_id=version.id).first()
    if existing_submission:
        # Reconstruct results for display
        answers_dict = json.loads(existing_submission.answers)
        results = []
        exam_questions = sorted(version.questions, key=lambda x: x.question_number)
        
        score = 0
        total = 0
        
        for eq in exam_questions:
            student_answer = answers_dict.get(str(eq.question_number))
            is_correct = False
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
                'resolution': question_resolution
            })
            total += 1
            
        return render_template('student/result.html', 
                               exam=exam, 
                               version=version, 
                               score=score, 
                               total=total, 
                               final_grade=existing_submission.score,
                               results=results,
                               submission=existing_submission)
    
    if request.method == 'POST':
        # Handle Image Upload
        if 'gabarito_img' in request.files:
            file = request.files['gabarito_img']
            if file.filename != '':
                filename = secure_filename(f"{unique_code}_{file.filename}")
                filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                
                # Process Image with OMR
                try:
                    # We need to know how many questions to look for
                    num_questions = len(version.questions)
                    detected_answers = process_exam_image(filepath, num_questions)
                    
                    if detected_answers:
                        flash('Respostas identificadas! Por favor, verifique e confirme abaixo.', 'success')
                    else:
                        flash('Não foi possível identificar as respostas na imagem. Por favor, preencha manualmente.', 'warning')
                        
                except Exception as e:
                    flash(f'Erro ao processar imagem: {str(e)}', 'error')
        
        # Handle Header Image Upload
        header_filename = None
        if 'header_image' in request.files:
            h_file = request.files['header_image']
            if h_file.filename != '':
                header_filename = secure_filename(f"header_{unique_code}_{h_file.filename}")
                h_filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], header_filename)
                h_file.save(h_filepath)
        
        # If we already have one from previous step (hidden field)
        if not header_filename and request.form.get('uploaded_header_filename'):
            header_filename = request.form.get('uploaded_header_filename')

        # If we just processed an image (detected or not), OR if the user submitted the form (confirmed answers)
        # We need to render the upload page again if it's just an image upload (no 'q_1' yet)
        
        if 'q_1' not in request.form:
             questions = sorted(version.questions, key=lambda x: x.question_number)
             return render_template('student/upload.html', 
                                    exam=exam, 
                                    version=version, 
                                    questions=questions, 
                                    detected_answers=detected_answers, 
                                    uploaded_filename=filename if 'filename' in locals() else None,
                                    uploaded_header_filename=header_filename)

        if 'q_1' in request.form:
            score = 0
            total = 0
            results = []
            answers_dict = {}
            
            # Get questions ordered by number
            exam_questions = sorted(version.questions, key=lambda x: x.question_number)
            
            for eq in exam_questions:
                student_answer = request.form.get(f'q_{eq.question_number}')
                answers_dict[eq.question_number] = student_answer
                is_correct = False
                if student_answer and student_answer == eq.correct_option_char:
                    score += 1
                    is_correct = True
                
                results.append({
                    'number': eq.question_number,
                    'statement': eq.question.statement,
                    'student_answer': student_answer,
                    'correct_answer': eq.correct_option_char,
                    'is_correct': is_correct,
                    'resolution': eq.question.resolution
                })
                total += 1
                
            final_grade = (score / total) * 10 if total > 0 else 0
            
            # Save Submission
            student_name = request.form.get('student_name')
            student_course = request.form.get('student_course')
            
            if student_name and student_course:
                # Check for duplicate (Strict: One per QR Code/Version)
                existing_submission = StudentSubmission.query.filter_by(
                    exam_version_id=version.id
                ).first()
                
                if existing_submission:
                    flash('Atenção: Este QR Code já foi utilizado para enviar um gabarito. Não é permitido enviar novamente.', 'error')
                    questions = sorted(version.questions, key=lambda x: x.question_number)
                    return render_template('student/upload.html', 
                                           exam=exam, 
                                           version=version, 
                                           questions=questions, 
                                           detected_answers=answers_dict, 
                                           uploaded_filename=request.form.get('uploaded_filename'),
                                           uploaded_header_filename=header_filename)

                submission = StudentSubmission(
                    exam_version_id=version.id,
                    student_name=student_name,
                    student_course=student_course,
                    image_path=request.form.get('uploaded_filename'),
                    header_image_path=header_filename,
                    answers=json.dumps(answers_dict),
                    score=final_grade,
                    total_questions=total
                )
                db.session.add(submission)
                db.session.commit()
            else:
                submission = None
            
            return render_template('student/result.html', 
                                   exam=exam, 
                                   version=version, 
                                   score=score, 
                                   total=total, 
                                   final_grade=final_grade,
                                   results=results,
                                   submission=submission)
        
        # If we are here, it means we uploaded an image but haven't confirmed answers yet.
        # We should render the upload page again but with detected_answers context
        questions = sorted(version.questions, key=lambda x: x.question_number)
        return render_template('student/upload.html', exam=exam, version=version, questions=questions, detected_answers=detected_answers, uploaded_filename=filename)

    questions = sorted(version.questions, key=lambda x: x.question_number)
    return render_template('student/upload.html', exam=exam, version=version, questions=questions)
