# Guia de Publicação no PythonAnywhere

Este guia passo a passo ajudará você a publicar o **Gerador de Provas** gratuitamente no PythonAnywhere.

## 1. Preparação (Local)

1.  **Baixe o código:** Certifique-se de ter todos os arquivos do projeto.
2.  **Compacte o projeto:** Crie um arquivo `.zip` contendo todos os arquivos da pasta do projeto (exceto a pasta `venv` ou `__pycache__`, se houver).
    *   Certifique-se de incluir: `app.py`, `config.py`, `models.py`, `requirements.txt`, `HELP.md` e as pastas `routes`, `templates`, `static`, `latex_templates`.

## 2. Configuração no PythonAnywhere

1.  **Crie uma conta:** Acesse [www.pythonanywhere.com](https://www.pythonanywhere.com/) e crie uma conta "Beginner" (gratuita).
2.  **Upload do Código:**
    *   Vá para a aba **Files**.
    *   Clique no botão "Upload a file" e envie o seu arquivo `.zip`.
    *   Abra um **Bash Console** (na aba Consoles).
    *   Descompacte o arquivo: `unzip nome_do_arquivo.zip` (substitua pelo nome real).
    *   *Dica:* Se descompactar em uma subpasta, mova os arquivos para a raiz ou ajuste os caminhos depois. O ideal é que `app.py` esteja em `/home/seu_usuario/ger_provas` (por exemplo).

3.  **Instalação das Dependências:**
    *   No Bash Console, navegue até a pasta do projeto: `cd ger_provas` (ou onde você descompactou).
    *   Crie um ambiente virtual: `python3 -m venv venv`
    *   Ative o ambiente: `source venv/bin/activate`
    *   Instale os pacotes: `pip install -r requirements.txt`

4.  **Configuração do Web App:**
    *   Vá para a aba **Web**.
    *   Clique em **Add a new web app**.
    *   Clique em **Next**.
    *   Escolha **Flask**.
    *   Escolha a versão do Python (ex: **Python 3.10**).
    *   No caminho do arquivo, coloque o caminho para o seu `app.py` (o sistema vai sugerir algo, pode aceitar por enquanto).
    *   **Importante:** Após criar, role para baixo até a seção **Virtualenv**.
    *   Digite o caminho do seu ambiente virtual: `/home/seu_usuario/ger_provas/venv` (ajuste conforme o nome da sua pasta).

5.  **Ajuste do Arquivo WSGI:**
    *   Na aba **Web**, clique no link do arquivo de configuração WSGI (algo como `/var/www/seu_usuario_pythonanywhere_com_wsgi.py`).
    *   Apague o conteúdo padrão e substitua por:

```python
import sys
import os

# Ajuste para o caminho da sua pasta
path = '/home/seu_usuario/ger_provas'
if path not in sys.path:
    sys.path.append(path)

# Importa o arquivo de entrada criado para o PythonAnywhere
from flask_app import app as application
```

6.  **Banco de Dados e Pastas:**
    *   Como estamos usando SQLite, o arquivo do banco será criado automaticamente na primeira execução.
    *   Certifique-se de que as pastas `static/uploads` e `static/qr_codes` existam. Se não, crie-as pelo terminal ou aba Files.

7.  **Finalizar:**
    *   Volte para a aba **Web**.
    *   Clique no botão verde **Reload**.
    *   Acesse o link do seu site (ex: `seu_usuario.pythonanywhere.com`).

## Observações
*   **PDFLaTeX:** O PythonAnywhere já tem o `pdflatex` instalado, então a geração de provas deve funcionar sem configuração extra.
*   **Renovação:** Lembre-se de logar a cada 3 meses para renovar o plano gratuito.
