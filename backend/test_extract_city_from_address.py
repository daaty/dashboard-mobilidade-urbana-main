#!/usr/bin/env python3
"""
Teste da nova função extract_city_from_address
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from services.city_service import extract_city_from_address

def test_extract_city_from_address():
    """Testa a extração de cidades de endereços completos"""
    print("🧪 TESTANDO EXTRAÇÃO DE CIDADES DE ENDEREÇOS")
    print("=" * 50)

    test_addresses = [
        "R. Piauí, 118 - Mãe De Deus, Peixoto De Azevedo - Mt, 78530-000, Brasil",
        "Hospital municipal de Nova Monte Verde - Rua Manoel Rodrigues de Souza, Nova Monte Verde - State of Mato Grosso, Brazil",
        "Avenida senador jonas pinheiro 35, Nova Monte Verde, Nova Monte Verde, Brasil",
        "Av. Brasil, 854 - Centro Novo, Peixoto De Azevedo - Mt",
        "Rua João Ferreira Da Silva N 52, Nova Monte Verde, Nova Monte Verde, Brasil, Portão Amarelo",
        "2Ggx+2X Nova Monte Verde",
        "MATUPA - MT",
        "Centro, Guaranta Do Norte - MT"
    ]

    print("📋 Testes de extração:")
    for address in test_addresses:
        extracted = extract_city_from_address(address)
        status = "✅" if extracted else "❌"
        print(f"{status} '{address[:60]}...' → '{extracted}'")

if __name__ == "__main__":
    test_extract_city_from_address()