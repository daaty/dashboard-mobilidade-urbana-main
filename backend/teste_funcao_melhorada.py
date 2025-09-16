#!/usr/bin/env python3
"""
Script para testar a função is_valid_address melhorada com os endereços problemáticos
"""

import re

def is_valid_address_melhorada(address_str):
    """
    Versão melhorada da função is_valid_address
    """
    if not address_str:
        return False

    address = str(address_str).strip()

    # Rejeitar strings muito curtas (provavelmente não são endereços)
    if len(address) < 5:
        return False

    address_lower = address.lower()

    # Rejeitar padrões que DEFINITIVAMENTE não são endereços
    invalid_patterns = [
        r'^\d{10,}$',      # Apenas números longos (IDs)
        r'^\+\d{10,}$',    # Telefone internacional longo
        r'^\d{8,11}$',     # Telefone brasileiro (8-11 dígitos)
        r'^nan$',          # Valor nulo
        r'^--$',           # Placeholder
        r'^none$',         # None value
        r'^null$',         # Null value
        r'^\s*$',          # String vazia
        r'^unnamed$',      # Unnamed
        r'^unknown$',      # Unknown
        r'^n/a$',          # N/A
    ]

    for pattern in invalid_patterns:
        if re.match(pattern, address_lower):
            return False

    # ACEITAR se tem estrutura de endereço geográfico
    # 1. Contém indicadores de endereço
    address_indicators = [
        'rua', 'avenida', 'av.', 'alameda', 'travessa', 'praça',
        'bairro', 'centro', 'vila', 'jardim', 'parque',
        'setor', 'loteamento', 'condomínio', 'residencial',
        'estrada', 'rodovia', 'km', 'número', 'n°', 'nº',
        'hospital', 'shopping', 'supermercado', 'farmacia',
        'escola', 'universidade', 'aeroporto', 'rodoviária',
        'cidade', 'município', 'distrito', 'zona'
    ]

    has_address_indicator = any(indicator in address_lower for indicator in address_indicators)

    # 2. Tem formato estruturado (separado por vírgulas)
    has_comma_structure = ',' in address and len(address.split(',')) >= 2

    # 3. Contém nome de cidade/estado brasileiro
    brazilian_locations = [
        'mato grosso', 'nova bandeirantes', 'peixoto de azevedo',
        'nova monte verde', 'guarantã do norte', 'brasil',
        'acre', 'alagoas', 'amapá', 'amazonas', 'bahia', 'ceará',
        'distrito federal', 'espírito santo', 'goiás', 'maranhão',
        'mato grosso do sul', 'minas gerais', 'pará', 'paraíba',
        'paraná', 'pernambuco', 'piauí', 'rio de janeiro',
        'rio grande do norte', 'rio grande do sul', 'rondônia',
        'roraima', 'santa catarina', 'são paulo', 'sergipe', 'tocantins'
    ]

    has_brazilian_location = any(location in address_lower for location in brazilian_locations)

    # 4. Parece coordenada geográfica (latitude,longitude)
    is_coordinate = bool(re.match(r'^-?\d+\.\d+,\s*-?\d+\.\d+$', address.strip()))

    # 5. Parece código Plus Code do Google (formato como 2G9F+68)
    is_plus_code = bool(re.match(r'^[A-Z0-9]{4,8}\+[A-Z0-9]{2,3}', address))

    # ACEITAR se qualquer uma das condições for verdadeira
    return (has_address_indicator or
            has_comma_structure or
            has_brazilian_location or
            is_coordinate or
            is_plus_code)

