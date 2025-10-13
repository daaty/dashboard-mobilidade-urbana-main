"""
🔍 TESTAR TODOS OS PERÍODOS DO ENDPOINT
Verificar se todos retornam 304 passageiros
"""

import requests

BASE_URL = "http://localhost:8000"

periods = ['today', '7_days', '30_days', '3_months', '6_months', '12_months']

print("="*100)
print("🔍 TESTANDO TODOS OS PERÍODOS")
print("="*100)
print()

all_ok = True

for period in periods:
    resp = requests.get(f"{BASE_URL}/api/passengers/kpis?period={period}", timeout=10)
    
    if resp.status_code == 200:
        data = resp.json()
        total = data.get('total_passengers')
        
        if total == 304:
            print(f"✅ {period:15} - {total} passageiros")
        else:
            print(f"❌ {period:15} - {total} passageiros (esperado: 304)")
            all_ok = False
    else:
        print(f"❌ {period:15} - Erro HTTP {resp.status_code}")
        all_ok = False

print()
print("="*100)

if all_ok:
    print("✅ TODOS OS PERÍODOS RETORNAM 304 PASSAGEIROS!")
    print()
    print("🔧 INSTRUÇÕES PARA O FRONTEND:")
    print("   1. Abra o navegador em http://localhost:5173")
    print("   2. Pressione Ctrl + Shift + R (hard reload)")
    print("   3. Ou abra DevTools (F12) > Network > marque 'Disable cache'")
    print("   4. Recarregue a página")
    print()
    print("📱 SE AINDA MOSTRAR 271:")
    print("   Abra o Console do navegador (F12 > Console) e execute:")
    print("   fetch('http://localhost:8000/api/passengers/kpis?period=3_months')")
    print("     .then(r => r.json())")
    print("     .then(d => console.log('Total:', d.total_passengers))")
else:
    print("❌ ALGUM PERÍODO NÃO ESTÁ RETORNANDO 304!")
    print("   Verifique a correção no backend.")

print("="*100)
