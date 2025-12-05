from app import create_app, db
from models import Question, Category, Exam
from services.exam_service import create_exam_logic
import random

app = create_app()

def test_difficulty_logic():
    with app.app_context():
        # Setup: Create a category and questions with different difficulties
        cat_name = "Test Difficulty"
        cat = Category.query.filter_by(name=cat_name).first()
        if not cat:
            cat = Category(name=cat_name)
            db.session.add(cat)
            db.session.commit()
            
        # Clear existing questions for this category to ensure clean test
        Question.query.filter_by(category_id=cat.id).delete()
        db.session.commit()
        
        # Create 10 Easy, 10 Medium, 10 Hard
        for i in range(10):
            db.session.add(Question(category_id=cat.id, statement=f"Easy {i}", alt_a="A", alt_b="B", correct="A", difficulty="Fácil"))
            db.session.add(Question(category_id=cat.id, statement=f"Medium {i}", alt_a="A", alt_b="B", correct="A", difficulty="Médio"))
            db.session.add(Question(category_id=cat.id, statement=f"Hard {i}", alt_a="A", alt_b="B", correct="A", difficulty="Difícil"))
        db.session.commit()
        
        print(f"Created 30 questions for category '{cat_name}'.")
        
        # Test Case 1: 50% Easy, 50% Hard (Total 10 questions)
        # Expected: 5 Easy, 0 Medium, 5 Hard
        print("\nTest Case 1: 50% Easy, 50% Hard (10 questions)")
        distribution = {cat.id: 10}
        difficulty_config = {'easy': 50, 'medium': 0, 'hard': 50}
        
        exam = create_exam_logic("Test Exam 1", "01/01/2025", "Test Course", None, 10, distribution, 1, difficulty_config=difficulty_config)
        
        # Verify selected questions
        version = exam.versions[0]
        questions = [eq.question for eq in version.questions]
        
        easy_count = sum(1 for q in questions if q.difficulty == 'Fácil')
        medium_count = sum(1 for q in questions if q.difficulty == 'Médio')
        hard_count = sum(1 for q in questions if q.difficulty == 'Difícil')
        
        print(f"Result: Easy={easy_count}, Medium={medium_count}, Hard={hard_count}")
        
        if easy_count == 5 and hard_count == 5:
            print("PASS")
        else:
            print("FAIL")
            
        # Test Case 2: Deficit handling
        # Request 100% Easy (10 questions), but only have 10. (Should use all 10)
        # Actually let's request 15 questions, 100% Easy. We only have 10 Easy.
        # Should fill remaining 5 with others.
        print("\nTest Case 2: Deficit Handling (15 questions, 100% Easy requested, only 10 available)")
        distribution = {cat.id: 15}
        difficulty_config = {'easy': 100, 'medium': 0, 'hard': 0}
        
        exam2 = create_exam_logic("Test Exam 2", "01/01/2025", "Test Course", None, 15, distribution, 1, difficulty_config=difficulty_config)
        
        version2 = exam2.versions[0]
        questions2 = [eq.question for eq in version2.questions]
        
        easy_count2 = sum(1 for q in questions2 if q.difficulty == 'Fácil')
        other_count2 = sum(1 for q in questions2 if q.difficulty != 'Fácil')
        
        print(f"Result: Easy={easy_count2}, Other={other_count2}")
        
        if easy_count2 == 10 and other_count2 == 5:
            print("PASS")
        else:
            print("FAIL")

        # Cleanup
        db.session.delete(exam)
        db.session.delete(exam2)
        # Note: Questions are left for manual inspection if needed, or could be deleted.

if __name__ == '__main__':
    test_difficulty_logic()
