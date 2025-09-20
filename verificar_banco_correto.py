import psycopg2
import json

try:
    # Usar as mesmas credenciais que o backend está usando
    connection = psycopg2.connect(
        host="148.230.73.27",
        port=5432,
        database="n8n_db",  # ESTE é o banco que o backend usa!
        user="n8n_user",
        password="n8n_pw"
    )
    
    cursor = connection.cursor()
    print("🔗 CONECTADO AO BANCO CORRETO (n8n_db)")
    print("=" * 50)
    
    # 1. Verificar se a tabela existe
    cursor.execute("""
        SELECT EXISTS (
           SELECT FROM information_schema.tables 
           WHERE table_name = 'driver_personal_details'
        );
    """)
    table_exists = cursor.fetchone()[0]
    print(f"📋 Tabela driver_personal_details existe: {table_exists}")
    
    if not table_exists:
        print("❌ A tabela driver_personal_details NÃO EXISTE no banco n8n_db!")
        print("Verificando quais tabelas existem...")
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """)
        tables = cursor.fetchall()
        print("Tabelas disponíveis:")
        for table in tables:
            print(f"  - {table[0]}")
    else:
        # Se existe, verificar os dados
        cursor.execute("SELECT COUNT(*) FROM driver_personal_details")
        total = cursor.fetchone()[0]
        print(f"📊 Total de registros: {total}")
        
        if total > 0:
            cursor.execute("""
                SELECT COUNT(*) 
                FROM driver_personal_details 
                WHERE rides_cancelled IS NOT NULL
                AND rides_cancelled::text != '{}'
                AND rides_cancelled::text != ''
            """)
            with_cancellations = cursor.fetchone()[0]
            print(f"🚫 Com dados de cancelamento: {with_cancellations}")
            
            if with_cancellations > 0:
                cursor.execute("""
                    SELECT driver_id, city, rides_cancelled::text
                    FROM driver_personal_details 
                    WHERE rides_cancelled IS NOT NULL
                    AND rides_cancelled::text != '{}'
                    AND rides_cancelled::text != ''
                    LIMIT 3
                """)
                samples = cursor.fetchall()
                print("📋 EXEMPLOS:")
                for driver_id, city, rides_cancelled in samples:
                    print(f"Driver {driver_id} - {city}")
                    try:
                        data = json.loads(rides_cancelled)
                        cancelled_rides = data.get('cancelled_rides', [])
                        print(f"  Canceladas: {len(cancelled_rides)}")
                        if cancelled_rides:
                            print(f"  Primeira: {cancelled_rides[0].get('cancelled_on', 'N/A')}")
                    except:
                        print(f"  Erro ao processar JSON")
                    print()
        
except Exception as e:
    print(f"❌ ERRO: {e}")
finally:
    if 'cursor' in locals():
        cursor.close()
    if 'connection' in locals():
        connection.close()