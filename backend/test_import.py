#!/usr/bin/env python3
"""
Teste do import da função normalize_city_name
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from services.city_service import normalize_city_name
    print("✅ Import bem-sucedido!")

    # Testar a função
    test_result = normalize_city_name("NOVA MONTE VERDE")
    print(f"Teste: normalize_city_name('NOVA MONTE VERDE') = '{test_result}'")

except ImportError as e:
    print(f"❌ Erro de import: {e}")
except Exception as e:
    print(f"❌ Erro geral: {e}")