#!/usr/bin/env python3
"""
Script para analisar as diferenças específicas entre KPIs e Mapa
Foca nas 8 corridas que estão nos KPIs mas não no mapa
"""

import requests
import json
from datetime import datetime, timedelta
from collections import defaultdict, Counter

def analisar_diferencas_especificas():
    """Analisa as diferenças específicas entre KPIs e mapa"""

    print("🔍 ANÁLISE ESPECÍFICA DAS DIFERENÇAS")
    print("=" * 60)

    base_url = "http://localhost:8000"
    metrics_url = f"{base_url}/api/metrics/overview"
    mapa_url = f"{base_url}/api/mapa-calor-problemas"

    try:
        # Obter dados de ambos os endpoints
        print("📡 Obtendo dados de ambos os endpoints...")

        metrics_response = requests.get(metrics_url, params={"periodo": "30d"})
        metrics_data = metrics_response.json()

        mapa_response = requests.get(mapa_url, params={"periodo": "30d"})
        mapa_data = mapa_response.json()

        print("✅ Dados obtidos com sucesso!")
        print()

        # Extrair IDs dos KPIs
        kpi_ids = set()
        kpi_por_status = {"concluida": set(), "cancelada": set(), "perdida": set()}

        for status in ["concluidas", "canceladas", "perdidas"]:
            if status in metrics_data:
                for corrida in metrics_data[status]:
                    ride_id = corrida.get("id_corrida")
                    if ride_id:
                        kpi_ids.add(ride_id)
                        # Mapear status
                        if status == "concluidas":
                            kpi_por_status["concluida"].add(ride_id)
                        elif status == "canceladas":
                            kpi_por_status["cancelada"].add(ride_id)
                        elif status == "perdidas":
                            kpi_por_status["perdida"].add(ride_id)

        # Extrair IDs do mapa
        mapa_ids = set()
        mapa_por_status = {"concluida": set(), "cancelada": set(), "perdida": set()}

        pontos = mapa_data.get("pontos", [])
        for ponto in pontos:
            # O mapa não tem ID direto, então vamos usar uma combinação única
            endereco = ponto.get("endereco", "")
            data = ponto.get("data", "")
            status = ponto.get("status", "")

            # Criar um ID único baseado em endereço + data + status
            unique_id = f"{endereco}|{data}|{status}"
            mapa_ids.add(unique_id)
            mapa_por_status[status].add(unique_id)

        print("📊 RESUMO DOS IDS:")
        print("-" * 40)
        print(f"Total IDs únicos nos KPIs: {len(kpi_ids)}")
        print(f"Total IDs únicos no mapa: {len(mapa_ids)}")
        print(f"Diferença: {len(kpi_ids) - len(mapa_ids)}")
        print()

        # Encontrar IDs que estão nos KPIs mas não no mapa
        ids_somente_kpi = kpi_ids - mapa_ids
        ids_somente_mapa = mapa_ids - kpi_ids

        print("🔍 ANÁLISE DAS DIFERENÇAS:")
        print("-" * 40)
        print(f"IDs só nos KPIs: {len(ids_somente_kpi)}")
        print(f"IDs só no mapa: {len(ids_somente_mapa)}")
        print()

        if ids_somente_kpi:
            print("📋 DETALHES DOS IDs SÓ NOS KPIs:")
            print("-" * 40)

            # Mostrar detalhes das corridas que estão só nos KPIs
            contador_status = Counter()

            for status in ["concluidas", "canceladas", "perdidas"]:
                if status in metrics_data:
                    for corrida in metrics_data[status]:
                        ride_id = corrida.get("id_corrida")
                        if ride_id in ids_somente_kpi:
                            contador_status[status] += 1

                            # Mostrar detalhes da primeira ocorrência
                            if contador_status[status] <= 3:  # Limitar a 3 exemplos por status
                                nome = corrida.get("nome", "N/A")[:30]
                                endereco = corrida.get("local", "N/A")[:40]
                                data = corrida.get("hora", "N/A")
                                print(f"  {status.upper()}: ID {ride_id}")
                                print(f"    Nome: {nome}...")
                                print(f"    Endereço: {endereco}...")
                                print(f"    Data: {data}")
                                print()

            print("📊 DISTRIBUIÇÃO POR STATUS (só nos KPIs):")
            for status, count in contador_status.items():
                print(f"  {status}: {count}")
            print()

        # Análise das possíveis causas
        print("🔍 ANÁLISE DAS POSSÍVEIS CAUSAS:")
        print("-" * 40)

        if ids_somente_kpi:
            print("❌ CORRIDAS AUSENTES NO MAPA:")
            print("   Estas corridas existem nos KPIs mas não aparecem no mapa.")
            print("   Possíveis causas:")
            print("   1. Endereço inválido ou não geocodificável")
            print("   2. Falha na extração de endereço dos dados")
            print("   3. Filtros de validação de endereço no mapa")
            print("   4. Problemas na conversão de dados JSON")
            print()

        if ids_somente_mapa:
            print("⚠️ CORRIDAS EXTRAS NO MAPA:")
            print("   Estas corridas aparecem no mapa mas não nos KPIs.")
            print("   Possíveis causas:")
            print("   1. Duplicatas não detectadas adequadamente")
            print("   2. Diferenças na interpretação de datas")
            print("   3. Problemas na deduplicação por ID")
            print()

        # Análise específica por status
        print("📈 ANÁLISE POR STATUS:")
        print("-" * 40)

        for status in ["concluida", "cancelada", "perdida"]:
            kpi_count = len(kpi_por_status[status])
            mapa_count = len(mapa_por_status[status])
            diff = kpi_count - mapa_count

            if diff != 0:
                print(f"❌ {status.upper()}: KPIs {kpi_count} vs Mapa {mapa_count} = {diff}")
            else:
                print(f"✅ {status.upper()}: Consistente ({kpi_count})")

        print()

        # Sugestões de correção
        print("🔧 SUGESTÕES DE CORREÇÃO:")
        print("-" * 40)

        if ids_somente_kpi:
            print("1. Verificar se as corridas ausentes têm endereços válidos")
            print("2. Melhorar a extração de endereços no endpoint do mapa")
            print("3. Considerar incluir corridas sem endereço como pontos genéricos")
            print("4. Verificar se há problemas na conversão de dados JSON")

        if ids_somente_mapa:
            print("1. Melhorar algoritmo de deduplicação")
            print("2. Verificar consistência na extração de IDs únicos")

        print()
        print("=" * 60)
        print("🏁 ANÁLISE ESPECÍFICA CONCLUÍDA")

    except Exception as e:
        print(f"❌ ERRO na análise: {str(e)}")
        print("Verifique se o servidor FastAPI está rodando na porta 8000")

if __name__ == "__main__":
    analisar_diferencas_especificas()