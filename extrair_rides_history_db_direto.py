"""
🔥 BUSCAR RIDES_HISTORY DIRETO NO BANCO DE DADOS
Sem endpoint, direto na tabela passenger_personal_details
"""

import asyncio
import asyncpg
import json
from datetime import datetime

# IDs dos 5 passageiros
PASSENGER_IDS = [
    "18756583",
    "18756825",
    "18762196",
    "18765654",
    "18766423"
]

async def buscar_rides_history():
    print("="*100)
    print("🔥 BUSCANDO RIDES_HISTORY DIRETO NO POSTGRESQL")
    print("="*100)
    print()
    
    # Conectar ao banco (credenciais do db.py)
    conn = await asyncpg.connect(
        host='148.230.73.27',
        port=5432,
        database='n8n_db',
        user='n8n_user',
        password='n8n_pw'
    )
    
    try:
        today_str = datetime.now().strftime("%d/%m/%Y")
        total_rides_today = 0
        passengers_with_data = 0
        
        for passenger_id in PASSENGER_IDS:
            print(f"📍 Passageiro: {passenger_id}")
            
            # Buscar rides_history direto
            query = """
            SELECT 
                passenger_id,
                rides_history,
                personal_data
            FROM passenger_personal_details
            WHERE passenger_id = $1
            """
            
            result = await conn.fetchrow(query, passenger_id)
            
            if result:
                rides_history = result['rides_history']
                personal_data = result['personal_data']
                
                # Converter de JSON se necessário
                if isinstance(personal_data, str):
                    personal_data = json.loads(personal_data)
                if isinstance(rides_history, str):
                    rides_history = json.loads(rides_history)
                
                print(f"  ✅ PASSAGEIRO EXISTE NA TABELA!")
                print()
                
                # Mostrar personal_data
                if personal_data:
                    print(f"  📋 Personal Data:")
                    print(f"     Nome: {personal_data.get('user_name', 'N/A')}")
                    print(f"     Telefone: {personal_data.get('user_phone', 'N/A')}")
                    print()
                
                # Mostrar rides_history
                if rides_history:
                    print(f"  🚗 RIDES_HISTORY:")
                    print(f"     Total de corridas no histórico: {len(rides_history)}")
                    print()
                    
                    # Filtrar corridas de hoje
                    rides_today = [r for r in rides_history if r.get('date', '').startswith(today_str)]
                    
                    if rides_today:
                        print(f"  ✅ CORRIDAS DE HOJE: {len(rides_today)}")
                        print()
                        
                        passengers_with_data += 1
                        total_rides_today += len(rides_today)
                        
                        for i, ride in enumerate(rides_today, 1):
                            print(f"     {i}. Data: {ride.get('date')}")
                            print(f"        Motorista: {ride.get('driver_id')} - {ride.get('driver_name', 'N/A')}")
                            print(f"        Valor: R$ {ride.get('user_fare')}")
                            print(f"        Status: Pago em {ride.get('preferred_mode', 'N/A')}")
                            print(f"        Engagement ID: {ride.get('engagement_id', 'N/A')}")
                            print()
                    else:
                        print(f"  ⚠️  Tem {len(rides_history)} corridas, mas NENHUMA de hoje")
                        print(f"     Última corrida: {rides_history[0].get('date', 'N/A') if rides_history else 'N/A'}")
                        print()
                else:
                    print(f"  ❌ rides_history está VAZIO ou NULL!")
                    print()
                    
                # Mostrar o JSON completo para debug
                print(f"  🔍 RIDES_HISTORY RAW (primeiras 500 chars):")
                rides_json = json.dumps(rides_history, ensure_ascii=False, indent=2)
                print(f"     {rides_json[:500]}...")
                print()
                
            else:
                print(f"  ❌ PASSAGEIRO NÃO EXISTE NA TABELA!")
                print()
            
            print("-"*100)
            print()
        
        print("="*100)
        print("📊 RESUMO FINAL")
        print("="*100)
        print()
        print(f"✅ Passageiros com corridas de HOJE: {passengers_with_data}/{len(PASSENGER_IDS)}")
        print(f"📊 Total de corridas de HOJE: {total_rides_today}")
        print()
        
        if total_rides_today > 0:
            print("="*100)
            print("🎯 CONCLUSÃO")
            print("="*100)
            print()
            print(f"Encontramos {total_rides_today} corridas de HOJE nos rides_history!")
            print("O endpoint /api/metrics/overview mostra 15 corridas de hoje.")
            print()
            
            if total_rides_today < 15:
                missing = 15 - total_rides_today
                print(f"⚠️  FALTAM {missing} corridas!")
                print(f"Essas {missing} corridas estão em OUTROS passageiros que não testamos ainda!")
            elif total_rides_today == 15:
                print("✅ ENCONTRAMOS TODAS AS 15 CORRIDAS!")
            print()
        
    finally:
        await conn.close()

# Executar
asyncio.run(buscar_rides_history())
