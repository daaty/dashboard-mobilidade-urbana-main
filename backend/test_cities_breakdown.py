import requests

def test_all_cities_breakdown():
    # Teste todas as cidades individualmente
    cities = ["all", "Guarantã do Norte", "Matupá", "Bandeirantes", "Nova Monte Verde"]
    
    total_from_individual = 0
    
    for city in cities:
        print(f'🧪 Testando {city}...')
        response = requests.get(f'http://localhost:8000/api/drivers/kpis?period=6_months&city={city}&status=all')
        data = response.json()
        
        if data.get('success'):
            rides = data["data"]["total_rides"]
            drivers = data["data"]["total_drivers"]
            avg_per_driver = rides / drivers if drivers > 0 else 0
            
            print(f'  Motoristas: {drivers}')
            print(f'  Corridas: {rides}')
            print(f'  Média por motorista: {avg_per_driver:.1f}')
            
            if city != "all":
                total_from_individual += rides
        else:
            print(f'  Erro: {data}')
        print()
    
    print(f'📊 RESUMO:')
    print(f'Total das cidades individuais: {total_from_individual}')
    print(f'Total "all": {rides if cities[0] == "all" else "N/A"}')
    print(f'Diferença: {121 - total_from_individual} corridas')

if __name__ == "__main__":
    test_all_cities_breakdown()
