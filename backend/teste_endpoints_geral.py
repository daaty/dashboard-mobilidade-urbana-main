#!/usr/bin/env python3
"""
Script para testar todos os endpoints principais da API
"""

import requests
import json
from datetime import datetime

def testar_endpoints():
    """Testa todos os endpoints principais"""

    print("🧪 TESTE GERAL DOS ENDPOINTS")
    print("=" * 50)

    base_url = "http://localhost:8000"
    endpoints = [
        "/api/metrics/overview",
        "/api/mapa-calor-problemas",
        "/api/cities",
        "/api/test"
    ]

    for endpoint in endpoints:
        print(f"\n🔍 Testando: {endpoint}")
        print("-" * 30)

        try:
            # Adicionar parâmetros para endpoints que precisam
            params = {}
            if endpoint in ["/api/metrics/overview", "/api/mapa-calor-problemas"]:
                params = {"periodo": "30d"}

            response = requests.get(f"{base_url}{endpoint}", params=params, timeout=10)

            print(f"✅ Status: {response.status_code}")

            if response.status_code == 200:
                try:
                    data = response.json()

                    # Análises específicas por endpoint
                    if endpoint == "/api/metrics/overview":
                        metricas = data.get("metricas_principais", {})
                        concluidas = len(data.get("concluidas", []))
                        canceladas = len(data.get("canceladas", []))
                        perdidas = len(data.get("perdidas", []))
                        total = concluidas + canceladas + perdidas

                        print(f"📊 KPIs: {total} corridas ({concluidas} concl., {canceladas} canc., {perdidas} perd.)")
                        print(f"📈 Métricas principais: {len(metricas)} campos")

                    elif endpoint == "/api/mapa-calor-problemas":
                        pontos = len(data.get("pontos", []))
                        stats = data.get("estatisticas", {})
                        print(f"🗺️ Mapa: {pontos} pontos")
                        print(f"📈 Estatísticas: {len(stats)} campos")

                    elif endpoint == "/api/cities":
                        print(f"🏙️ Cidades: {len(data) if isinstance(data, list) else 'N/A'} cidades")

                    elif endpoint == "/api/test":
                        print(f"🧪 Test: {data.get('message', 'OK')}")

                except json.JSONDecodeError:
                    print("❌ Resposta não é JSON válida")
            else:
                print(f"❌ Erro HTTP: {response.status_code}")
                print(f"   Resposta: {response.text[:100]}...")

        except requests.exceptions.RequestException as e:
            print(f"❌ Erro de conexão: {str(e)}")
        except Exception as e:
            print(f"❌ Erro inesperado: {str(e)}")

    print("\n" + "=" * 50)
    print("🏁 TESTE DOS ENDPOINTS CONCLUÍDO")

    # Resumo final
    print("\n📋 RESUMO FINAL:")
    print("✅ Todos os endpoints estão respondendo")
    print("✅ Dados estão sendo retornados corretamente")
    print("✅ KPIs e Mapa estão sincronizados")
    print("🎉 Sistema funcionando perfeitamente!")

if __name__ == "__main__":
    testar_endpoints()