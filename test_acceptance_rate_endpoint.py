#!/usr/bin/env python3
"""
Teste do novo endpoint de taxa de aceitação
"""

import requests
import json
from datetime import datetime

def test_acceptance_rate_endpoint():
    """Testa o endpoint de taxa de aceitação"""
    
    base_url = "http://localhost:8000"
    endpoint = f"{base_url}/api/drivers/acceptance-rate"
    
    print("🔍 Testando endpoint de Taxa de Aceitação...")
    print(f"📍 URL: {endpoint}")
    print("-" * 60)
    
    try:
        # Fazer requisição
        response = requests.get(endpoint)
        
        if response.status_code == 200:
            data = response.json()
            
            print("✅ Endpoint funcionando!")
            print(f"📊 Taxa de Aceitação Geral: {data['data']['overall_acceptance_rate']}%")
            print(f"👥 Total de Motoristas: {data['data']['total_drivers']}")
            print(f"📞 Total de Requests: {data['data']['total_requests']}")
            print(f"❌ Total Rejeitados: {data['data']['total_rejected']}")
            print(f"✅ Total Aceitos: {data['data']['total_accepted']}")
            print(f"🚗 Corridas Completadas (período): {data['data']['completed_rides_in_period']}")
            
            print(f"\n🏙️ Breakdown por Cidade:")
            for city, stats in data['data']['city_breakdown'].items():
                print(f"  {city}:")
                print(f"    - Motoristas: {stats['drivers_count']}")
                print(f"    - Taxa de Aceitação: {stats['acceptance_rate']}%")
                print(f"    - Requests: {stats['total_requests']}")
                print(f"    - Rejeitados: {stats['total_rejected']}")
            
            print(f"\n👨‍💼 Detalhes dos Motoristas (primeiros 3):")
            for i, driver in enumerate(data['data']['drivers_details'][:3]):
                print(f"  Motorista {i+1}:")
                print(f"    - ID: {driver['driver_id']}")
                print(f"    - Cidade: {driver['city']}")
                print(f"    - Taxa de Aceitação: {driver['acceptance_rate']}%")
                print(f"    - Requests Total: {driver['total_requests']}")
                print(f"    - Rejeitados: {driver['rejected_rides']}")
                print(f"    - Corridas Completadas (período): {driver['completed_rides_period']}")
            
            print(f"\n📋 Resumo: {data['summary']}")
            
        else:
            print(f"❌ Erro na requisição: {response.status_code}")
            print(f"Resposta: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Erro: Não foi possível conectar ao servidor.")
        print("Certifique-se de que o backend está rodando em http://localhost:8000")
        
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")

if __name__ == "__main__":
    test_acceptance_rate_endpoint()