"""
🔥 BUSCAR TODOS OS PASSAGEIROS COM RIDES_HISTORY DE HOJE
"""

import asyncio
import asyncpg
import json
from datetime import datetime

async def buscar_todos_passengers_hoje():
    print("="*100)
    print("🔥 BUSCANDO TODOS OS PASSAGEIROS COM CORRIDAS DE HOJE")
    print("="*100)
    print()
    
    # Conectar ao banco
    conn = await asyncpg.connect(
        host='148.230.73.27',
        port=5432,
        database='n8n_db',
        user='n8n_user',
        password='n8n_pw'
    )
    
    try:
        today_str = datetime.now().strftime("%d/%m/%Y")
        
        print(f"📅 Buscando corridas de: {today_str}")
        print()
        
        # Buscar TODOS os passageiros que têm rides_history
        query = """
        SELECT 
            passenger_id,
            rides_history,
            personal_data
        FROM passenger_personal_details
        WHERE rides_history IS NOT NULL 
          AND rides_history != '[]'
        ORDER BY passenger_id
        """
        
        results = await conn.fetch(query)
        
        print(f"✅ Total de passageiros com rides_history: {len(results)}")
        print()
        
        passengers_with_rides_today = []
        total_rides_today = 0
        
        for result in results:
            passenger_id = result['passenger_id']
            rides_history = result['rides_history']
            personal_data = result['personal_data']
            
            # Converter de JSON se necessário
            if isinstance(personal_data, str):
                personal_data = json.loads(personal_data)
            if isinstance(rides_history, str):
                rides_history = json.loads(rides_history)
            
            # Filtrar corridas de hoje
            if rides_history:
                rides_today = [r for r in rides_history if r.get('date', '').startswith(today_str)]
                
                if rides_today:
                    passengers_with_rides_today.append({
                        'passenger_id': passenger_id,
                        'name': personal_data.get('user_name', 'N/A'),
                        'phone': personal_data.get('user_phone', 'N/A'),
                        'rides': rides_today
                    })
                    total_rides_today += len(rides_today)
        
        print("="*100)
        print("📊 RESULTADO")
        print("="*100)
        print()
        print(f"✅ Passageiros com corridas de HOJE: {len(passengers_with_rides_today)}")
        print(f"📊 Total de corridas de HOJE: {total_rides_today}")
        print()
        
        if passengers_with_rides_today:
            print("="*100)
            print("📋 LISTA COMPLETA")
            print("="*100)
            print()
            
            total_valor = 0
            
            for i, p_data in enumerate(passengers_with_rides_today, 1):
                p_id = p_data['passenger_id']
                name = p_data['name']
                phone = p_data['phone']
                rides = p_data['rides']
                
                valor_passenger = sum(float(r.get('user_fare', 0)) for r in rides)
                total_valor += valor_passenger
                
                print(f"{i}. Passageiro: {p_id}")
                print(f"   Nome: {name}")
                print(f"   Telefone: {phone}")
                print(f"   Corridas hoje: {len(rides)}")
                print(f"   Valor total: R$ {valor_passenger:.2f}")
                print()
                
                for j, ride in enumerate(rides, 1):
                    print(f"      {j}. {ride.get('date')} | R$ {ride.get('user_fare')} | {ride.get('driver_name')} | Engagement: {ride.get('engagement_id')}")
                
                print()
            
            print("="*100)
            print("💰 TOTAIS")
            print("="*100)
            print()
            print(f"📊 Total de corridas: {total_rides_today}")
            print(f"💵 Valor total: R$ {total_valor:.2f}")
            print()
            
            print("="*100)
            print("🎯 COMPARAÇÃO COM ENDPOINT")
            print("="*100)
            print()
            print(f"rides_history (banco): {total_rides_today} corridas")
            print(f"/api/metrics/overview: 15 corridas")
            print()
            
            if total_rides_today < 15:
                missing = 15 - total_rides_today
                print(f"⚠️  FALTAM {missing} CORRIDAS!")
                print(f"Essas {missing} corridas estão em rides_data mas NÃO foram sincronizadas para rides_history!")
                print()
                print("🔧 AÇÃO NECESSÁRIA:")
                print("   Executar script de sincronização para atualizar rides_history dos passageiros!")
            elif total_rides_today == 15:
                print("✅ PERFEITO! Todos os dados estão sincronizados!")
            else:
                print(f"⚠️  ATENÇÃO! rides_history tem MAIS corridas ({total_rides_today}) do que o endpoint ({15})!")
            print()
        
    finally:
        await conn.close()

# Executar
asyncio.run(buscar_todos_passengers_hoje())
