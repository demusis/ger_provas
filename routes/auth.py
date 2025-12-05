from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from functools import wraps
from models import User
from werkzeug.security import check_password_hash

bp = Blueprint('auth', __name__, url_prefix='/auth')

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect(url_for('auth.login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        password = request.form.get('password')
        # We assume single user 'admin' for now, or we could add username field to login form
        user = User.query.filter_by(username='admin').first()
        
        if user and check_password_hash(user.password_hash, password):
            session['logged_in'] = True
            flash('Login realizado com sucesso!', 'success')
            next_url = request.args.get('next')
            return redirect(next_url or url_for('questions.list_questions'))
        else:
            flash('Senha incorreta.', 'error')
    
    return render_template('auth/login.html')

@bp.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('Você saiu do sistema.', 'info')
    return redirect(url_for('auth.login'))
