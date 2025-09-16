#!/usr/bin/env python3
"""
Script para comparar dados brutos entre os endpoints de métricas e mapa
"""

import requests
import json
from datetime import datetime

def comparar_dados_brutos():
    """Compara os dados brutos entre os dois endpoints"""

    print("🔍 COMPARAÇÃO DE DADOS BRUTOS: KPIs vs MAPA")
    print("=" * 70)

    base_url = "http://localhost:8000"

    try:
        # Obter dados de ambos os endpoints
        print("📡 Obtendo dados dos endpoints...")

        # KPIs
        kpi_response = requests.get(f"{base_url}/api/metrics/overview?periodo=30d")
        kpi_data = kpi_response.json()

        # Mapa
        mapa_response = requests.get(f"{base_url}/api/mapa-calor-problemas?periodo=30d")
        mapa_data = mapa_response.json()

        print("✅ Dados obtidos com sucesso!")
        print()

        # Análise das estatísticas
        stats_mapa = mapa_data.get("estatisticas", {})
        print("📊 ESTATÍSTICAS DO MAPA:")
        print(f"   Total de registros processados: {stats_mapa.get('total_registros_processados', 'N/A')}")
        print(f"   Pontos geocodificados: {stats_mapa.get('pontos_geocodificados', 'N/A')}")
        print(f"   IDs únicos processados: {stats_mapa.get('ids_unicos_processados', 'N/A')}")
        print(f"   Duplicatas removidas: {stats_mapa.get('duplicatas_removidas', 'N/A')}")
        print()

        # Comparar totais por status
        canceladas_kpi = len(kpi_data.get("canceladas", []))
        concluidas_kpi = len(kpi_data.get("concluidas", []))
        perdidas_kpi = len(kpi_data.get("perdidas", []))

        pontos_mapa = mapa_data.get("pontos", [])
        canceladas_mapa = len([p for p in pontos_mapa if p.get("status") == "cancelada"])
        concluidas_mapa = len([p for p in pontos_mapa if p.get("status") == "concluida"])
        perdidas_mapa = len([p for p in pontos_mapa if p.get("status") == "perdida"])

        print("📈 COMPARAÇÃO DE TOTAIS:")
        print("-" * 40)
        print(f"{'Status':<12} {'KPIs':<8} {'Mapa':<8} {'Diferença':<10}")
        print("-" * 40)
        print(f"{'Canceladas':<12} {canceladas_kpi:<8} {canceladas_mapa:<8} {canceladas_kpi - canceladas_mapa:<10}")
        print(f"{'Concluídas':<12} {concluidas_kpi:<8} {concluidas_mapa:<8} {concluidas_kpi - concluidas_mapa:<10}")
        print(f"{'Perdidas':<12} {perdidas_kpi:<8} {perdidas_mapa:<8} {perdidas_kpi - perdidas_mapa:<10}")
        print()

        # Investigar especificamente as corridas canceladas
        print("🔍 ANÁLISE ESPECÍFICA: CANCELADAS")
        print("-" * 35)

        canceladas_kpi_list = kpi_data.get("canceladas", [])

        # Verificar se as corridas canceladas têm IDs únicos
        ids_canceladas_kpi = set()
        for corrida in canceladas_kpi_list:
            ride_id = corrida.get("id_corrida")
            if ride_id:
                ids_canceladas_kpi.add(str(ride_id))

        print(f"IDs únicos de canceladas nos KPIs: {len(ids_canceladas_kpi)}")

        # Verificar se há duplicatas
        if len(ids_canceladas_kpi) != len(canceladas_kpi_list):
            print(f"⚠️  DUPLICATAS ENCONTRADAS: {len(canceladas_kpi_list) - len(ids_canceladas_kpi)} duplicatas")
        else:
            print("✅ Nenhuma duplicata encontrada nas canceladas dos KPIs")

        # Verificar período das corridas canceladas
        print("\n📅 VERIFICAÇÃO DE PERÍODO:")
        periodo_atual = datetime.now()
        periodo_30d_atras = periodo_atual.replace(day=periodo_atual.day - 30) if periodo_atual.day > 30 else periodo_atual.replace(month=periodo_atual.month - 1, day=periodo_atual.day)

        corridas_fora_periodo = 0
        for corrida in canceladas_kpi_list:
            data_str = corrida.get("hora", "")
            if data_str:
                try:
                    # Tentar diferentes formatos de data
                    if "T" in data_str:
                        dt_corrida = datetime.fromisoformat(data_str.replace("Z", "+00:00"))
                    else:
                        dt_corrida = datetime.strptime(data_str, "%Y-%m-%d %H:%M:%S")

                    if dt_corrida < periodo_30d_atras or dt_corrida > periodo_atual:
                        corridas_fora_periodo += 1
                except Exception as e:
                    print(f"❌ Erro ao parsear data: {data_str} - {str(e)}")

        print(f"Corridas canceladas fora do período de 30 dias: {corridas_fora_periodo}")

        # Verificar endereços vazios ou inválidos
        enderecos_vazios = 0
        enderecos_invalidos = 0

        for corrida in canceladas_kpi_list:
            endereco = corrida.get("local", "").strip()
            if not endereco:
                enderecos_vazios += 1
            elif len(endereco) < 10:
                enderecos_invalidos += 1

        print(f"Endereços vazios: {enderecos_vazios}")
        print(f"Endereços muito curtos (< 10 chars): {enderecos_invalidos}")

        # Verificar se o problema está na geocodificação
        print("\n🌍 ANÁLISE DE GEOCODIFICAÇÃO:")
        print("-" * 30)

        # Simular geocodificação para alguns endereços
        enderecos_teste = []
        for corrida in canceladas_kpi_list[:3]:  # Testar primeiros 3
            endereco = corrida.get("local", "").strip()
            if endereco:
                enderecos_teste.append(endereco[:50])

        print("Endereços de exemplo para geocodificação:")
        for i, endereco in enumerate(enderecos_teste, 1):
            print(f"{i}. {endereco}...")

        print("\n💡 POSSÍVEIS CAUSAS IDENTIFICADAS:")
        print("-" * 35)

        if corridas_fora_periodo > 0:
            print(f"1. 📅 PERÍODO: {corridas_fora_periodo} corridas fora do período de 30 dias")

        if enderecos_vazios > 0 or enderecos_invalidos > 0:
            print(f"2. 📍 ENDEREÇOS: {enderecos_vazios + enderecos_invalidos} corridas com endereços problemáticos")

        if len(ids_canceladas_kpi) != canceladas_mapa:
            print("3. 🔢 CONTAGEM: Diferença entre IDs únicos e pontos no mapa")

        print("4. 🗺️ GEOCODIFICAÇÃO: Endereços podem não estar sendo geocodificados")
        print("5. ⚙️ LÓGICA: Possível diferença na lógica de processamento entre endpoints")

        print("\n🔧 RECOMENDAÇÕES PARA DEBUG:")
        print("-" * 30)
        print("1. Adicionar logs detalhados no endpoint do mapa")
        print("2. Verificar se a geocodificação está funcionando")
        print("3. Comparar a estrutura dos dados brutos")
        print("4. Testar com uma corrida cancelada específica")
        print("5. Verificar se há filtros adicionais sendo aplicados")

        print("\n" + "=" * 70)
        print("🏁 COMPARAÇÃO DE DADOS BRUTOS CONCLUÍDA")

    except Exception as e:
        print(f"❌ ERRO na comparação: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    comparar_dados_brutos()