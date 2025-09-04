import json

def analyze_driver_duplicates():
    # Ler o arquivo de dados adicionais
    with open('ADDITIONDATA', 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    driver_counts = {}
    driver_cancellations = {}
    
    print("=== ANÁLISE DE DRIVERS DUPLICADOS ===\n")
    
    for i, line in enumerate(lines[1:], 1):  # Pular o cabeçalho
        line = line.strip()
        if not line:
            continue
            
        try:
            data = json.loads(line)
            
            # Verificar se há cancelamentos
            driver_cancelled = 0
            user_cancelled = 0
            driver_id = ""
            driver_name = ""
            
            # Tentar diferentes formatos de chave
            if 'driver_cancelled_rides' in data:
                driver_cancelled = int(data['driver_cancelled_rides'])
            elif 'Driver Cancelled Rides' in data:
                driver_cancelled = int(data['Driver Cancelled Rides'])
                
            if 'user_cancelled_rides' in data:
                user_cancelled = int(data['user_cancelled_rides'])
            elif 'User Cancelled Rides' in data:
                user_cancelled = int(data['User Cancelled Rides'])
            
            driver_id = data.get('Driver ID', data.get('driver_id', f'Unknown_{i}'))
            driver_name = data.get('Driver Name', data.get('driver_name', f'Driver {i}'))
            
            # Contar ocorrências do driver
            if driver_id not in driver_counts:
                driver_counts[driver_id] = 0
                driver_cancellations[driver_id] = {
                    'name': driver_name,
                    'total_cancelled': 0,
                    'records': []
                }
            
            driver_counts[driver_id] += 1
            total_cancelled = driver_cancelled + user_cancelled
            driver_cancellations[driver_id]['total_cancelled'] += total_cancelled
            
            if total_cancelled > 0:
                driver_cancellations[driver_id]['records'].append({
                    'line': i,
                    'driver_cancelled': driver_cancelled,
                    'user_cancelled': user_cancelled
                })
                
        except json.JSONDecodeError as e:
            print(f"Erro ao processar linha {i}: {e}")
            continue
    
    print("=== DRIVERS COM MÚLTIPLOS REGISTROS ===")
    for driver_id, count in driver_counts.items():
        if count > 1:
            print(f"Driver {driver_id}: {count} registros")
            if driver_cancellations[driver_id]['total_cancelled'] > 0:
                print(f"  Nome: {driver_cancellations[driver_id]['name']}")
                print(f"  Total cancelamentos: {driver_cancellations[driver_id]['total_cancelled']}")
                for record in driver_cancellations[driver_id]['records']:
                    print(f"    Linha {record['line']}: {record['driver_cancelled']} + {record['user_cancelled']} = {record['driver_cancelled'] + record['user_cancelled']}")
            print()
    
    print("=== TODOS OS DRIVERS COM CANCELAMENTOS ===")
    total_all_cancellations = 0
    for driver_id, data in driver_cancellations.items():
        if data['total_cancelled'] > 0:
            print(f"Driver {driver_id} ({data['name']}): {data['total_cancelled']} cancelamentos")
            total_all_cancellations += data['total_cancelled']
    
    print(f"\nTOTAL GERAL DE CANCELAMENTOS: {total_all_cancellations}")

if __name__ == "__main__":
    analyze_driver_duplicates()
