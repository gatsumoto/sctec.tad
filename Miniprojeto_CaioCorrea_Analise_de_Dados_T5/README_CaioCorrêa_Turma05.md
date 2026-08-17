# Miniprojeto - Análise de Dados de Varejo

**Aluno:** Caio Corrêa
**Turma:** Turma 05

## 📋 Sobre o Projeto
Este repositório contém o miniprojeto de Análise de Dados desenvolvido em Python, aplicando as melhores práticas de programação (PEP 8) e um pipeline completo de ETL (Extract, Transform, Load).

## 🛠️ Stack Tecnológico Utilizado
- **Linguagem:** Python
- **Manipulação e Análise:** Pandas e NumPy
- **Limpeza de Dados:** Expressões Regulares (`re`)
- **Visualização Gráfica:** Matplotlib e Seaborn

---

## 📈 Etapas do Pipeline e Sprints
1. **Coleta:** Importação da base de dados `varejo.csv` e verificação inicial de tipos, colunas e dimensões.
2. **Transformação (ETL):** Limpeza de strings com Regex e conversão segura da coluna de data (`datetime64`).
3. **Limpeza de Nulos e Duplicatas:** Remoção de duplicatas estruturais e preenchimento preventivo de valores categóricos e físicos.
4. **Análise Estatística e Agrupamentos:** - Estatísticas descritivas da coluna de número de filhos (`CL_FHL`).
   - Agrupamentos estratégicos (top clientes, volume por categoria e série temporal).
5. **Relatório e Documentação:** Auditoria final dos registros e consolidação dos insights de negócio.

---

## 💡 Reflexão Teórica: ETL e Qualidade de Dados
O processo de ETL é fundamental para garantir a integridade dos dados antes da geração de relatórios e gráficos. Através da extração estruturada, tratamento de inconsistências e carga de dados limpos, evitou-se distorções estatísticas, assegurando análises confiáveis e tomadas de decisão assertivas.

## 💡 Principais Insights Obtidos
1. **Perfil Demográfico:** O comportamento de consumo varia de acordo com as características demográficas dos clientes.
2. **Concentração de Vendas:** Determinadas categorias de produtos lideram o volume de transações comerciais.
3. **Evolução Temporal:** A análise de série temporal demonstra a flutuação do volume de vendas ao longo dos meses.
4. **Qualidade dos Dados:** O tratamento de duplicatas e nulos preservou a integridade informacional da base.

---

## 🚀 Como Executar o Projeto

Você pode executar este projeto de duas formas diferentes. Certifique-se apenas de que o arquivo de dados `varejo.csv` está no mesmo diretório do arquivo do notebook.

### Opção 1: Executando no VSCode
1. Abra o Visual Studio Code.
2. Certifique-se de ter as extensões do Python e Jupyter instaladas.
3. Abra o arquivo do notebook (`.ipynb`) correspondente ao projeto.
4. Clique na opção **"Run All" (Executar Todas)** no topo do notebook para rodar todas as células sequencialmente.

### Opção 2: Executando no Google Colab
1. Faça o upload do arquivo do notebook e do arquivo `varejo.csv` para o seu ambiente do Google Colab.
2. No menu superior, clique em **Ambiente de execução (Runtime)**.
3. Selecione a opção **Executar tudo (Run all)** para processar todas as etapas do pipeline de ponta a ponta.

---

## 🔗 Repositório no GitHub
[Repositório Oficial do Projeto](https://github.com/gatsumoto/sctec.tad/tree/main/Miniprojeto_CaioCorrea_Analise_de_Dados_T5)
