#!/usr/bin/env python3
"""
Teste direto da API /api/metrics/overview com filtro de cidade
"""

import requests

def test_api_city_filter():
    """Testa a API diretamente com filtro de cidade"""
    print("🧪 TESTANDO API /api/metrics/overview COM FILTRO DE CIDADE")
    print("=" * 60)

    base_url = "http://localhost:8000"

    # Teste 1: Sem filtro de cidade
    print("\n1️⃣ Teste SEM filtro de cidade:")
    try:
        response = requests.get(f"{base_url}/api/metrics/overview?periodo=30d")
        if response.status_code == 200:
            data = response.json()
            total_corridas = data.get('total_corridas_solicitadas', 0)
            print(f"   ✅ Status: {response.status_code}")
            print(f"   📊 Total de corridas: {total_corridas}")
        else:
            print(f"   ❌ Status: {response.status_code}")
            print(f"   📝 Resposta: {response.text[:200]}...")
    except Exception as e:
        print(f"   ❌ Erro: {e}")

    # Teste 2: Com filtro de cidade
    print("\n2️⃣ Teste COM filtro de cidade (GUARANTA DO NORTE):")
    try:
        response = requests.get(f"{base_url}/api/metrics/overview?periodo=30d&cidade=GUARANTA%20DO%20NORTE")
        if response.status_code == 200:
            data = response.json()
            total_corridas = data.get('total_corridas_solicitadas', 0)
            print(f"   ✅ Status: {response.status_code}")
            print(f"   📊 Total de corridas filtradas: {total_corridas}")
            print(f"   🏙️ Cidade filtrada: GUARANTA DO NORTE")
        else:
            print(f"   ❌ Status: {response.status_code}")
            print(f"   📝 Resposta: {response.text[:200]}...")
    except Exception as e:
        print(f"   ❌ Erro: {e}")

    # Teste 3: Verificar se o backend está rodando
    print("\n3️⃣ Verificando se o backend está rodando:")
    try:
        response = requests.get(f"{base_url}/docs")
        if response.status_code == 200:
            print("   ✅ Backend está rodando")
        else:
            print(f"   ❌ Backend não responde: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Erro de conexão: {e}")

if __name__ == "__main__":
    test_api_city_filter()