from flask import Flask, render_template
from config import Config
from models import db
import os

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)

    # Ensure upload and qr folders exist
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['QR_FOLDER'], exist_ok=True)

    with app.app_context():
        db.create_all()
        
        # Create default admin user if not exists
        from models import User
        from werkzeug.security import generate_password_hash
        
        if not User.query.filter_by(username='admin').first():
            hashed_password = generate_password_hash('admin')
            admin = User(username='admin', password_hash=hashed_password)
            db.session.add(admin)
            db.session.commit()
            print("Admin user created.")
            
        # Migrate Courses
        from models import Exam, Course
        exams = Exam.query.all()
        for exam in exams:
            if exam.course and not exam.course_id:
                # Check if course exists
                course = Course.query.filter_by(name=exam.course).first()
                if not course:
                    course = Course(name=exam.course)
                    db.session.add(course)
                    db.session.commit()
                
                exam.course_id = course.id
                db.session.commit()
                print(f"Migrated exam {exam.id} to course {course.name}")

    # Register Blueprints
    from routes.questions import bp as questions_bp
    app.register_blueprint(questions_bp)

    from routes.exams import bp as exams_bp
    app.register_blueprint(exams_bp)

    from routes.student import bp as student_bp
    app.register_blueprint(student_bp)

    from routes.grades import bp as grades_bp
    app.register_blueprint(grades_bp)

    from routes.categories import bp as categories_bp
    app.register_blueprint(categories_bp)

    from routes.settings import bp as settings_bp
    app.register_blueprint(settings_bp)

    from routes.auth import bp as auth_bp
    app.register_blueprint(auth_bp)

    from routes.courses import bp as courses_bp
    app.register_blueprint(courses_bp)

    @app.route('/')
    def index():
        return render_template('index.html')

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
