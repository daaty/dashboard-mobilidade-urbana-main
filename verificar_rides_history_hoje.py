"""
🔍 VERIFICAR RIDES_HISTORY - Quantas corridas de HOJE existem?
Análise direta do rides_history para ver a data das corridas
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"

print("="*100)
print("🔍 ANÁLISE DO RIDES_HISTORY - Corridas de HOJE")
print(f"📅 Data de HOJE: {datetime.now().strftime('%d/%m/%Y')}")
print("="*100)
print()

# Obter lista completa de passageiros
print("1️⃣  Obtendo todos os passageiros...")
resp = requests.get(f"{BASE_URL}/api/passengers/list", params={"period": "all_time", "city": "all", "limit": 10000})
passengers = resp.json()

print(f"📊 Total de passageiros: {len(passengers)}")
print()

# Analisar rides_history de cada um
print("2️⃣  Analisando rides_history de todos os passageiros...")
print("-"*100)

hoje_str = datetime.now().strftime('%d/%m/%Y')
corridas_hoje = []
total_corridas_historico = 0
passageiros_com_corridas_hoje = []

# Precisamos buscar os dados completos via endpoint que retorna rides_history
# Vamos usar o analytics que retorna dados completos
resp_analytics = requests.get(f"{BASE_URL}/api/passengers/analytics", params={"period": "all_time", "city": "all"})
analytics_data = resp_analytics.json()

print("📊 Dados do analytics (todos os tempos):")
print(json.dumps(analytics_data.get('summary', {}), indent=2))
print()

# Agora vamos verificar cada passageiro individualmente
print("\n3️⃣  Verificando corridas de HOJE no rides_history...")
print("-"*100)

# Como não temos acesso direto ao rides_history via API, vamos analisar
# usando o endpoint que já processa isso

# Testar com diferentes períodos
periodos = ["today", "7_days", "30_days", "all_time"]

print(f"\n📊 CORRIDAS POR PERÍODO (via passengers/analytics):")
print(f"{'Período':<15} | {'Total Corridas':<15} | {'Total Revenue':<15}")
print("-"*50)

for periodo in periodos:
    resp = requests.get(f"{BASE_URL}/api/passengers/analytics", params={"period": periodo, "city": "all"})
    data = resp.json()
    summary = data.get('summary', {})
    
    total = summary.get('total_rides', 0)
    revenue = summary.get('total_revenue', 0)
    
    print(f"{periodo:<15} | {total:<15} | R$ {revenue:<13.2f}")

print()
print("="*100)
print("🎯 ANÁLISE")
print("="*100)
print()

# Comparar com rides_data
resp_metrics = requests.get(f"{BASE_URL}/api/metrics/overview", params={"periodo": "hoje"})
metrics = resp_metrics.json()
total_metrics = len(metrics.get('concluidas', [])) + len(metrics.get('canceladas', [])) + len(metrics.get('perdidas', []))

resp_today = requests.get(f"{BASE_URL}/api/passengers/analytics", params={"period": "today", "city": "all"})
today_data = resp_today.json()
total_today = today_data.get('summary', {}).get('total_rides', 0)

print(f"📊 rides_data (metrics/overview hoje): {total_metrics} corridas")
print(f"📊 rides_history (passengers/analytics today): {total_today} corridas")
print(f"⚠️  DIFERENÇA: {total_metrics - total_today} corridas")
print()

print("💡 CONCLUSÃO:")
print()
if total_today < total_metrics:
    print(f"   ❌ Apenas {total_today} das {total_metrics} corridas de HOJE estão no rides_history")
    print(f"   ❌ {total_metrics - total_today} corridas ({((total_metrics - total_today)/total_metrics*100):.1f}%) estão FALTANDO")
    print()
    print("   🔍 POSSÍVEIS CAUSAS:")
    print()
    print("   1️⃣  FORMATO DE DATA DIFERENTE:")
    print("      • rides_data usa: '2025-10-12 18:35:37'")
    print("      • rides_history usa: '18/08/2025 12:12 pm'")
    print("      • A comparação pode estar falhando!")
    print()
    print("   2️⃣  RIDES_HISTORY NÃO ATUALIZADO:")
    print("      • As corridas de hoje ainda não foram adicionadas ao rides_history")
    print("      • Processo de sincronização não executou")
    print()
    print("   3️⃣  FILTRO DE DATA NO CÓDIGO:")
    print("      • A função process_rides_history() pode estar com bug")
    print("      • Está parseando '18/08/2025' mas hoje é '12/10/2025'")
    print()
    print("   🔧 PRÓXIMO PASSO:")
    print("      • Verificar se rides_history TEM corridas com data 12/10/2025")
    print("      • Se NÃO tem, o problema é sincronização")
    print("      • Se TEM, o problema é no filtro de data do código")

print()
print("="*100)
