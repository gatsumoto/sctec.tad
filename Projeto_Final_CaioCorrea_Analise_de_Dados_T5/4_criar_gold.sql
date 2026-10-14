-- ============================================================
-- 4_criar_gold.sql
-- Camada Gold: indicadores agregados por orgao superior
-- Fonte: tabelas Silver do banco transparencia
-- ============================================================

BEGIN;

-- 1. Criar a tabela Gold, caso ainda nao exista.
CREATE TABLE IF NOT EXISTS gold_resumo_orgaos (
    nome_orgao_superior VARCHAR(255) PRIMARY KEY,
    quantidade_viagens BIGINT NOT NULL,
    gasto_total NUMERIC(15, 2) NOT NULL,
    custo_medio NUMERIC(15, 2) NOT NULL,
    total_pagamentos NUMERIC(15, 2) NOT NULL
);

-- 2. Limpar os dados anteriores para evitar duplicacoes.
TRUNCATE TABLE gold_resumo_orgaos;

-- 3. Carregar os indicadores agregados.
-- Os pagamentos sao agrupados por viagem antes do JOIN,
-- evitando a multiplicacao dos valores financeiros.
INSERT INTO gold_resumo_orgaos (
    nome_orgao_superior,
    quantidade_viagens,
    gasto_total,
    custo_medio,
    total_pagamentos
)
SELECT
    v.nome_orgao_superior,
    COUNT(*) AS quantidade_viagens,
    ROUND(SUM(v.valor_total), 2) AS gasto_total,
    ROUND(AVG(v.valor_total), 2) AS custo_medio,
    ROUND(SUM(COALESCE(p.total_pago, 0)), 2) AS total_pagamentos
FROM silver_viagem AS v
LEFT JOIN (
    SELECT
        id_viagem,
        SUM(valor) AS total_pago
    FROM silver_pagamento
    GROUP BY id_viagem
) AS p
    ON v.id_viagem = p.id_viagem
GROUP BY v.nome_orgao_superior;

-- 4. Criar a VIEW com o ranking dos orgaos.
CREATE OR REPLACE VIEW gold_ranking_orgaos AS
SELECT
    ROW_NUMBER() OVER (
        ORDER BY gasto_total DESC, nome_orgao_superior
    ) AS posicao,
    nome_orgao_superior,
    quantidade_viagens,
    gasto_total,
    custo_medio,
    total_pagamentos
FROM gold_resumo_orgaos;

COMMIT;