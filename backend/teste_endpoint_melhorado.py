#!/usr/bin/env python3
"""
Script para testar o endpoint do mapa após as melhorias
"""

import requests

def testar_endpoint_melhorado():
    """Testa o endpoint do mapa após aplicar as melhorias"""

    print("🧪 TESTANDO ENDPOINT DO MAPA APÓS MELHORIAS")
    print("=" * 50)

    try:
        # Testar KPIs
        print("📊 Testando KPIs...")
        kpi_response = requests.get("http://localhost:8000/api/metrics/overview?periodo=30d")
        kpi_data = kpi_response.json()
        canceladas_kpi = len(kpi_data.get("canceladas", []))
        print(f"Canceladas nos KPIs: {canceladas_kpi}")

        # Testar Mapa
        print("🗺️ Testando Mapa...")
        mapa_response = requests.get("http://localhost:8000/api/mapa-calor-problemas?periodo=30d")
        mapa_data = mapa_response.json()
        pontos = mapa_data.get("pontos", [])
        canceladas_mapa = len([p for p in pontos if p.get("status") == "cancelada"])
        print(f"Canceladas no mapa: {canceladas_mapa}")

        # Comparar
        diferenca = canceladas_kpi - canceladas_mapa
        print(f"\n🔍 DIFERENÇA: {diferenca} corridas canceladas")

        if diferenca == 0:
            print("✅ PERFEITO! Todas as corridas canceladas estão no mapa!")
        elif diferenca <= 2:
            print("✅ QUASE LÁ! Diferença mínima, provavelmente geocodificação.")
        else:
            print("❌ AINDA HÁ DIFERENÇA SIGNIFICATIVA.")

        print("\n📈 ESTATÍSTICAS DO MAPA:")
        stats = mapa_data.get("estatisticas", {})
        print(f"   Total registros processados: {stats.get('total_registros_processados', 'N/A')}")
        print(f"   Pontos geocodificados: {stats.get('pontos_geocodificados', 'N/A')}")
        print(f"   Duplicatas removidas: {stats.get('duplicatas_removidas', 'N/A')}")

        # Mostrar alguns endereços de exemplo das canceladas no mapa
        if canceladas_mapa > 0:
            print(f"\n📍 EXEMPLOS DE ENDEREÇOS NO MAPA:")
            canceladas_exemplos = [p for p in pontos if p.get("status") == "cancelada"][:3]
            for i, exemplo in enumerate(canceladas_exemplos, 1):
                endereco = exemplo.get("endereco", "N/A")[:50]
                print(f"   {i}. {endereco}...")

    except Exception as e:
        print(f"❌ ERRO no teste: {str(e)}")

if __name__ == "__main__":
    testar_endpoint_melhorado()