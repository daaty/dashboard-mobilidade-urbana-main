"""
🎯 DIAGNÓSTICO FINAL - Por que apenas 3 corridas ao invés de 15?
"""

import requests
import json

BASE_URL = "http://localhost:8000"

print("="*100)
print("🎯 DIAGNÓSTICO FINAL - RIDES_DATA vs RIDES_HISTORY")
print("="*100)
print()

# 1. Obter corridas do metrics (rides_data)
print("1️⃣  Corridas no RIDES_DATA (tabela principal)")
print("-"*100)

resp = requests.get(f"{BASE_URL}/api/metrics/overview", params={"periodo": "hoje"})
data = resp.json()

concluidas = data.get('concluidas', [])
canceladas = data.get('canceladas', [])
perdidas = data.get('perdidas', [])

total_rides_data = len(concluidas) + len(canceladas) + len(perdidas)

print(f"📊 Total: {total_rides_data} corridas")
print(f"   ✅ {len(concluidas)} concluídas")
print(f"   ❌ {len(canceladas)} canceladas")
print(f"   ⏱️  {len(perdidas)} perdidas")
print()

# Salvar primeira corrida como exemplo
if concluidas:
    print("📋 Exemplo de corrida concluída:")
    primeira = concluidas[0]
    print(json.dumps(primeira, indent=2, ensure_ascii=False)[:500])
    print()

# 2. Obter corridas do passengers (rides_history)
print("\n2️⃣  Corridas no RIDES_HISTORY (passenger_personal_details)")
print("-"*100)

resp2 = requests.get(f"{BASE_URL}/api/passengers/kpis", params={"period": "today"})
data2 = resp2.json()

total_rides_history = data2.get('total_rides', 0)

print(f"📊 Total: {total_rides_history} corridas")
print(f"💰 Receita: R$ {data2.get('total_revenue', 0):.2f}")
print()

# 3. Análise
print("\n3️⃣  ANÁLISE COMPARATIVA")
print("-"*100)

diferenca = total_rides_data - total_rides_history
percentual = (total_rides_history / total_rides_data * 100) if total_rides_data > 0 else 0

print(f"📊 rides_data: {total_rides_data} corridas")
print(f"📊 rides_history: {total_rides_history} corridas")
print(f"⚠️  DIFERENÇA: {diferenca} corridas ({100-percentual:.1f}% faltando)")
print()

# 4. Conclusão
print("\n4️⃣  CONCLUSÃO")
print("="*100)
print()

if diferenca > 0:
    print(f"❌ PROBLEMA IDENTIFICADO:")
    print()
    print(f"   {diferenca} corridas existem no RIDES_DATA mas NÃO estão no RIDES_HISTORY!")
    print()
    print("💡 POSSÍVEIS CAUSAS:")
    print()
    print("   1️⃣  SINCRONIZAÇÃO ATRASADA")
    print("      • As corridas foram adicionadas ao rides_data recentemente")
    print("      • O processo que popula rides_history ainda não executou")
    print("      • Pode haver um job/cron que sincroniza periodicamente")
    print()
    print("   2️⃣  PROCESSO DE SINCRONIZAÇÃO QUEBRADO")
    print("      • O processo que deveria copiar dados está com erro")
    print("      • Falta trigger ou procedure para sincronização automática")
    print()
    print("   3️⃣  DADOS INCOMPLETOS")
    print("      • Algumas corridas não têm passenger_id válido")
    print("      • O passenger_id pode não estar mapeado corretamente")
    print()
    print("   4️⃣  FORMATO DE DATA DIFERENTE")
    print("      • rides_data pode usar um formato de data")
    print("      • rides_history pode usar outro formato")
    print("      • A comparação de datas pode estar falhando")
    print()
    print("🔧 PRÓXIMAS AÇÕES:")
    print()
    print("   ✅ Verificar se existe processo de sincronização")
    print("   ✅ Conferir logs de importação de dados")
    print("   ✅ Verificar se passenger_id está presente em todas as corridas")
    print("   ✅ Confirmar formato de data em ambas as tabelas")
    print("   ✅ Executar sincronização manual se necessário")
    
else:
    print("✅ DADOS SINCRONIZADOS!")
    print("   Ambas as fontes têm o mesmo número de corridas.")

print()
print("="*100)
