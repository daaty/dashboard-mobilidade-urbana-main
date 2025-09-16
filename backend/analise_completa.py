#!/usr/bin/env python3
"""
Análise completa para encontrar a causa raiz das corridas canceladas faltantes
"""

import requests
import json
import re

def analise_completa():
    """Análise completa do problema das corridas canceladas faltantes"""

    print("🔍 ANÁLISE COMPLETA: CORRIDAS CANCELADAS FALTANTES")
    print("=" * 70)

    base_url = "http://localhost:8000"

    try:
        # Obter dados de ambos os endpoints
        print("📡 Obtendo dados completos...")

        kpi_response = requests.get(f"{base_url}/api/metrics/overview?periodo=30d")
        kpi_data = kpi_response.json()

        mapa_response = requests.get(f"{base_url}/api/mapa-calor-problemas?periodo=30d")
        mapa_data = mapa_response.json()

        print("✅ Dados obtidos!")
        print()

        # Análise estatística
        canceladas_kpi = kpi_data.get("canceladas", [])
        pontos_mapa = mapa_data.get("pontos", [])
        canceladas_mapa = [p for p in pontos_mapa if p.get("status") == "cancelada"]

        print("📊 ESTATÍSTICAS GERAIS:")
        print(f"   Canceladas nos KPIs: {len(canceladas_kpi)}")
        print(f"   Canceladas no mapa: {len(canceladas_mapa)}")
        print(f"   Diferença: {len(canceladas_kpi) - len(canceladas_mapa)}")
        print()

        # Verificar se os IDs são realmente únicos
        print("🔢 ANÁLISE DE DUPLICATAS:")
        ids_kpi = set()
        ids_mapa = set()

        for corrida in canceladas_kpi:
            ride_id = corrida.get("id_corrida")
            if ride_id:
                ids_kpi.add(str(ride_id))

        for ponto in canceladas_mapa:
            # O mapa não tem ID direto, vamos usar combinação única
            endereco = ponto.get("endereco", "")
            data = ponto.get("data", "")
            unique_id = f"{endereco}|{data}"
            ids_mapa.add(unique_id)

        print(f"   IDs únicos nos KPIs: {len(ids_kpi)}")
        print(f"   IDs únicos no mapa: {len(ids_mapa)}")
        print()

        # Análise de endereços
        print("📍 ANÁLISE DE ENDEREÇOS:")
        enderecos_kpi = set()
        enderecos_mapa = set()

        for corrida in canceladas_kpi:
            endereco = corrida.get("local", "").strip()
            if endereco:
                enderecos_kpi.add(endereco)

        for ponto in canceladas_mapa:
            endereco = ponto.get("endereco", "").strip()
            if endereco:
                enderecos_mapa.add(endereco)

        print(f"   Endereços únicos nos KPIs: {len(enderecos_kpi)}")
        print(f"   Endereços únicos no mapa: {len(enderecos_mapa)}")
        print(f"   Endereços em comum: {len(enderecos_kpi.intersection(enderecos_mapa))}")
        print()

        # HIPÓTESE 1: Problema na geocodificação
        print("🌍 HIPÓTESE 1: PROBLEMA DE GEOCODIFICAÇÃO")
        print("-" * 45)

        stats = mapa_data.get("estatisticas", {})
        total_processados = stats.get("total_registros_processados", 0)
        pontos_geocodificados = stats.get("pontos_geocodificados", 0)
        duplicatas_removidas = stats.get("duplicatas_removidas", 0)

        print(f"   Total de registros processados: {total_processados}")
        print(f"   Pontos geocodificados: {pontos_geocodificados}")
        print(f"   Duplicatas removidas: {duplicatas_removidas}")
        print(f"   Taxa de geocodificação: {(pontos_geocodificados/total_processados*100):.1f}%" if total_processados > 0 else "N/A")

        if pontos_geocodificados < total_processados * 0.8:  # Menos de 80% geocodificados
            print("   ❌ HIPÓTESE CONFIRMADA: Baixa taxa de geocodificação!")
            print("   💡 Isso explicaria por que muitas corridas não aparecem no mapa.")
        else:
            print("   ✅ HIPÓTESE DESCARTADA: Taxa de geocodificação adequada.")
        print()

        # HIPÓTESE 2: Filtros adicionais
        print("🔍 HIPÓTESE 2: FILTROS ADICIONAIS")
        print("-" * 35)

        # Verificar se há filtros de cidade ativos
        cidade_filtro = stats.get("cidade_filtro")
        if cidade_filtro:
            print(f"   ❌ FILTRO ATIVO: Cidade = {cidade_filtro}")
            print("   💡 Isso pode estar removendo corridas de outras cidades.")
        else:
            print("   ✅ Nenhum filtro de cidade ativo.")

        # Verificar período
        periodo = stats.get("periodo", "N/A")
        dt_inicio = stats.get("data_inicio", "N/A")
        dt_fim = stats.get("data_fim", "N/A")
        print(f"   Período analisado: {periodo} ({dt_inicio} até {dt_fim})")
        print()

        # HIPÓTESE 3: Problema na extração de endereços
        print("⚙️ HIPÓTESE 3: PROBLEMA NA EXTRAÇÃO DE ENDEREÇOS")
        print("-" * 48)

        # Verificar se os endereços dos KPIs estão sendo processados
        enderecos_kpi_list = list(enderecos_kpi)
        enderecos_nao_encontrados = []

        for endereco_kpi in enderecos_kpi_list[:10]:  # Verificar primeiros 10
            encontrado = False
            for endereco_mapa in enderecos_mapa:
                # Comparação aproximada
                if (endereco_kpi.lower().replace("...", "").strip() in endereco_mapa.lower() or
                    endereco_mapa.lower() in endereco_kpi.lower().replace("...", "").strip()):
                    encontrado = True
                    break

            if not encontrado:
                enderecos_nao_encontrados.append(endereco_kpi[:50])

        if enderecos_nao_encontrados:
            print(f"   ❌ ENDEREÇOS NÃO ENCONTRADOS: {len(enderecos_nao_encontrados)}")
            print("   💡 Estes endereços dos KPIs não aparecem no mapa.")
            for endereco in enderecos_nao_encontrados[:3]:
                print(f"      - {endereco}...")
        else:
            print("   ✅ Todos os endereços dos KPIs foram encontrados no mapa.")
        print()

        # DIAGNÓSTICO FINAL
        print("🎯 DIAGNÓSTICO FINAL:")
        print("-" * 20)

        if pontos_geocodificados < total_processados * 0.8:
            print("🔴 CAUSA PRINCIPAL: GEOCODIFICAÇÃO FRACA")
            print("   Muitos endereços não estão sendo geocodificados com sucesso.")
            print("   Solução: Melhorar o serviço de geocodificação.")

        elif enderecos_nao_encontrados:
            print("🔴 CAUSA PRINCIPAL: EXTRAÇÃO DE ENDEREÇOS")
            print("   Os endereços não estão sendo extraídos corretamente.")
            print("   Solução: Verificar a lógica de extração de endereços.")

        elif cidade_filtro:
            print("🔴 CAUSA PRINCIPAL: FILTRO DE CIDADE")
            print("   Filtros estão removendo corridas de outras cidades.")
            print("   Solução: Remover ou ajustar filtros.")

        else:
            print("🔴 CAUSA PRINCIPAL: DESCONHECIDA")
            print("   Nenhuma das hipóteses principais se confirmou.")
            print("   Solução: Investigação mais profunda necessária.")

        print("\n📋 PRÓXIMAS AÇÕES RECOMENDADAS:")
        print("-" * 32)
        print("1. Verificar se o servidor foi reiniciado após as mudanças")
        print("2. Adicionar logs detalhados no processamento do mapa")
        print("3. Testar geocodificação manual dos endereços faltantes")
        print("4. Verificar se há diferenças na estrutura dos dados brutos")
        print("5. Considerar implementar cache de geocodificação")

        print("\n" + "=" * 70)
        print("🏁 ANÁLISE COMPLETA CONCLUÍDA")

    except Exception as e:
        print(f"❌ ERRO na análise completa: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    analise_completa()