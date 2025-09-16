#!/usr/bin/env python3
"""
Teste simples da função normalize_city_name
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.city_service import normalize_city_name

def test_normalize_city():
    print("🧪 TESTANDO FUNÇÃO normalize_city_name")
    print("=" * 50)

    test_cases = [
        "MATUPA",
        "MATUPÁ",
        "PEIXOTO",
        "PEIXOTO DE AZEVEDO",
        "GUARANTA",
        "GUARANTA DO NORTE",
        "NOVA MONTE VERDE",
        "NOVA BANDEIRANTES",
        "BANDEIRANTES",
        "MONTE VERDE",
        "",  # vazio
        "NAN",  # inválido
        "UNDEFINED",  # inválido
        None  # None
    ]

    print("📋 RESULTADOS:")
    for city in test_cases:
        try:
            result = normalize_city_name(city)
            status = "✅" if result else "❌"
            print(f"   {status} '{city}' -> '{result}'")
        except Exception as e:
            print(f"   ❌ '{city}' -> ERRO: {e}")

if __name__ == "__main__":
    test_normalize_city()