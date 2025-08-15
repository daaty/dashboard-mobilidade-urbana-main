import os
import psycopg2
from dotenv import load_dotenv

# Carregar variáveis do .env
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    print("❌ DATABASE_URL não encontrada no .env!")
    exit(1)

# Ajustar string para psycopg2 se necessário
if DATABASE_URL.startswith("postgresql+asyncpg"):
    DATABASE_URL = DATABASE_URL.replace("postgresql+asyncpg", "postgresql")

print(f"🔗 Usando string de conexão: {DATABASE_URL}")

try:
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    print("🏗️ Conexão estabelecida com sucesso!")
    # Teste simples: listar tabelas
    cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';")
    tabelas = cur.fetchall()
    print(f"📋 Tabelas existentes: {[t[0] for t in tabelas]}")
    cur.close()
    conn.close()
    print("✅ Teste de conexão finalizado!")
except Exception as e:
    print(f"❌ Erro ao conectar: {e}")
