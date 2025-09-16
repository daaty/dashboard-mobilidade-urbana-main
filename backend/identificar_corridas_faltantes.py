#!/usr/bin/env python3
"""
Script para identificar exatamente quais corridas canceladas estão faltando no mapa
"""

import requests
import json

def identificar_corridas_faltantes():
    """Identifica exatamente quais corridas canceladas estão faltando"""

    print("🔍 IDENTIFICANDO CORRIDAS CANCELADAS FALTANTES")
    print("=" * 60)

    base_url = "http://localhost:8000"

    try:
        # Obter dados de ambos os endpoints
        print("📡 Obtendo dados dos endpoints...")

        kpi_response = requests.get(f"{base_url}/api/metrics/overview?periodo=30d")
        kpi_data = kpi_response.json()

        mapa_response = requests.get(f"{base_url}/api/mapa-calor-problemas?periodo=30d")
        mapa_data = mapa_response.json()

        print("✅ Dados obtidos com sucesso!")
        print()

        # Extrair corridas canceladas
        canceladas_kpi = kpi_data.get("canceladas", [])
        pontos_mapa = mapa_data.get("pontos", [])
        canceladas_mapa = [p for p in pontos_mapa if p.get("status") == "cancelada"]

        print(f"📊 CANCELADAS KPIs: {len(canceladas_kpi)}")
        print(f"🗺️ CANCELADAS MAPA: {len(canceladas_mapa)}")
        print(f"❌ FALTANTES: {len(canceladas_kpi) - len(canceladas_mapa)}")
        print()

        # Criar mapa de endereços do mapa para comparação
        enderecos_mapa = set()
        for ponto in canceladas_mapa:
            endereco = ponto.get("endereco", "").strip().lower()
            if endereco:
                # Normalizar endereço para comparação
                endereco_norm = endereco.replace("...", "").strip()
                enderecos_mapa.add(endereco_norm)

        print("🔍 ANALISANDO CORRIDAS FALTANTES:")
        print("-" * 40)

        corridas_faltantes = []
        for corrida in canceladas_kpi:
            endereco_kpi = corrida.get("local", "").strip()

            # Verificar se este endereço aparece no mapa
            endereco_encontrado = False
            for endereco_mapa in enderecos_mapa:
                # Comparação flexível
                if (endereco_kpi.lower().replace("...", "").strip() in endereco_mapa or
                    endereco_mapa in endereco_kpi.lower().replace("...", "").strip()):
                    endereco_encontrado = True
                    break

            if not endereco_encontrado:
                corridas_faltantes.append({
                    "id": corrida.get("id_corrida", "N/A"),
                    "nome": corrida.get("nome", "N/A"),
                    "endereco": endereco_kpi,
                    "hora": corrida.get("hora", "N/A"),
                    "motivo": corrida.get("motivo", "N/A")
                })

        print(f"Encontradas {len(corridas_faltantes)} corridas canceladas faltantes:")
        print()

        for i, corrida in enumerate(corridas_faltantes, 1):
            print(f"{i}. ID: {corrida['id']}")
            print(f"   Nome: {corrida['nome']}")
            print(f"   Endereço: {corrida['endereco'][:60]}...")
            print(f"   Hora: {corrida['hora']}")
            print(f"   Motivo: {corrida['motivo']}")
            print()

        # Análise dos endereços faltantes
        print("🔧 ANÁLISE DOS ENDEREÇOS FALTANTES:")
        print("-" * 35)

        if corridas_faltantes:
            print("Características dos endereços faltantes:")

            for corrida in corridas_faltantes:
                endereco = corrida['endereco']
                print(f"\n📍 '{endereco[:50]}...'")

                # Análise detalhada
                tem_rua = 'rua' in endereco.lower()
                tem_avenida = 'avenida' in endereco.lower()
                tem_travessa = 'travessa' in endereco.lower()
                tem_praca = 'praça' in endereco.lower()
                tem_virgulas = ',' in endereco
                tem_mato_grosso = 'mato grosso' in endereco.lower()
                tem_cidade = any(cidade in endereco.lower() for cidade in ['nova bandeirantes', 'peixoto de azevedo', 'nova monte verde', 'guarantã do norte'])
                is_plus_code = any(char.isdigit() for char in endereco[:10]) and any(char.isupper() for char in endereco[:10])
                tem_telefone = any(char.isdigit() for char in endereco[:15])

                print(f"   ✅ Tem indicador rua/av/trav/praça: {tem_rua or tem_avenida or tem_travessa or tem_praca}")
                print(f"   ✅ Tem vírgulas: {tem_virgulas}")
                print(f"   ✅ Tem Mato Grosso: {tem_mato_grosso}")
                print(f"   ✅ Tem nome de cidade: {tem_cidade}")
                print(f"   ✅ Parece Plus Code: {is_plus_code}")
                print(f"   ⚠️  Pode ser telefone: {tem_telefone}")
                print(f"   📏 Comprimento: {len(endereco)} caracteres")

        print("\n" + "=" * 60)
        print("💡 DIAGNÓSTICO:")
        print("-" * 12)

        if len(corridas_faltantes) == 0:
            print("✅ Nenhuma corrida cancelada faltante! Problema resolvido!")
        elif len(corridas_faltantes) <= 2:
            print(f"✅ Quase resolvido! Apenas {len(corridas_faltantes)} corridas faltantes.")
            print("   Provavelmente problema de geocodificação ou matching de endereços.")
        else:
            print(f"❌ Ainda há {len(corridas_faltantes)} corridas canceladas faltantes.")
            print("   Possíveis causas:")
            print("   1. Endereços não estão sendo extraídos corretamente")
            print("   2. Geocodificação está falhando para estes endereços")
            print("   3. Filtros adicionais estão removendo estas corridas")
            print("   4. Problema na detecção de telefones vs endereços")

        print("\n🔧 PRÓXIMAS AÇÕES RECOMENDADAS:")
        print("-" * 30)
        print("1. Verificar se estes endereços passam na validação is_valid_address")
        print("2. Testar geocodificação manual destes endereços")
        print("3. Adicionar logs detalhados para estes casos específicos")
        print("4. Verificar se há diferença na estrutura dos dados brutos")

        print("\n" + "=" * 60)
        print("🏁 IDENTIFICAÇÃO CONCLUÍDA")

    except Exception as e:
        print(f"❌ ERRO na identificação: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    identificar_corridas_faltantes()