#!/usr/bin/env python3
"""
Teste do endpoint de taxa de aceitação CORRIGIDO
"""

import requests
import json
from datetime import datetime

def test_real_acceptance_rate():
    """Testa o endpoint corrigido de taxa de aceitação"""
    
    base_url = "http://localhost:8000"
    endpoint = f"{base_url}/api/drivers/acceptance-rate"
    
    print("TESTE DA TAXA DE ACEITACAO REAL")
    print("=" * 50)
    
    try:
        # Fazer requisição
        response = requests.get(endpoint)
        
        if response.status_code == 200:
            data = response.json()
            
            print("DADOS REAIS DA TAXA DE ACEITACAO:")
            print("-" * 40)
            print(f"Taxa de Aceitacao REAL: {data['data']['overall_acceptance_rate']}%")
            print(f"Total de Motoristas: {data['data']['total_drivers']}")
            print(f"Total de Requests: {data['data']['total_requests']}")
            print(f"Success Rides: {data['data']['total_success_rides']}")
            print(f"Total de Falhas: {data['data']['total_failures']}")
            print(f"Corridas Completadas (periodo): {data['data']['completed_rides_in_period']}")
            
            print(f"\nBREAKDOWN POR CIDADE:")
            for city, stats in data['data']['city_breakdown'].items():
                success_rate = stats.get('acceptance_rate', 0)
                drivers = stats.get('drivers_count', 0)
                requests = stats.get('total_requests', 0)
                success = stats.get('total_success', 0)
                failures = stats.get('total_failures', 0)
                
                print(f"  {city}:")
                print(f"    - Taxa Real: {success_rate}%")
                print(f"    - Motoristas: {drivers}")
                print(f"    - Requests: {requests}")
                print(f"    - Sucessos: {success}")
                print(f"    - Falhas: {failures}")
            
            print(f"\nDETALHES DOS MOTORISTAS (primeiros 5):")
            for i, driver in enumerate(data['data']['drivers_details'][:5]):
                print(f"  {i+1}. ID {driver['driver_id']} ({driver['city']}):")
                print(f"     - Taxa: {driver['acceptance_rate']}%")
                print(f"     - Requests: {driver['total_requests']}")
                print(f"     - Success: {driver['success_rides']}")
                print(f"     - Rejected: {driver['rejected_rides']}")
                print(f"     - Missed: {driver.get('missed_rides', 0)}")
                print(f"     - Driver Cancelled: {driver.get('driver_cancelled_total', 0)}")
                print(f"     - User Cancelled: {driver.get('user_cancelled_total', 0)}")
                print(f"     - Total Failures: {driver.get('total_failures', 0)}")
            
            print(f"\nRESUMO: {data['summary']}")
            
        else:
            print(f"Erro na requisicao: {response.status_code}")
            print(f"Resposta: {response.text}")
            
    except Exception as e:
        print(f"Erro inesperado: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_real_acceptance_rate()