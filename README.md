# Gerador e Corretor de Provas

Uma plataforma completa para gestão, geração e correção automática de avaliações acadêmicas. O sistema permite criar bancos de questões robustos, gerar provas com múltiplas versões aleatórias (anti-cola), e realizar a correção automática através de leitura de gabaritos por imagem.

## 🚀 Funcionalidades Principais

### 📚 Banco de Questões
- **Gestão Completa:** Cadastro de questões com suporte nativo a **LaTeX** para fórmulas matemáticas.
- **Categorização:** Organize por Disciplina, Categoria, Dificuldade (Fácil, Médio, Difícil) e Tags.
- **Importação:** Importação em massa via arquivos **CSV**.
- **Visualização Detalhada:** Pré-visualização com renderização matemática.

### 📝 Geração de Provas
- **Versões Aleatórias:** Gere até 26 versões diferentes da mesma prova (A, B, C...) com questões e alternativas embaralhadas automaticamente.
- **Controle Preciso:** Defina limites de questões por categoria (Min/Max) e distribuição de dificuldade (Ex: 30% Fácil, 50% Médio, 20% Difícil).
- **Exportação Profissional:**
  - **PDF:** Prova pronta para impressão.
  - **LaTeX:** Código fonte aberto para personalização.
  - **Gabaritos:** Folhas de resposta geradas automaticamente.
- **QR Code:** Cada prova recebe um identificador único para rastreamento automático.

### 📸 Correção Automática (Computer Vision)
- **Leitura de Gabarito:** O aluno ou professor envia uma foto do cartão de respostas.
- **Processamento Inteligente:** O sistema identifica o QR Code (para saber a versão da prova) e reconhece as marcações do aluno.
- **Feedback Imediato:** Nota calculada instantaneamente com base nos pesos das questões.

### 📊 Dashboard e Analytics
Análise estatística profunda para melhoria pedagógica:
- **Métricas Básicas:** Média, Mediana, Mínima, Máxima.
- **Confiabilidade:** Cálculo automático do **Alfa de Cronbach**.
- **Análise de Itens:** Índice de Discriminação (biserial) para identificar questões problemáticas.
- **Distribuição:** Gráficos de frequência, Assimetria (Skewness) e Curtose.

### ⚙️ Administração
- **Backup e Restauração:** Ferramentas para exportar e importar todo o banco de dados (JSON).
- **Reset:** Funcionalidade para limpar o sistema para novos semestres.

## 🛠️ Tecnologias
- **Backend:** Python (Flask), SQLAlchemy.
- **Frontend:** Bootstrap 5, Jinja2, Chart.js.
- **Processamento:** OpenCV (leitura de imagens), Pandas/NumPy (estatísticas), PDFLaTeX.

## 📦 Como Rodar

1. **Instalar dependências**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Inicializar Banco de Dados**:
   ```bash
   python seed_db.py
   ```

3. **Rodar a Aplicação**:
   ```bash
   python app.py
   ```
   Acesse em `http://127.0.0.1:5000`.

## 📂 Estrutura do Projeto

- `app.py`: Aplicação principal.
- `routes/`: Controladores (Provas, Questões, Dashboard, Alunos).
- `services/`: Lógica de negócio (Geração de PDF, Estatísticas, Leitura de Imagem).
- `models.py`: Esquema do banco de dados (SQLite).
- `templates/`: Views HTML.

---
Desenvolvido para otimizar o tempo de professores e garantir a qualidade das avaliações.
