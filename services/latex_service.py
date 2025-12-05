import os
from flask import url_for
from jinja2 import Environment, FileSystemLoader
from models import Exam

def generate_exam_latex(exam_id):
    exam = Exam.query.get_or_404(exam_id)
    
    # Setup Jinja2 for LaTeX
    # We use different delimiters to avoid conflict with LaTeX syntax
    env = Environment(
        loader=FileSystemLoader(os.path.join(os.getcwd(), 'latex_templates')),
        block_start_string='\\BLOCK{',
        block_end_string='}',
        variable_start_string='\\VAR{',
        variable_end_string='}',
        comment_start_string='\\#{',
        comment_end_string='}',
        line_statement_prefix='%%',
        line_comment_prefix='%#',
        trim_blocks=True,
        autoescape=False,
    )
    
    template = env.get_template('exam_template.tex')
    
    # Prepare data structure for template
    # We need to resolve the shuffled alternatives for the template
    versions_data = []
    for version in exam.versions:
        questions_data = []
        for eq in version.questions:
            q = eq.question
            
            if not q:
                # Question was deleted
                questions_data.append({
                    'number': eq.question_number,
                    'statement': "QUESTÃO DELETADA",
                    'alts': ["", "", "", "", ""]
                })
                continue

            order = eq.get_alternatives_order() # e.g. ['C', 'A', 'D', 'B']
            
            # Map new positions to content
            # Position A (index 0) gets content of original key order[0]
            alts = []
            original_map = {
                'A': q.alt_a, 
                'B': q.alt_b, 
                'C': q.alt_c, 
                'D': q.alt_d,
                'E': q.alt_e if hasattr(q, 'alt_e') else ''
            }
            
            for key in order:
                alts.append(original_map.get(key, ''))
                
            questions_data.append({
                'number': eq.question_number,
                'statement': q.statement,
                'alts': alts # List of strings [content_of_pos_A, content_of_pos_B...]
            })
            
        versions_data.append({
            'label': version.label,
            'qr_code': f"{version.unique_code}.png",
            'qr_url': url_for('student.upload_answers', unique_code=version.unique_code, _external=True),
            'questions': questions_data
        })
        
    return template.render(
        exam=exam,
        versions=versions_data,
        cwd=os.getcwd().replace('\\', '/') # Fix paths for LaTeX
    )
