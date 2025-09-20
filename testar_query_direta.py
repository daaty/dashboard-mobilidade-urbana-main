import os
from sqlalchemy import create_engine, text
from datetime import datetime, timedelta
import json

# Usar as mesmas configurações do backend
SYNC_DATABASE_URL = "postgresql://n8n_user:n8n_pw@148.230.73.27:5432/n8n_db"

engine = create_engine(SYNC_DATABASE_URL, pool_pre_ping=True)

def calculate_date_range(period: str):
    """Calcular range de datas baseado no período"""
    end_date = datetime.now().date()
    
    if period == "hoje":
        start_date = end_date
    elif period == "7_days":
        start_date = end_date - timedelta(days=7)
    elif period == "30_days":
        start_date = end_date - timedelta(days=30)
    elif period == "3_months":
        start_date = end_date - timedelta(days=90)
    elif period == "6_months":
        start_date = end_date - timedelta(days=180)
    elif period == "12_months":
        start_date = end_date - timedelta(days=365)
    else:
        start_date = end_date - timedelta(days=30)
    
    return start_date, end_date

def testar_query_cancelamentos():
    with engine.connect() as connection:
        period = "30_days"
        city = "all"
        
        start_date, end_date = calculate_date_range(period)
        print(f"🔍 TESTE DIRETO DA QUERY")
        print(f"Período: {period} ({start_date} até {end_date})")
        print(f"Cidade: {city}")
        print("=" * 50)
        
        # Query exata do endpoint
        cancellation_query = """
        SELECT driver_id, city, rides_cancelled
        FROM driver_personal_details 
        WHERE rides_cancelled IS NOT NULL
        AND rides_cancelled::text != '{}'
        AND rides_cancelled::text != ''
        AND rides_cancelled::text LIKE '%cancelled_rides%'
        """
        
        cancellation_params = {}
        if city != "all" and city != "":
            cancellation_query += " AND city = :city"
            cancellation_params['city'] = city
            
        print(f"Query: {cancellation_query}")
        print(f"Params: {cancellation_params}")
        
        result = connection.execute(text(cancellation_query), cancellation_params)
        records = result.fetchall()
        
        print(f"\n📊 Registros encontrados: {len(records)}")
        
        total_cancelled_rides = 0
        for record in records:
            driver_id, driver_city, rides_cancelled_str = record
            
            try:
                # Verificar se já é dict ou se precisa ser parseado
                if isinstance(rides_cancelled_str, dict):
                    rides_cancelled_data = rides_cancelled_str
                elif isinstance(rides_cancelled_str, str):
                    rides_cancelled_data = json.loads(rides_cancelled_str)
                else:
                    print(f"Driver {driver_id}: Tipo inesperado - {type(rides_cancelled_str)}")
                    continue
                
                if not rides_cancelled_data.get('cancelled_rides'):
                    print(f"Driver {driver_id}: Sem cancelled_rides no JSON")
                    continue
                    
                cancelled_rides_list = rides_cancelled_data['cancelled_rides']
                print(f"Driver {driver_id} ({driver_city}): {len(cancelled_rides_list)} corridas no histórico")
                
                driver_cancelled_in_period = 0
                
                for ride in cancelled_rides_list:
                    cancelled_date_str = ride.get('cancelled_on')
                    if not cancelled_date_str:
                        continue
                        
                    try:
                        cancelled_date = datetime.strptime(cancelled_date_str, '%Y-%m-%d %H:%M:%S')
                        
                        if start_date <= cancelled_date.date() <= end_date:
                            total_cancelled_rides += 1
                            driver_cancelled_in_period += 1
                            
                    except (ValueError, TypeError) as date_error:
                        print(f"  Erro na data {cancelled_date_str}: {date_error}")
                        continue
                
                if driver_cancelled_in_period > 0:
                    print(f"  ✅ {driver_cancelled_in_period} corridas no período!")
                else:
                    print(f"  ❌ Nenhuma corrida no período")
                        
            except Exception as e:
                print(f"Driver {driver_id}: Erro processando JSON - {e}")
                continue
        
        print(f"\n🎯 RESULTADO FINAL: {total_cancelled_rides} corridas canceladas")
        
        if total_cancelled_rides == 0:
            print(f"\n🔍 INVESTIGAÇÃO ADICIONAL:")
            print("Verificando se existem dados mas com datas fora do período...")
            
            for record in records[:3]:
                driver_id, driver_city, rides_cancelled_str = record
                try:
                    data = json.loads(rides_cancelled_str)
                    rides = data.get('cancelled_rides', [])
                    print(f"\nDriver {driver_id}:")
                    for ride in rides[:3]:  # Mostrar só as 3 primeiras
                        date_str = ride.get('cancelled_on', 'N/A')
                        print(f"  - {date_str}")
                        if date_str != 'N/A':
                            try:
                                date_obj = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S').date()
                                if date_obj < start_date:
                                    print(f"    ❌ Anterior ao período (antes de {start_date})")
                                elif date_obj > end_date:
                                    print(f"    ❌ Posterior ao período (depois de {end_date})")
                                else:
                                    print(f"    ✅ Dentro do período!")
                            except:
                                print(f"    ❌ Data inválida")
                except Exception as e:
                    print(f"  Erro: {e}")

if __name__ == "__main__":
    testar_query_cancelamentos()