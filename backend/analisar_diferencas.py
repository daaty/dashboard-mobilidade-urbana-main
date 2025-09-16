#!/usr/bin/env python3
"""
Análise detalhada das diferenças entre os dois endpoints
"""
import requests
import json
from datetime import datetime

def analisar_diferencas_processamento():
    """Analisa as diferenças na lógica de processamento entre os endpoints"""

    print("🔍 ANÁLISE DETALHADA DAS DIFERENÇAS")
    print("=" * 60)

    # 1. Verificar se ambos usam os mesmos filtros de período
    print("\n📅 1. VERIFICAÇÃO DE FILTROS DE PERÍODO:")
    print("   Ambos os endpoints usam timedelta(days=180) para 6m - ✅ IGUAIS")

    # 2. Comparar processamento de dados brutos
    print("\n📊 2. COMPARAÇÃO DE DADOS BRUTOS:")

    # Buscar dados do PostgreSQL diretamente
    try:
        # Vou fazer uma query simples para contar registros por tipo
        print("   🔍 Analisando estrutura dos dados no PostgreSQL...")

        # Testar endpoint de métricas com debug
        response_kpis = requests.get('http://localhost:8000/api/metrics/overview?periodo=6m', timeout=10)
        if response_kpis.status_code == 200:
            data_kpis = response_kpis.json()
            evolucao = data_kpis.get('evolucao', [])
            print(f"   📈 KPIs - Dias com dados: {len(evolucao)}")

            # Mostrar alguns dias de exemplo
            if evolucao:
                print("   📋 Exemplos de dias (KPIs):")
                for i, dia in enumerate(evolucao[:3]):
                    print(f"      {dia['data']}: {dia['concluidas'] + dia['canceladas'] + dia['perdidas']} corridas")

        # Testar endpoint do mapa
        response_mapa = requests.get('http://localhost:8000/api/mapa-calor-problemas?periodo=6m', timeout=10)
        if response_mapa.status_code == 200:
            data_mapa = response_mapa.json()
            pontos = data_mapa.get('pontos', [])
            print(f"   🗺️ Mapa - Total pontos: {len(pontos)}")

            # Analisar distribuição temporal dos pontos
            datas_pontos = {}
            for ponto in pontos:
                if ponto.get('data'):
                    try:
                        data_str = ponto['data'][:10]  # YYYY-MM-DD
                        datas_pontos[data_str] = datas_pontos.get(data_str, 0) + 1
                    except:
                        pass

            print(f"   🗺️ Mapa - Dias com pontos: {len(datas_pontos)}")

            # Mostrar alguns dias de exemplo
            if datas_pontos:
                print("   📋 Exemplos de dias (Mapa):")
                sorted_datas = sorted(datas_pontos.items())[-3:]  # Últimos 3 dias
                for data, count in sorted_datas:
                    print(f"      {data}: {count} pontos")

    except Exception as e:
        print(f"   ❌ Erro na análise: {e}")

    # 3. Possíveis causas das diferenças
    print("\n🎯 3. POSSÍVEIS CAUSAS DAS DIFERENÇAS:")

    print("   🔍 CAUSA 1: Lógica de deduplicação")
    print("      - KPIs: Usa sets para deduplicação por ID")
    print("      - Mapa: Pode não ter deduplicação ou usar critério diferente")

    print("\n   🔍 CAUSA 2: Critérios de validação de data")
    print("      - Ambos usam extract_datetime_from_record()")
    print("      - Mas podem ter validações diferentes para datas inválidas")

    print("\n   🔍 CAUSA 3: Processamento de diferentes tipos de registros")
    print("      - Ambos processam: Completed, Cancelled, Missed Rides")
    print("      - Mas podem interpretar os dados de forma diferente")

    print("\n   🔍 CAUSA 4: Filtros adicionais no mapa")
    print("      - Mapa filtra apenas registros com endereço válido")
    print("      - KPIs podem incluir registros sem endereço")

    # 4. Verificar se o problema está na deduplicação
    print("\n🧪 4. TESTE DE DEDUPLICAÇÃO:")
    print("   Verificando se há diferença na lógica de deduplicação...")

    # Vou analisar alguns registros de exemplo
    if 'data_mapa' in locals():
        print(f"   📊 Analisando {min(10, len(pontos))} pontos do mapa...")

        # Verificar IDs duplicados
        ids_vistos = set()
        duplicados = 0

        for ponto in pontos[:50]:  # Analisar primeiros 50
            ponto_id = ponto.get('id_corrida') or ponto.get('id')
            if ponto_id:
                if ponto_id in ids_vistos:
                    duplicados += 1
                else:
                    ids_vistos.add(ponto_id)

        print(f"   🔄 IDs duplicados encontrados: {duplicados}")
        print(f"   📊 IDs únicos: {len(ids_vistos)}")

if __name__ == "__main__":
    analisar_diferencas_processamento()