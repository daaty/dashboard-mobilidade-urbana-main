import psycopg2
import json

def extract_ratings_from_postgres():
    """
    Conecta no PostgreSQL e extrai TODOS os ratings dos motoristas
    """
    
    # Configurações do banco (do .env)
    DB_CONFIG = {
        'host': '148.230.73.27',
        'port': 5432,
        'database': 'n8n_db',
        'user': 'n8n_user',
        'password': 'n8n_pw'
    }
    
    try:
        print("=== CONECTANDO NO POSTGRESQL ===")
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        print("=== EXTRAINDO TODOS OS RATINGS ===")
        
        # Query simples: buscar TODOS os registros de drivers_data
        query = """
        SELECT driver_id, name, page_source, additional_data
        FROM drivers_data 
        WHERE additional_data IS NOT NULL
        """
        
        cursor.execute(query)
        results = cursor.fetchall()
        
        print(f"Total de registros encontrados: {len(results)}")
        
        ratings_found = []
        
        for row in results:
            driver_id, name, page_source, additional_data = row
            
            if not additional_data:
                continue
                
            try:
                # Se additional_data for string, fazer parse JSON
                if isinstance(additional_data, str):
                    data = json.loads(additional_data)
                else:
                    data = additional_data
                
                # Procurar ratings em diferentes formatos
                rating = None
                
                # Formato 1: "Driver Ratings"
                if 'Driver Ratings' in data:
                    rating_str = data['Driver Ratings']
                    if rating_str and rating_str != '--' and rating_str != 'N/A':
                        try:
                            rating = float(rating_str)
                        except:
                            pass
                
                # Formato 2: "driver_ratings"
                if not rating and 'driver_ratings' in data:
                    rating_str = data['driver_ratings']
                    if rating_str and rating_str != '--' and rating_str != 'N/A':
                        try:
                            rating = float(rating_str)
                        except:
                            pass
                
                # Formato 3: "rating"
                if not rating and 'rating' in data:
                    rating_str = data['rating']
                    if rating_str and rating_str != '--' and rating_str != 'N/A':
                        try:
                            rating = float(rating_str)
                        except:
                            pass
                
                # Se encontrou rating válido
                if rating and 0 <= rating <= 5:
                    ratings_found.append({
                        'driver_id': driver_id,
                        'name': name,
                        'page_source': page_source,
                        'rating': rating
                    })
                    
                    print(f"RATING ENCONTRADO:")
                    print(f"  ID: {driver_id}")
                    print(f"  Nome: {name}")
                    print(f"  Page: {page_source}")
                    print(f"  Rating: {rating}")
                    print()
                    
            except (json.JSONDecodeError, ValueError, TypeError) as e:
                continue
        
        print("=== RESUMO DOS RATINGS ===")
        print(f"Total de ratings encontrados: {len(ratings_found)}")
        
        if ratings_found:
            # Distribuição
            excellent = len([r for r in ratings_found if r['rating'] >= 4.5])
            good = len([r for r in ratings_found if 4.0 <= r['rating'] < 4.5])
            average = len([r for r in ratings_found if 3.5 <= r['rating'] < 4.0])
            below = len([r for r in ratings_found if r['rating'] < 3.5])
            
            print(f"Excelente (≥4.5): {excellent}")
            print(f"Bom (4.0-4.4): {good}")
            print(f"Médio (3.5-3.9): {average}")
            print(f"Abaixo (<3.5): {below}")
            
            avg_rating = sum([r['rating'] for r in ratings_found]) / len(ratings_found)
            print(f"Rating médio: {avg_rating:.2f}")
        
        # Fechar conexão
        cursor.close()
        conn.close()
        
        return ratings_found
        
    except Exception as e:
        print(f"ERRO AO CONECTAR NO POSTGRESQL: {e}")
        return None

if __name__ == "__main__":
    ratings = extract_ratings_from_postgres()
    if ratings:
        print(f"\n🎯 RESULTADO: {len(ratings)} RATINGS ENCONTRADOS!")
    else:
        print("❌ NENHUM RATING ENCONTRADO!")
