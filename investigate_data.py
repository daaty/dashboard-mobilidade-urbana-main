import psycopg2
import json
import os
from dotenv import load_dotenv

# Carregar variáveis do .env
load_dotenv('backend/.env')

def investigate_data_format():
    """
    Investiga o formato real dos dados no PostgreSQL
    """
    
    DB_CONFIG = {
        'host': os.getenv('DB_HOST'),
        'port': int(os.getenv('DB_PORT')),
        'database': os.getenv('DB_NAME'),
        'user': os.getenv('DB_USER'),
        'password': os.getenv('DB_PASSWORD')
    }
    
    try:
        print("=== INVESTIGANDO FORMATO DOS DADOS ===")
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Buscar apenas 1 registro para investigar
        query = """
        SELECT driver_id, name, additional_data, page_source
        FROM drivers_data 
        WHERE page_source = 'Active Drivers' 
        AND driver_id = '17177142'
        LIMIT 1
        """
        
        cursor.execute(query)
        result = cursor.fetchone()
        
        if result:
            driver_id, name, additional_data, page_source = result
            
            print(f"Driver: {name} ({driver_id})")
            print(f"Page source: {page_source}")
            print(f"Tipo do additional_data: {type(additional_data)}")
            print(f"Additional data raw: {repr(additional_data)}")
            
            if isinstance(additional_data, dict):
                print("É um dicionário Python!")
                print(f"Chaves: {list(additional_data.keys())}")
                if 'Driver Ratings' in additional_data:
                    print(f"Driver Ratings: {additional_data['Driver Ratings']}")
            elif isinstance(additional_data, str):
                print("É uma string, tentando JSON parse...")
                try:
                    parsed = json.loads(additional_data)
                    print("JSON válido!")
                    print(f"Chaves: {list(parsed.keys())}")
                except:
                    print("Não é JSON válido!")
            else:
                print("Tipo desconhecido!")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"ERRO: {e}")

if __name__ == "__main__":
    investigate_data_format()
