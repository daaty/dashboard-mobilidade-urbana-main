import requests
import json

def test_city_filter():
    print('🧪 Testando filtro de cidade Nova Monte Verde...')
    
    # Teste com cidade específica
    response = requests.get('http://localhost:8000/api/drivers/list?period=30_days&city=Nova Monte Verde&status=all')
    data = response.json()
    
    print(f'Status: {response.status_code}')
    
    if data.get('success'):
        drivers_data = data.get('data', {})
        drivers = drivers_data.get('drivers', [])
        print(f'Motoristas encontrados em Nova Monte Verde: {len(drivers)}')
        
        for driver in drivers[:3]:
            name = driver.get('name', 'N/A')
            city = driver.get('city', 'N/A')
            hours = driver.get('hours_online', 0)
            print(f'- {name} | Cidade: {city} | Horas: {hours}h')
    else:
        print(f'Erro: {data}')
    
    print('\n🧪 Testando filtro com todas as cidades...')
    
    # Teste com todas as cidades
    response2 = requests.get('http://localhost:8000/api/drivers/list?period=30_days&city=all&status=all')
    data2 = response2.json()
    
    print(f'Status: {response2.status_code}')
    
    if data2.get('success'):
        drivers_data2 = data2.get('data', {})
        drivers2 = drivers_data2.get('drivers', [])
        print(f'Motoristas encontrados (todas as cidades): {len(drivers2)}')
    else:
        print(f'Erro: {data2}')

if __name__ == "__main__":
    test_city_filter()
