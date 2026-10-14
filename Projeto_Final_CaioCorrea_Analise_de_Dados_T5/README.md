# Projeto Final — Análise de Dados com Python

**Autor:** Caio Corrêa  

**Curso:** Análise de Dados com Python — SCTEC  

**Turma:** T5  

**Projeto:** Avaliativo — Módulo 1

## Análise de Viagens a Serviço — Dados de 2025

Projeto desenvolvido como atividade avaliativa do curso de Análise de Dados com Python, utilizando um pipeline ETL (*Extract, Transform, Load*) para processar e analisar dados de viagens a serviço.

O projeto utiliza Python e PostgreSQL para extrair, armazenar, transformar e analisar os dados, organizados em três camadas: **Raw, Silver e Gold**.

## Objetivo

Construir um processo de tratamento e análise de dados que permita identificar padrões relacionados às viagens a serviço, aos gastos, aos pagamentos e aos meios de transporte.

## Tecnologias utilizadas

- Python 3.14
- PostgreSQL
- Pandas
- Psycopg2
- Matplotlib
- Jupyter Notebook
- Git e GitHub

## Arquitetura do projeto

O pipeline está organizado em três camadas:

### Raw — Dados brutos

Armazena os registros extraídos dos arquivos CSV, preservando os dados de origem.

**Tabelas:** `raw_viagem`, `raw_pagamento`, `raw_passagem` e `raw_trecho`.

### Silver — Dados tratados

Contém os dados transformados e estruturados, com conversão de tipos e aplicação de regras de integridade.

**Tabelas:** `silver_viagem`, `silver_pagamento`, `silver_passagem` e `silver_trecho`.

### Gold — Dados agregados

Disponibiliza informações consolidadas para análise, permitindo consultar indicadores por órgão superior.

- `gold_resumo_orgaos` — tabela com indicadores agregados por órgão superior.
- `gold_ranking_orgaos` — VIEW que apresenta a classificação dos órgãos por gastos totais.

## Fonte dos dados

O projeto utiliza arquivos CSV referentes ao **primeiro semestre de 2025**, disponibilizados pela instituição de ensino por meio do Google Drive. Os dados dizem respeito a viagens a serviço e têm como referência o Portal da Transparência do Governo Federal.

**Arquivos utilizados:**

- `2025_Viagem.csv`
- `2025_Pagamento.csv`
- `2025_Passagem.csv`
- `2025_Trecho.csv`

### Disponibilidade do conjunto de dados

O conjunto utilizado foi disponibilizado pela instituição de ensino em um arquivo ZIP contendo os quatro CSVs.

