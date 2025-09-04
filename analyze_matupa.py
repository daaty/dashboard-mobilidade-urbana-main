import json

def analyze_matupa_drivers():
    # Ler o arquivo de dados adicionais
    with open('ADDITIONDATA', 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    matupa_drivers = []
    total_cancelled = 0
    
    print("=== ANÁLISE DOS MOTORISTAS DE MATUPÁ ===\n")
    
    for i, line in enumerate(lines[1:], 1):  # Pular o cabeçalho
        line = line.strip()
        if not line:
            continue
            
        try:
            data = json.loads(line)
            
            # Verificar se há cancelamentos
            driver_cancelled = 0
            user_cancelled = 0
            city = ""
            
            # Tentar diferentes formatos de chave
            if 'driver_cancelled_rides' in data:
                driver_cancelled = int(data['driver_cancelled_rides'])
            elif 'Driver Cancelled Rides' in data:
                driver_cancelled = int(data['Driver Cancelled Rides'])
                
            if 'user_cancelled_rides' in data:
                user_cancelled = int(data['user_cancelled_rides'])
            elif 'User Cancelled Rides' in data:
                user_cancelled = int(data['User Cancelled Rides'])
            
            # Verificar se tem city
            if 'city' in data:
                city = data['city']
            elif 'City' in data:
                city = data['City']
            
            # Se há cancelamentos, verificar se é de Matupá
            if driver_cancelled > 0 or user_cancelled > 0:
                driver_name = data.get('Driver Name', data.get('driver_name', f'Driver {i}'))
                driver_id = data.get('Driver ID', data.get('driver_id', 'N/A'))
                
                print(f"Driver com cancelamentos: {driver_name} (ID: {driver_id})")
                print(f"  Cidade: '{city}'")
                print(f"  Corridas canceladas pelo motorista: {driver_cancelled}")
                print(f"  Corridas canceladas pelo usuário: {user_cancelled}")
                print()
                
                if city.lower() == "matupá" or "matupá" in city.lower():
                    matupa_drivers.append({
                        'name': driver_name,
                        'id': driver_id,
                        'cancelled': driver_cancelled + user_cancelled
                    })
                    total_cancelled += driver_cancelled + user_cancelled
                
        except json.JSONDecodeError as e:
            print(f"Erro ao processar linha {i}: {e}")
            continue
    
    print("=== MOTORISTAS DE MATUPÁ COM CANCELAMENTOS ===")
    print(f"Total encontrados: {len(matupa_drivers)}")
    print(f"Total de cancelamentos: {total_cancelled}")
    
    for driver in matupa_drivers:
        print(f"- {driver['name']} (ID: {driver['id']}): {driver['cancelled']} cancelamentos")

if __name__ == "__main__":
    analyze_matupa_drivers()
