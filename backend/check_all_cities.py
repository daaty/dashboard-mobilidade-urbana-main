import requests

def check_all_cities():
    response = requests.get('http://localhost:8000/api/drivers/cities')
    data = response.json()
    
    print('🏙️ Todas as cidades na base:')
    total_cities_count = 0
    
    for city in data.get('data', []):
        name = city.get('name', 'N/A')
        count = city.get('count', 0)
        total_cities_count += count
        print(f'- {name} ({count} motoristas)')
    
    print(f'\nTotal de motoristas pelas cidades: {total_cities_count}')
    
    # Agora testar cada cidade individualmente para encontrar a corrida perdida
    print('\n🔍 Testando cada cidade para encontrar a corrida perdida:')
    total_rides_from_cities = 0
    
    for city in data.get('data', []):
        city_name = city.get('name', '')
        if city_name and city_name != 'N/A':
            response2 = requests.get(f'http://localhost:8000/api/drivers/kpis?period=6_months&city={city_name}&status=all')
            data2 = response2.json()
            
            if data2.get('success'):
                rides = data2["data"]["total_rides"]
                total_rides_from_cities += rides
                if rides > 0:
                    print(f'  {city_name}: {rides} corridas')
    
    print(f'\nTotal de corridas das cidades: {total_rides_from_cities}')
    print(f'Total esperado: 121')
    print(f'Diferença: {121 - total_rides_from_cities}')

if __name__ == "__main__":
    check_all_cities()
