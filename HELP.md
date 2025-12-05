# Guia de Ajuda - Gerador de Provas

Bem-vindo ao sistema de Gestão e Geração de Provas. Este guia detalha todas as funcionalidades disponíveis para facilitar o seu trabalho.

## 1. Banco de Questões

Centralize todas as suas questões em um único lugar.

### Gerenciar Questões
- **Listar:** Visualize todas as questões cadastradas com paginação (10 por página).
- **Filtrar:** Utilize a barra de busca para filtrar por **Categoria**, **Dificuldade** (Fácil, Médio, Difícil) ou **Tags**.
- **Ações:** Use os botões para **Ver**, **Editar** ou **Excluir** questões individualmente.

### Criar/Editar Questão
- **Enunciado e Alternativas:** Suporte completo para texto e fórmulas matemáticas (LaTeX).
- **Parâmetros:**
  - **Categoria:** Classifique a questão (ex: Álgebra, Geometria).
  - **Dificuldade:** Defina o nível de desafio.
  - **Tags:** Etiquetas para facilitar a busca (ex: "ENEM", "2024").
  - **Peso:** Valor da questão na nota final.
  - **Resolução/Comentário:** Texto explicativo para o gabarito.

### Importação em Massa (CSV)
- Clique em **"Importar CSV"** na tela do Banco de Questões.
- **Modelo:** Baixe a planilha de exemplo para garantir a formatação correta.
- **Campos Obrigatórios:** Categoria, Enunciado, Alternativas A/B, Correta, Peso.
- O sistema detecta automaticamente separadores (vírgula ou ponto-e-vírgula).

---

## 2. Gerar Provas

Crie avaliações personalizadas em poucos cliques.

### Configuração
1. **Dados Básicos:** Título, Data, Instituição, Curso.
2. **Seleção de Questões:**
   - Defina a **quantidade mínima e máxima** de questões desejadas para cada Categoria.
   - O sistema selecionará aleatoriamente as questões respeitando esses limites e a dificuldade (se especificada).

### Versões e Exportação
- **Múltiplas Versões:** Gere até 26 versões (A, B, C...) da mesma prova. As questões e alternativas são embaralhadas automaticamente para garantir a lisura.
- **QR Code:** Cada prova recebe um identificador único (QR Code) no cabeçalho para leitura automática.
- **Downloads:**
  - **PDF da Prova:** Arquivo pronto para impressão.
  - **Gabarito (PDF):** Tabela de respostas para correção manual.
  - **Arquivo LaTeX (.tex):** Código fonte para personalização avançada.

---

## 3. Aplicação e Correção

Automatize a correção das provas aplicadas.

### Upload de Respostas
1. Acesse **"Notas"** > **"Upload de Gabarito"**.
2. **Cabeçalho:** Envie uma foto da área de identificação da prova (Nome, Data).
3. **Cartão de Respostas:** Envie a foto do gabarito preenchido pelo aluno.
4. O sistema lerá o QR Code para identificar a versão e corrigirá as alternativas marcadas.

### Revisão
- O sistema exibe o que foi detectado. Se houver erro na leitura, você pode corrigir manualmente antes de salvar a nota.

---

## 4. Dashboard e Estatísticas

Analise o desempenho da turma com métricas avançadas.

### Cartões de Métricas
- **Média, Mediana, Mínima, Máxima:** Visão geral das notas.
- **Desvio Padrão:** Mede a dispersão das notas (homogeneidade da turma).
- **Assimetria (Skewness):** Indica se as notas concentram-se acima ou abaixo da média.
- **Curtose:** Indica o "achatamento" da curva de distribuição.
- **Alfa de Cronbach:** Coeficiente de confiabilidade da prova (consistência interna).
  - *> 0.9:* Excelente
  - *> 0.7:* Aceitável
  - *< 0.6:* Questionável

### Gráficos e Tabelas
- **Distribuição de Notas:** Histograma para visualizar a frequência de notas.
- **Análise de Questões:** Lista as questões com maior taxa de erro.
  - **Discriminação (D):** Mede se a questão diferencia os bons alunos dos demais. (Verde = Bom discriminador).

---

## 5. Configurações

- **Backup:** Baixe todo o seu banco de dados em formato JSON.
- **Restaurar:** Recupere seus dados a partir de um backup (Modo Substituir ou Acrescentar).
- **Reiniciar:** Apaga **TODOS** os dados do sistema. Cuidado!

---

## Dicas de LaTeX

Para inserir fórmulas matemáticas, use `$$` no início e no fim.

- **Fração:** `$$ \frac{numerador}{denominador} $$`
- **Raiz:** `$$ \sqrt{x} $$`
- **Potência/Índice:** `$$ x^2 + y_1 $$`
- **Símbolos:** `$$ \pi, \alpha, \beta, \infty, \neq, \leq $$`


