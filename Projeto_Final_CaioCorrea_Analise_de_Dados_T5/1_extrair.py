"""
1_extrair.py
------------
Etapa de extracao do pipeline ETL.

Responsavel por baixar os dados de viagens a servico
e preparar os arquivos CSV para carregamento na camada Raw.
"""

import zipfile

import gdown

from config import ARQUIVOS, DRIVE_FILE_ID, PASTA_DADOS


def baixar_zip():
    """Baixa o arquivo ZIP do Google Drive, caso ainda nao exista."""

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
    """Extrai os quatro arquivos CSV do ZIP para a pasta data."""

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


if __name__ == "__main__":
    caminho_zip = baixar_zip()
    extrair_csvs(caminho_zip)