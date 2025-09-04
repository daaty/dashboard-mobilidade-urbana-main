import requests
import json

def test_vehicle_data():
    print('🧪 Testando dados de veículos - Guarantã do Norte...')
    response = requests.get('http://localhost:8000/api/drivers/list?period=6_months&city=Guarantã do Norte&status=all&limit=50&offset=0')
    data = response.json()

    if data.get('success'):
        drivers_data = data.get('data', {})
        drivers = drivers_data.get('drivers', [])
        print(f'Motoristas encontrados: {len(drivers)}')
        
        vehicle_stats = {}
        
        for i, driver in enumerate(drivers[:3]):  # Testar primeiros 3
            name = driver.get('name', 'N/A')
            
            # Verificar dados pessoais
            personal_data_raw = driver.get('data', {}).get('personal_data')
            vehicle_type = 'Não especificado'
            
            print(f'\n{i+1}. {name}:')
            print(f'   Personal data existe: {personal_data_raw is not None}')
            
            if personal_data_raw:
                try:
                    personal_data = json.loads(personal_data_raw) if isinstance(personal_data_raw, str) else personal_data_raw
                    vehicle_type = personal_data.get('vehicle_type', 'Não especificado')
                    vehicle_no = personal_data.get('vehicle_no', 'N/A')
                    print(f'   Vehicle type: {vehicle_type}')
                    print(f'   Vehicle no: {vehicle_no}')
                except Exception as e:
                    print(f'   Erro ao processar personal_data: {e}')
            
            # Contar veículos
            if vehicle_type not in vehicle_stats:
                vehicle_stats[vehicle_type] = 0
            vehicle_stats[vehicle_type] += 1
        
        print(f'\n📊 Resumo dos tipos de veículos:')
        for vehicle, count in vehicle_stats.items():
            print(f'   {vehicle}: {count} motoristas')
    else:
        print(f'Erro: {data}')

if __name__ == "__main__":
    test_vehicle_data()
