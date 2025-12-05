from flask_sqlalchemy import SQLAlchemy
import json
from datetime import datetime

db = SQLAlchemy()

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200))

    def __repr__(self):
        return f'<Category {self.name}>'

class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    statement = db.Column(db.Text, nullable=False)  # LaTeX
    alt_a = db.Column(db.Text, nullable=False)
    alt_b = db.Column(db.Text, nullable=False)
    alt_c = db.Column(db.Text, nullable=False)
    alt_d = db.Column(db.Text, nullable=False)
    alt_e = db.Column(db.Text) # Nullable, as it depends on num_alternatives
    num_alternatives = db.Column(db.Integer, default=4, nullable=False)
    correct = db.Column(db.String(1), nullable=False) # 'A', 'B', 'C', 'D', 'E'
    resolution = db.Column(db.Text) # LaTeX
    comment = db.Column(db.Text) # Internal comment/notes

    category = db.relationship('Category', backref=db.backref('questions', lazy=True))

class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)

    def __repr__(self):
        return f'<Course {self.name}>'

class Exam(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    date = db.Column(db.String(20), nullable=False)
    course = db.Column(db.String(100), nullable=True) # Deprecated, keeping for migration
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=True) # Nullable for now until migration
    show_resolution = db.Column(db.Boolean, default=True, nullable=False)
    
    course_rel = db.relationship('Course', backref='exams')
    versions = db.relationship('ExamVersion', backref='exam', lazy=True)

class ExamVersion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    exam_id = db.Column(db.Integer, db.ForeignKey('exam.id'), nullable=False)
    label = db.Column(db.String(10), nullable=False) # e.g., "A", "B", "1", "2"
    unique_code = db.Column(db.String(36), unique=True, nullable=False) # UUID for QR
    
    questions = db.relationship('ExamQuestion', backref='version', lazy=True, order_by='ExamQuestion.question_number')

class ExamQuestion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    version_id = db.Column(db.Integer, db.ForeignKey('exam_version.id'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'), nullable=False)
    question_number = db.Column(db.Integer, nullable=False)
    
    # The correct option char for THIS version (e.g., if original correct was A, but A moved to C position, this is 'C')
    correct_option_char = db.Column(db.String(1), nullable=False) 
    
    # Store how alternatives were shuffled: e.g., {"A": "alt_c_content", "B": "alt_a_content", ...} 
    # OR simpler: just store the mapping of original letters to new positions?
    # Let's store the order of original keys: e.g. ["C", "A", "D", "B"] means:
    # Position A has content of original C
    # Position B has content of original A
    # ...
    alternatives_order = db.Column(db.String(200), nullable=False) # JSON string

    question = db.relationship('Question')

    def get_alternatives_order(self):
        return json.loads(self.alternatives_order)

class StudentSubmission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    exam_version_id = db.Column(db.Integer, db.ForeignKey('exam_version.id'), nullable=False)
    student_name = db.Column(db.String(100), nullable=False)
    student_course = db.Column(db.String(100), nullable=False)
    submission_date = db.Column(db.DateTime, default=datetime.utcnow)
    image_path = db.Column(db.String(200))
    header_image_path = db.Column(db.String(200)) # Path to header image
    answers = db.Column(db.Text) # JSON string of answers
    score = db.Column(db.Float)
    total_questions = db.Column(db.Integer)
    
    version = db.relationship('ExamVersion', backref='submissions')

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)

    def __repr__(self):
        return f'<User {self.username}>'
