import psycopg2
import json
import os
from dotenv import load_dotenv

# Carregar variáveis do .env
load_dotenv('backend/.env')

def check_hours_data():
    """
    Verifica quais dados de horas estão disponíveis no additional_data
    """
    
    DB_CONFIG = {
        'host': os.getenv('DB_HOST'),
        'port': int(os.getenv('DB_PORT')),
        'database': os.getenv('DB_NAME'),
        'user': os.getenv('DB_USER'),
        'password': os.getenv('DB_PASSWORD')
    }
    
    try:
        print("=== VERIFICANDO DADOS DE HORAS ===")
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Buscar registros de Driver Performance especificamente
        query = """
        SELECT driver_id, name, additional_data, page_source
        FROM drivers_data 
        WHERE additional_data IS NOT NULL
        AND page_source = 'Driver Performance'
        LIMIT 5
        """
        
        cursor.execute(query)
        results = cursor.fetchall()
        
        print(f"Analisando {len(results)} registros para buscar dados de horas:")
        
        hours_keys_found = set()
        
        for row in results:
            driver_id, name, additional_data, page_source = row
            
            if isinstance(additional_data, dict):
                data = additional_data
            elif isinstance(additional_data, str):
                try:
                    data = json.loads(additional_data)
                except:
                    continue
            else:
                continue
                
            print(f"\n📋 Driver: {name} ({driver_id}) - Page: {page_source}")
            
            # Procurar chaves relacionadas a horas
            hour_related_keys = [k for k in data.keys() if 'hour' in k.lower() or 'time' in k.lower() or 'online' in k.lower()]
            
            if hour_related_keys:
                print(f"   Chaves relacionadas a horas: {hour_related_keys}")
                for key in hour_related_keys:
                    print(f"   {key}: {data[key]}")
                    hours_keys_found.add(key)
            else:
                print("   Nenhuma chave relacionada a horas encontrada")
        
        print(f"\n=== RESUMO ===")
        print(f"Chaves de horas encontradas em todos os registros: {list(hours_keys_found)}")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"ERRO: {e}")

if __name__ == "__main__":
    check_hours_data()
