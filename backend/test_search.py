import requests
import json

def test_passenger_search():
    base_url = "http://localhost:8000/api/passengers"
    
    print("=== TESTANDO BUSCA DE PASSAGEIROS ===\n")
    
    # Teste 1: Sem filtros
    print("1. 🔍 TESTE SEM FILTROS (limit=3)")
    response = requests.get(f"{base_url}/list?limit=3")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Retornou {len(data)} passageiros")
        for p in data:
            print(f"   - {p['user_name']} (ID: {p['passenger_id']})")
    else:
        print(f"❌ Erro {response.status_code}: {response.text}")
    
    print("\n" + "-"*50 + "\n")
    
    # Teste 2: Busca por "halef" (minúsculo)
    print("2. 🔍 TESTE BUSCA: 'halef'")
    response = requests.get(f"{base_url}/list?search=halef&limit=50")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Retornou {len(data)} passageiros")
        for p in data:
            print(f"   - {p['user_name']} (ID: {p['passenger_id']}) - {p['city']}")
    else:
        print(f"❌ Erro {response.status_code}: {response.text}")
    
    print("\n" + "-"*50 + "\n")
    
    # Teste 3: Busca por "Halef" (maiúsculo)  
    print("3. 🔍 TESTE BUSCA: 'Halef'")
    response = requests.get(f"{base_url}/list?search=Halef&limit=50")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Retornou {len(data)} passageiros")
        for p in data:
            print(f"   - {p['user_name']} (ID: {p['passenger_id']}) - {p['city']}")
    else:
        print(f"❌ Erro {response.status_code}: {response.text}")
    
    print("\n" + "-"*50 + "\n")
    
    # Teste 4: Buscar todos e verificar se Halef está lá
    print("4. 🔍 BUSCANDO TODOS OS PASSAGEIROS (limit=100)")
    response = requests.get(f"{base_url}/list?limit=100")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Total de passageiros: {len(data)}")
        
        # Procurar por Halef manualmente
        halef_passengers = [p for p in data if p['user_name'] and 'halef' in p['user_name'].lower()]
        
        if halef_passengers:
            print(f"🎯 ENCONTRADOS {len(halef_passengers)} passageiros com 'Halef':")
            for p in halef_passengers:
                print(f"   - {p['user_name']} (ID: {p['passenger_id']}) - {p['city']} - Status: {p['status']}")
        else:
            print("❌ Nenhum passageiro 'Halef' encontrado na lista")
            
        # Mostrar alguns nomes para debug
        print(f"\n📋 Primeiros 5 nomes da lista:")
        for i, p in enumerate(data[:5]):
            print(f"   {i+1}. {p['user_name']} (ID: {p['passenger_id']})")
            
    else:
        print(f"❌ Erro {response.status_code}: {response.text}")

if __name__ == "__main__":
    test_passenger_search()