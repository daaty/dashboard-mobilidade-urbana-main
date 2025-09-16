#!/usr/bin/env python3
"""
Script para investigar especificamente as 5 corridas canceladas que estão faltando no mapa
"""

import requests
import json
from datetime import datetime

def investigar_canceladas_faltantes():
    """Investiga as corridas canceladas que estão nos KPIs mas não no mapa"""

    print("🔍 INVESTIGAÇÃO: CORRIDAS CANCELADAS FALTANTES NO MAPA")
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

        # Extrair corridas canceladas dos KPIs
        canceladas_kpi = kpi_data.get("canceladas", [])
        print(f"📊 CANCELADAS NOS KPIs: {len(canceladas_kpi)} corridas")

        # Extrair pontos cancelados do mapa
        pontos_mapa = mapa_data.get("pontos", [])
        canceladas_mapa = [p for p in pontos_mapa if p.get("status") == "cancelada"]
        print(f"🗺️ CANCELADAS NO MAPA: {len(canceladas_mapa)} pontos")
        print()

        # Criar sets de IDs para comparação
        ids_kpi = set()
        for corrida in canceladas_kpi:
            ride_id = corrida.get("id_corrida")
            if ride_id:
                ids_kpi.add(str(ride_id))

        ids_mapa = set()
        for ponto in canceladas_mapa:
            # O mapa não tem ID direto, vamos usar uma combinação única
            endereco = ponto.get("endereco", "")
            data = ponto.get("data", "")
            unique_id = f"{endereco}|{data}"
            ids_mapa.add(unique_id)

        # Encontrar diferenças
        canceladas_faltantes = []
        for corrida in canceladas_kpi:
            ride_id = corrida.get("id_corrida")
            endereco = corrida.get("local", "")  # Usar o campo 'local' que contém o endereço
            data = corrida.get("hora", "")

            # Criar ID único similar ao usado no mapa
            unique_id = f"{endereco}|{data}"

            if unique_id not in ids_mapa:
                canceladas_faltantes.append({
                    "id_corrida": ride_id,
                    "endereco": endereco,
                    "data": data,
                    "nome": corrida.get("nome", "N/A"),
                    "motivo": corrida.get("motivo", "N/A")
                })

        print(f"❌ CANCELADAS FALTANTES NO MAPA: {len(canceladas_faltantes)}")
        print()

        if canceladas_faltantes:
            print("📋 DETALHES DAS CANCELADAS FALTANTES:")
            print("-" * 50)

            for i, corrida in enumerate(canceladas_faltantes, 1):
                print(f"{i}. ID: {corrida['id_corrida']}")
                print(f"   Nome: {corrida['nome']}")
                print(f"   Endereço: {corrida['endereco'][:60]}...")
                print(f"   Data: {corrida['data']}")
                print(f"   Motivo: {corrida['motivo']}")
                print()

            # Análise dos endereços
            print("🔍 ANÁLISE DOS ENDEREÇOS:")
            print("-" * 30)

            enderecos_invalidos = 0
            enderecos_vazios = 0
            enderecos_com_telefone = 0

            for corrida in canceladas_faltantes:
                endereco = corrida['endereco'].strip()

                if not endereco:
                    enderecos_vazios += 1
                elif any(char.isdigit() for char in endereco[:15]):  # Possível telefone
                    enderecos_com_telefone += 1
                    print(f"📞 POSSÍVEL TELEFONE: {endereco[:30]}...")
                else:
                    # Verificar se é um endereço válido
                    endereco_lower = endereco.lower()
                    indicadores_endereco = ['rua', 'avenida', 'av.', 'alameda', 'travessa', 'praça', 'bairro']
                    tem_indicador = any(indicador in endereco_lower for indicador in indicadores_endereco)

                    if not tem_indicador:
                        enderecos_invalidos += 1
                        print(f"❌ ENDEREÇO INVÁLIDO: {endereco[:50]}...")

            print()
            print("📊 RESUMO DA ANÁLISE:")
            print(f"   Endereços vazios: {enderecos_vazios}")
            print(f"   Possíveis telefones: {enderecos_com_telefone}")
            print(f"   Endereços inválidos: {enderecos_invalidos}")
            print()

        # Análise da lógica de extração
        print("🔧 ANÁLISE DA LÓGICA DE EXTRAÇÃO:")
        print("-" * 40)

        print("1. O mapa usa a seguinte lógica para corridas canceladas:")
        print("   - Detecta se rec[5] é telefone (regex para +5566...)")
        print("   - Se for telefone: busca endereço em rec[8], rec[9], rec[6]")
        print("   - Se não for telefone: usa rec[5] e rec[6] como endereços")
        print()

        print("2. Possíveis causas das canceladas faltantes:")
        print("   - Endereços vazios ou inválidos")
        print("   - Telefones sendo confundidos com endereços")
        print("   - Problemas na detecção de telefones")
        print("   - Endereços não geocodificáveis")
        print()

        print("3. Sugestões de correção:")
        print("   - Melhorar validação de endereços")
        print("   - Ajustar regex de detecção de telefones")
        print("   - Adicionar fallbacks para endereços vazios")
        print("   - Melhorar função is_valid_address()")

        print()
        print("=" * 60)
        print("🏁 INVESTIGAÇÃO CONCLUÍDA")

    except Exception as e:
        print(f"❌ ERRO na investigação: {str(e)}")
        print("Verifique se o servidor FastAPI está rodando na porta 8000")

if __name__ == "__main__":
    investigar_canceladas_faltantes()