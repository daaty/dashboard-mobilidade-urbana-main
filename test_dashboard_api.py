#!/usr/bin/env python3
import requests
import json

def test_dashboard_api():
    """Testa os endpoints do dashboard"""
    
    base_url = "http://localhost:5000"
    
    endpoints = [
        "/api/dashboard/overview",
        "/api/dashboard/municipios",
        "/api/dashboard/metricas-diarias",
        "/api/metrics/kpis"
    ]
    
    print("🔍 Testando endpoints da API do Dashboard...")
    print("=" * 50)
    
    for endpoint in endpoints:
        url = f"{base_url}{endpoint}"
        
        try:
            print(f"\n📡 Testando: {endpoint}")
            response = requests.get(url)
            
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"   ✅ Dados recebidos: {json.dumps(data, indent=2, ensure_ascii=False)[:200]}...")
                except:
                    print(f"   📝 Resposta (texto): {response.text[:200]}...")
            else:
                print(f"   ❌ Erro: {response.text}")
                
        except requests.exceptions.ConnectionError:
            print(f"   ❌ Erro de conexão: Servidor não está rodando")
        except Exception as e:
            print(f"   ❌ Erro: {e}")

if __name__ == "__main__":
    test_dashboard_api()
