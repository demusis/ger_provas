import random
from flask import url_for
import string
import uuid
import json
from models import db, Exam, ExamVersion, ExamQuestion, Question, Category
from services.qr_service import generate_qr_code

def select_safe(pool, n):
    if len(pool) >= n:
        return random.sample(pool, n), 0
    else:
        # Return all elements and the deficit
        return pool, n - len(pool)

def create_exam_logic(title, date, course_name, course_id, total_questions_ignored, distribution_config, num_versions, show_resolution=True, max_grade=10.0, difficulty_config=None):
    if difficulty_config is None:
        difficulty_config = {'easy': 33, 'medium': 33, 'hard': 34}
        
    # Normalize percentages to 1.0
    total_pct = sum(difficulty_config.values())
    if total_pct == 0: total_pct = 1
    pct_easy = difficulty_config['easy'] / total_pct
    pct_medium = difficulty_config['medium'] / total_pct
    pct_hard = difficulty_config['hard'] / total_pct

    # Create Exam record first
    exam = Exam(title=title, date=date, course=course_name, course_id=course_id, show_resolution=show_resolution, max_grade=max_grade)
    db.session.add(exam)
    db.session.commit()
    
    # Generate Versions
    for i in range(num_versions):
        # 1. Select questions for this specific version
        version_selected_questions = []
        
        # Iterate over configured categories
        for cat_id, config in distribution_config.items():
            # Determine count for this category in this version
            count = 0
            if isinstance(config, dict) and 'min' in config and 'max' in config:
                count = random.randint(config['min'], config['max'])
            elif isinstance(config, int):
                count = config
            
            if count <= 0:
                continue

            # Get all questions for this category
            # OPTIMIZATION: We could fetch these once outside the loop if memory allows, 
            # but for randomness and "replace=False" semantics across versions (if we wanted that) we might need care.
            # Here we want independent sampling per version, so fetching (or using cached list) is fine.
            # Because we re-sample from the FULL pool every time, we get independent versions.
            
            q_easy = Question.query.filter_by(category_id=cat_id, difficulty='Fácil').all()
            q_medium = Question.query.filter_by(category_id=cat_id, difficulty='Médio').all()
            q_hard = Question.query.filter_by(category_id=cat_id, difficulty='Difícil').all()
            
            target_easy = int(count * pct_easy)
            target_medium = int(count * pct_medium)
            target_hard = count - target_easy - target_medium 
            
            selected_cat = []
            
            # Try to fulfill targets
            picked_easy, deficit_easy = select_safe(q_easy, target_easy)
            selected_cat.extend(picked_easy)
            
            picked_medium, deficit_medium = select_safe(q_medium, target_medium + deficit_easy)
            selected_cat.extend(picked_medium)
            
            picked_hard, deficit_hard = select_safe(q_hard, target_hard + deficit_medium)
            selected_cat.extend(picked_hard)
            
            # Fallback: Fill deficit with ANY remaining questions from this category
            if deficit_hard > 0:
                remaining = []
                remaining.extend([q for q in q_easy if q not in selected_cat])
                remaining.extend([q for q in q_medium if q not in selected_cat])
                remaining.extend([q for q in q_hard if q not in selected_cat])
                
                if len(remaining) < deficit_hard:
                    raise ValueError(f"Não há questões suficientes na categoria ID {cat_id} para preencher a versão {i+1}. Necessário: {count}, Disponível: {len(selected_cat) + len(remaining)}.")
                    
                selected_cat.extend(random.sample(remaining, deficit_hard))
                
            version_selected_questions.extend(selected_cat)

        if not version_selected_questions:
             raise ValueError("Nenhuma questão foi selecionada. Verifique as configurações das categorias.")

        # Generate random 5-char label
        version_label = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
        unique_code = str(uuid.uuid4())
        
        exam_version = ExamVersion(
            exam_id=exam.id,
            label=version_label,
            unique_code=unique_code
        )
        db.session.add(exam_version)
        db.session.commit()
        
        qr_data = url_for('student.upload_answers', unique_code=unique_code, _external=True)
        generate_qr_code(qr_data, f"{unique_code}.png")
        
        # Shuffle questions for this version
        version_questions_final = version_selected_questions[:]
        random.shuffle(version_questions_final)
        
        for idx, q in enumerate(version_questions_final):
            # Shuffle alternatives
            original_alts = {
                'A': q.alt_a, 'B': q.alt_b, 'C': q.alt_c, 'D': q.alt_d,
                'E': q.alt_e if hasattr(q, 'alt_e') else ''
            }
            
            num_alts = 4
            if hasattr(q, 'num_alternatives'):
                num_alts = q.num_alternatives

            all_keys = ['A', 'B', 'C', 'D', 'E']
            keys = all_keys[:num_alts]
            random.shuffle(keys)
            
            new_correct_char = ''
            for new_pos_idx, original_key in enumerate(keys):
                if original_key == q.correct:
                    new_correct_char = chr(65 + new_pos_idx)
                    break
            
            if not new_correct_char:
                # Should not happen if data is consistent
                new_correct_char = 'X' 

            exam_question = ExamQuestion(
                version_id=exam_version.id,
                question_id=q.id,
                question_number=idx + 1,
                correct_option_char=new_correct_char,
                alternatives_order=json.dumps(keys)
            )
            db.session.add(exam_question)
            
        db.session.commit()
        
    return exam
