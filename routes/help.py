from flask import Blueprint, render_template, current_app
import os

bp = Blueprint('help', __name__, url_prefix='/help')

@bp.route('/')
def index():
    # Read the HELP.md file
    help_file_path = os.path.join(current_app.root_path, 'HELP.md')
    content = ""
    try:
        with open(help_file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        content = f"# Erro\n\nNão foi possível carregar o arquivo de ajuda: {str(e)}"
        
    return render_template('help.html', content=content)
