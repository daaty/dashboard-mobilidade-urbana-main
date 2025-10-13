"""
🧪 TESTAR CORREÇÃO DO ENDPOINT /api/passengers/kpis
Deve retornar 304 passageiros agora
"""

import requests
import time

BASE_URL = "http://localhost:8000"

print("="*100)
print("🧪 TESTANDO CORREÇÃO DO ENDPOINT")
print("="*100)
print()

print("⏳ Aguardando 3 segundos para o uvicorn recarregar...")
time.sleep(3)
print()

print("📍 Testando: /api/passengers/kpis?period=3_months")
print()

try:
    resp = requests.get(f"{BASE_URL}/api/passengers/kpis?period=3_months", timeout=30)
    
    if resp.status_code == 200:
        data = resp.json()
        
        print("✅ RESPOSTA RECEBIDA!")
        print()
        
        print("="*100)
        print("📊 RESULTADO")
        print("="*100)
        print()
        print(f"✅ Total de Passageiros: {data.get('total_passengers')}")
        print(f"✅ Passageiros Ativos: {data.get('active_passengers')}")
        print(f"📊 Total de Corridas: {data.get('total_rides')}")
        print(f"💵 Receita Total: R$ {data.get('total_revenue', 0):.2f}")
        print(f"⭐ Média de Avaliação: {data.get('avg_rating', 0):.2f}")
        print(f"🏙️  Total de Cidades: {data.get('cities_count')}")
        print(f"📅 Registrados este mês: {data.get('registered_this_month')}")
        print(f"🚫 Bloqueados: {data.get('blocked_passengers')}")
        print()
        
        print("="*100)
        print("🎯 COMPARAÇÃO")
        print("="*100)
        print()
        print(f"Banco de dados: 304 passageiros")
        print(f"API retorna: {data.get('total_passengers')} passageiros")
        print()
        
        if data.get('total_passengers') == 304:
            print("✅ ✅ ✅ PERFEITO! TODOS OS 304 PASSAGEIROS ESTÃO SENDO RETORNADOS!")
            print()
            print("🎉 CORREÇÃO APLICADA COM SUCESSO!")
        elif data.get('total_passengers') == 271:
            print("❌ AINDA ESTÁ RETORNANDO 271...")
            print("⚠️  O uvicorn pode não ter recarregado ainda. Aguarde alguns segundos e teste novamente.")
        else:
            print(f"⚠️  Retornou {data.get('total_passengers')} passageiros (esperado: 304)")
        print()
        
    else:
        print(f"❌ Erro HTTP {resp.status_code}")
        print(resp.text)
        
except Exception as e:
    print(f"❌ Erro: {e}")
    import traceback
    traceback.print_exc()

print()
