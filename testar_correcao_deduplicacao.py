#!/usr/bin/env python3
"""
Script para testar se a deduplicação no endpoint do mapa foi corrigida
"""
import requests
import json
from datetime import datetime

def testar_endpoint_mapa():
    """Testa o endpoint do mapa de calor após correção de deduplicação"""

    # URL do endpoint do mapa
    url_mapa = "http://localhost:8000/api/mapa-calor-problemas"

    # Parâmetros para teste (6 meses)
    params = {
        "periodo": "6m"
    }

    try:
        print("🔍 Testando endpoint do mapa de calor...")
        response = requests.get(url_mapa, params=params)

        if response.status_code == 200:
            data = response.json()
            pontos = data.get("pontos", [])
            stats = data.get("estatisticas", {})

            print("✅ Endpoint do mapa funcionando!")
            print(f"📊 Total de pontos: {len(pontos)}")
            print(f"📈 Total registros processados: {stats.get('total_registros_processados', 0)}")
            print(f"🔢 IDs únicos processados: {stats.get('ids_unicos_processados', 0)}")
            print(f"🗑️ Duplicatas removidas: {stats.get('duplicatas_removidas', 0)}")

            # Contar por status
            status_count = {}
            for ponto in pontos:
                status = ponto.get("status", "desconhecido")
                status_count[status] = status_count.get(status, 0) + 1

            print("\n📋 Distribuição por status:")
            for status, count in status_count.items():
                print(f"  {status}: {count}")

            # Comparar com KPIs esperados
            total_pontos = len(pontos)
            if total_pontos <= 251:  # Deve ser menor ou igual aos 251 dos KPIs
                print(f"\n✅ SUCESSO: Total de pontos ({total_pontos}) está consistente com KPIs (251)")
                print("🎉 Correção de deduplicação aplicada com sucesso!")
            else:
                print(f"\n⚠️ ATENÇÃO: Total de pontos ({total_pontos}) ainda maior que KPIs (251)")
                print("🔧 Pode haver mais duplicatas ou outro problema")

        else:
            print(f"❌ Erro no endpoint do mapa: {response.status_code}")
            print(response.text)

    except Exception as e:
        print(f"❌ Erro ao testar endpoint: {str(e)}")

def testar_endpoint_kpis():
    """Testa o endpoint de métricas para comparação"""

    # URL do endpoint de métricas
    url_kpis = "http://localhost:8000/api/metrics/overview"

    # Parâmetros para teste (6 meses)
    params = {
        "periodo": "6m"
    }

    try:
        print("\n🔍 Testando endpoint de KPIs para comparação...")
        response = requests.get(url_kpis, params=params)

        if response.status_code == 200:
            data = response.json()
            metrics = data.get("metrics", {})

            total_corridas = metrics.get("total_corridas", 0)
            print(f"📊 KPIs - Total de corridas: {total_corridas}")

            # Detalhes por status
            print("📋 Detalhamento KPIs:")
            print(f"  Concluídas: {metrics.get('concluidas', 0)}")
            print(f"  Canceladas: {metrics.get('canceladas', 0)}")
            print(f"  Perdidas: {metrics.get('perdidas', 0)}")

        else:
            print(f"❌ Erro no endpoint de KPIs: {response.status_code}")

    except Exception as e:
        print(f"❌ Erro ao testar KPIs: {str(e)}")

if __name__ == "__main__":
    print("🧪 TESTE DE CORREÇÃO DE DEDUPLICAÇÃO")
    print("=" * 50)

    testar_endpoint_mapa()
    testar_endpoint_kpis()

    print("\n" + "=" * 50)
    print("🏁 Teste concluído!")