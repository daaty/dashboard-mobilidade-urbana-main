import psycopg2
import json

# Configuração do banco
DB_CONFIG = {
    'host': '148.230.73.27',
    'port': 5432,
    'database': 'n8n_db',
    'user': 'n8n_user',
    'password': 'n8n_pw'
}

def examine_ride_structure():
    """Examina a estrutura real dos dados de corrida"""
    print("=" * 60)
    print("EXAMINANDO ESTRUTURA DAS CORRIDAS")
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
            LIMIT 2
        ''')
        
        drivers = cur.fetchall()
        
        for driver in drivers:
            driver_id, name, rides_history = driver
            print(f"\n🚗 Driver: {name} (ID: {driver_id})")
            
            if rides_history:
                rides = rides_history if isinstance(rides_history, list) else []
                print(f"   📊 Total de corridas: {len(rides)}")
                
                # Examinar as primeiras corridas
                for i, ride in enumerate(rides[:2]):
                    print(f"\n   🔍 CORRIDA {i+1}:")
                    print(f"   Tipo: {type(ride)}")
                    
                    if isinstance(ride, dict):
                        print(f"   Chaves disponíveis:")
                        for key in ride.keys():
                            value = ride[key]
                            if isinstance(value, str) and len(value) > 100:
                                print(f"     {key}: {type(value)} (texto longo: {len(value)} chars)")
                            else:
                                print(f"     {key}: {value} ({type(value)})")
                    else:
                        print(f"   Valor: {ride}")
                        
                    print(f"   " + "-"*50)
        
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    examine_ride_structure()
