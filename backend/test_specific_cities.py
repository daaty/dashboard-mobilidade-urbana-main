import requests

def test_specific_cities():
    # Teste Guarantã do Norte
    print('🧪 Testando Guarantã do Norte...')
    response = requests.get('http://localhost:8000/api/drivers/kpis?period=30_days&city=Guarantã do Norte&status=all')
    data = response.json()
    if data.get('success'):
        print(f'Motoristas: {data["data"]["total_drivers"]}')
        print(f'Corridas: {data["data"]["total_rides"]}')
    else:
        print('Erro ou sem dados')

    print()

    # Teste Matupá  
    print('🧪 Testando Matupá...')
    response2 = requests.get('http://localhost:8000/api/drivers/kpis?period=30_days&city=Matupá&status=all')
    data2 = response2.json()
    if data2.get('success'):
        print(f'Motoristas: {data2["data"]["total_drivers"]}')
        print(f'Corridas: {data2["data"]["total_rides"]}')
    else:
        print('Erro ou sem dados')

if __name__ == "__main__":
    test_specific_cities()
