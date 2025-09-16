#!/usr/bin/env python3
"""
Teste da normalização de MATUPA/MATUPÁ
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from services.city_service import normalize_city_name

def test_matupa_normalization():
    """Testa se MATUPA e MATUPÁ são normalizados corretamente"""
    print("🧪 TESTANDO NORMALIZAÇÃO DE MATUPA")
    print("=" * 40)

    test_cases = [
        "MATUPA",
        "MATUPÁ",
        "matupa",
        "matupá",
        "Mt Matupa",
        "MT MATUPÁ",
        "Cidade de Matupa",
        "MATUPA - MT"
    ]

    print("📋 Testes de normalização:")
    for test_case in test_cases:
        normalized = normalize_city_name(test_case)
        status = "✅" if normalized else "❌"
        print(f"{status} '{test_case}' → '{normalized}'")

    # Teste específico da função extract_city_from_record
    print("\n🔍 Teste com registro simulado:")
    from app.api.metrics import extract_city_from_record

    # Simular um registro onde MATUPÁ está no índice 15
    mock_record = [""] * 16  # 16 campos vazios
    mock_record[15] = "MATUPÁ"

    detected_city = extract_city_from_record(mock_record)
    print(f"Registro com 'MATUPÁ' no índice 15 → Detectada como: '{detected_city}'")

if __name__ == "__main__":
    test_matupa_normalization()