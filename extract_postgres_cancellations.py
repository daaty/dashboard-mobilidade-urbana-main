import psycopg2
import json
from datetime import datetime, timedelta

def extract_cancellations_from_postgres():
    """
    Conecta no PostgreSQL e extrai TODAS as corridas canceladas do additional_data
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
        
        print("=== EXTRAINDO TODOS OS CANCELAMENTOS ===")
        
        # Query simples: buscar TODOS os registros de drivers_data
        query = """
        SELECT driver_id, name, page_source, additional_data
        FROM drivers_data 
        WHERE additional_data IS NOT NULL
        """
        
        cursor.execute(query)
        results = cursor.fetchall()
        
        print(f"Total de registros encontrados: {len(results)}")
        
        total_driver_cancelled = 0
        total_user_cancelled = 0
        drivers_with_cancellations = []
        
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
                
                # Extrair cancelamentos - tentar diferentes formatos
                driver_cancelled = 0
                user_cancelled = 0
                
                # Formato 1: chaves minúsculas
                if 'driver_cancelled_rides' in data:
                    driver_cancelled = int(data.get('driver_cancelled_rides', 0))
                if 'user_cancelled_rides' in data:
                    user_cancelled = int(data.get('user_cancelled_rides', 0))
                
                # Formato 2: chaves com maiúsculas
                if driver_cancelled == 0 and 'Driver Cancelled Rides' in data:
                    driver_cancelled = int(data.get('Driver Cancelled Rides', 0))
                if user_cancelled == 0 and 'User Cancelled Rides' in data:
                    user_cancelled = int(data.get('User Cancelled Rides', 0))
                
                # Se há cancelamentos, registrar
                if driver_cancelled > 0 or user_cancelled > 0:
                    total_driver_cancelled += driver_cancelled
                    total_user_cancelled += user_cancelled
                    
                    drivers_with_cancellations.append({
                        'driver_id': driver_id,
                        'name': name,
                        'page_source': page_source,
                        'driver_cancelled': driver_cancelled,
                        'user_cancelled': user_cancelled,
                        'total_cancelled': driver_cancelled + user_cancelled
                    })
                    
                    print(f"CANCELAMENTO ENCONTRADO:")
                    print(f"  ID: {driver_id}")
                    print(f"  Nome: {name}")
                    print(f"  Page: {page_source}")
                    print(f"  Canceladas pelo motorista: {driver_cancelled}")
                    print(f"  Canceladas pelo usuário: {user_cancelled}")
                    print()
                    
            except (json.JSONDecodeError, ValueError, TypeError) as e:
                print(f"Erro ao processar driver {driver_id}: {e}")
                continue
        
        print("=== RESUMO FINAL ===")
        print(f"Total de cancelamentos pelo motorista: {total_driver_cancelled}")
        print(f"Total de cancelamentos pelo usuário: {total_user_cancelled}")
        print(f"TOTAL GERAL DE CANCELAMENTOS: {total_driver_cancelled + total_user_cancelled}")
        print(f"Drivers com cancelamentos: {len(drivers_with_cancellations)}")
        
        # Fechar conexão
        cursor.close()
        conn.close()
        
        return {
            'total_cancelled': total_driver_cancelled + total_user_cancelled,
            'driver_cancelled': total_driver_cancelled,
            'user_cancelled': total_user_cancelled,
            'drivers_count': len(drivers_with_cancellations)
        }
        
    except Exception as e:
        print(f"ERRO AO CONECTAR NO POSTGRESQL: {e}")
        return None

if __name__ == "__main__":
    result = extract_cancellations_from_postgres()
    if result:
        print(f"\n🎯 RESULTADO: {result['total_cancelled']} CORRIDAS CANCELADAS NO TOTAL!")
    else:
        print("❌ FALHA AO EXTRAIR DADOS!")
