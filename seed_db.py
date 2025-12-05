from app import create_app
from models import db, Category, Question

app = create_app()

with app.app_context():
    # Create Categories
    cat_calc = Category(name="Cálculo I", description="Limites, Derivadas e Integrais")
    cat_alg = Category(name="Álgebra Linear", description="Matrizes e Vetores")
    
    db.session.add(cat_calc)
    db.session.add(cat_alg)
    db.session.commit()
    
    # Create Questions
    q1 = Question(
        category_id=cat_calc.id,
        statement=r"\frac{d}{dx}(x^2)",
        alt_a=r"2x",
        alt_b=r"x",
        alt_c=r"x^2",
        alt_d=r"2",
        correct="A",
        resolution=r"\text{A derivada de } x^n \text{ é } nx^{n-1}. \text{ Logo, } 2x^{2-1} = 2x."
    )
    
    q2 = Question(
        category_id=cat_calc.id,
        statement=r"\int_0^1 x dx",
        alt_a=r"1",
        alt_b=r"0.5",
        alt_c=r"0",
        alt_d=r"2",
        correct="B",
        resolution=r"\left[\frac{x^2}{2}\right]_0^1 = \frac{1}{2} - 0 = 0.5"
    )
    
    q3 = Question(
        category_id=cat_alg.id,
        statement=r"\text{O determinante de } \begin{pmatrix} 1 & 0 \\ 0 & 1 \end{pmatrix}",
        alt_a=r"0",
        alt_b=r"1",
        alt_c=r"2",
        alt_d=r"-1",
        correct="B",
        resolution=r"1 \times 1 - 0 \times 0 = 1"
    )

    q4 = Question(
        category_id=cat_alg.id,
        statement=r"\text{Se } A = \begin{pmatrix} 1 & 2 \\ 3 & 4 \end{pmatrix}, \text{ então } A^T \text{ é:}",
        alt_a=r"\begin{pmatrix} 1 & 3 \\ 2 & 4 \end{pmatrix}",
        alt_b=r"\begin{pmatrix} 4 & 3 \\ 2 & 1 \end{pmatrix}",
        alt_c=r"\begin{pmatrix} 1 & 2 \\ 3 & 4 \end{pmatrix}",
        alt_d=r"\begin{pmatrix} 1 & 0 \\ 0 & 1 \end{pmatrix}",
        correct="A",
        resolution=r"\text{A transposta troca linhas por colunas.}"
    )

    db.session.add_all([q1, q2, q3, q4])
    db.session.commit()
    
    print("Database seeded successfully!")
