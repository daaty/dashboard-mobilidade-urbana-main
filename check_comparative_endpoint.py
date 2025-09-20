#!/usr/bin/env python3
"""
Script para verificar se o endpoint /api/metrics/comparative está retornando dados válidos
"""
import requests
import json
from datetime import datetime, timedelta

def test_comparative_endpoint():
    base_url = "http://localhost:8000"
    endpoint = "/api/metrics/comparative"
    
    # Teste com diferentes parâmetros
    test_cases = [
        {"periodo": "30d", "cidade": "todas"},
        {"periodo": "7d", "cidade": "todas"},
        {"periodo": "hoje", "cidade": "todas"},
    ]
    
    print("🔍 VERIFICANDO ENDPOINT COMPARATIVE")
    print("=" * 50)
    
    for i, params in enumerate(test_cases, 1):
        print(f"\n📋 TESTE {i}: {params}")
        print("-" * 30)
        
        try:
            response = requests.get(f"{base_url}{endpoint}", params=params)
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"Success: {data.get('success', False)}")
                print(f"Período: {data.get('periodo', 'N/A')}")
                print(f"Cidade: {data.get('ciudad', 'N/A')}")
                print(f"Unit Type: {data.get('unit_type', 'N/A')}")
                
                comparative_data = data.get('comparative_data', [])
                print(f"Total de registros: {len(comparative_data)}")
                
                if comparative_data:
                    # Verificar primeiros registros
                    print("\n📊 PRIMEIROS 3 REGISTROS:")
                    for j, item in enumerate(comparative_data[:3]):
                        print(f"  {j+1}. {item}")
                    
                    # Verificar se há dados não-zero
                    total_rides = sum(item.get('total', 0) for item in comparative_data)
                    total_concluidas = sum(item.get('concluidas', 0) for item in comparative_data)
                    total_canceladas = sum(item.get('canceladas', 0) for item in comparative_data)
                    total_perdidas = sum(item.get('perdidas', 0) for item in comparative_data)
                    
                    print(f"\n📈 TOTAIS SOMADOS:")
                    print(f"  Total: {total_rides}")
                    print(f"  Concluídas: {total_concluidas}")
                    print(f"  Canceladas: {total_canceladas}")
                    print(f"  Perdidas: {total_perdidas}")
                    
                    # Verificar registros com dados
                    records_with_data = [item for item in comparative_data if item.get('total', 0) > 0]
                    print(f"  Registros com dados: {len(records_with_data)}")
                    
                    if records_with_data:
                        print(f"  Exemplo com dados: {records_with_data[0]}")
                else:
                    print("❌ Nenhum dado retornado!")
                    
            else:
                print(f"❌ Erro HTTP: {response.status_code}")
                print(f"Resposta: {response.text[:200]}")
                
        except Exception as e:
            print(f"❌ Erro na requisição: {e}")
    
    print("\n" + "=" * 50)
    print("🔚 VERIFICAÇÃO CONCLUÍDA")

if __name__ == "__main__":
    test_comparative_endpoint()