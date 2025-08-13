#!/usr/bin/env python3
"""
Script para verificar se a tabela rides_data existe no PostgreSQL
"""

import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

# Carrega variáveis de ambiente
load_dotenv()

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://n8n_user:n8n_pw@148.230.73.27:5432/n8n_db"
).replace("postgresql+asyncpg://", "postgresql://")

def check_postgres_table():
    """Verifica se a tabela rides_data existe no PostgreSQL"""
    
    print("🔍 Verificando tabela rides_data no PostgreSQL...")
    print(f"🔗 Conectando em: {DATABASE_URL}")
    
    try:
        engine = create_engine(DATABASE_URL, echo=True)
        
        with engine.connect() as conn:
            # Listar todas as tabelas
            print("\n📋 Todas as tabelas no banco:")
            result = conn.execute(text("SELECT tablename FROM pg_tables WHERE schemaname = 'public'"))
            tables = result.fetchall()
            for table in tables:
                print(f"  - {table[0]}")
            
            # Verificar se rides_data existe
            result = conn.execute(text("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'rides_data')"))
            exists = result.fetchone()[0]
            
            if exists:
                print("\n✅ Tabela rides_data EXISTE!")
                
                # Contar registros
                result = conn.execute(text("SELECT COUNT(*) FROM rides_data"))
                count = result.fetchone()[0]
                print(f"📊 Total de registros: {count}")
                
                # Ver estrutura
                result = conn.execute(text("""
                    SELECT column_name, data_type 
                    FROM information_schema.columns 
                    WHERE table_name = 'rides_data'
                    ORDER BY ordinal_position
                """))
                columns = result.fetchall()
                print("\n🏗️ Estrutura da tabela:")
                for col in columns:
                    print(f"  - {col[0]}: {col[1]}")
                
                # Ver um registro exemplo
                result = conn.execute(text("SELECT table_name, data_hash, scraped_at, source FROM rides_data LIMIT 1"))
                sample = result.fetchone()
                if sample:
                    print(f"\n📝 Registro exemplo:")
                    print(f"  - table_name: {sample[0]}")
                    print(f"  - data_hash: {sample[1]}")
                    print(f"  - scraped_at: {sample[2]}")
                    print(f"  - source: {sample[3]}")
                
            else:
                print("\n❌ Tabela rides_data NÃO EXISTE!")
                
    except Exception as e:
        print(f"❌ Erro ao conectar: {e}")

if __name__ == "__main__":
    check_postgres_table()
