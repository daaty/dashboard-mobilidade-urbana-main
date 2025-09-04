import psycopg2
import json
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

def check_drivers_tables():
    try:
        # Configuração do PostgreSQL
        conn = psycopg2.connect(
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT"),
            database=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD")
        )
        
        cursor = conn.cursor()
        
        print("🔍 Verificando tabelas de motoristas no PostgreSQL...")
        print(f"🔗 Conectando em: postgresql://{os.getenv('DB_USER')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}")
        
        # Verificar se as tabelas existem
        tables_to_check = ['drivers_data', 'driver_personal_details']
        
        for table in tables_to_check:
            print(f"\n📋 Analisando tabela: {table}")
            
            # Verificar se existe
            cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = %s
                )
            """, (table,))
            
            exists = cursor.fetchone()[0]
            
            if exists:
                print(f"✅ Tabela {table} EXISTE!")
                
                # Contar registros
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                print(f"📊 Total de registros: {count}")
                
                # Ver estrutura
                cursor.execute("""
                    SELECT column_name, data_type
                    FROM information_schema.columns
                    WHERE table_name = %s
                    ORDER BY ordinal_position
                """, (table,))
                
                columns = cursor.fetchall()
                print("🏗️ Estrutura da tabela:")
                for col_name, col_type in columns:
                    print(f"  - {col_name}: {col_type}")
                
                # Ver alguns registros exemplo
                if count > 0:
                    cursor.execute(f"SELECT * FROM {table} LIMIT 2")
                    rows = cursor.fetchall()
                    
                    print("\n📝 Registros exemplo:")
                    for i, row in enumerate(rows, 1):
                        print(f"  Registro {i}:")
                        for j, (col_name, _) in enumerate(columns):
                            value = row[j]
                            if isinstance(value, str) and len(str(value)) > 100:
                                value = str(value)[:100] + "..."
                            print(f"    {col_name}: {value}")
            else:
                print(f"❌ Tabela {table} NÃO EXISTE!")
        
        # Verificar se há dados JSON na tabela drivers_data
        print("\n🔍 Analisando dados JSON na tabela drivers_data...")
        cursor.execute("SELECT id, data_hash, driver_data FROM drivers_data LIMIT 1")
        row = cursor.fetchone()
        
        if row:
            print(f"📄 Exemplo de dados JSON:")
            try:
                driver_data = json.loads(row[2])
                print(f"  - ID: {row[0]}")
                print(f"  - Hash: {row[1]}")
                print(f"  - Estrutura JSON (chaves): {list(driver_data.keys())}")
                
                # Mostrar um exemplo de motorista
                if isinstance(driver_data, list) and len(driver_data) > 0:
                    print(f"  - Exemplo motorista: {list(driver_data[0].keys())}")
                elif isinstance(driver_data, dict):
                    print(f"  - Dados do motorista: {list(driver_data.keys())}")
                    
            except json.JSONDecodeError as e:
                print(f"  ❌ Erro ao decodificar JSON: {e}")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    check_drivers_tables()
