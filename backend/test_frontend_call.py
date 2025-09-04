import requests

def test_frontend_call():
    # Simular exatamente a chamada que o frontend faz
    print('🧪 Simulando chamada do frontend...')
    response = requests.get('http://localhost:8000/api/drivers/list?period=6_months&city=Guarantã do Norte&status=all&limit=50&offset=0')
    data = response.json()

    print(f'Status: {response.status_code}')
    print(f'Success: {data.get("success")}')

    if data.get('success'):
        drivers_info = data.get('data', {})
        print(f'Estrutura: {list(drivers_info.keys())}')
        drivers = drivers_info.get('drivers', [])
        print(f'Motoristas: {len(drivers)}')
        print(f'Total count: {drivers_info.get("total_count", "N/A")}')
        
        if drivers:
            print('\nPrimeiro motorista:')
            first_driver = drivers[0]
            print(f'  Nome: {first_driver.get("name")}')
            print(f'  Cidade: {first_driver.get("city")}')
            print(f'  Horas: {first_driver.get("hours_online")}')
            print(f'  Rating: {first_driver.get("rating")}')
            print(f'  Todas as chaves: {list(first_driver.keys())}')
    else:
        print(f'Erro na API: {data}')

if __name__ == "__main__":
    test_frontend_call()
