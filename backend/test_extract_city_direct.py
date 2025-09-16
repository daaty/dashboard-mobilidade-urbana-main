#!/usr/bin/env python3
"""
Teste direto da função extract_city_from_record
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.api.metrics import extract_city_from_record

def test_extract_city_from_record():
    """Testa diretamente a função extract_city_from_record"""
    print("🧪 TESTANDO extract_city_from_record DIRETAMENTE")
    print("=" * 50)

    # Teste com registros simulados baseados nos dados reais
    test_records = [
        # Registro com MATUPA
        [""] * 16,  # Criar lista de 16 elementos vazios
        # Registro com PEIXOTO DE AZEVEDO
        [""] * 16,
        # Registro com NOVA MONTE VERDE
        [""] * 16,
    ]

    # Preencher os índices 5 e 6 com endereços reais
    test_records[0][5] = "R. 6 H-3, 325, Matupá - Mt"
    test_records[0][6] = "Centro, Matupá - MT"

    test_records[1][5] = "R. Piauí, 142 – Mãe De Deus, Peixoto De Azevedo – Mt"
    test_records[1][6] = "Av. Brasil, 854 - Centro Novo, Peixoto De Azevedo - Mt"

    test_records[2][5] = "Avenida Mato Grosso, 28, Centro, Nova Monte Verde"
    test_records[2][6] = "Hospital municipal de Nova Monte Verde"

    expected_cities = ["MATUPA", "PEIXOTO DE AZEVEDO", "NOVA MONTE VERDE"]

    print("📋 Testes com registros simulados:")
    for i, (record, expected) in enumerate(zip(test_records, expected_cities)):
        detected = extract_city_from_record(record)
        status = "✅" if detected == expected else "❌"
        print(f"{status} Registro {i+1}: Esperado '{expected}' → Detectado '{detected}'")
        print(f"   Endereços: '{record[5][:40]}...' | '{record[6][:40]}...'")

if __name__ == "__main__":
    test_extract_city_from_record()