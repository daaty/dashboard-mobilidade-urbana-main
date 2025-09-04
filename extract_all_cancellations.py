import sqlite3
import json

def extract_all_cancellations():
    print("=== EXTRAINDO TODAS AS CORRIDAS CANCELADAS DO ADDITIONAL_DATA ===\n")
    
    try:
        conn = sqlite3.connect('drivers_data.db')
        cursor = conn.cursor()
        
        # Buscar TODOS os registros com additional_data
        cursor.execute('SELECT driver_id, name, page_source, additional_data FROM drivers_data WHERE additional_data IS NOT NULL')
        all_records = cursor.fetchall()
        
        total_driver_cancelled = 0
        total_user_cancelled = 0
        records_with_cancellations = []
        
        print(f"Total de registros encontrados: {len(all_records)}\n")
        
        for i, record in enumerate(all_records):
            driver_id, name, page_source, additional_data_str = record
            
            try:
                # Parse do JSON
                additional_data = json.loads(additional_data_str)
                
                # Extrair cancelamentos - TODAS as possíveis variações
                driver_cancelled = 0
                user_cancelled = 0
                
                # Formato 1: snake_case
                if 'driver_cancelled_rides' in additional_data:
                    driver_cancelled = int(additional_data['driver_cancelled_rides'])
                if 'user_cancelled_rides' in additional_data:
                    user_cancelled = int(additional_data['user_cancelled_rides'])
                
                # Formato 2: Title Case
                if 'Driver Cancelled Rides' in additional_data:
                    driver_cancelled = int(additional_data['Driver Cancelled Rides'])
                if 'User Cancelled Rides' in additional_data:
                    user_cancelled = int(additional_data['User Cancelled Rides'])
                
                # Se há cancelamentos, mostrar
                if driver_cancelled > 0 or user_cancelled > 0:
                    print(f"REGISTRO {i+1}:")
                    print(f"  Driver ID: {driver_id}")
                    print(f"  Nome: {name}")
                    print(f"  Page Source: {page_source}")
                    print(f"  Driver Cancelled: {driver_cancelled}")
                    print(f"  User Cancelled: {user_cancelled}")
                    print(f"  Total Cancelled: {driver_cancelled + user_cancelled}")
                    print()
                    
                    total_driver_cancelled += driver_cancelled
                    total_user_cancelled += user_cancelled
                    
                    records_with_cancellations.append({
                        'driver_id': driver_id,
                        'name': name,
                        'page_source': page_source,
                        'driver_cancelled': driver_cancelled,
                        'user_cancelled': user_cancelled
                    })
                    
            except json.JSONDecodeError as e:
                print(f"ERRO JSON no registro {i+1} (Driver ID: {driver_id}): {e}")
                continue
            except Exception as e:
                print(f"ERRO no registro {i+1} (Driver ID: {driver_id}): {e}")
                continue
        
        print("=== RESUMO FINAL ===")
        print(f"Total de registros com cancelamentos: {len(records_with_cancellations)}")
        print(f"Total driver cancelled: {total_driver_cancelled}")
        print(f"Total user cancelled: {total_user_cancelled}")
        print(f"TOTAL GERAL CANCELADAS: {total_driver_cancelled + total_user_cancelled}")
        
        conn.close()
        
    except Exception as e:
        print(f"ERRO GERAL: {e}")

if __name__ == "__main__":
    extract_all_cancellations()
