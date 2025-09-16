#!/usr/bin/env python3
"""
Script para testar e melhorar a função is_valid_address
"""

import re

def is_valid_address_original(address_str):
    """
    Função original - muito rigorosa
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

def is_valid_address_melhorada(address_str):
    """
    Versão melhorada - mais permissiva mas ainda segura
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

def testar_enderecos():
    """Testa a função com os endereços problemáticos"""

    enderecos_teste = [
        "566, Rua João Florentino de Mello, Nova Bandeirantes, Nova B...",
        "Nova Monte Verde, Mato Grosso...",
        "Travessa Eldorado, 128, Nova Bandeirantes, Mato Gross...",
        "000, Nova Bandeirantes, Nova Bandeirantes, Brasil, Setor...",
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

    print("🧪 TESTE DA FUNÇÃO IS_VALID_ADDRESS")
    print("=" * 80)
    print(f"{'Endereço':<50} {'Original':<10} {'Melhorada':<10}")
    print("-" * 80)

    for endereco in enderecos_teste:
        original = is_valid_address_original(endereco)
        melhorada = is_valid_address_melhorada(endereco)
        status_orig = "✅" if original else "❌"
        status_mel = "✅" if melhorada else "❌"

        print(f"{endereco[:48]:<50} {status_orig:<10} {status_mel:<10}")

    print("\n📊 RESUMO DOS TESTES:")
    print("-" * 40)

    validos_original = sum(1 for e in enderecos_teste if is_valid_address_original(e))
    validos_melhorada = sum(1 for e in enderecos_teste if is_valid_address_melhorada(e))

    print(f"Endereços válidos (Original): {validos_original}/{len(enderecos_teste)}")
    print(f"Endereços válidos (Melhorada): {validos_melhorada}/{len(enderecos_teste)}")
    print(f"Melhoria: +{validos_melhorada - validos_original} endereços")

if __name__ == "__main__":
    testar_enderecos()