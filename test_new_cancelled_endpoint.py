#!/usr/bin/env python3
"""Testar o NOVO endpoint /api/drivers/cancelled-rides"""

import requests
import json

def test_new_cancelled_endpoint():
    """Testa o novo endpoint que usa a query exata que funciona"""
    
    url = "http://localhost:8000/api/drivers/cancelled-rides"
    params = {
        "period": "30_days",
        "city": "all"
    }
    
    print(f"🔥 TESTANDO NOVO ENDPOINT: {url}")
    print(f"Parameters: {params}")
    print("="*60)
    
    try:
        response = requests.get(url, params=params)
        print(f"Status code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("RESPOSTA COMPLETA:")
            print(json.dumps(data, indent=2))
            
            if data.get('success') and 'data' in data:
                result_data = data['data']
                cancelled_count = result_data.get('total_cancelled_rides', 0)
                
                print(f"\n🎯 RESULTADO:")
                print(f"Total de corridas canceladas: {cancelled_count}")
                print(f"Drivers com canceladas: {result_data.get('drivers_with_cancelled', 0)}")
                print(f"Período: {result_data.get('period', 'N/A')}")
                
                if cancelled_count == 22:
                    print("✅ PERFEITO! Encontramos os 22 cancelamentos esperados!")
                elif cancelled_count == 0:
                    print("❌ AINDA 0 - há problema na query/conexão")
                else:
                    print(f"⚠️ {cancelled_count} cancelamentos (esperávamos 22)")
                    
            else:
                print("❌ Resposta inválida")
                
        else:
            print(f"❌ HTTP {response.status_code}: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ ERRO DE CONEXÃO: {e}")
    except Exception as e:
        print(f"❌ ERRO: {e}")

if __name__ == "__main__":
    test_new_cancelled_endpoint()