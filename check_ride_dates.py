import psycopg2
import json
from datetime import datetime

# Configuração do banco
DB_CONFIG = {
    'host': '148.230.73.27',
    'port': 5432,
    'database': 'n8n_db',
    'user': 'n8n_user',
    'password': 'n8n_pw'
}

def check_ride_dates():
    """Verifica as datas das corridas"""
    print("=" * 60)
    print("VERIFICANDO DATAS DAS CORRIDAS")
    print("=" * 60)
    
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        
        cur.execute('''
            SELECT 
                dd.driver_id,
                dd.name,
                dpd.rides_history
            FROM drivers_data dd
            LEFT JOIN driver_personal_details dpd ON dd.driver_id = dpd.driver_id
            WHERE dpd.rides_history IS NOT NULL
            LIMIT 3
        ''')
        
        drivers = cur.fetchall()
        all_dates = []
        
        for driver in drivers:
            driver_id, name, rides_history = driver
            print(f"\n🚗 Driver: {name} (ID: {driver_id})")
            
            if rides_history:
                rides = rides_history if isinstance(rides_history, list) else []
                print(f"   📊 Total de corridas: {len(rides)}")
                
                for i, ride in enumerate(rides):
                    if isinstance(ride, dict):
                        ride_date = ride.get('date')
                        ride_status = ride.get('status', 'N/A')
                        
                        if ride_date:
                            all_dates.append(ride_date)
                            print(f"   🕐 Corrida {i+1}: {ride_date} | Status: {ride_status}")
                            
                            # Tentar parsear a data
                            try:
                                if 'T' in ride_date:
                                    parsed_date = datetime.fromisoformat(ride_date.replace('Z', '+00:00'))
                                else:
                                    parsed_date = datetime.strptime(ride_date, '%Y-%m-%d')
                                
                                days_ago = (datetime.now() - parsed_date).days
                                print(f"      ⏰ Data parseada: {parsed_date.strftime('%Y-%m-%d %H:%M')} ({days_ago} dias atrás)")
                            except Exception as e:
                                print(f"      ❌ Erro ao parsear: {e}")
                        
                        if i >= 4:  # Limitar a 5 corridas por motorista
                            break
        
        # Resumo das datas
        if all_dates:
            print(f"\n📅 RESUMO DAS DATAS:")
            print(f"Total de corridas verificadas: {len(all_dates)}")
            
            # Converter todas as datas
            parsed_dates = []
            for date_str in all_dates:
                try:
                    if 'T' in date_str:
                        parsed_date = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                    else:
                        parsed_date = datetime.strptime(date_str, '%Y-%m-%d')
                    parsed_dates.append(parsed_date)
                except:
                    continue
            
            if parsed_dates:
                oldest = min(parsed_dates)
                newest = max(parsed_dates)
                now = datetime.now()
                
                print(f"Data mais antiga: {oldest.strftime('%Y-%m-%d %H:%M')} ({(now - oldest).days} dias atrás)")
                print(f"Data mais recente: {newest.strftime('%Y-%m-%d %H:%M')} ({(now - newest).days} dias atrás)")
                print(f"Data atual: {now.strftime('%Y-%m-%d %H:%M')}")
                
                # Verificar se há corridas nos últimos períodos
                days_7 = sum(1 for d in parsed_dates if (now - d).days <= 7)
                days_30 = sum(1 for d in parsed_dates if (now - d).days <= 30)
                days_90 = sum(1 for d in parsed_dates if (now - d).days <= 90)
                
                print(f"\n📊 CORRIDAS POR PERÍODO:")
                print(f"Últimos 7 dias: {days_7} corridas")
                print(f"Últimos 30 dias: {days_30} corridas")  
                print(f"Últimos 90 dias: {days_90} corridas")
                
                # Recomendação de período
                if days_90 > 0:
                    print(f"\n✅ RECOMENDAÇÃO: Usar período de 90 dias ou maior")
                elif days_30 > 0:
                    print(f"\n✅ RECOMENDAÇÃO: Usar período de 30 dias ou maior")
                else:
                    print(f"\n⚠️ RECOMENDAÇÃO: Usar período maior que 90 dias ou remover filtro de data")
        
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    check_ride_dates()
