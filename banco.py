import psycopg2
from psycopg2 import Error
from config import POSTGRES_CONFIG

def conectar():
    try:
        return psycopg2.connect(**POSTGRES_CONFIG)
    except (Error, UnicodeDecodeError) as erro:
        raise RuntimeError(
            f"Não foi possível conectar ao PostgreSQL em "
            f"{POSTGRES_CONFIG['host']}:{POSTGRES_CONFIG['port']} / database "
            f"'{POSTGRES_CONFIG['dbname']}'. Verifique o .env e se rodou "
            f"o script '0_criar_banco.sql'. Detalhe: {erro}"
        )