import asyncio
import asyncpg
import json
from datetime import datetime, timedelta

async def test_rides_today():
    print("=== INICIANDO TESTE ===")
    try:
        print("Tentando conectar no PostgreSQL...")
        # Conectar DIRETO no PostgreSQL
        conn = await asyncpg.connect(
            host="148.230.73.27",
            port=5432,
            database="n8n_db",
            user="n8n_user",
            password="n8n_pw"
        )
        
        print("=== CONECTADO NO BANCO POSTGRESQL ===")
        
        # Data de hoje
        today = datetime.now()
        today_str = today.strftime("%d/%m/%Y")
        print(f"Procurando corridas de HOJE: {today_str}")
        
        # Buscar TODOS os motoristas com rides_history
        print("\n=== BUSCANDO MOTORISTAS COM RIDES_HISTORY ===")
        motoristas = await conn.fetch("""
            SELECT driver_id, rides_history::text 
            FROM driver_personal_details 
            WHERE rides_history IS NOT NULL 
            AND char_length(rides_history::text) > 10
            LIMIT 10
        """)
        
        print(f"Encontrados {len(motoristas)} motoristas com histórico de corridas")
        
        total_corridas_hoje = 0
        total_motoristas_com_corridas_hoje = 0
        
        for motorista in motoristas:
            driver_id = motorista[0]
            rides_history = motorista[1]
            
            try:
                # Parse do JSON
                if isinstance(rides_history, str):
                    rides_data = json.loads(rides_history)
                else:
                    rides_data = rides_history
                
                corridas_hoje = 0
                
                # MOSTRAR TODAS AS DATAS PARA DEBUG
                print(f"\nDriver {driver_id} tem {len(rides_data)} corridas:")
                for ride in rides_data:
                    if ride.get('drop_time'):
                        date_part = ride['drop_time'].split(' : ')[0]
                        print(f"  - Data: {date_part}")
                
                # Verificar cada corrida
                for ride in rides_data:
                    if not ride.get('drop_time'):
                        continue
                        
                    # Parse formato: "04/09/2025 : 6:00 pm"
                    date_part = ride['drop_time'].split(' : ')[0]
                    
                    if date_part == today_str:
                        corridas_hoje += 1
                        print(f"CORRIDA HOJE - Driver {driver_id}: {ride}")
                
                if corridas_hoje > 0:
                    total_corridas_hoje += corridas_hoje
                    total_motoristas_com_corridas_hoje += 1
                    print(f"Driver {driver_id}: {corridas_hoje} corridas hoje")
                    
            except Exception as e:
                print(f"Erro ao processar rides_history do driver {driver_id}: {e}")
                continue
        
        print(f"\n=== RESULTADO FINAL ===")
        print(f"Total de corridas HOJE: {total_corridas_hoje}")
        print(f"Motoristas com corridas HOJE: {total_motoristas_com_corridas_hoje}")
        
        # Vamos testar com 20/08/2025 que tem corridas REAIS
        test_date = "20/08/2025"
        print(f"\n=== TESTANDO COM DATA QUE TEM CORRIDAS: {test_date} ===")
        
        corridas_teste = 0
        for motorista in motoristas:
            driver_id = motorista[0]
            rides_history = motorista[1]
            
            try:
                if isinstance(rides_history, str):
                    rides_data = json.loads(rides_history)
                else:
                    rides_data = rides_history
                
                for ride in rides_data:
                    if not ride.get('drop_time'):
                        continue
                        
                    date_part = ride['drop_time'].split(' : ')[0]
                    if date_part == test_date:
                        corridas_teste += 1
                        print(f"CORRIDA em {test_date} - Driver {driver_id}: {ride}")
            except:
                continue
                
        print(f"Total de corridas em {test_date}: {corridas_teste}")
        
        await conn.close()
        
    except Exception as e:
        print(f"ERRO: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("=== EXECUTANDO SCRIPT ===")
    asyncio.run(test_rides_today())
    print("=== SCRIPT FINALIZADO ===")
