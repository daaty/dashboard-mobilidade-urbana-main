import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    print("❌ DATABASE_URL não encontrada no .env!")
    exit(1)
if DATABASE_URL.startswith("postgresql+asyncpg"):
    DATABASE_URL = DATABASE_URL.replace("postgresql+asyncpg", "postgresql")

try:
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    print("\n📋 TABELA fases_planejamento:")
    cur.execute("SELECT * FROM fases_planejamento LIMIT 5;")
    for row in cur.fetchall():
        print(row)
    print("\n📋 TABELA metas_progressivas:")
    cur.execute("SELECT * FROM metas_progressivas LIMIT 5;")
    for row in cur.fetchall():
        print(row)
    cur.close()
    conn.close()
except Exception as e:
    print(f"❌ Erro ao consultar tabelas: {e}")
