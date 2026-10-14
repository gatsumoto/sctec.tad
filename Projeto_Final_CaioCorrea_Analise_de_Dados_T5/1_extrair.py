"""
1_extrair.py
------------
Etapa de extracao do pipeline ETL.

Responsavel por baixar os dados de viagens a servico,
extrair os arquivos CSV e carregar a camada Raw.
"""

import io
import zipfile
from contextlib import closing

import gdown
import pandas as pd
from psycopg2 import sql

from banco import conectar
from config import (
    ARQUIVOS,
    CSV_ENCODING,
    CSV_SEPARADOR,
    DRIVE_FILE_ID,
    PASTA_DADOS,
    TAMANHO_BLOCO,
)


def baixar_zip():
    """Baixa o ZIP do Google Drive caso ainda nao exista."""

    PASTA_DADOS.mkdir(parents=True, exist_ok=True)

    caminho_zip = PASTA_DADOS / "viagens_2025.zip"

    if caminho_zip.exists():
        print(f"Arquivo ZIP ja existe: {caminho_zip}")
        return caminho_zip

    print("Iniciando download do arquivo ZIP...")

    resultado = gdown.download(
        id=DRIVE_FILE_ID,
        output=str(caminho_zip),
        quiet=False,
    )

    if resultado is None:
        raise RuntimeError("Nao foi possivel baixar o arquivo ZIP.")

    print("Download concluido com sucesso.")
    return caminho_zip


def extrair_csvs(caminho_zip):
    """Verifica o ZIP e extrai os quatro arquivos CSV."""

    print("Verificando os arquivos dentro do ZIP...")

    with zipfile.ZipFile(caminho_zip, "r") as arquivo_zip:
        arquivo_corrompido = arquivo_zip.testzip()

        if arquivo_corrompido is not None:
            raise RuntimeError(
                f"Arquivo corrompido dentro do ZIP: {arquivo_corrompido}"
            )

        arquivos_esperados = {
            configuracao["csv"]
            for configuracao in ARQUIVOS.values()
        }

        arquivos_encontrados = set(arquivo_zip.namelist())
        arquivos_ausentes = arquivos_esperados - arquivos_encontrados

        if arquivos_ausentes:
            raise RuntimeError(
                f"Arquivos CSV ausentes no ZIP: {arquivos_ausentes}"
            )

        for nome_csv in sorted(arquivos_esperados):
            destino = PASTA_DADOS / nome_csv

            if destino.exists():
                print(f"CSV ja existe: {nome_csv}")
                continue

            arquivo_zip.extract(nome_csv, path=PASTA_DADOS)
            print(f"CSV extraido: {nome_csv}")

    print("Verificacao e extracao dos CSVs concluidas.")


def carregar_raw():
    """Carrega os quatro CSVs nas tabelas Raw do PostgreSQL."""

    print("\nIniciando carregamento da camada Raw...")

    # closing garante o fechamento da conexao.
    # O contexto da conexao controla commit e rollback.
    with closing(conectar()) as conexao, conexao, conexao.cursor() as cursor:
        for configuracao in ARQUIVOS.values():
            tabela = configuracao["tabela_raw"]
            caminho_csv = PASTA_DADOS / configuracao["csv"]

            if not caminho_csv.is_file():
                raise FileNotFoundError(
                    f"Arquivo CSV nao encontrado: {caminho_csv}"
                )

            print(f"\nPreparando tabela {tabela}...")

            # Consulta as colunas na ordem definida no PostgreSQL.
            cursor.execute(
                """
                SELECT column_name
                FROM information_schema.columns
                WHERE table_schema = 'public'
                  AND table_name = %s
                ORDER BY ordinal_position
                """,
                (tabela,),
            )

            colunas = [linha[0] for linha in cursor.fetchall()]

            if not colunas:
                raise RuntimeError(
                    f"Tabela nao encontrada: {tabela}"
                )

            # Confere a estrutura do CSV antes de limpar a tabela.
            cabecalho = pd.read_csv(
                caminho_csv,
                sep=CSV_SEPARADOR,
                encoding=CSV_ENCODING,
                nrows=0,
            )

            if len(cabecalho.columns) != len(colunas):
                raise ValueError(
                    f"Quantidade de colunas incompativel em {tabela}: "
                    f"CSV={len(cabecalho.columns)}, "
                    f"PostgreSQL={len(colunas)}"
                )

            # FORCE_NOT_NULL preserva campos vazios como strings vazias.
            colunas_sql = sql.SQL(", ").join(
                sql.Identifier(coluna) for coluna in colunas
            )

            comando_copy = sql.SQL(
                "COPY {} ({}) FROM STDIN "
                "WITH ("
                "FORMAT CSV, "
                "DELIMITER ',', "
                "FORCE_NOT_NULL ({})"
                ")"
            ).format(
                sql.Identifier(tabela),
                colunas_sql,
                colunas_sql,
            )

            comando_truncate = sql.SQL(
                "TRUNCATE TABLE {}"
            ).format(
                sql.Identifier(tabela)
            )

            # A limpeza so sera confirmada se toda a carga funcionar.
            cursor.execute(comando_truncate)

            total = 0

            leitor = pd.read_csv(
                caminho_csv,
                sep=CSV_SEPARADOR,
                encoding=CSV_ENCODING,
                dtype=str,
                keep_default_na=False,
                chunksize=TAMANHO_BLOCO,
            )

            for numero_bloco, bloco in enumerate(leitor, start=1):
                if len(bloco.columns) != len(colunas):
                    raise ValueError(
                        "Quantidade de colunas incompativel "
                        f"no bloco {numero_bloco} de {tabela}"
                    )

                buffer = io.StringIO()

                bloco.to_csv(
                    buffer,
                    index=False,
                    header=False,
                    na_rep="",
                    lineterminator="\n",
                )

                buffer.seek(0)

                cursor.copy_expert(
                    comando_copy.as_string(conexao),
                    buffer,
                )

                total += len(bloco)

                print(
                    f"{tabela} | Bloco {numero_bloco} | "
                    f"Total carregado: {total:,}"
                )

            print(
                f"Tabela {tabela}: {total:,} registros carregados."
            )

    print("\nCarregamento da camada Raw concluido.")


if __name__ == "__main__":
    try:
        caminho_zip = baixar_zip()
        extrair_csvs(caminho_zip)
        carregar_raw()

        print("\nPipeline de extracao finalizado com sucesso.")

    except Exception as erro:
        print(f"\nErro durante a extracao: {erro}")
        raise