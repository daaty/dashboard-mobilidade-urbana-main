import requests
import psycopg2
import json

def check_drivers_without_city():
    """Verificar se há motoristas/corridas sem cidade definida"""
    
    # Conectar ao PostgreSQL
    conn = psycopg2.connect(
        host="148.230.73.27",
        port=5432,
        database="n8n_db",
        user="n8n_user",
        password="n8n_password"
    )
    
    cur = conn.cursor()
    
    # Query para encontrar motoristas sem cidade ou com cidade NULL/vazia
    query = """
    WITH ranked_drivers AS (
        SELECT 
            dd.driver_id,
            dd.name,
            dd.additional_data,
            dd.page_source,
            dpd.city as dpd_city,
            dpd.rides_history,
            ROW_NUMBER() OVER (
                PARTITION BY dd.driver_id 
                ORDER BY 
                    CASE dd.page_source 
                        WHEN 'Active Drivers' THEN 1
                        WHEN 'Driver Performance' THEN 2  
                        WHEN 'Leaderboard' THEN 3
                        WHEN 'Drivers Enrollment' THEN 4
                        WHEN 'Deactive Drivers' THEN 5
                        ELSE 6
                    END
            ) as rn
        FROM drivers_data dd
        LEFT JOIN driver_personal_details dpd ON dd.driver_id = dpd.driver_id
        WHERE dd.page_source IN ('Active Drivers', 'Deactive Drivers', 'Driver Performance', 'Leaderboard', 'Drivers Enrollment')
    )
    SELECT 
        driver_id, name, additional_data, dpd_city, rides_history
    FROM ranked_drivers 
    WHERE rn = 1
    """
    
    cur.execute(query)
    drivers = cur.fetchall()
    
    drivers_without_city = []
    drivers_with_rides_no_city = []
    
    for driver in drivers:
        driver_id, name, additional_data, dpd_city, rides_history = driver
        
        # Parse additional_data
        try:
            add_data = json.loads(additional_data) if isinstance(additional_data, str) else additional_data
            city_from_additional = add_data.get('City', '') if add_data else ''
        except:
            city_from_additional = ''
        
        # Verificar se tem cidade definida
        has_city = bool(dpd_city) or bool(city_from_additional)
        
        if not has_city:
            drivers_without_city.append((driver_id, name))
            
            # Verificar se tem corridas
            try:
                rides = json.loads(rides_history) if rides_history else []
                if rides:
                    drivers_with_rides_no_city.append((driver_id, name, len(rides)))
            except:
                pass
    
    print(f'🔍 Motoristas sem cidade definida: {len(drivers_without_city)}')
    for driver_id, name in drivers_without_city:
        print(f'  - {name} (ID: {driver_id})')
    
    print(f'\n🚗 Motoristas sem cidade COM corridas: {len(drivers_with_rides_no_city)}')
    for driver_id, name, ride_count in drivers_with_rides_no_city:
        print(f'  - {name} (ID: {driver_id}) - {ride_count} corridas')
    
    cur.close()
    conn.close()

if __name__ == "__main__":
    check_drivers_without_city()
