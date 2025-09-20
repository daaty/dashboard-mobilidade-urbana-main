import psycopg2
import json
from datetime import datetime, timedelta

try:
    connection = psycopg2.connect(
        host="148.230.73.27",
        port=5432,
        database="n8n_db",
        user="n8n_user",
        password="n8n_pw"
    )
    
    cursor = connection.cursor()
    print("🔍 ANÁLISE DETALHADA DOS CANCELAMENTOS")
    print("=" * 50)
    
    # Pegar todos os drivers com dados de cancelamento
    cursor.execute("""
        SELECT driver_id, city, rides_cancelled::text
        FROM driver_personal_details 
        WHERE rides_cancelled IS NOT NULL
        AND rides_cancelled::text != '{}'
        AND rides_cancelled::text != ''
        AND rides_cancelled::text LIKE '%cancelled_rides%'
    """)
    
    all_drivers = cursor.fetchall()
    print(f"📊 Total de drivers com dados de cancelamento: {len(all_drivers)}")
    
    # Analisar períodos
    today = datetime.now().date()
    periods = {
        '7_days': today - timedelta(days=7),
        '30_days': today - timedelta(days=30),
        '6_months': today - timedelta(days=180)
    }
    
    print(f"📅 Data atual: {today}")
    print(f"Períodos de análise:")
    for period, start_date in periods.items():
        print(f"  - {period}: desde {start_date}")
    
    results = {}
    
    for period, start_date in periods.items():
        results[period] = {
            'total_cancelled': 0,
            'drivers_with_cancelled': 0,
            'details': []
        }
        
        print(f"\n🔍 ANÁLISE PERÍODO: {period} (desde {start_date})")
        print("-" * 40)
        
        for driver_id, city, rides_cancelled_str in all_drivers:
            try:
                data = json.loads(rides_cancelled_str)
                cancelled_rides = data.get('cancelled_rides', [])
                
                driver_cancelled_in_period = 0
                
                for ride in cancelled_rides:
                    cancelled_date_str = ride.get('cancelled_on')
                    if cancelled_date_str:
                        try:
                            cancelled_date = datetime.strptime(cancelled_date_str, '%Y-%m-%d %H:%M:%S').date()
                            
                            if cancelled_date >= start_date:
                                driver_cancelled_in_period += 1
                                results[period]['total_cancelled'] += 1
                                
                        except ValueError as date_error:
                            print(f"  ⚠️ Data inválida para driver {driver_id}: {cancelled_date_str}")
                
                if driver_cancelled_in_period > 0:
                    results[period]['drivers_with_cancelled'] += 1
                    results[period]['details'].append({
                        'driver_id': driver_id,
                        'city': city,
                        'cancelled_in_period': driver_cancelled_in_period
                    })
                    
                    if len(results[period]['details']) <= 5:  # Mostrar só os primeiros 5
                        print(f"  ✅ Driver {driver_id} ({city}): {driver_cancelled_in_period} canceladas")
                        
            except Exception as e:
                print(f"  ❌ Erro processando driver {driver_id}: {e}")
        
        print(f"📊 RESULTADO {period}:")
        print(f"  Total canceladas: {results[period]['total_cancelled']}")
        print(f"  Drivers com canceladas: {results[period]['drivers_with_cancelled']}")
    
    # Mostrar resumo final
    print(f"\n📊 RESUMO FINAL:")
    print("=" * 50)
    for period in ['7_days', '30_days', '6_months']:
        total = results[period]['total_cancelled']
        drivers = results[period]['drivers_with_cancelled']
        print(f"{period:10}: {total:3d} canceladas de {drivers:2d} drivers")
    
    # Verificar se filtro por cidade afeta resultado
    print(f"\n🏙️ TESTE DE FILTRO POR CIDADE (30 dias):")
    print("-" * 40)
    
    cities = ['Matupá', 'Nova Monte Verde', 'Guarantã do Norte', 'Peixoto de Azevedo']
    thirty_days_ago = today - timedelta(days=30)
    
    for city in cities:
        city_cancelled = 0
        city_drivers = 0
        
        for driver_id, driver_city, rides_cancelled_str in all_drivers:
            if driver_city.strip().lower() == city.lower():
                try:
                    data = json.loads(rides_cancelled_str)
                    cancelled_rides = data.get('cancelled_rides', [])
                    
                    driver_cancelled_in_period = 0
                    for ride in cancelled_rides:
                        cancelled_date_str = ride.get('cancelled_on')
                        if cancelled_date_str:
                            try:
                                cancelled_date = datetime.strptime(cancelled_date_str, '%Y-%m-%d %H:%M:%S').date()
                                if cancelled_date >= thirty_days_ago:
                                    driver_cancelled_in_period += 1
                                    city_cancelled += 1
                            except:
                                continue
                    
                    if driver_cancelled_in_period > 0:
                        city_drivers += 1
                        
                except Exception as e:
                    continue
        
        print(f"{city:20}: {city_cancelled:3d} canceladas de {city_drivers:2d} drivers")

except Exception as e:
    print(f"❌ ERRO: {e}")
finally:
    if 'cursor' in locals():
        cursor.close()
    if 'connection' in locals():
        connection.close()