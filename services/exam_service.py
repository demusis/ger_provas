import random
import string
import uuid
import json
from models import db, Exam, ExamVersion, ExamQuestion, Question, Category
from services.qr_service import generate_qr_code

def create_exam_logic(title, date, course_name, course_id, total_questions, distribution, num_versions, show_resolution=True):
    # distribution is a dict: {category_id: count}
    
    # 1. Select questions based on distribution
    selected_questions = []
    for cat_id, count in distribution.items():
        questions = Question.query.filter_by(category_id=cat_id).all()
        if len(questions) < count:
            raise ValueError(f"Not enough questions for category {cat_id}")
        selected_questions.extend(random.sample(questions, count))
    
    # Create Exam record
    exam = Exam(title=title, date=date, course=course_name, course_id=course_id, show_resolution=show_resolution)
    db.session.add(exam)
    db.session.commit()
    
    # 2. Generate Versions
    for i in range(num_versions):
        # Generate random 5-char label (e.g. X7B29)
        version_label = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
        unique_code = str(uuid.uuid4())
        
        exam_version = ExamVersion(
            exam_id=exam.id,
            label=version_label,
            unique_code=unique_code
        )
        db.session.add(exam_version)
        db.session.commit()
        
        # Generate QR Code
        # URL format: http://<host>/exam/<unique_code>/upload
        # For now we just encode the unique_code or a relative URL
        # In production, this should be a full URL
        qr_data = f"http://localhost:5000/student/{unique_code}"
        generate_qr_code(qr_data, f"{unique_code}.png")
        
        # Shuffle questions for this version
        version_questions = selected_questions[:]
        random.shuffle(version_questions)
        
        for idx, q in enumerate(version_questions):
            # Shuffle alternatives
            # Original map: 'A': q.alt_a, 'B': q.alt_b, ...
            # We want to shuffle the CONTENTS but keep track of where the CORRECT one went.
            
            original_alts = {
                'A': q.alt_a,
                'B': q.alt_b,
                'C': q.alt_c,
                'D': q.alt_d,
                'E': q.alt_e if hasattr(q, 'alt_e') else ''
            }
            
            # Keys to shuffle
            num_alts = q.num_alternatives if hasattr(q, 'num_alternatives') else 4
            all_keys = ['A', 'B', 'C', 'D', 'E']
            keys = all_keys[:num_alts]
            random.shuffle(keys) # e.g. ['C', 'A', 'B'] for 3 alts
            
            # This means:
            # Position A will hold content of original C
            # Position B will hold content of original A
            # ...
            
            # Find where the correct answer went
            # q.correct is e.g. 'A'
            # We need to find which NEW position holds 'A'
            # If keys[0] == 'A', then New Position A holds Original A.
            # If keys[1] == 'A', then New Position B holds Original A.
            
            new_correct_char = ''
            for new_pos_idx, original_key in enumerate(keys):
                if original_key == q.correct:
                    new_correct_char = chr(65 + new_pos_idx) # 0->A, 1->B...
                    break
            
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