def testar_enderecos_problematicos():
    """Testa os endereços problemáticos que não aparecem no mapa"""

    print("🧪 TESTE DA FUNÇÃO IS_VALID_ADDRESS MELHORADA")
    print("=" * 60)

    # Endereços que estão nos KPIs mas não no mapa
    enderecos_problematicos = [
        "566, Rua João Florentino de Mello, Nova Bandeirantes, Nova B...",
        "Nova Monte Verde, Mato Grosso...",
        "Travessa Eldorado, 128, Nova Bandeirantes, Mato Gross...",
        "000, Nova Bandeirantes, Nova Bandeirantes, Brasil, Setor pra...",
        "Estrada do urtigão, santa Terezinha 1, Nova Monte Ver...",
        "Avenida Brasil, 883, Centro, Peixoto de Azevedo, Mato...",
        "Rua Amélia Bodete, 579, Jerusalém, Peixoto de Azevedo...",
        "2G9F+68 Nova Monte Verde...",
        "Rua Curitiba, 1250, Jardim Vitória, Guarantã do Norte...",
        "Avenida senador jonas pinheiro 35, Nova Monte Verde...",
        "Unnamed...",
        "Nova Bandeirantes, Mato Grosso",
        "Peixoto de Azevedo, Mato Grosso",
        "Guarantã do Norte, Mato Grosso",
        "Centro, Nova Monte Verde",
        "Jardim Vitória, Guarantã do Norte"
    ]

    print(f"Testando {len(enderecos_problematicos)} endereços problemáticos:")
    print("-" * 50)

    enderecos_validos = 0
    enderecos_invalidos = 0

    for i, endereco in enumerate(enderecos_problematicos, 1):
        valido = is_valid_address_melhorada(endereco)

        status = "✅ VÁLIDO" if valido else "❌ INVÁLIDO"
        print("2d")

        if valido:
            enderecos_validos += 1
        else:
            enderecos_invalidos += 1

            # Diagnóstico do porquê é inválido
            print("      🔍 DIAGNÓSTICO:")

            if len(endereco) < 5:
                print("         - Endereço muito curto")
            elif re.match(r'^\d{10,}$', endereco.lower()):
                print("         - Parece ser apenas números (ID/telefone)")
            elif re.match(r'^\+\d{10,}$', endereco):
                print("         - Parece ser telefone internacional")
            elif re.match(r'^\d{8,11}$', endereco.replace(' ', '').replace('-', '')):
                print("         - Parece ser telefone brasileiro")
            elif endereco.lower().strip() in ['nan', '--', 'none', 'null', 'unnamed', 'unknown', 'n/a']:
                print("         - Valor nulo ou placeholder")
            else:
                # Verificar se tem indicadores de endereço
                indicadores = ['rua', 'avenida', 'av.', 'alameda', 'travessa', 'praça']
                has_indicador = any(ind in endereco.lower() for ind in indicadores)
                has_virgulas = ',' in endereco
                has_mato_grosso = 'mato grosso' in endereco.lower()
                is_plus_code = bool(re.match(r'^[A-Z0-9]{4,8}\+[A-Z0-9]{2,3}', endereco))

                print(f"         - Tem indicador: {has_indicador}")
                print(f"         - Tem vírgulas: {has_virgulas}")
                print(f"         - Mato Grosso: {has_mato_grosso}")
                print(f"         - Plus Code: {is_plus_code}")

    print("\n" + "=" * 60)
    print("📊 RESULTADO DO TESTE:")
    print("-" * 25)
    print(f"Endereços válidos: {enderecos_validos}/{len(enderecos_problematicos)}")
    print(f"Endereços inválidos: {enderecos_invalidos}/{len(enderecos_problematicos)}")
    print(f"Taxa de validação: {(enderecos_validos/len(enderecos_problematicos)*100):.1f}%")
    if enderecos_validos > 10:  # Se mais de 10 forem válidos, deve aparecer no mapa
        print("✅ RESULTADO: A função melhorada deve resolver o problema!")
        print("   Com essa validação, a maioria dos endereços seria aceita.")
    else:
        print("❌ RESULTADO: Ainda há endereços inválidos demais.")
        print("   Pode haver outro problema além da validação.")

    print("\n🔧 PRÓXIMAS AÇÕES:")
    print("-" * 18)
    print("1. Aplicar a função melhorada no código do backend")
    print("2. Testar o endpoint do mapa novamente")
    print("3. Verificar se as corridas canceladas agora aparecem")
    print("4. Se ainda faltarem, investigar geocodificação")

if __name__ == "__main__":
    testar_enderecos_problematicos()