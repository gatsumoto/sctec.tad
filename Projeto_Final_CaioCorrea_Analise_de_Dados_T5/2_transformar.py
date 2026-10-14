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


def validar_datas_passagens(cursor):
    """Verifica as datas de emissao preenchidas das passagens."""

    print("Validando datas de emissao das passagens...")

    cursor.execute(
        """
        SELECT COUNT(*)
        FROM raw_passagem
        WHERE NULLIF(TRIM(data_emissao), '') IS NOT NULL
          AND TO_CHAR(
              TO_DATE(TRIM(data_emissao), 'DD/MM/YYYY'),
              'DD/MM/YYYY'
          ) <> TRIM(data_emissao)
        """
    )

    quantidade_invalidas = cursor.fetchone()[0]

    if quantidade_invalidas > 0:
        raise ValueError(
            f"Foram encontradas {quantidade_invalidas} "
            "passagens com datas de emissao invalidas."
        )

    print("Datas de emissao validadas com sucesso.")


def validar_datas_trechos(cursor):
    """Verifica as datas de origem e destino dos trechos."""

    print("Validando datas dos trechos...")

    cursor.execute(
        """
        SELECT
            COUNT(*) FILTER (
                WHERE
                    TO_CHAR(
                        TO_DATE(origem_data, 'DD/MM/YYYY'),
                        'DD/MM/YYYY'
                    ) <> origem_data
                    OR
                    TO_CHAR(
                        TO_DATE(destino_data, 'DD/MM/YYYY'),
                        'DD/MM/YYYY'
                    ) <> destino_data
            ) AS datas_invalidas,

            COUNT(*) FILTER (
                WHERE
                    TO_DATE(destino_data, 'DD/MM/YYYY')
                    < TO_DATE(origem_data, 'DD/MM/YYYY')
            ) AS datas_invertidas

        FROM raw_trecho;
        """
    )

    datas_invalidas, datas_invertidas = cursor.fetchone()

    if datas_invalidas > 0:
        raise ValueError(
            f"Foram encontrados {datas_invalidas} "
            "trechos com datas invalidas."
        )

    if datas_invertidas > 0:
        raise ValueError(
            f"Foram encontrados {datas_invertidas} "
            "trechos com datas invertidas."
        )

    print("Datas dos trechos validadas com sucesso.")


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

    print(f"Viagens transformadas: {cursor.rowcount:,} registros.")


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

    print(f"Pagamentos transformados: {cursor.rowcount:,} registros.")


def transformar_passagens(cursor):
    """Transforma os registros de raw_passagem em silver_passagem."""

    print("Iniciando transformacao das passagens...")

    cursor.execute(
        """
        INSERT INTO silver_passagem (
            id_viagem,
            meio_transporte,
            pais_origem_ida,
            uf_origem_ida,
            cidade_origem_ida,
            pais_destino_ida,
            uf_destino_ida,
            cidade_destino_ida,
            valor_passagem,
            taxa_servico,
            data_emissao
        )
        SELECT
            NULLIF(TRIM(id_viagem), ''),
            NULLIF(TRIM(meio_transporte), ''),
            NULLIF(TRIM(pais_origem_ida), ''),
            NULLIF(TRIM(uf_origem_ida), ''),
            NULLIF(TRIM(cidade_origem_ida), ''),
            NULLIF(TRIM(pais_destino_ida), ''),
            NULLIF(TRIM(uf_destino_ida), ''),
            NULLIF(TRIM(cidade_destino_ida), ''),

            REPLACE(valor_passagem, ',', '.')::NUMERIC(10, 2),
            REPLACE(taxa_servico, ',', '.')::NUMERIC(10, 2),

            TO_DATE(
                NULLIF(TRIM(data_emissao), ''),
                'DD/MM/YYYY'
            )

        FROM raw_passagem;
        """
    )

    print(f"Passagens transformadas: {cursor.rowcount:,} registros.")


def transformar_trechos(cursor):
    """Transforma os registros de raw_trecho em silver_trecho."""

    print("Iniciando transformacao dos trechos...")

    cursor.execute(
        """
        INSERT INTO silver_trecho (
            id_viagem,
            sequencia_trecho,
            origem_data,
            origem_uf,
            origem_cidade,
            destino_data,
            destino_uf,
            destino_cidade,
            meio_transporte,
            numero_diarias
        )
        SELECT
            NULLIF(TRIM(id_viagem), ''),

            TRIM(sequencia_trecho)::INTEGER,

            TO_DATE(origem_data, 'DD/MM/YYYY'),

            NULLIF(TRIM(origem_uf), ''),
            NULLIF(TRIM(origem_cidade), ''),

            TO_DATE(destino_data, 'DD/MM/YYYY'),

            NULLIF(TRIM(destino_uf), ''),
            NULLIF(TRIM(destino_cidade), ''),
            NULLIF(TRIM(meio_transporte), ''),

            REPLACE(numero_diarias, ',', '.')::NUMERIC(10, 2)

        FROM raw_trecho;
        """
    )

    print(f"Trechos transformados: {cursor.rowcount:,} registros.")


def main():
    """Executa a transformacao da camada Raw para Silver."""

    print("Iniciando etapa de transformacao...")

    with closing(conectar()) as conexao, conexao, conexao.cursor() as cursor:
        validar_datas_viagens(cursor)
        validar_datas_passagens(cursor)
        validar_datas_trechos(cursor)

        limpar_silver(cursor)

        transformar_viagens(cursor)
        transformar_pagamentos(cursor)
        transformar_passagens(cursor)
        transformar_trechos(cursor)

    print("Transformacao concluida com sucesso.")


if __name__ == "__main__":
    try:
        main()
    except Exception as erro:
        print(f"Erro durante a transformacao: {erro}")
        raise