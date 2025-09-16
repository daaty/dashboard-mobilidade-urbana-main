#!/usr/bin/env python3
"""
Script para investigar a estrutura dos dados brutos no banco de dados
"""

import requests
import json
from datetime import datetime

def investigar_estrutura_dados():
    """Investiga a estrutura dos dados brutos no banco"""

    print("🔍 INVESTIGAÇÃO DA ESTRUTURA DOS DADOS BRUTOS")
    print("=" * 60)

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

        # Investigar a estrutura das corridas canceladas nos KPIs
        canceladas_kpi = kpi_data.get("canceladas", [])

        print("📊 ESTRUTURA DOS DADOS - CANCELADAS NOS KPIs:")
        print("-" * 45)

        if canceladas_kpi:
            primeira_cancelada = canceladas_kpi[0]
            print("Campos disponíveis na primeira corrida cancelada:")
            for key, value in primeira_cancelada.items():
                tipo_valor = type(value).__name__
                if isinstance(value, str) and len(value) > 50:
                    value_preview = value[:47] + "..."
                else:
                    value_preview = str(value)
                print(f"  {key}: {value_preview} ({tipo_valor})")

            print(f"\nTotal de campos: {len(primeira_cancelada)}")
        else:
            print("Nenhuma corrida cancelada encontrada nos KPIs")

        print()

        # Investigar pontos no mapa
        pontos_mapa = mapa_data.get("pontos", [])
        canceladas_mapa = [p for p in pontos_mapa if p.get("status") == "cancelada"]

        print("🗺️ ESTRUTURA DOS DADOS - CANCELADAS NO MAPA:")
        print("-" * 40)

        if canceladas_mapa:
            primeiro_ponto = canceladas_mapa[0]
            print("Campos disponíveis no primeiro ponto cancelado:")
            for key, value in primeiro_ponto.items():
                tipo_valor = type(value).__name__
                if isinstance(value, str) and len(value) > 50:
                    value_preview = value[:47] + "..."
                else:
                    value_preview = str(value)
                print(f"  {key}: {value_preview} ({tipo_valor})")

            print(f"\nTotal de campos: {len(primeiro_ponto)}")
        else:
            print("Nenhuma corrida cancelada encontrada no mapa")

        print()

        # Comparar IDs entre os dois
        print("🔗 COMPARAÇÃO DE IDs:")
        print("-" * 20)

        # IDs das canceladas nos KPIs
        ids_kpi = set()
        for corrida in canceladas_kpi:
            # Tentar diferentes campos que podem conter ID
            for campo in ["id_corrida", "id", "ride_id", "corrida_id"]:
                if campo in corrida and corrida[campo]:
                    ids_kpi.add(str(corrida[campo]))
                    break

        # IDs das canceladas no mapa (não há ID direto, usar combinação única)
        ids_mapa = set()
        for ponto in canceladas_mapa:
            endereco = ponto.get("endereco", "")
            data = ponto.get("data", "")
            unique_id = f"{endereco}|{data}"
            ids_mapa.add(unique_id)

        print(f"IDs únicos nas canceladas dos KPIs: {len(ids_kpi)}")
        print(f"IDs únicos nas canceladas do mapa: {len(ids_mapa)}")

        # Verificar se há IDs em comum (se os dados são da mesma fonte)
        if ids_kpi and ids_mapa:
            # Para comparar, vamos ver se os endereços dos KPIs aparecem nos pontos do mapa
            enderecos_kpi = set()
            for corrida in canceladas_kpi:
                endereco = corrida.get("local", "").strip()
                if endereco:
                    enderecos_kpi.add(endereco)

            enderecos_mapa = set()
            for ponto in canceladas_mapa:
                endereco = ponto.get("endereco", "").strip()
                if endereco:
                    enderecos_mapa.add(endereco)

            enderecos_comuns = enderecos_kpi.intersection(enderecos_mapa)
            enderecos_somente_kpi = enderecos_kpi - enderecos_mapa
            enderecos_somente_mapa = enderecos_mapa - enderecos_kpi

            print(f"Endereços em comum: {len(enderecos_comuns)}")
            print(f"Endereços só nos KPIs: {len(enderecos_somente_kpi)}")
            print(f"Endereços só no mapa: {len(enderecos_somente_mapa)}")

            if enderecos_somente_kpi:
                print("\n📍 ENDEREÇOS SÓ NOS KPIs (não aparecem no mapa):")
                for endereco in list(enderecos_somente_kpi)[:3]:  # Mostrar primeiros 3
                    print(f"  - {endereco[:50]}...")

        print()

        # Análise temporal
        print("⏰ ANÁLISE TEMPORAL:")
        print("-" * 18)

        periodo_atual = datetime.now()
        periodo_30d_atras = periodo_atual.replace(day=periodo_atual.day - 30) if periodo_atual.day > 30 else periodo_atual.replace(month=periodo_atual.month - 1, day=periodo_atual.day)

        corridas_fora_periodo_kpi = 0
        corridas_fora_periodo_mapa = 0

        for corrida in canceladas_kpi:
            data_str = corrida.get("hora", "")
            if data_str:
                try:
                    if "T" in data_str:
                        dt_corrida = datetime.fromisoformat(data_str.replace("Z", "+00:00"))
                    else:
                        dt_corrida = datetime.strptime(data_str, "%Y-%m-%d %H:%M:%S")

                    if dt_corrida < periodo_30d_atras or dt_corrida > periodo_atual:
                        corridas_fora_periodo_kpi += 1
                except:
                    pass

        for ponto in canceladas_mapa:
            data_str = ponto.get("data", "")
            if data_str:
                try:
                    if "T" in data_str:
                        dt_corrida = datetime.fromisoformat(data_str.replace("Z", "+00:00"))
                    else:
                        dt_corrida = datetime.strptime(data_str, "%Y-%m-%d %H:%M:%S")

                    if dt_corrida < periodo_30d_atras or dt_corrida > periodo_atual:
                        corridas_fora_periodo_mapa += 1
                except:
                    pass

        print(f"Corridas canceladas fora do período (KPIs): {corridas_fora_periodo_kpi}")
        print(f"Corridas canceladas fora do período (Mapa): {corridas_fora_periodo_mapa}")

        print()

        print("💡 DIAGNÓSTICO FINAL:")
        print("-" * 18)

        if len(ids_kpi) != len(canceladas_mapa):
            print(f"🔴 DIFERENÇA PRINCIPAL: {len(ids_kpi)} canceladas nos KPIs vs {len(canceladas_mapa)} no mapa")

        if enderecos_somente_kpi:
            print(f"🔴 ENDEREÇOS FALTANTES: {len(enderecos_somente_kpi)} endereços dos KPIs não aparecem no mapa")

        if corridas_fora_periodo_kpi > 0 or corridas_fora_periodo_mapa > 0:
            print("🔴 PERÍODO: Algumas corridas podem estar fora do período de 30 dias")

        print("🔴 CONCLUSÃO: Os dados parecem vir da mesma fonte, mas há diferença no processamento")

        print("\n🔧 PRÓXIMAS AÇÕES RECOMENDADAS:")
        print("-" * 30)
        print("1. Verificar logs detalhados do endpoint do mapa")
        print("2. Adicionar debug prints na geocodificação")
        print("3. Comparar exatamente os mesmos registros brutos")
        print("4. Verificar se há filtros adicionais no mapa")
        print("5. Testar geocodificação manual dos endereços faltantes")

        print("\n" + "=" * 60)
        print("🏁 INVESTIGAÇÃO DA ESTRUTURA CONCLUÍDA")

    except Exception as e:
        print(f"❌ ERRO na investigação: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    investigar_estrutura_dados()