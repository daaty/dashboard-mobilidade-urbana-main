#!/usr/bin/env python3
"""
Script detalhado para investigar a extração de endereços das corridas canceladas
"""

import requests
import json
import re
from datetime import datetime

def is_valid_address(address_str):
    """
    Função de validação de endereços (igual ao backend)
    """
    if not address_str or len(address_str) < 10:
        return False

    address_lower = str(address_str).lower().strip()

    # Rejeitar se contém padrões que indicam que NÃO é endereço
    invalid_patterns = [
        r'^\d{10,}$',  # Apenas números (telefones/IDs)
        r'^\+\d+',     # Telefone internacional
        r'^\d{8,11}$', # Telefone brasileiro
        r'^nan$',      # Valor nulo
        r'^--$',       # Placeholder
        r'^none$',     # None value
        r'^\s*$',      # String vazia
    ]

    for pattern in invalid_patterns:
        if re.match(pattern, address_lower):
            return False

    # Deve conter pelo menos um indicador de endereço
    address_indicators = [
        'rua', 'avenida', 'av.', 'alameda', 'travessa', 'praça',
        'bairro', 'centro', 'vila', 'jardim', 'parque',
        'setor', 'loteamento', 'condomínio', 'residencial',
        'estrada', 'rodovia', 'km', 'número', 'n°', 'nº',
        'hospital', 'shopping', 'supermercado', 'farmacia',
        'escola', 'universidade', 'aeroporto', 'rodoviária'
    ]

    has_address_indicator = any(indicator in address_lower for indicator in address_indicators)

    # Ou deve ter formato de endereço estruturado (rua, cidade, estado)
    has_comma_structure = ',' in address_lower and len(address_lower.split(',')) >= 2

    return has_address_indicator or has_comma_structure

def investigar_extracao_detalhada():
    """Investigação detalhada da extração de endereços"""

    print("🔍 INVESTIGAÇÃO DETALHADA: EXTRAÇÃO DE ENDEREÇOS CANCELADAS")
    print("=" * 80)

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

        # Análise detalhada de cada corrida cancelada
        print("🔧 ANÁLISE DETALHADA DA EXTRAÇÃO:")
        print("-" * 60)

        for i, corrida in enumerate(canceladas_kpi[:5], 1):  # Analisar primeiras 5
            print(f"\n{i}. CORRIDA ID: {corrida.get('id_corrida', 'N/A')}")
            print(f"   Nome: {corrida.get('nome', 'N/A')}")
            print(f"   Endereço KPI: {corrida.get('local', 'N/A')[:60]}...")

            endereco_kpi = corrida.get('local', '')

            # Simular a lógica de extração do mapa
            endereco_extraido = None
            telefone_detectado = False

            # Simular detecção de telefone (rec[5])
            # Como não temos os dados brutos, vamos assumir alguns cenários
            print("   📞 Simulação de detecção de telefone:")

            # Cenário 1: rec[5] não é telefone
            endereco_cenario1 = endereco_kpi if is_valid_address(endereco_kpi) else None
            print(f"      Cenário 1 (rec[5] não telefone): {'✅' if endereco_cenario1 else '❌'}")

            # Cenário 2: rec[5] é telefone, tentar rec[6]
            endereco_cenario2 = endereco_kpi if is_valid_address(endereco_kpi) else None
            print(f"      Cenário 2 (rec[5] telefone, usar rec[6]): {'✅' if endereco_cenario2 else '❌'}")

            # Cenário 3: rec[5] é telefone, tentar rec[8]
            # Simular um endereço alternativo
            endereco_alternativo = "Rua Alternativa, 123, Centro"
            endereco_cenario3 = endereco_alternativo if is_valid_address(endereco_alternativo) else None
            print(f"      Cenário 3 (rec[5] telefone, usar rec[8]): {'✅' if endereco_cenario3 else '❌'}")

            # Validação final
            endereco_final = endereco_cenario1 or endereco_cenario2 or endereco_cenario3
            print(f"   🎯 Endereço final válido: {'✅' if endereco_final else '❌'}")

            if not endereco_final:
                print("   ⚠️  MOTIVO DA FALHA:")
                if not endereco_kpi:
                    print("      - Endereço vazio no KPI")
                elif not is_valid_address(endereco_kpi):
                    print("      - Endereço não passou na validação is_valid_address()")
                    print(f"      - Comprimento: {len(endereco_kpi)} caracteres")
                    print(f"      - Contém indicadores: {any(ind in endereco_kpi.lower() for ind in ['rua', 'avenida', 'av.', 'alameda', 'travessa', 'praça'])}")
                    print(f"      - Tem vírgulas: {',' in endereco_kpi}")

        print("\n" + "=" * 80)
        print("🔍 POSSÍVEIS CAUSAS DO PROBLEMA:")
        print("-" * 40)

        print("1. 🔍 DIFERENÇA NOS DADOS BRUTOS:")
        print("   - O endpoint de métricas pode estar usando dados diferentes")
        print("   - Verificar se ambos endpoints usam a mesma fonte de dados")
        print()

        print("2. 📍 LÓGICA DE EXTRAÇÃO DIFERENTE:")
        print("   - Verificar se os índices dos campos são os mesmos")
        print("   - Comparar a lógica de detecção de telefones")
        print("   - Verificar ordem de fallback dos endereços")
        print()

        print("3. ⚙️ VALIDAÇÃO DE ENDEREÇO:")
        print("   - Função is_valid_address() pode estar rejeitando endereços válidos")
        print("   - Endereços podem estar sendo truncados ou corrompidos")
        print()

        print("4. 🗂️ FILTROS APLICADOS:")
        print("   - Filtros de período podem estar excluindo corridas")
        print("   - Filtros de cidade podem estar ativos")
        print("   - Deduplicação pode estar removendo corridas")
        print()

        print("5. 🐛 POSSÍVEIS BUGS:")
        print("   - Erro na conversão de dados JSON")
        print("   - Problema na detecção de telefones")
        print("   - Falha na extração de data/hora")
        print()

        print("📋 PRÓXIMOS PASSOS RECOMENDADOS:")
        print("-" * 35)
        print("1. Comparar os dados brutos entre os dois endpoints")
        print("2. Adicionar logs detalhados na extração de endereços")
        print("3. Testar a função is_valid_address() com casos reais")
        print("4. Verificar se há diferenças na estrutura dos dados")
        print("5. Testar com uma corrida cancelada específica")

        print("\n" + "=" * 80)
        print("🏁 INVESTIGAÇÃO DETALHADA CONCLUÍDA")

    except Exception as e:
        print(f"❌ ERRO na investigação detalhada: {str(e)}")
        print("Verifique se o servidor FastAPI está rodando na porta 8000")

if __name__ == "__main__":
    investigar_extracao_detalhada()