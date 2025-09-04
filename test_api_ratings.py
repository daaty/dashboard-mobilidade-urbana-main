import psycopg2
import json
import os
from dotenv import load_dotenv

# Carregar variáveis do .env
load_dotenv('backend/.env')

def test_ratings_extraction():
    """
    Testa a extração de ratings usando a mesma conexão da API
    """
    
    # Usar as mesmas configurações da API
    DB_CONFIG = {
        'host': os.getenv('DB_HOST'),
        'port': int(os.getenv('DB_PORT')),
        'database': os.getenv('DB_NAME'),
        'user': os.getenv('DB_USER'),
        'password': os.getenv('DB_PASSWORD')
    }
    
    try:
        print("=== TESTANDO EXTRAÇÃO DE RATINGS (MESMA LÓGICA DA API) ===")
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # TESTAR QUERY SIMPLES - APENAS Active Drivers
        simple_query = """
        SELECT 
            driver_id, name, additional_data, page_source
        FROM drivers_data 
        WHERE page_source = 'Active Drivers'
        """
        
        cursor.execute(simple_query)
        results = cursor.fetchall()
        
        print(f"Total de drivers únicos: {len(results)}")
        
        ratings = []
        debug_count = 0
        
        for row in results:
            driver_id, name, additional_data_str, page_source = row
            
            debug_count += 1
            if debug_count <= 3:  # Mostrar primeiros 3 para debug
                print(f"DEBUG Driver {debug_count}: {name} ({driver_id})")
                if additional_data_str:
                    try:
                        data = json.loads(additional_data_str)
                        rating_keys = [k for k in data.keys() if 'rating' in k.lower()]
                        print(f"  Rating keys: {rating_keys}")
                        if 'Driver Ratings' in data:
                            print(f"  Driver Ratings: {data['Driver Ratings']}")
                    except:
                        print(f"  Erro no JSON")
            
            if not additional_data_str:
                continue
                
            try:
                # CORRIGIR: additional_data pode já ser um dicionário
                if isinstance(additional_data_str, dict):
                    additional_data = additional_data_str
                elif isinstance(additional_data_str, str):
                    additional_data = json.loads(additional_data_str)
                else:
                    continue
                
                # APLICAR MESMA LÓGICA DO SCRIPT
                driver_rating = None
                
                # Formato 1: "Driver Ratings"
                if 'Driver Ratings' in additional_data:
                    rating_str = additional_data['Driver Ratings']
                    if rating_str and rating_str != '--' and rating_str != 'N/A':
                        try:
                            driver_rating = float(rating_str)
                        except:
                            pass
                
                # Formato 2: "driver_ratings"
                if not driver_rating and 'driver_ratings' in additional_data:
                    rating_str = additional_data['driver_ratings']
                    if rating_str and rating_str != '--' and rating_str != 'N/A':
                        try:
                            driver_rating = float(rating_str)
                        except:
                            pass
                
                # Formato 3: "rating"
                if not driver_rating and 'rating' in additional_data:
                    rating_str = additional_data['rating']
                    if rating_str and rating_str != '--' and rating_str != 'N/A':
                        try:
                            driver_rating = float(rating_str)
                        except:
                            pass
                
                # Se encontrou rating válido
                if driver_rating and 0 <= driver_rating <= 5:
                    ratings.append(driver_rating)
                    print(f"Rating encontrado: {name} ({driver_id}) - {driver_rating} - Page: {page_source}")
                    
            except (json.JSONDecodeError, ValueError, TypeError) as e:
                continue
        
        print(f"\n=== RESULTADO ===")
        print(f"Total de ratings extraídos: {len(ratings)}")
        
        if ratings:
            # Calcular distribuição
            excellent = len([r for r in ratings if r >= 4.5])
            good = len([r for r in ratings if 4.0 <= r < 4.5])
            average = len([r for r in ratings if 3.5 <= r < 4.0])
            below = len([r for r in ratings if r < 3.5])
            
            print(f"Excelente (≥4.5): {excellent}")
            print(f"Bom (4.0-4.4): {good}")
            print(f"Médio (3.5-3.9): {average}")
            print(f"Abaixo (<3.5): {below}")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"ERRO: {e}")

if __name__ == "__main__":
    test_ratings_extraction()
