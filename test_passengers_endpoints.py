#!/usr/bin/env python3
"""
Script para testar os novos endpoints de passageiros
"""
import requests
import json

# Base URL da API
BASE_URL = "http://localhost:8000/api"

def test_passengers_endpoints():
    """Testa todos os novos endpoints de passageiros"""
    endpoints_to_test = [
        {
            "name": "KPIs dos Passageiros",
            "url": f"{BASE_URL}/passengers/kpis",
            "params": {"period": "3_months", "city": "all"}
        },
        {
            "name": "Distribuição por Cidade",
            "url": f"{BASE_URL}/passengers/by-city",
            "params": {"period": "3_months"}
        },
        {
            "name": "Lista de Passageiros",
            "url": f"{BASE_URL}/passengers/list",
            "params": {"limit": 10, "city": "all", "order_by": "rides_count"}
        },
        {
            "name": "Top Performers",
            "url": f"{BASE_URL}/passengers/top-performers",
            "params": {"metric": "rides", "limit": 5, "period": "3_months"}
        },
        {
            "name": "Analytics Avançados",
            "url": f"{BASE_URL}/passengers/analytics",
            "params": {"period": "3_months", "city": "all"}
        }
    ]
    
    print("🧪 TESTANDO ENDPOINTS DOS PASSAGEIROS")
    print("=" * 50)
    
    for endpoint in endpoints_to_test:
        try:
            print(f"\n📍 Testando: {endpoint['name']}")
            print(f"   URL: {endpoint['url']}")
            print(f"   Params: {endpoint['params']}")
            
            response = requests.get(endpoint['url'], params=endpoint['params'], timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Sucesso! Resposta:")
                
                # Mostrar preview dos dados retornados
                if isinstance(data, dict):
                    for key, value in list(data.items())[:5]:  # Primeiros 5 campos
                        if isinstance(value, (int, float, str, bool)):
                            print(f"      • {key}: {value}")
                        elif isinstance(value, list):
                            print(f"      • {key}: [{len(value)} itens]")
                        elif isinstance(value, dict):
                            print(f"      • {key}: {{{len(value)} campos}}")
                        else:
                            print(f"      • {key}: {type(value).__name__}")
                            
                elif isinstance(data, list):
                    print(f"      • Lista com {len(data)} itens")
                    if data and isinstance(data[0], dict):
                        print(f"      • Primeiro item: {list(data[0].keys())}")
                        
            else:
                print(f"   ❌ Erro {response.status_code}: {response.text[:200]}...")
                
        except requests.exceptions.ConnectionError:
            print(f"   ⚠️  Servidor não está rodando em {BASE_URL}")
            break
        except Exception as e:
            print(f"   ❌ Erro: {str(e)}")

def test_specific_passenger():
    """Testa endpoint de passageiro específico"""
    print(f"\n📍 Testando: Detalhes de Passageiro Específico")
    
    try:
        # Primeiro, buscar um passenger_id válido
        response = requests.get(f"{BASE_URL}/passengers/list", params={"limit": 1}, timeout=10)
        
        if response.status_code == 200:
            passengers = response.json()
            if passengers:
                passenger_id = passengers[0]['passenger_id']
                
                # Agora testar o endpoint específico
                response = requests.get(f"{BASE_URL}/passengers/{passenger_id}", timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"   ✅ Detalhes do passageiro {passenger_id}:")
                    print(f"      • Nome: {data.get('personal_info', {}).get('user_name', 'N/A')}")
                    print(f"      • Cidade: {data.get('city', 'N/A')}")
                    print(f"      • Corridas: {data.get('rides_summary', {}).get('total_rides', 0)}")
                    print(f"      • Receita: R$ {data.get('rides_summary', {}).get('total_revenue', 0):.2f}")
                else:
                    print(f"   ❌ Erro {response.status_code}: {response.text[:200]}...")
            else:
                print("   ⚠️  Nenhum passageiro encontrado para teste")
        else:
            print(f"   ❌ Erro ao buscar passageiros: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Erro: {str(e)}")

if __name__ == "__main__":
    print("🚀 Iniciando testes dos endpoints de passageiros...")
    test_passengers_endpoints()
    test_specific_passenger()
    print(f"\n✅ Testes concluídos!")