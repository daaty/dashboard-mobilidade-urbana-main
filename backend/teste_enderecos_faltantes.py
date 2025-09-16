#!/usr/bin/env python3
"""
Teste específico dos endereços faltantes com a função melhorada
"""

import re

def is_valid_address_melhorada(address_str):
    """Versão melhorada da função is_valid_address"""
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
    # 1. Contém indicadores de endereço (expandido para Mato Grosso)
    address_indicators = [
        'rua', 'avenida', 'av.', 'alameda', 'travessa', 'praça',
        'bairro', 'centro', 'vila', 'jardim', 'parque',
        'setor', 'loteamento', 'condomínio', 'residencial',
        'estrada', 'rodovia', 'km', 'número', 'n°', 'nº',
        'hospital', 'shopping', 'supermercado', 'farmacia',
        'escola', 'universidade', 'aeroporto', 'rodoviária',
        'cidade', 'município', 'distrito', 'zona',
        # Indicadores específicos de Mato Grosso
        'linha', 'ramal', 'sítio', 'fazenda', 'chácara',
        'comunidade', 'aglomeração', 'povoado', 'aldeia'
    ]

    has_address_indicator = any(indicator in address_lower for indicator in address_indicators)

    # 2. Tem formato estruturado (separado por vírgulas)
    has_comma_structure = ',' in address and len(address.split(',')) >= 2

    # 3. Contém nome de cidade/estado brasileiro (expandido)
    brazilian_locations = [
        'mato grosso', 'nova bandeirantes', 'peixoto de azevedo',
        'nova monte verde', 'guarantã do norte', 'brasil',
        'acre', 'alagoas', 'amapá', 'amazonas', 'bahia', 'ceará',
        'distrito federal', 'espírito santo', 'goiás', 'maranhão',
        'mato grosso do sul', 'minas gerais', 'pará', 'paraíba',
        'paraná', 'pernambuco', 'piauí', 'rio de janeiro',
        'rio grande do norte', 'rio grande do sul', 'rondônia',
        'roraima', 'santa catarina', 'são paulo', 'sergipe', 'tocantins',
        # Cidades específicas de Mato Grosso
        'cuiabá', 'várzea grande', 'rondonópolis', 'sinop',
        'tangará da serra', 'sorriso', 'cáceres', 'barra do garças'
    ]

    has_brazilian_location = any(location in address_lower for location in brazilian_locations)

    # 4. Parece coordenada geográfica (latitude,longitude)
    is_coordinate = bool(re.match(r'^-?\d+\.\d+,\s*-?\d+\.\d+$', address.strip()))

    # 5. Parece código Plus Code do Google (formato como 2G9F+68)
    is_plus_code = bool(re.match(r'^[A-Z0-9]{4,8}\+[A-Z0-9]{2,3}', address))

    # 6. Parece endereço estruturado (número + nome + cidade)
    # Exemplo: "1250, Rua Curitiba, Jardim Vitória"
    is_structured_address = bool(re.match(r'^\d+\s*,?\s*[A-Za-zÀ-ÿ]', address))

    # ACEITAR se qualquer uma das condições for verdadeira
    return (has_address_indicator or
            has_comma_structure or
            has_brazilian_location or
            is_coordinate or
            is_plus_code or
            is_structured_address)

def testar_enderecos_faltantes():
    """Testa especificamente os endereços das corridas faltantes"""

    print("🎯 TESTE ESPECÍFICO DOS ENDEREÇOS FALTANTES")
    print("=" * 60)

    # Endereços das corridas que ainda estão faltando
    enderecos_faltantes = [
        "Estrada do urtigão, santa Terezinha 1, Nova Monte Verde, Nova Monte Verde...",
        "Rua Curitiba, 1250, Jardim Vitória, Guarantã do Norte, Mato Grosso...",
        "Unnamed...",
        "Unnamed..."
    ]

    print("Testando os endereços das 4 corridas canceladas que ainda faltam:")
    print()

    validos = 0
    for i, endereco in enumerate(enderecos_faltantes, 1):
        valido = is_valid_address_melhorada(endereco)

        status = "✅ VÁLIDO" if valido else "❌ INVÁLIDO"
        print("2d")

        if valido:
            validos += 1

            # Mostrar por que foi aceito
            print("      🎯 ACEITO POR:")
            endereco_lower = endereco.lower()

            if any(ind in endereco_lower for ind in ['estrada', 'rua', 'avenida', 'linha', 'ramal']):
                print("         - Tem indicador de endereço")
            if ',' in endereco and len(endereco.split(',')) >= 2:
                print("         - Tem estrutura com vírgulas")
            if any(loc in endereco_lower for loc in ['mato grosso', 'nova monte verde', 'guarantã']):
                print("         - Contém localização brasileira")
            if re.match(r'^\d+\s*,?\s*[A-Za-zÀ-ÿ]', endereco):
                print("         - Parece endereço estruturado")
        else:
            # Mostrar por que foi rejeitado
            print("      ❌ REJEITADO POR:")
            if len(endereco) < 5:
                print("         - Endereço muito curto")
            elif re.match(r'^unnamed', endereco.lower()):
                print("         - É um placeholder 'unnamed'")
            else:
                print("         - Não atende aos critérios de endereço")

        print()

    print("=" * 60)
    print("📊 RESULTADO:")
    print(f"   Endereços testados: {len(enderecos_faltantes)}")
    print(f"   Endereços válidos: {validos}")
    print(f"   Endereços inválidos: {len(enderecos_faltantes) - validos}")
    print(f"   Taxa de validação: {(validos/len(enderecos_faltantes)*100):.1f}%")
    if validos >= 2:
        print("✅ RESULTADO: A função melhorada deve corrigir pelo menos 2 dos 4 endereços!")
        print("   Isso reduziria a diferença de 5 para no máximo 3 corridas.")
    else:
        print("❌ RESULTADO: A função melhorada não resolve o problema principal.")
        print("   Ainda há muitos endereços sendo rejeitados.")

    print("\n🔧 ANÁLISE DETALHADA:")
    print("   1. 'Estrada do urtigão...' - Deve ser ACEITO (tem 'estrada' + cidades)")
    print("   2. 'Rua Curitiba...' - Deve ser ACEITO (tem 'rua' + cidades + MT)")
    print("   3. 'Unnamed...' - Deve ser REJEITADO (placeholder)")
    print("   4. 'Unnamed...' - Deve ser REJEITADO (placeholder)")

    print("\n📈 EXPECTATIVA:")
    print("   Com essa melhoria, devemos ver pelo menos 2 corridas a mais no mapa.")
    print("   A diferença deve cair de 5 para 3 (ou menos).")

if __name__ == "__main__":
    testar_enderecos_faltantes()