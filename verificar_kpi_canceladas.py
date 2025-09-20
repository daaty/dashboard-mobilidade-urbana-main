import requests
import json

def verificar_corridas_canceladas():
    """Verifica os dados de corridas canceladas no KPI e endpoint detalhado"""
    
    print("=" * 80)
    print("🔍 ANÁLISE DO KPI 'CORRIDAS CANCELADAS' - VALOR: 251")
    print("=" * 80)
    
    # 1. Testar o endpoint de KPIs
    print("\n1. 🎯 ENDPOINT DE KPIs (/api/drivers/kpis)")
    print("-" * 50)
    
    try:
        response = requests.get('http://localhost:8000/api/drivers/kpis?period=30_days&city=all&status=all')
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                kpis = data.get('data', {})
                cancelled_rides = kpis.get('cancelled_rides', 0)
                total_rides = kpis.get('total_rides', 0)
                
                print(f"✅ Corridas Canceladas: {cancelled_rides}")
                print(f"📊 Total de Corridas: {total_rides}")
                print(f"📈 Taxa de Cancelamento: {(cancelled_rides / total_rides * 100):.2f}%" if total_rides > 0 else "0%")
                
                # Mostrar outros campos relacionados
                print(f"📍 Período: {kpis.get('period', 'N/A')}")
                print(f"🏙️ Cidade: {kpis.get('city_filter', 'N/A')}")
                
            else:
                print(f"❌ Erro na resposta: {data.get('message', 'Desconhecido')}")
        else:
            print(f"❌ Erro HTTP {response.status_code}")
    except Exception as e:
        print(f"❌ Erro ao conectar: {e}")
    
    # 2. Testar algumas variações de filtros
    print("\n2. 🔄 TESTE COM DIFERENTES FILTROS")
    print("-" * 50)
    
    filtros_teste = [
        ("7_days", "all"),
        ("30_days", "all"),
        ("6_months", "all"),
        ("30_days", "Matupá"),
        ("30_days", "Nova Monte Verde"),
    ]
    
    for period, city in filtros_teste:
        try:
            response = requests.get(f'http://localhost:8000/api/drivers/kpis?period={period}&city={city}&status=all')
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    cancelled = data['data'].get('cancelled_rides', 0)
                    total = data['data'].get('total_rides', 0)
                    print(f"📅 {period} | 🏙️ {city}: {cancelled} canceladas de {total} totais")
                else:
                    print(f"❌ {period} | {city}: Erro - {data.get('message', 'N/A')}")
            else:
                print(f"❌ {period} | {city}: HTTP {response.status_code}")
        except Exception as e:
            print(f"❌ {period} | {city}: Erro - {e}")
    
    # 3. Verificar estrutura dos dados raw
    print("\n3. 🔍 VERIFICAÇÃO DE DADOS RAW (Driver Performance)")
    print("-" * 50)
    
    try:
        # Fazer uma requisição direta ao banco via script de análise
        import subprocess
        import sys
        import os
        
        # Criar script temporário para verificar dados
        script_content = '''
import psycopg2
import json

try:
    # Conectar ao PostgreSQL
    connection = psycopg2.connect(
        host="148.230.73.27",
        port=5432,
        database="grupo_matupa_novo",
        user="grupo_matupa",
        password="4c66a4c3-3b0a-4e81-9b30-b5b1074b1ebb"
    )
    
    cursor = connection.cursor()
    
    print("🔍 ANÁLISE DIRETA NO BANCO DE DADOS")
    print("=" * 50)
    
    # Query para contar registros com cancelamentos
    query = """
    SELECT 
        COUNT(*) as total_records,
        COUNT(CASE WHEN additional_data IS NOT NULL THEN 1 END) as with_additional_data,
        COUNT(CASE WHEN additional_data::text LIKE '%cancelled_rides%' THEN 1 END) as with_cancelled_data
    FROM drivers_data 
    WHERE page_source = 'Driver Performance'
    """
    
    cursor.execute(query)
    result = cursor.fetchone()
    
    print(f"📊 Total de registros Driver Performance: {result[0]}")
    print(f"📝 Com additional_data: {result[1]}")
    print(f"🚫 Com dados de cancelamento: {result[2]}")
    
    # Buscar alguns exemplos de cancelamentos
    query = """
    SELECT driver_id, name, additional_data::text
    FROM drivers_data 
    WHERE page_source = 'Driver Performance'
    AND additional_data::text LIKE '%cancelled_rides%'
    LIMIT 10
    """
    
    cursor.execute(query)
    records = cursor.fetchall()
    
    print(f"\\n📋 EXEMPLOS DE REGISTROS COM CANCELAMENTOS:")
    print("-" * 40)
    
    total_driver_cancelled = 0
    total_user_cancelled = 0
    
    for i, (driver_id, name, additional_data_str) in enumerate(records, 1):
        try:
            additional_data = json.loads(additional_data_str)
            driver_cancelled = int(additional_data.get('driver_cancelled_rides', 0))
            user_cancelled = int(additional_data.get('user_cancelled_rides', 0))
            total = driver_cancelled + user_cancelled
            
            total_driver_cancelled += driver_cancelled
            total_user_cancelled += user_cancelled
            
            print(f"{i}. Driver {driver_id} ({name})")
            print(f"   🚗 Driver cancelou: {driver_cancelled}")
            print(f"   👤 Usuário cancelou: {user_cancelled}")
            print(f"   📊 Total: {total}")
            print()
            
        except Exception as e:
            print(f"{i}. Erro ao processar {driver_id}: {e}")
    
    print(f"🔢 TOTAIS DOS EXEMPLOS:")
    print(f"🚗 Total canceladas por drivers: {total_driver_cancelled}")
    print(f"👤 Total canceladas por usuários: {total_user_cancelled}")
    print(f"📊 Total geral: {total_driver_cancelled + total_user_cancelled}")
    
except Exception as e:
    print(f"❌ Erro na conexão: {e}")
finally:
    if 'cursor' in locals():
        cursor.close()
    if 'connection' in locals():
        connection.close()
'''
        
        # Salvar script temporário
        with open('temp_check_cancelados.py', 'w', encoding='utf-8') as f:
            f.write(script_content)
        
        print("🔗 Executando verificação direta no banco...")
        result = subprocess.run([sys.executable, 'temp_check_cancelados.py'], 
                              capture_output=True, text=True, cwd='.')
        
        if result.returncode == 0:
            print(result.stdout)
        else:
            print(f"❌ Erro na execução: {result.stderr}")
        
        # Limpar arquivo temporário
        try:
            os.remove('temp_check_cancelados.py')
        except:
            pass
            
    except Exception as e:
        print(f"❌ Erro ao executar verificação: {e}")

if __name__ == "__main__":
    verificar_corridas_canceladas()