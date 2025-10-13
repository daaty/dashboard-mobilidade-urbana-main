"""
🔄 TESTE APÓS REINICIAR UVICORN
"""

import requests
import time

print("="*100)
print("🔄 AGUARDANDO UVICORN REINICIAR...")
print("="*100)
print()
print("⏳ Aguardando 5 segundos...")
time.sleep(5)
print()

BASE_URL = "http://localhost:8000"

print("📍 Testando: /api/passengers/kpis?period=3_months")
print()

try:
    resp = requests.get(f"{BASE_URL}/api/passengers/kpis?period=3_months", timeout=30)
    
    if resp.status_code == 200:
        data = resp.json()
        
        print("="*100)
        print("📊 RESULTADO")
        print("="*100)
        print()
        print(f"Total de Passageiros: {data.get('total_passengers')}")
        print(f"Passageiros Ativos: {data.get('active_passengers')}")
        print(f"Total de Corridas: {data.get('total_rides')}")
        print(f"Receita Total: R$ {data.get('total_revenue', 0):.2f}")
        print()
        
        if data.get('total_passengers') == 304:
            print("✅ ✅ ✅ PERFEITO! Backend retorna 304!")
            print()
            print("🔧 AGORA NO NAVEGADOR:")
            print("   1. Pressione F12 (DevTools)")
            print("   2. Vá na aba Network")
            print("   3. Recarregue a página (F5)")
            print("   4. Procure pela requisição 'kpis'")
            print("   5. Clique nela e veja a resposta")
            print()
            print("   Se a resposta mostrar 304 mas o frontend mostra 271,")
            print("   então o problema é no COMPONENTE React!")
        else:
            print(f"❌ Backend ainda retorna {data.get('total_passengers')}!")
            print("⚠️  UVICORN NÃO RECARREGOU!")
            print()
            print("SOLUÇÃO: REINICIE O UVICORN MANUALMENTE:")
            print("   1. Terminal uvicorn: Ctrl + C")
            print("   2. Execute: uvicorn main:app --reload --host 0.0.0.0 --port 8000")
        
    else:
        print(f"❌ Erro HTTP {resp.status_code}")
        print("⚠️  Backend não está respondendo!")
        print()
        print("Reinicie o uvicorn!")
        
except Exception as e:
    print(f"❌ Erro: {e}")
    print()
    print("⚠️  Backend não está rodando!")
    print()
    print("Inicie o uvicorn:")
    print("   cd backend")
    print("   uvicorn main:app --reload --host 0.0.0.0 --port 8000")

print()
print("="*100)
