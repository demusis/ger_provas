from flask import Blueprint, render_template, request, redirect, url_for, flash
from models import db, Question, Category, ExamQuestion
from routes.auth import login_required

bp = Blueprint('questions', __name__, url_prefix='/questions')

@bp.route('/')
@login_required
def list_questions():
    category_id = request.args.get('category_id', type=int)
    categories = Category.query.all()
    
    difficulty = request.args.get('difficulty')
    tag = request.args.get('tag')
    
    query = Question.query
    
    if category_id:
        query = query.filter_by(category_id=category_id)
        
    if difficulty:
        query = query.filter_by(difficulty=difficulty)
        
    if tag:
        # Simple LIKE search for tags
        query = query.filter(Question.tags.like(f'%{tag}%'))
        
    page = request.args.get('page', 1, type=int)
    per_page = 10
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    questions = pagination.items
        
    return render_template('questions/list.html', questions=questions, pagination=pagination, categories=categories, selected_category_id=category_id, selected_difficulty=difficulty, selected_tag=tag)

@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_question():
    categories = Category.query.all()
    if request.method == 'POST':
        category_id = request.form.get('category_id')
        new_category_name = request.form.get('new_category_name')
        
        if new_category_name:
            category = Category(name=new_category_name)
            db.session.add(category)
            db.session.commit()
            category_id = category.id
            
        num_alternatives = int(request.form.get('num_alternatives', 4))
        weight = float(request.form.get('weight', 1.0))
        
        question = Question(
            category_id=category_id,
            statement=request.form.get('statement'),
            alt_a=request.form.get('alt_a'),
            alt_b=request.form.get('alt_b'),
            alt_c=request.form.get('alt_c') if num_alternatives >= 3 else '',
            alt_d=request.form.get('alt_d') if num_alternatives >= 4 else '',
            alt_e=request.form.get('alt_e') if num_alternatives >= 5 else '',
            num_alternatives=num_alternatives,
            correct=request.form.get('correct'),
            resolution=request.form.get('resolution'),
            comment=request.form.get('comment'),
            weight=weight,
            difficulty=request.form.get('difficulty', 'Médio'),
            tags=request.form.get('tags', '')
        )
        db.session.add(question)
        db.session.commit()
        flash('Questão criada com sucesso!')
        return redirect(url_for('questions.list_questions'))
        
    return render_template('questions/create.html', categories=categories)

@bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_question(id):
    question = Question.query.get_or_404(id)
    categories = Category.query.all()
    
    if request.method == 'POST':
        question.category_id = request.form.get('category_id')
        question.statement = request.form.get('statement')
        question.num_alternatives = int(request.form.get('num_alternatives', 4))
        question.alt_a = request.form.get('alt_a')
        question.alt_b = request.form.get('alt_b')
        question.alt_c = request.form.get('alt_c') if question.num_alternatives >= 3 else ''
        question.alt_d = request.form.get('alt_d') if question.num_alternatives >= 4 else ''
        question.alt_e = request.form.get('alt_e') if question.num_alternatives >= 5 else ''
        question.correct = request.form.get('correct')
        question.resolution = request.form.get('resolution')
        question.comment = request.form.get('comment')
        question.weight = float(request.form.get('weight', 1.0))
        question.difficulty = request.form.get('difficulty', 'Médio')
        question.tags = request.form.get('tags', '')
        
        db.session.commit()
        flash('Questão atualizada!')
        return redirect(url_for('questions.list_questions'))
        
    return render_template('questions/edit.html', question=question, categories=categories)

@bp.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete_question(id):
    question = Question.query.get_or_404(id)
    
    # Check if question is used in any exam
    usage_count = ExamQuestion.query.filter_by(question_id=id).count()
    if usage_count > 0:
        flash('Não é possível excluir esta questão pois ela está sendo utilizada em uma ou mais provas.', 'error')
        return redirect(url_for('questions.list_questions'))
        
    db.session.delete(question)
    db.session.commit()
    flash('Questão removida!')
    return redirect(url_for('questions.list_questions'))

@bp.route('/get/<int:id>')
@login_required
def get_question(id):
    question = Question.query.get_or_404(id)
    return {
        'id': question.id,
        'category': question.category.name,
        'statement': question.statement,
        'alt_a': question.alt_a,
        'alt_b': question.alt_b,
        'alt_c': question.alt_c,
        'alt_d': question.alt_d,
        'alt_e': question.alt_e,
        'correct': question.correct,
        'resolution': question.resolution,
        'comment': question.comment,
        'difficulty': question.difficulty,
        'tags': question.tags
    }

