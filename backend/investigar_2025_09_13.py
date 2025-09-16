#!/usr/bin/env python3
"""
Investigação detalhada do dia 2025-09-13
"""
import requests
from collections import defaultdict

def investigar_dia_especifico():
    """Investiga em detalhes o dia 2025-09-13"""

    print("🔍 INVESTIGAÇÃO DETALHADA - 2025-09-13")
    print("=" * 60)

    try:
        # 1. Dados dos KPIs para este dia
        print("\n📊 1. DADOS DOS KPIs (2025-09-13):")
        response_kpis = requests.get('http://localhost:8000/api/metrics/overview?periodo=6m', timeout=10)
        if response_kpis.status_code == 200:
            data_kpis = response_kpis.json()
            evolucao = data_kpis.get('evolucao', [])

            for dia in evolucao:
                if dia['data'] == '2025-09-13':
                    print(f"   Concluídas: {dia['concluidas']}")
                    print(f"   Canceladas: {dia['canceladas']}")
                    print(f"   Perdidas: {dia['perdidas']}")
                    print(f"   Total: {dia['concluidas'] + dia['canceladas'] + dia['perdidas']}")
                    break

        # 2. Dados do mapa para este dia
        print("\n🗺️ 2. DADOS DO MAPA (2025-09-13):")
        response_mapa = requests.get('http://localhost:8000/api/mapa-calor-problemas?periodo=6m', timeout=10)
        if response_mapa.status_code == 200:
            data_mapa = response_mapa.json()
            pontos = data_mapa.get('pontos', [])

            pontos_dia = []
            for ponto in pontos:
                if ponto.get('data') and ponto['data'].startswith('2025-09-13'):
                    pontos_dia.append(ponto)

            print(f"   Total de pontos: {len(pontos_dia)}")

            # Contar por status
            status_count = defaultdict(int)
            for ponto in pontos_dia:
                status = ponto.get('status', 'desconhecido')
                status_count[status] += 1

            for status, count in status_count.items():
                print(f"   {status.title()}: {count}")

        # 3. Análise dos pontos do mapa
        print("\n🔍 3. ANÁLISE DETALHADA DOS PONTOS:")
        if pontos_dia:
            print(f"   Analisando {min(10, len(pontos_dia))} primeiros pontos:")

            for i, ponto in enumerate(pontos_dia[:10]):
                print(f"   {i+1}. Status: {ponto.get('status', 'N/A')}")
                print(f"      Endereço: {ponto.get('endereco', 'N/A')[:60]}...")
                print(f"      Data: {ponto.get('data', 'N/A')}")
                print(f"      ID: {ponto.get('id_corrida', 'N/A')}")
                print()

        # 4. Verificar se há duplicatas ou problemas de validação
        print("\n🧪 4. VERIFICAÇÃO DE QUALIDADE:")

        # Verificar IDs únicos
        ids_unicos = set()
        ids_duplicados = []

        for ponto in pontos_dia:
            ponto_id = ponto.get('id_corrida') or ponto.get('id') or str(ponto)
            if ponto_id in ids_unicos:
                ids_duplicados.append(ponto_id)
            else:
                ids_unicos.add(ponto_id)

        print(f"   IDs únicos: {len(ids_unicos)}")
        print(f"   IDs duplicados: {len(ids_duplicados)}")

        if ids_duplicados:
            print(f"   🔴 Exemplos de duplicatas: {ids_duplicados[:3]}")

        # Verificar endereços válidos
        enderecos_validos = 0
        enderecos_invalidos = 0

        for ponto in pontos_dia:
            endereco = ponto.get('endereco', '')
            if endereco and len(endereco.strip()) > 10:  # Endereço mínimo
                enderecos_validos += 1
            else:
                enderecos_invalidos += 1

        print(f"   ✅ Endereços válidos: {enderecos_validos}")
        print(f"   ❌ Endereços inválidos: {enderecos_invalidos}")

    except Exception as e:
        print(f"❌ Erro na investigação: {e}")

if __name__ == "__main__":
    investigar_dia_especifico()