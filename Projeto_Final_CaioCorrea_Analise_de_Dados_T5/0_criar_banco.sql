-- ============================================================
-- Projeto Final - Análise de Dados com Python
-- Pipeline ETL - Viagens a Serviço
-- Banco de dados: PostgreSQL
-- ============================================================

-- Fase 0: criação do banco de dados

CREATE DATABASE transparencia;
-- ============================================================
-- Fase 0: criação das tabelas da camada Raw
-- ============================================================

-- Tabela Raw: viagens
-- Origem: 2025_Viagem.csv

CREATE TABLE raw_viagem (
    id_viagem              VARCHAR(255),
    num_proposta           VARCHAR(255),
    situacao               VARCHAR(255),
    viagem_urgente         VARCHAR(255),
    justificativa_urgencia VARCHAR(4000),
    cod_orgao_superior     VARCHAR(255),
    nome_orgao_superior    VARCHAR(255),
    cod_orgao_solicitante  VARCHAR(255),
    nome_orgao_solicitante VARCHAR(255),
    cpf_viajante           VARCHAR(255),
    nome_viajante          VARCHAR(255),
    cargo                  VARCHAR(255),
    funcao                 VARCHAR(255),
    descricao_funcao       VARCHAR(255),
    data_inicio            VARCHAR(255),
    data_fim               VARCHAR(255),
    destinos               VARCHAR(4000),
    motivo                 VARCHAR(4000),
    valor_diarias          VARCHAR(255),
    valor_passagens        VARCHAR(255),
    valor_devolucao        VARCHAR(255),
    valor_outros_gastos    VARCHAR(255)
);