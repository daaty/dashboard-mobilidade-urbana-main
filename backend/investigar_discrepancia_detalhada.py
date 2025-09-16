#!/usr/bin/env python3
"""
Script para investigar discrepâncias entre KPIs e Mapa de Calor
Comparação detalhada dos dados retornados por ambos os endpoints
"""

import requests
import json
from datetime import datetime, timedelta
from collections import defaultdict, Counter

def comparar_endpoints_detalhado():
    """Compara detalhadamente os dados entre KPIs e Mapa"""

    print("🔍 INVESTIGAÇÃO DETALHADA: KPIs vs Mapa de Calor")
    print("=" * 60)

    # URLs dos endpoints
    base_url = "http://localhost:8000"
    metrics_url = f"{base_url}/api/metrics/overview"
    mapa_url = f"{base_url}/api/mapa-calor-problemas"

    try:
        # Fazer requests para ambos os endpoints
        print("📡 Fazendo requests para ambos os endpoints...")

        # KPIs
        metrics_response = requests.get(metrics_url, params={"periodo": "30d"})
        metrics_data = metrics_response.json()

        # Mapa
        mapa_response = requests.get(mapa_url, params={"periodo": "30d"})
        mapa_data = mapa_response.json()

        print("✅ Dados obtidos com sucesso!")
        print()

        # Análise dos KPIs
        print("📊 ANÁLISE DOS KPIs:")
        print("-" * 30)

        concluidas_kpi = len(metrics_data.get("concluidas", []))
        canceladas_kpi = len(metrics_data.get("canceladas", []))
        perdidas_kpi = len(metrics_data.get("perdidas", []))
        total_kpi = concluidas_kpi + canceladas_kpi + perdidas_kpi

        print(f"Total de corridas (KPIs): {total_kpi}")
        print(f"  Concluídas: {concluidas_kpi}")
        print(f"  Canceladas: {canceladas_kpi}")
        print(f"  Perdidas: {perdidas_kpi}")
        print()

        # Análise do Mapa
        print("🗺️ ANÁLISE DO MAPA:")
        print("-" * 30)

        pontos = mapa_data.get("pontos", [])
        stats = mapa_data.get("estatisticas", {})

        # Contar por status
        status_counter = Counter(ponto.get("status") for ponto in pontos)

        concluidas_mapa = status_counter.get("concluida", 0)
        canceladas_mapa = status_counter.get("cancelada", 0)
        perdidas_mapa = status_counter.get("perdida", 0)
        total_mapa = len(pontos)

        print(f"Total de pontos (Mapa): {total_mapa}")
        print(f"  Concluídas: {concluidas_mapa}")
        print(f"  Canceladas: {canceladas_mapa}")
        print(f"  Perdidas: {perdidas_mapa}")
        print()

        # Estatísticas do processamento
        print("📈 ESTATÍSTICAS DO PROCESSAMENTO:")
        print("-" * 30)
        print(f"Total registros processados: {stats.get('total_registros_processados', 0)}")
        print(f"IDs únicos processados: {stats.get('ids_unicos_processados', 0)}")
        print(f"Duplicatas removidas: {stats.get('duplicatas_removidas', 0)}")
        print(f"Pontos geocodificados: {stats.get('pontos_geocodificados', 0)}")
        print()

        # Comparação detalhada
        print("⚖️ COMPARAÇÃO DETALHADA:")
        print("-" * 30)

        diff_total = total_kpi - total_mapa
        diff_concluidas = concluidas_kpi - concluidas_mapa
        diff_canceladas = canceladas_kpi - canceladas_mapa
        diff_perdidas = perdidas_kpi - perdidas_mapa

        print(f"Diferença total: KPIs {total_kpi} vs Mapa {total_mapa} = {diff_total}")
        print(f"Diferença concluídas: KPIs {concluidas_kpi} vs Mapa {concluidas_mapa} = {diff_concluidas}")
        print(f"Diferença canceladas: KPIs {canceladas_kpi} vs Mapa {canceladas_mapa} = {diff_canceladas}")
        print(f"Diferença perdidas: KPIs {perdidas_kpi} vs Mapa {perdidas_mapa} = {diff_perdidas}")
        print()

        # Análise de possíveis causas
        print("🔍 ANÁLISE DE POSSÍVEIS CAUSAS:")
        print("-" * 30)

        if diff_total != 0:
            print("❌ DIFERENÇA NO TOTAL GERAL")
            print("  Possíveis causas:")
            print("  - Filtros diferentes aplicados")
            print("  - Problemas na geocodificação (mapa só mostra pontos com endereço válido)")
            print("  - Diferenças na validação de dados")
            print("  - Problemas na extração de datas")
        else:
            print("✅ TOTAL GERAL CONSISTENTE")

        if diff_concluidas != 0:
            print(f"❌ DIFERENÇA EM CONCLUÍDAS: {diff_concluidas}")
        else:
            print("✅ CONCLUÍDAS CONSISTENTES")

        if diff_canceladas != 0:
            print(f"❌ DIFERENÇA EM CANCELADAS: {diff_canceladas}")
        else:
            print("✅ CANCELADAS CONSISTENTES")

        if diff_perdidas != 0:
            print(f"❌ DIFERENÇA EM PERDIDAS: {diff_perdidas}")
        else:
            print("✅ PERDIDAS CONSISTENTES")

        print()

        # Análise dos dados brutos
        print("🔬 ANÁLISE DOS DADOS BRUTOS:")
        print("-" * 30)

        # Verificar se há dados nos KPIs
        if not metrics_data.get("concluidas") and not metrics_data.get("canceladas") and not metrics_data.get("perdidas"):
            print("⚠️ AVISO: Endpoint de métricas retornou arrays vazios!")
            print("   Isso pode indicar problema no endpoint de métricas.")
        else:
            print("✅ Endpoint de métricas tem dados válidos")

        # Verificar dados do mapa
        if not pontos:
            print("⚠️ AVISO: Endpoint do mapa retornou array vazio!")
        else:
            print("✅ Endpoint do mapa tem dados válidos")

            # Mostrar alguns exemplos de pontos
            print("\n📍 Exemplos de pontos do mapa:")
            for i, ponto in enumerate(pontos[:3]):
                print(f"  {i+1}. Status: {ponto.get('status')}, Endereço: {ponto.get('endereco', 'N/A')[:50]}...")

        print()

        # Verificar filtros aplicados
        print("🎯 VERIFICAÇÃO DE FILTROS:")
        print("-" * 30)
        print(f"Período aplicado: 30d")
        print(f"Filtro de cidade: Todas as cidades")
        print(f"Data início (estimada): {(datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')}")
        print(f"Data fim: {datetime.now().strftime('%Y-%m-%d')}")

        # Verificar se os filtros estão sendo aplicados corretamente
        if pontos:
            # Verificar se há pontos fora do período
            datas_invalidas = []
            for ponto in pontos:
                data_str = ponto.get('data')
                if data_str:
                    try:
                        data = datetime.fromisoformat(data_str.replace('Z', '+00:00'))
                        if data < datetime.now() - timedelta(days=30):
                            datas_invalidas.append(data_str)
                    except:
                        pass

            if datas_invalidas:
                print(f"⚠️ AVISO: {len(datas_invalidas)} pontos com datas fora do período de 30 dias")
            else:
                print("✅ Todas as datas dos pontos estão dentro do período")

        print()
        print("=" * 60)
        print("🏁 INVESTIGAÇÃO CONCLUÍDA")

    except Exception as e:
        print(f"❌ ERRO na investigação: {str(e)}")
        print("Verifique se o servidor FastAPI está rodando na porta 8000")

if __name__ == "__main__":
    comparar_endpoints_detalhado()