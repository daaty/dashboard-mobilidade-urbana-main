"""
🔍 MONITORAR REQUISIÇÕES AO ENDPOINT
Vamos ver EXATAMENTE o que o frontend está pedindo
"""

import time
from datetime import datetime

print("="*100)
print("🔍 MONITORANDO LOGS DO UVICORN")
print("="*100)
print()
print("📌 Aguardando requisições ao endpoint /api/passengers/kpis...")
print("📌 Recarregue a página do dashboard AGORA e veja o que aparece aqui!")
print()
print("⏰ Monitorando... (Ctrl+C para parar)")
print()
print("-"*100)
print()

# Nota: Este script apenas orienta - os logs aparecerão no terminal do uvicorn
print("⚠️  ATENÇÃO: Os logs aparecerão no terminal do UVICORN!")
print()
print("Procure por linhas como:")
print('  INFO:     127.0.0.1:XXXXX - "GET /api/passengers/kpis?period=XXXXX HTTP/1.1" 200 OK')
print()
print("E veja qual PERIOD está sendo usado!")
print()
print("="*100)
print()
print("🧪 TESTE MANUAL:")
print()
print("No CONSOLE DO NAVEGADOR (F12 > Console), execute:")
print()
print("""
fetch('http://localhost:8000/api/passengers/kpis?period=3_months')
  .then(r => r.json())
  .then(d => {
    console.log('=====================================')
    console.log('TESTE DIRETO DO ENDPOINT:')
    console.log('Total de passageiros:', d.total_passengers)
    console.log('Passageiros ativos:', d.active_passengers)
    console.log('=====================================')
    if (d.total_passengers === 304) {
      console.log('✅ ENDPOINT RETORNA 304!')
      console.log('❌ MAS FRONTEND MOSTRA 271')
      console.log('🔍 PROBLEMA: O frontend não está atualizando o estado!')
    } else if (d.total_passengers === 271) {
      console.log('❌ ENDPOINT RETORNA 271!')
      console.log('🔍 PROBLEMA: O backend não está usando a correção!')
    }
  })
""")
print()
print("="*100)
