# Gerador de Provas Flask

Aplicação web para gerar provas de múltipla escolha em LaTeX, com suporte a aleatorização, QR Code e correção automática.

## Funcionalidades

- Cadastro de questões com suporte a LaTeX.
- Organização por categorias.
- Geração de provas com múltiplas versões (questões e alternativas embaralhadas).
- Exportação para PDF (via .tex).
- Geração de QR Code único para cada versão.
- Interface para aluno enviar gabarito (foto + transcrição) e receber nota imediata.

## Como Rodar

1. **Instalar dependências**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Inicializar Banco de Dados (Seed)**:
   Isso criará o arquivo `app.db` e adicionará algumas questões de exemplo.
   ```bash
   python seed_db.py
   ```

3. **Rodar a Aplicação**:
   ```bash
   python app.py
   ```
   Acesse em `http://127.0.0.1:5000`.

## Fluxo de Uso

1. Vá em **Questões** e cadastre novas perguntas (use LaTeX nos campos).
2. Vá em **Provas** -> **Nova Prova**.
3. Defina o título, número de versões e quantas questões de cada categoria deseja.
4. Baixe o arquivo `.tex` gerado e compile (ex: no Overleaf ou localmente com `pdflatex`).
5. O PDF terá um QR Code. Escaneie-o (ou acesse a URL simulada) para ir à página de resposta.
6. Envie as respostas e veja a correção.

## Estrutura

- `app.py`: Entrada da aplicação.
- `models.py`: Modelos do banco de dados.
- `routes/`: Rotas separadas por módulo.
- `services/`: Lógica de negócio (Geração de prova, LaTeX, QR).
- `templates/`: Arquivos HTML e Jinja2.
- `latex_templates/`: Templates .tex.
