import requests

API_URL = "http://localhost:8000"

print("Testando endpoints usados pelo useMetasProgress:\n")

# 1. Endpoint de campanhas
print("1. GET /api/campanhas")
try:
    resp = requests.get(f"{API_URL}/api/campanhas")
    print(f"   Status: {resp.status_code}")
    if resp.status_code == 200:
        data = resp.json()
        total = len(data) if isinstance(data, list) else data.get('total', 'unknown')
        print(f"   ✅ Retornou {total} campanhas")
    else:
        print(f"   ❌ Erro: {resp.text[:200]}")
except Exception as e:
    print(f"   ❌ Exception: {e}")

# 2. Endpoint financeiro
print("\n2. GET /api/financeiro/overview?periodo=90")
try:
    resp = requests.get(f"{API_URL}/api/financeiro/overview?periodo=90")
    print(f"   Status: {resp.status_code}")
    if resp.status_code == 200:
        print(f"   ✅ OK")
    else:
        print(f"   ❌ Erro: {resp.text[:200]}")
except Exception as e:
    print(f"   ❌ Exception: {e}")

# 3. Endpoint de KPIs (exemplo com Matupá)
print("\n3. GET /api/drivers/kpis?period=3_months&city=Matupá")
try:
    resp = requests.get(f"{API_URL}/api/drivers/kpis?period=3_months&city=Matupá")
    print(f"   Status: {resp.status_code}")
    if resp.status_code == 200:
        data = resp.json()
        print(f"   ✅ OK - Success: {data.get('success')}")
    else:
        print(f"   ❌ Erro: {resp.text[:200]}")
except Exception as e:
    print(f"   ❌ Exception: {e}")
