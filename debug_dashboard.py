from app import create_app
from models import Exam

app = create_app()

with app.app_context():
    try:
        print("Testing Dashboard Route Logic...")
        exams = Exam.query.order_by(Exam.id.desc()).all()
        print(f"Found {len(exams)} exams.")
        for exam in exams:
            print(f"Exam: {exam.title}, Course: {exam.course}, Date: {exam.date}")
            
        print("Rendering template...")
        from flask import render_template
        with app.test_request_context():
            # Mock session if needed, but dashboard index doesn't use session except for base.html
            # base.html uses session.get('logged_in')
            from flask import session
            session['logged_in'] = True
            rendered = render_template('dashboard/index.html', exams=exams)
            print("Template rendered successfully.")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
