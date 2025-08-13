import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

def main():
    try:
        # Conectar diretamente ao PostgreSQL
        conn = psycopg2.connect(
            host=os.getenv("DB_HOST", "localhost"),
            database=os.getenv("DB_NAME", "mobilidade_urbana"),
            user=os.getenv("DB_USER", "postgres"),
            password=os.getenv("DB_PASSWORD", "123456"),
            port=os.getenv("DB_PORT", "5432")
        )
        cursor = conn.cursor()
        
        # Verificar se a tabela existe
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'rides_data'
            );
        """)
        table_exists = cursor.fetchone()[0]
        print(f"Tabela rides_data existe: {table_exists}")
        
        if table_exists:
            # Contar registros totais
            cursor.execute("SELECT COUNT(*) FROM rides_data;")
            total = cursor.fetchone()[0]
            print(f"Total de registros: {total}")
            
            # Contar por table_name
            cursor.execute("""
                SELECT table_name, COUNT(*) 
                FROM rides_data 
                GROUP BY table_name;
            """)
            results = cursor.fetchall()
            print("\nRegistros por tipo:")
            for table_name, count in results:
                print(f"  {table_name}: {count}")
            
            # Mostrar algumas colunas dos primeiros registros
            cursor.execute("""
                SELECT id, table_name, created_at, fare 
                FROM rides_data 
                ORDER BY created_at DESC 
                LIMIT 5;
            """)
            recent = cursor.fetchall()
            print("\nÚltimos 5 registros:")
            for record in recent:
                print(f"  ID: {record[0]}, Type: {record[1]}, Created: {record[2]}, Fare: {record[3]}")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"Erro ao conectar ao banco: {e}")

if __name__ == "__main__":
    main()
