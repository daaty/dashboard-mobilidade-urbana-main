#!/usr/bin/env python3
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from services.city_service import normalize_city_name

def matches_city_filter(cidade_item, cidade_filter):
    """Compara cidade de forma robusta, lidando com None e diferenças de formatação"""
    if not cidade_filter:
        return True  # Sem filtro, aceitar tudo

    if not cidade_item:
        return False  # Item sem cidade não corresponde a filtro

    # Aplicar normalização completa a ambas as strings
    item_norm = normalize_city_name(str(cidade_item).strip())
    filter_norm = normalize_city_name(str(cidade_filter).strip())

    # Se a normalização falhar, usar o valor original em maiúsculo
    if not item_norm:
        item_norm = str(cidade_item).strip().upper()
    if not filter_norm:
        filter_norm = str(cidade_filter).strip().upper()

    print(f"Comparando: '{cidade_item}' -> '{item_norm}' com '{cidade_filter}' -> '{filter_norm}'")
    return item_norm == filter_norm

# Testes
print("=== Teste da função matches_city_filter ===")

test_cases = [
    ("MATUPA", "MATUPA"),
    ("PEIXOTO DE AZEVEDO", "PEIXOTO DE AZEVEDO"),
    ("PEIXOTO", "PEIXOTO DE AZEVEDO"),
    ("NOVA MONTE VERDE", "NOVA MONTE VERDE"),
    ("GUARANTA DO NORTE", "GUARANTA DO NORTE"),
]

for item, filtro in test_cases:
    result = matches_city_filter(item, filtro)
    print(f"Resultado: {result}")
    print()