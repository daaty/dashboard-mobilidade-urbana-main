#!/usr/bin/env python3
"""
Script para testar a geocodificação dos endereços das corridas canceladas
"""

import requests
import json
import re
from datetime import datetime

def testar_geocodificacao():
    """Testa a geocodificação dos endereços das corridas canceladas"""

    print("🗺️ TESTE DE GEOCODIFICAÇÃO: CORRIDAS CANCELADAS")
    print("=" * 60)

    base_url = "http://localhost:8000"

    try:
        # Obter dados dos KPIs
        print("📡 Obtendo dados das corridas canceladas...")

        kpi_response = requests.get(f"{base_url}/api/metrics/overview?periodo=30d")
        kpi_data = kpi_response.json()

        canceladas_kpi = kpi_data.get("canceladas", [])
        print(f"✅ Encontradas {len(canceladas_kpi)} corridas canceladas")
        print()

        # Coletar endereços únicos para teste
        enderecos_unicos = set()
        for corrida in canceladas_kpi:
            endereco = corrida.get("local", "").strip()
            if endereco:
                enderecos_unicos.add(endereco)

        print(f"📍 Endereços únicos encontrados: {len(enderecos_unicos)}")
        print()

        # Testar geocodificação de alguns endereços
        print("🔍 TESTANDO GEOCODIFICAÇÃO:")
        print("-" * 30)

        enderecos_teste = list(enderecos_unicos)[:5]  # Testar primeiros 5

        for i, endereco in enumerate(enderecos_teste, 1):
            print(f"\n{i}. Testando endereço: {endereco[:50]}...")

            # Simular o processo de geocodificação
            # Verificar se o endereço parece válido
            endereco_lower = endereco.lower()

            # Verificar indicadores de endereço
            indicadores = ['rua', 'avenida', 'av.', 'alameda', 'travessa', 'praça',
                          'bairro', 'centro', 'vila', 'jardim', 'parque', 'setor',
                          'estrada', 'rodovia', 'km', 'número', 'n°', 'nº']

            has_indicador = any(indicador in endereco_lower for indicador in indicadores)
            has_virgulas = ',' in endereco
            has_mato_grosso = 'mato grosso' in endereco_lower
            is_plus_code = bool(re.match(r'^[A-Z0-9]{4,8}\+[A-Z0-9]{2,3}', endereco))

            print(f"   📊 Características:")
            print(f"      - Tem indicador: {'✅' if has_indicador else '❌'}")
            print(f"      - Tem vírgulas: {'✅' if has_virgulas else '❌'}")
            print(f"      - Mato Grosso: {'✅' if has_mato_grosso else '❌'}")
            print(f"      - Plus Code: {'✅' if is_plus_code else '❌'}")
            print(f"      - Comprimento: {len(endereco)} caracteres")

            # Simular geocodificação
            # Na prática, isso seria feito com Google Maps API
            geocodificavel = has_indicador or has_virgulas or has_mato_grosso or is_plus_code

            if geocodificavel:
                print("   🎯 RESULTADO: Provavelmente geocodificável")
            else:
                print("   ❌ RESULTADO: Provavelmente NÃO geocodificável")
                print("   💡 MOTIVOS:")
                if not has_indicador and not has_virgulas and not has_mato_grosso:
                    print("      - Não tem indicadores de endereço")
                if len(endereco) < 10:
                    print("      - Endereço muito curto")

        print("\n" + "=" * 60)
        print("🔍 ANÁLISE GERAL DA GEOCODIFICAÇÃO:")
        print("-" * 40)

        # Estatísticas dos endereços
        enderecos_validos = 0
        enderecos_invalidos = 0
        enderecos_plus_code = 0
        enderecos_mato_grosso = 0

        for endereco in enderecos_unicos:
            endereco_lower = endereco.lower()

            if re.match(r'^[A-Z0-9]{4,8}\+[A-Z0-9]{2,3}', endereco):
                enderecos_plus_code += 1
            elif 'mato grosso' in endereco_lower:
                enderecos_mato_grosso += 1
            elif any(ind in endereco_lower for ind in indicadores):
                enderecos_validos += 1
            else:
                enderecos_invalidos += 1

        print(f"Endereços válidos (com indicadores): {enderecos_validos}")
        print(f"Endereços Mato Grosso: {enderecos_mato_grosso}")
        print(f"Plus Codes: {enderecos_plus_code}")
        print(f"Endereços inválidos: {enderecos_invalidos}")
        print()

        print("💡 DIAGNÓSTICO:")
        print("-" * 15)

        total_enderecos = len(enderecos_unicos)
        enderecos_geocodificaveis = enderecos_validos + enderecos_mato_grosso + enderecos_plus_code

        print(f"Total de endereços únicos: {total_enderecos}")
        print(f"Endereços provavelmente geocodificáveis: {enderecos_geocodificaveis}")
        print(f"Taxa de geocodificação esperada: {(enderecos_geocodificaveis/total_enderecos*100):.1f}%")

        if enderecos_invalidos > 0:
            print(f"\n⚠️  {enderecos_invalidos} endereços podem não ser geocodificáveis")
            print("Isso explicaria por que algumas corridas não aparecem no mapa!")

        print("\n🔧 POSSÍVEIS SOLUÇÕES:")
        print("-" * 20)
        print("1. Melhorar a geocodificação para endereços de Mato Grosso")
        print("2. Adicionar suporte para Plus Codes")
        print("3. Implementar fallbacks para endereços inválidos")
        print("4. Melhorar a validação de endereços antes da geocodificação")
        print("5. Adicionar logs detalhados da geocodificação")

        print("\n" + "=" * 60)
        print("🏁 TESTE DE GEOCODIFICAÇÃO CONCLUÍDO")

    except Exception as e:
        print(f"❌ ERRO no teste de geocodificação: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    testar_geocodificacao()