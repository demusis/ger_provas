from flask import Blueprint, render_template, request, redirect, url_for, flash
from models import db, Category, Question

bp = Blueprint('categories', __name__, url_prefix='/categories')

@bp.route('/')
def list_categories():
    categories = Category.query.order_by(Category.name).all()
    return render_template('categories/list.html', categories=categories)

@bp.route('/create', methods=['POST'])
def create_category():
    name = request.form.get('name')
    if name:
        category = Category(name=name)
        db.session.add(category)
        db.session.commit()
        flash('Categoria criada com sucesso!', 'success')
    else:
        flash('Nome da categoria é obrigatório.', 'error')
    return redirect(url_for('categories.list_categories'))

@bp.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_category(id):
    category = Category.query.get_or_404(id)
    
    if request.method == 'POST':
        name = request.form.get('name')
        if name:
            category.name = name
            db.session.commit()
            flash('Categoria atualizada!', 'success')
            return redirect(url_for('categories.list_categories'))
        else:
            flash('Nome da categoria é obrigatório.', 'error')
            
    return render_template('categories/edit.html', category=category)

@bp.route('/delete/<int:id>', methods=['POST'])
def delete_category(id):
    category = Category.query.get_or_404(id)
    
    # Check if category is empty
    if category.questions:
        flash(f'Não é possível excluir a categoria "{category.name}" pois ela contém questões.', 'error')
    else:
        db.session.delete(category)
        db.session.commit()
        flash('Categoria excluída com sucesso!', 'success')
        
    return redirect(url_for('categories.list_categories'))
