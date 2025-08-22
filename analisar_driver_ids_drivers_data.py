import psycopg2
import json
from collections import Counter

def analisar_driver_ids():
    try:
        # Conectar ao banco
        conn = psycopg2.connect(
            host="148.230.73.27",
            database="n8n_db", 
            user="n8n_user",
            password="n8n_pw",
            port=5432
        )
        cursor = conn.cursor()
        
        # Buscar todos os driver_ids
        cursor.execute("""
            SELECT driver_id, COUNT(*) as count
            FROM drivers_data 
            GROUP BY driver_id
            ORDER BY count DESC, driver_id
        """)
        
        rows = cursor.fetchall()
        
        print(f"=== ANÁLISE DOS DRIVER_IDS NA TABELA DRIVERS_DATA ===")
        print(f"Total de driver_ids únicos: {len(rows)}")
        print()
        
        # Mostrar todos os driver_ids e suas contagens
        total_registros = 0
        for driver_id, count in rows:
            total_registros += count
            print(f"driver_id: '{driver_id}' - {count} registro(s)")
        
        print(f"\nTotal de registros na tabela: {total_registros}")
        
        # Verificar quantos são válidos (não são "0", "1", etc.)
        driver_ids_validos = [driver_id for driver_id, count in rows 
                             if driver_id and len(str(driver_id)) > 1 and str(driver_id) not in ['0', '1', 'None']]
        
        print(f"\nDriver_ids válidos (não são '0', '1', etc.): {len(driver_ids_validos)}")
        for driver_id in driver_ids_validos:
            print(f"- {driver_id}")
        
        # Buscar detalhes dos registros para entender melhor
        print(f"\n=== DETALHES DOS REGISTROS ===")
        cursor.execute("""
            SELECT id, driver_id, name, mobile, data_type
            FROM drivers_data 
            ORDER BY id
        """)
        
        all_rows = cursor.fetchall()
        for row in all_rows:
            id_reg, driver_id, name, mobile, data_type = row
            print(f"ID {id_reg:2d}: driver_id='{driver_id}' | name='{name}' | mobile='{mobile}' | type={data_type}")
        
        conn.close()
        
    except Exception as e:
        print(f"Erro: {e}")

if __name__ == "__main__":
    analisar_driver_ids()