[Arquivo ZIP — Viagens a Serviço (2025)](https://drive.google.com/file/d/1R6re1574aCeqNfwJXQ_T7BwHCEsPfgvc/view)

O download é realizado automaticamente pelo script `1_extrair.py`, utilizando a biblioteca `gdown`. O identificador do arquivo está configurado na variável `DRIVE_FILE_ID`, em `config.py`.

Os arquivos baixados são armazenados localmente na pasta `data/`, que não é versionada no GitHub.

**Observação:** o acesso ao ZIP depende das permissões de compartilhamento do arquivo no Google Drive. O link acima corresponde ao identificador configurado no projeto; seu acesso público deve ser confirmado.

## Estrutura do projeto

```text
Projeto_Final_CaioCorrea_Analise_de_Dados_T5/
├── 0_criar_banco.sql
├── 1_extrair.py
├── 2_transformar.py
├── 3_analise.ipynb
├── 4_criar_gold.sql
├── banco.py
├── config.py
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

| Arquivo | Finalidade |
|---|---|
| `0_criar_banco.sql` | Criação do banco de dados e das tabelas Raw e Silver |
| `1_extrair.py` | Download, extração e carregamento dos dados brutos |
| `2_transformar.py` | Transformação e carregamento dos dados na camada Silver |
| `3_analise.ipynb` | Consultas SQL, análises de negócio e visualizações gráficas |
| `4_criar_gold.sql` | Criação e atualização da camada Gold |
| `banco.py` | Conexão com o PostgreSQL |
| `config.py` | Configurações do projeto e parâmetros de processamento |
| `requirements.txt` | Dependências Python |
| `.env.example` | Modelo das variáveis de ambiente |
| `.gitignore` | Configuração dos arquivos ignorados pelo Git |

## Pré-requisitos

- Python 3.14
- PostgreSQL
- Git
- VS Code ou outro editor compatível com Jupyter Notebook

As instruções a seguir consideram Windows com Git Bash.

## Configuração do ambiente

### 1. Clonar o repositório

```bash
git clone https://github.com/gatsumoto/sctec.tad.git
cd sctec.tad/Projeto_Final_CaioCorrea_Analise_de_Dados_T5
```

### 2. Criar e ativar o ambiente virtual

```bash
python -m venv .venv
source .venv/Scripts/activate
```

### 3. Instalar as dependências

```bash
python -m pip install -r requirements.txt
```

### 4. Configurar as variáveis de ambiente

Crie uma cópia do arquivo `.env.example`:

```bash
cp .env.example .env
```

Edite o `.env` com as credenciais do PostgreSQL:

```dotenv
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_USER=postgres
POSTGRES_PASSWORD=sua_senha_aqui
POSTGRES_DATABASE=transparencia
```

**Importante:** o `.env` contém informações sensíveis e não deve ser enviado ao GitHub. O projeto utiliza `config.py` para carregar essas configurações.

## Execução do pipeline ETL

### Etapa 1 — Criar o banco de dados e as tabelas

Abra `0_criar_banco.sql` em um cliente PostgreSQL, como o pgAdmin.

Primeiro, conectado ao banco administrativo `postgres`, execute **apenas**:

```sql
CREATE DATABASE transparencia;
```

Se o banco já existir, pule essa instrução.

Depois, **conecte-se ao banco `transparencia`** e execute os comandos `CREATE TABLE` restantes de `0_criar_banco.sql`. Serão criadas quatro tabelas Raw e quatro Silver.

**Atenção:** não execute o arquivo inteiro conectado ao banco `postgres`, pois as tabelas seriam criadas no banco incorreto. A criação do banco e das tabelas é uma etapa de configuração inicial.

### Etapa 2 — Extrair os dados

```bash
python 1_extrair.py
```

O script baixa o ZIP disponibilizado pela instituição, extrai os quatro CSVs e carrega os registros nas tabelas Raw. A leitura utiliza blocos de até **50.000 registros** para controlar o consumo de memória.

### Etapa 3 — Transformar os dados

```bash
python 2_transformar.py
```

O script converte e trata os dados, carregando os registros na camada Silver.

### Etapa 4 — Criar a camada Gold

Conectado ao banco `transparencia`, execute o conteúdo de `4_criar_gold.sql` em um cliente PostgreSQL.

O script cria e atualiza a tabela `gold_resumo_orgaos` e a VIEW `gold_ranking_orgaos`, consolidando quantidade de viagens, gastos totais, custo médio e total de pagamentos por órgão superior. A atualização da tabela Gold foi implementada para evitar duplicação de registros em reexecuções.

### Etapa 5 — Executar as análises

Abra `3_analise.ipynb`, selecione o interpretador Python do ambiente `.venv` e execute as células em sequência.

O notebook apresenta consultas SQL, tabelas de resultados, gráficos com Matplotlib, interpretações e validações de consistência entre as camadas Silver e Gold.

## Ordem de execução

1. `0_criar_banco.sql` (em duas conexões, conforme explicado acima)
2. `1_extrair.py`
3. `2_transformar.py`
4. `4_criar_gold.sql`
5. `3_analise.ipynb`

**Observação:** embora o notebook tenha prefixo `3`, a camada Gold deve ser criada antes da execução de suas consultas de validação.

## Análises de negócio

O notebook `3_analise.ipynb` apresenta sete análises com base nos dados da camada Silver.

### 1. Quais são os cinco órgãos com maiores gastos em viagens?

O **Ministério da Justiça e Segurança Pública** apresentou o maior valor, com aproximadamente **R$ 486,93 milhões**.

### 2. Quais são os três destinos com maior custo médio de viagem?

Os três maiores custos médios encontrados foram aproximadamente **R$ 245,85 mil**, **R$ 216,73 mil** e **R$ 207,22 mil**. Cada um desses destinos apresentou apenas uma viagem no conjunto analisado; portanto, os resultados não indicam necessariamente um padrão recorrente.

### 3. Qual foi a viagem de maior duração?

A maior duração encontrada foi de **384 dias**, com valor total registrado de **R$ 0,00**. Trata-se de uma situação atípica que merece atenção na interpretação dos dados.

### 4. Qual tipo de pagamento apresentou o maior valor médio?

A categoria **DIÁRIAS** apresentou o maior valor médio, aproximadamente **R$ 2.078,28 por registro**.

### 5. Qual foi o meio de transporte mais utilizado?

A categoria **Veículo Oficial** apresentou a maior frequência, com **386.424 registros** nos trechos. A análise também identificou registros classificados como `"Inválido"`.

### 6. Qual foi a unidade federativa de destino mais frequente?

**São Paulo** apresentou a maior frequência, com **82.722 registros**, seguido pelo **Distrito Federal**, com **79.962 registros**. Também foram identificados valores inválidos nesse campo.

### 7. Qual órgão pagou mais no total?

O **Fundo Nacional de Segurança Pública** apresentou o maior valor acumulado de pagamentos, totalizando **R$ 278.481.047,89**, distribuídos em **79.816 registros**.

A categoria **"Sigiloso"** ficou em segundo lugar, com **R$ 200.484.801,68**, seguida pelo **Comando da Aeronáutica**, com aproximadamente **R$ 81,77 milhões**.

O resultado foi obtido a partir da soma dos valores da tabela `silver_pagamento`, agrupados por `nome_orgao_pagador`. A identificação "Sigiloso" limita a atribuição de parte dos pagamentos a órgãos específicos.

**Análise complementar — maior pagamento individual identificável:** desconsiderando identificações nulas, vazias ou classificadas como "Sigiloso", o maior registro individual foi de **R$ 145.973,58**, associado ao **Ministério das Relações Exteriores**, na categoria **PASSAGEM**. Esse indicador não deve ser confundido com o total acumulado por órgão.

## Validação dos dados

Foram realizadas verificações de consistência entre as camadas Silver e Gold.

| Indicador | Resultado |
|---|---:|
| Viagens processadas | 341.860 |
| Pagamentos processados | 606.916 |
| Passagens processadas | 167.260 |
| Trechos processados | 763.349 |
| Órgãos superiores na camada Gold | 35 |
| Gastos totais com viagens | R$ 1.188.144.731,13 |
| Total de pagamentos | R$ 1.194.365.457,37 |

Os totais de viagens, gastos e pagamentos da camada Gold foram comparados com os respectivos totais da camada Silver, apresentando resultados equivalentes.

**Observação:** gastos com viagens e pagamentos são indicadores distintos e não precisam apresentar o mesmo total entre si.

## Possíveis melhorias

- Investigar registros classificados como `"Inválido"` e suas causas.
- Examinar viagens com duração atípica ou valores zerados.
- Acrescentar testes automatizados para validação de dados e execução do pipeline.
- Avaliar a portabilidade do ambiente de instalação para outros sistemas operacionais.

## Considerações finais

O projeto permitiu aplicar conceitos de extração, transformação, armazenamento e análise de dados utilizando Python e PostgreSQL.

A organização em camadas **Raw, Silver e Gold** possibilitou separar os dados originais dos dados tratados e das informações agregadas para análise. As consultas SQL e visualizações gráficas ajudaram a identificar padrões de gastos, pagamentos, destinos e meios de transporte.

Também foram identificadas limitações na qualidade dos dados, como valores inválidos, registros sigilosos e situações atípicas, que devem ser consideradas na interpretação dos resultados.
