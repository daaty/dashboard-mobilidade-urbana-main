import requests

API_URL = "http://localhost:8000"

print("\n" + "="*80)
print("TESTE DO ENDPOINT /api/drivers/kpis")
print("="*80)
print()

try:
    response = requests.get(f"{API_URL}/api/drivers/kpis?period=6_months")
    
    if response.status_code == 200:
        data = response.json()
        
        print("✅ Endpoint respondeu com sucesso!")
        print()
        print(f"📊 Total de Motoristas: {data.get('data', {}).get('total_drivers', 0)}")
        print(f"✅ Motoristas Ativos: {data.get('data', {}).get('active_drivers', 0)}")
        print(f"❌ Motoristas Inativos: {data.get('data', {}).get('inactive_drivers', 0)}")
        print(f"🟢 Motoristas Online: {data.get('data', {}).get('online_drivers', 0)}")
        print()
        
        active = data.get('data', {}).get('active_drivers', 0)
        
        if active == 42:
            print("🎉 SUCESSO! O endpoint está retornando 42 motoristas ativos (valor correto)")
        elif active == 24:
            print("❌ ERRO! O endpoint ainda está retornando 24 (motoristas com corridas)")
            print("   Esperado: 42 (motoristas com status Active/Online/Offline)")
        else:
            print(f"⚠️  ATENÇÃO! O endpoint está retornando {active} motoristas ativos")
            print("   Esperado: 42")
        
    else:
        print(f"❌ Erro HTTP {response.status_code}")
        print(f"Response: {response.text}")
        
except requests.exceptions.ConnectionError:
    print("❌ ERRO: Backend não está rodando!")
    print("   Execute: uvicorn main:app --reload --host 0.0.0.0 --port 8000")
    
except Exception as e:
    print(f"❌ Erro: {e}")

print()
print("="*80)
