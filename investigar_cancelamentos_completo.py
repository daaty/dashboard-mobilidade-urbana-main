import requests
import json

def investigar_dados_cancelamentos():
    """Investiga por que estamos obtendo 0 cancelamentos"""
    
    print("=" * 80)
    print("🔍 INVESTIGAÇÃO: POR QUE 0 CORRIDAS CANCELADAS?")
    print("=" * 80)
    
    # Vamos criar um script para verificar diretamente no banco
    script_content = '''
import psycopg2
import json
from datetime import datetime, timedelta

try:
    # Conectar ao PostgreSQL - usando as credenciais do backend
    connection = psycopg2.connect(
        host="148.230.73.27",
        port=5432,
        database="grupo_matupa_novo",
        user="postgres",  # Tentando com postgres
        password="4c66a4c3-3b0a-4e81-9b30-b5b1074b1ebb"
    )
    
    cursor = connection.cursor()
    
    print("🔍 INVESTIGAÇÃO DIRETA NO BANCO DE DADOS")
    print("=" * 50)
    
    # 1. Verificar se a tabela driver_personal_details existe e tem dados
    query1 = """
    SELECT COUNT(*) 
    FROM driver_personal_details
    """
    cursor.execute(query1)
    total_records = cursor.fetchone()[0]
    print(f"📊 Total de registros em driver_personal_details: {total_records}")
    
    # 2. Verificar quantos têm rides_cancelled não nulo
    query2 = """
    SELECT COUNT(*) 
    FROM driver_personal_details 
    WHERE rides_cancelled IS NOT NULL
    """
    cursor.execute(query2)
    with_rides_cancelled = cursor.fetchone()[0]
    print(f"📝 Registros com rides_cancelled não nulo: {with_rides_cancelled}")
    
    # 3. Verificar tipos de dados em rides_cancelled
    query3 = """
    SELECT rides_cancelled::text, LENGTH(rides_cancelled::text)
    FROM driver_personal_details 
    WHERE rides_cancelled IS NOT NULL
    LIMIT 10
    """
    cursor.execute(query3)
    samples = cursor.fetchall()
    print(f"\\n📋 EXEMPLOS DE rides_cancelled:")
    for i, (data, length) in enumerate(samples, 1):
        print(f"{i}. Tamanho: {length} chars")
        if length > 100:
            print(f"   Início: {data[:100]}...")
        else:
            print(f"   Dados: {data}")
        print()
    
    # 4. Verificar se existem corridas canceladas válidas
    query4 = """
    SELECT driver_id, city, rides_cancelled::text
    FROM driver_personal_details 
    WHERE rides_cancelled IS NOT NULL
    AND rides_cancelled::text != '{}'
    AND rides_cancelled::text != ''
    AND rides_cancelled::text LIKE '%cancelled_rides%'
    LIMIT 5
    """
    cursor.execute(query4)
    valid_records = cursor.fetchall()
    print(f"🎯 REGISTROS COM DADOS DE CANCELAMENTO:")
    print(f"Total encontrados: {len(valid_records)}")
    
    for i, (driver_id, city, rides_cancelled_str) in enumerate(valid_records, 1):
        try:
            data = json.loads(rides_cancelled_str)
            cancelled_rides = data.get('cancelled_rides', [])
            total_cancelled = data.get('total_cancelled_rides', len(cancelled_rides))
            
            print(f"\\n{i}. Driver {driver_id} - {city}")
            print(f"   Total canceladas: {total_cancelled}")
            
            if cancelled_rides:
                print(f"   Primeira corrida cancelada:")
                first_ride = cancelled_rides[0]
                print(f"   - Data: {first_ride.get('cancelled_on', 'N/A')}")
                print(f"   - Por: {first_ride.get('cancelled_by', 'N/A')}")
                print(f"   - Motivo: {first_ride.get('reason', 'N/A')}")
            
        except Exception as e:
            print(f"{i}. Erro ao processar driver {driver_id}: {e}")
    
    # 5. Verificar datas específicas
    print(f"\\n📅 ANÁLISE DE DATAS:")
    if valid_records:
        for driver_id, city, rides_cancelled_str in valid_records[:2]:
            try:
                data = json.loads(rides_cancelled_str)
                cancelled_rides = data.get('cancelled_rides', [])
                
                print(f"\\nDriver {driver_id} - Datas de cancelamento:")
                for ride in cancelled_rides[:5]:
                    cancelled_date = ride.get('cancelled_on')
                    if cancelled_date:
                        # Converter para datetime
                        date_obj = datetime.strptime(cancelled_date, '%Y-%m-%d %H:%M:%S')
                        print(f"  - {cancelled_date} ({date_obj.date()})")
                        
                        # Verificar se está nos últimos 30 dias
                        thirty_days_ago = datetime.now().date() - timedelta(days=30)
                        if date_obj.date() >= thirty_days_ago:
                            print(f"    ✅ Dentro dos últimos 30 dias!")
                        else:
                            print(f"    ❌ Fora dos últimos 30 dias (mais de 30 dias atrás)")
                            
            except Exception as e:
                print(f"Erro ao analisar datas do driver {driver_id}: {e}")
    
    # 6. Testar a query exata que o endpoint está usando
    print(f"\\n🔧 TESTANDO QUERY EXATA DO ENDPOINT:")
    thirty_days_ago = datetime.now().date() - timedelta(days=30)
    today = datetime.now().date()
    
    query_endpoint = """
    SELECT driver_id, city, rides_cancelled
    FROM driver_personal_details 
    WHERE rides_cancelled IS NOT NULL
    AND rides_cancelled::text != '{}'
    AND rides_cancelled::text != ''
    """
    
    cursor.execute(query_endpoint)
    endpoint_records = cursor.fetchall()
    
    print(f"Registros encontrados pela query: {len(endpoint_records)}")
    
    total_within_period = 0
    for driver_id, city, rides_cancelled_str in endpoint_records:
        try:
            data = json.loads(rides_cancelled_str)
            cancelled_rides = data.get('cancelled_rides', [])
            
            for ride in cancelled_rides:
                cancelled_date_str = ride.get('cancelled_on')
                if cancelled_date_str:
                    cancelled_date = datetime.strptime(cancelled_date_str, '%Y-%m-%d %H:%M:%S').date()
                    if thirty_days_ago <= cancelled_date <= today:
                        total_within_period += 1
                        
        except Exception as e:
            continue
    
    print(f"Total de cancelamentos nos últimos 30 dias: {total_within_period}")

except Exception as e:
    print(f"Erro na conexão: {e}")
    
    # Tentar com credenciais alternativas
    try:
        print("\\nTentando com credenciais alternativas...")
        connection = psycopg2.connect(
            host="148.230.73.27",
            port=5432,
            database="grupo_matupa_novo",
            user="grupo_matupa_user",
            password="4c66a4c3-3b0a-4e81-9b30-b5b1074b1ebb"
        )
        print("✅ Conectado com grupo_matupa_user!")
        
        cursor = connection.cursor()
        cursor.execute("SELECT COUNT(*) FROM driver_personal_details")
        count = cursor.fetchone()[0]
        print(f"Total de registros: {count}")
        
    except Exception as e2:
        print(f"Também falhou: {e2}")
        
finally:
    if 'cursor' in locals():
        cursor.close()
    if 'connection' in locals():
        connection.close()
'''
    
    # Salvar e executar script
    with open('investigar_cancelamentos.py', 'w', encoding='utf-8') as f:
        f.write(script_content)
    
    print("🔗 Executando investigação no banco...")
    import subprocess
    import sys
    import os
    
    result = subprocess.run([sys.executable, 'investigar_cancelamentos.py'], 
                          capture_output=True, text=True, cwd='.')
    
    if result.returncode == 0:
        print(result.stdout)
    else:
        print(f"❌ Erro: {result.stderr}")
    
    # Limpar arquivo
    try:
        os.remove('investigar_cancelamentos.py')
    except:
        pass

if __name__ == "__main__":
    investigar_dados_cancelamentos()