@bp.route('/import', methods=['POST'])
@login_required
def import_questions():
    if 'file' not in request.files:
        flash('Nenhum arquivo enviado.', 'error')
        return redirect(url_for('questions.list_questions'))
        
    file = request.files['file']
    if file.filename == '':
        flash('Nenhum arquivo selecionado.', 'error')
        return redirect(url_for('questions.list_questions'))
        
    if not file.filename.endswith('.csv'):
        flash('Formato inválido. Por favor envie um arquivo CSV.', 'error')
        return redirect(url_for('questions.list_questions'))
        
    import csv
    import io
    
    try:
        # Use utf-8-sig to handle optional BOM automatically
        stream = io.StringIO(file.stream.read().decode("utf-8-sig"), newline=None)
        
        # Try to sniff delimiter, default to comma if fails, but fallback to semicolon check
        try:
            sample = stream.read(1024)
            stream.seek(0)
            dialect = csv.Sniffer().sniff(sample)
        except csv.Error:
            dialect = 'excel' # Default
            
        csv_input = csv.DictReader(stream, dialect=dialect)
        
        # Normalize fieldnames (strip whitespace)
        if csv_input.fieldnames:
             csv_input.fieldnames = [name.strip() for name in csv_input.fieldnames]

        # If headers are not found (e.g. wrong delimiter assumed), try forcing comma
        if csv_input.fieldnames and 'Enunciado' not in csv_input.fieldnames and 'statement' not in csv_input.fieldnames and 'Categoria' not in csv_input.fieldnames:
             stream.seek(0)
             csv_input = csv.DictReader(stream, delimiter=',')
             if csv_input.fieldnames:
                csv_input.fieldnames = [name.strip() for name in csv_input.fieldnames]
        
        count = 0
        ignored_count = 0
        for row in csv_input:
            # Map Portuguese headers to internal names
            # 'Categoria', 'Enunciado', 'Alternativa A', ...
            
            # Helper to get value safely from potential Portuguese keys
            def get_val(keys):
                for k in keys:
                    if k in row and row[k]:
                        return row[k]
                return None
            
            statement = get_val(['Enunciado', 'enunciado', 'statement'])
            correct = get_val(['Correta', 'correta', 'correct'])
            alt_a = get_val(['Alternativa A', 'alternativa a', 'alt_a'])
            alt_b = get_val(['Alternativa B', 'alternativa b', 'alt_b'])
            weight_val = get_val(['Peso', 'peso', 'weight'])
            difficulty = get_val(['Dificuldade', 'dificuldade', 'difficulty']) or 'Médio'
            tags = get_val(['Tags', 'tags']) or ''
            
            # Basic validation
            if not statement or not correct or not alt_a or not alt_b or not weight_val:
                ignored_count += 1
                continue
                
            # Get or Create Category
            category_name = get_val(['Categoria', 'categoria', 'category']) or 'Geral'
            category_name = category_name.strip()
            
            category = Category.query.filter_by(name=category_name).first()
            if not category:
                category = Category(name=category_name)
                db.session.add(category)
                db.session.commit()
                
            alt_c = get_val(['Alternativa C', 'alternativa c', 'alt_c']) or ''
            alt_d = get_val(['Alternativa D', 'alternativa d', 'alt_d']) or ''
            alt_e = get_val(['Alternativa E', 'alternativa e', 'alt_e']) or ''
            
            # Determine num_alternatives
            num_alt = 2
            if alt_c: num_alt = 3
            if alt_d: num_alt = 4
            if alt_e: num_alt = 5
            
            try:
                weight = float(weight_val.replace(',', '.'))
            except ValueError:
                # If weight is invalid number, we count as ignored row now? 
                # Or default to 1.0? User said "mandatory", usually implies valid presence.
                # Let's count as ignored if invalid to be strict as requested.
                ignored_count += 1
                continue
                
            resolution = get_val(['Resolução', 'Resolucao', 'resolução', 'resolucao', 'resolution']) or ''
            
            question = Question(
                category_id=category.id,
                statement=statement,
                alt_a=alt_a,
                alt_b=alt_b,
                alt_c=alt_c,
                alt_d=alt_d,
                alt_e=alt_e,
                num_alternatives=num_alt,
                correct=correct.upper(),
                resolution=resolution,
                weight=weight,
                difficulty=difficulty,
                tags=tags
            )
            db.session.add(question)
            count += 1
            
        db.session.commit()
        
        msg = f'{count} questões importadas com sucesso. {ignored_count} linhas ignoradas.'
        if ignored_count > 0:
            flash(msg, 'warning')
        else:
            flash(msg, 'success')
        
    except Exception as e:
        flash(f'Erro ao processar arquivo: {str(e)}', 'error')
        
    return redirect(url_for('questions.list_questions'))

@bp.route('/template')
@login_required
def download_template():
    import csv
    import io
    from flask import Response
    
    output = io.StringIO()
    output.write(u'\ufeff') # Add BOM for Excel
    # Force quotes for all fields to prevent delimiter issues
    writer = csv.writer(output, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
    
    # Header in Portuguese
    writer.writerow(['Categoria', 'Enunciado', 'Alternativa A', 'Alternativa B', 'Alternativa C', 'Alternativa D', 'Alternativa E', 'Correta', 'Peso', 'Dificuldade', 'Tags', 'Resolução'])
    
    # Example Rows
    writer.writerow([
        'Cálculo', 
        'Qual é a derivada de $f(x) = x^2$?', 
        '$x$', 
        '$2x$', 
        '$2$', 
        '$x^2$', 
        '$0$', 
        'B', 
        '1,0', 
        'Fácil',
        'Cálculo I, Derivadas',
        'A regra do tombo diz que a derivada de $x^n$ é $nx^{n-1}$.'
    ])
    
    writer.writerow([
        'Banco de Dados', 
        'Em um Modelo Entidade-Relacionamento (MER), o que um losango representa?', 
        'Entidade', 
        'Atributo', 
        'Relacionamento', 
        'Cardinalidade', 
        'Chave Primária', 
        'C', 
        '1,5', 
        'Médio',
        'Modelagem, MER',
        'Retângulos representam entidades, elipses representam atributos e losangos representam relacionamentos.'
    ])
    
    writer.writerow([
        'Metodologia Científica', 
        'Qual é tipicamente o primeiro passo do método científico?', 
        'Formulação de Hipóteses', 
        'Experimentação', 
        'Observação', 
        'Conclusão', 
        'Análise de Dados', 
        'C', 
        '1,0', 
        'Fácil',
        'Metodologia',
        'O processo geralmente se inicia com a observação de um fenômeno ou problema.'
    ])
    
    output.seek(0)
    
    return Response(
        output,
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment;filename=modelo_importacao.csv"}
    )
