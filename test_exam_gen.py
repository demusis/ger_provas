from app import create_app
from models import db, Category
from services.exam_service import create_exam_logic
from services.latex_service import generate_exam_latex
import os

app = create_app()

with app.app_context():
    # Ensure we have categories
    cat_calc = Category.query.filter_by(name="Cálculo I").first()
    cat_alg = Category.query.filter_by(name="Álgebra Linear").first()
    
    if not cat_calc or not cat_alg:
        print("Categories not found. Run seed_db.py first.")
        exit(1)
        
    print("Generating Exam...")
    # Generate an exam
    try:
        exam = create_exam_logic(
            title="Teste Automatizado",
            date="02/12/2025",
            course="Engenharia",
            total_questions=2,
            distribution={cat_calc.id: 1, cat_alg.id: 1},
            num_versions=2
        )
        print(f"Exam generated with ID: {exam.id}")
        
        # Generate LaTeX
        print("Generating LaTeX...")
        latex = generate_exam_latex(exam.id)
        
        # Save to file to check
        with open("test_exam.tex", "w", encoding="utf-8") as f:
            f.write(latex)
            
        print("LaTeX generated successfully at test_exam.tex")
        
        # Check if QR codes exist
        for v in exam.versions:
            qr_path = os.path.join(app.config['QR_FOLDER'], f"{v.unique_code}.png")
            if os.path.exists(qr_path):
                print(f"QR Code found: {qr_path}")
            else:
                print(f"ERROR: QR Code not found: {qr_path}")
                
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
