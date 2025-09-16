#!/usr/bin/env python3
"""
Debug do que normalize_city_name retorna para endereços
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from services.city_service import normalize_city_name, extract_city_from_address

def debug_normalize_city_name():
    """Debug do que normalize_city_name retorna"""
    print("🔍 DEBUG normalize_city_name")
    print("=" * 40)

    test_addresses = [
        "R. 6 H-3, 325, Matupá - Mt",
        "R. Piauí, 142 – Mãe De Deus, Peixoto De Azevedo – Mt",
        "Avenida Mato Grosso, 28, Centro, Nova Monte Verde"
    ]

    for address in test_addresses:
        print(f"\n📍 Endereço: '{address}'")

        # Testar normalize_city_name
        normalized = normalize_city_name(address)
        print(f"   normalize_city_name() → '{normalized}'")

        # Testar extract_city_from_address
        extracted = extract_city_from_address(address)
        print(f"   extract_city_from_address() → '{extracted}'")

        # Verificar se normalize_city_name deveria retornar None
        if normalized and len(normalized) > 20:  # Se é muito longo, provavelmente é um endereço
            print("   ⚠️  normalize_city_name retornou endereço completo (deveria ser None)")
        elif normalized:
            print("   ✅ normalize_city_name retornou cidade válida")
        else:
            print("   ✅ normalize_city_name retornou None (correto)")

if __name__ == "__main__":
    debug_normalize_city_name()