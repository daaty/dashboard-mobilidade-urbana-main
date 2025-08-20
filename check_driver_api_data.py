#!/usr/bin/env python3
"""
Script para verificar os dados retornados pela API de drivers
"""

import requests
import json

def check_api_data():
    """Verificar dados da API de drivers"""
    
    api_url = "https://fastapi.urbanmt.com.br/api/drivers/overview"
    
    try:
        print("Fazendo requisição para:", api_url)
        response = requests.get(api_url, timeout=30)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            print(f"\n=== ESTRUTURA DA RESPOSTA ===")
            print(f"total_drivers: {data.get('total_drivers', 'N/A')}")
            print(f"active_drivers: {data.get('active_drivers', 'N/A')}")
            print(f"average_rating: {data.get('average_rating', 'N/A')}")
            print(f"total_rides_completed: {data.get('total_rides_completed', 'N/A')}")
            print(f"avg_rides_per_driver: {data.get('avg_rides_per_driver', 'N/A')}")
            
            print(f"\n=== DRIVERS BY STATUS ===")
            drivers_by_status = data.get('drivers_by_status', {})
            for status, count in drivers_by_status.items():
                print(f"{status}: {count}")
                
            print(f"\n=== TOP DRIVERS ===")
            top_drivers = data.get('top_drivers', [])
            for i, driver in enumerate(top_drivers[:3]):
                print(f"{i+1}. {driver.get('name', 'N/A')} - Rating: {driver.get('rating', 'N/A')} - Rides: {driver.get('total_rides', 'N/A')}")
            
            print(f"\n=== PERFORMANCE METRICS ===")
            perf = data.get('performance_metrics', {})
            for metric, value in perf.items():
                print(f"{metric}: {value}")
                
            print(f"\n=== KPI METRICS ===")
            kpis = data.get('kpi_metrics', {})
            for kpi, value in kpis.items():
                print(f"{kpi}: {value}")
            
            # Salvar resposta completa em arquivo
            with open('api_drivers_response.json', 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print(f"\nResposta completa salva em: api_drivers_response.json")
            
        else:
            print(f"Erro na API: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"Erro ao conectar com a API: {e}")

if __name__ == "__main__":
    check_api_data()
