import zipfile
import pandas as pd
from pathlib import Path
from config import PASTA_DADOS, ARQUIVOS, CSV_SEPARADOR, CSV_ENCODING
from banco import conectar
from io import StringIO

def extrair_zip_local():
    arquivo_zip = PASTA_DADOS / "dados.zip"
    
    if not arquivo_zip.exists():
        print(f"Erro: O ficheiro 'dados.zip' não foi encontrado dentro da pasta 'data'!")
        return False

    print("A extrair ficheiros CSV localmente...")
    with zipfile.ZipFile(arquivo_zip, "r") as zf:
        zf.extractall(PASTA_DADOS)
    print("Extração concluída com sucesso!")
    return True

def carregar_raw():
    conexao = conectar()
    cursor = conexao.cursor()
    
    try:
        for chave, info in ARQUIVOS.items():
            caminho_csv = PASTA_DADOS / info["csv"]
            tabela = info["tabela_raw"]
            
            if not caminho_csv.exists():
                encontrados = list(PASTA_DADOS.rglob(info["csv"]))
                if encontrados:
                    caminho_csv = encontrados[0]
                else:
                    print(f"Aviso: Ficheiro {info['csv']} não encontrado.")
                    continue

            print(f"A carregar {info['csv']} para a tabela {tabela} (Raw)...")
            
            cursor.execute(f"TRUNCATE TABLE {tabela} CASCADE;")
            conexao.commit()
            
            for chunk in pd.read_csv(caminho_csv, sep=CSV_SEPARADOR, encoding=CSV_ENCODING, dtype=str, chunksize=50000, low_memory=False):
                chunk = chunk.where(pd.notnull(chunk), None)
                
                output = StringIO()
                chunk.to_csv(output, sep='\t', index=False, header=False, na_rep='\\N')
                output.seek(0)
                
                cursor.copy_expert(f"COPY {tabela} FROM STDIN WITH CSV DELIMITER E'\\t' NULL '\\N'", output)
                conexao.commit()
                
            print(f"Tabela {tabela} carregada com sucesso!")
    finally:
        cursor.close()
        conexao.close()

if __name__ == "__main__":
    if extrair_zip_local():
        carregar_raw()
        print("Processo de carga Raw concluído com sucesso!")