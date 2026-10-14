"""
2_transformar.py
----------------
Etapa de transformacao do pipeline ETL.

Responsavel por converter os dados da camada Raw
para a camada Silver no PostgreSQL.
"""

from contextlib import closing

from banco import conectar


def validar_datas_viagens(cursor):
    """Verifica se as datas das viagens sao validas."""

    print("Validando datas das viagens...")

    cursor.execute(
        """
        SELECT COUNT(*)
        FROM raw_viagem
        WHERE
            TO_CHAR(
                TO_DATE(data_inicio, 'DD/MM/YYYY'),
                'DD/MM/YYYY'
            ) <> data_inicio
            OR
            TO_CHAR(
                TO_DATE(data_fim, 'DD/MM/YYYY'),
                'DD/MM/YYYY'
            ) <> data_fim
        """
    )

    quantidade_invalidas = cursor.fetchone()[0]

    if quantidade_invalidas > 0:
        raise ValueError(
            f"Foram encontradas {quantidade_invalidas} "
            "viagens com datas invalidas."
        )

    print("Datas das viagens validadas com sucesso.")


def limpar_silver(cursor):
    """Limpa as tabelas Silver respeitando as chaves estrangeiras."""

    print("Preparando tabelas Silver...")

    cursor.execute(
        """
        TRUNCATE TABLE
            silver_pagamento,
            silver_passagem,
            silver_trecho,
            silver_viagem
        RESTART IDENTITY
        """
    )

    print("Tabelas Silver preparadas com sucesso.")


def transformar_viagens(cursor):
    """Transforma os registros de raw_viagem em silver_viagem."""

    print("Iniciando transformacao das viagens...")

    cursor.execute(
        """
        INSERT INTO silver_viagem (
            id_viagem,
            num_proposta,
            situacao,
            viagem_urgente,
            cod_orgao_superior,
            nome_orgao_superior,
            nome_viajante,
            cargo,
            data_inicio,
            data_fim,
            destinos,
            motivo,
            valor_diarias,
            valor_passagens,
            valor_devolucao,
            valor_outros_gastos,
            valor_total,
            duracao_dias
        )
        SELECT
            NULLIF(TRIM(id_viagem), ''),
            NULLIF(TRIM(num_proposta), ''),
            NULLIF(TRIM(situacao), ''),
            NULLIF(TRIM(viagem_urgente), ''),
            NULLIF(TRIM(cod_orgao_superior), ''),
            NULLIF(TRIM(nome_orgao_superior), ''),
            NULLIF(TRIM(nome_viajante), ''),
            NULLIF(TRIM(cargo), ''),

            TO_DATE(data_inicio, 'DD/MM/YYYY'),
            TO_DATE(data_fim, 'DD/MM/YYYY'),

            NULLIF(TRIM(destinos), ''),
            NULLIF(TRIM(motivo), ''),

            REPLACE(valor_diarias, ',', '.')::NUMERIC(10, 2),
            REPLACE(valor_passagens, ',', '.')::NUMERIC(10, 2),
            REPLACE(valor_devolucao, ',', '.')::NUMERIC(10, 2),
            REPLACE(valor_outros_gastos, ',', '.')::NUMERIC(10, 2),

            (
                REPLACE(valor_diarias, ',', '.')::NUMERIC
                + REPLACE(valor_passagens, ',', '.')::NUMERIC
                + REPLACE(valor_outros_gastos, ',', '.')::NUMERIC
                - REPLACE(valor_devolucao, ',', '.')::NUMERIC
            )::NUMERIC(12, 2),

            (
                TO_DATE(data_fim, 'DD/MM/YYYY')
                - TO_DATE(data_inicio, 'DD/MM/YYYY')
                + 1
            )

        FROM raw_viagem;
        """
    )

    print(
        f"Viagens transformadas: {cursor.rowcount:,} registros."
    )


def transformar_pagamentos(cursor):
    """Transforma os registros de raw_pagamento em silver_pagamento."""

    print("Iniciando transformacao dos pagamentos...")

    cursor.execute(
        """
        INSERT INTO silver_pagamento (
            id_viagem,
            num_proposta,
            nome_orgao_pagador,
            nome_ug_pagadora,
            tipo_pagamento,
            valor
        )
        SELECT
            NULLIF(TRIM(id_viagem), ''),
            NULLIF(TRIM(num_proposta), ''),
            NULLIF(TRIM(nome_orgao_pagador), ''),
            NULLIF(TRIM(nome_ug_pagadora), ''),
            NULLIF(TRIM(tipo_pagamento), ''),
            REPLACE(valor, ',', '.')::NUMERIC(10, 2)
        FROM raw_pagamento;
        """
    )

    print(
        f"Pagamentos transformados: {cursor.rowcount:,} registros."
    )


def main():
    """Executa a transformacao da camada Raw para Silver."""

    print("Iniciando etapa de transformacao...")

    with closing(conectar()) as conexao, conexao, conexao.cursor() as cursor:
        validar_datas_viagens(cursor)
        limpar_silver(cursor)
        transformar_viagens(cursor)
        transformar_pagamentos(cursor)

    print("Transformacao concluida com sucesso.")


if __name__ == "__main__":
    try:
        main()
    except Exception as erro:
        print(f"Erro durante a transformacao: {erro}")
        raise