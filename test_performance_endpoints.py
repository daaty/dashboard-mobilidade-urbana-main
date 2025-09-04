import psycopg2
import json
import requests
from datetime import datetime, timedelta

# Configuração do banco
DB_CONFIG = {
    'host': '148.230.73.27',
    'port': 5432,
    'database': 'n8n_db',
    'user': 'n8n_user',
    'password': 'n8n_pw'
}

# URL base da API
API_BASE = "http://localhost:8000"

def test_database_dates():
    """Testa as datas das corridas no banco"""
    print("=" * 50)
    print("TESTANDO DATAS DAS CORRIDAS NO BANCO")
    print("=" * 50)
    
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        
        # Verificar datas das corridas
        cur.execute('''
            SELECT 
                dd.driver_id,
                dd.name,
                dpd.rides_history
            FROM drivers_data dd
            LEFT JOIN driver_personal_details dpd ON dd.driver_id = dpd.driver_id
            WHERE dpd.rides_history IS NOT NULL
            LIMIT 5
        ''')
        
        drivers = cur.fetchall()
        ride_dates = []
        
        for driver in drivers:
            driver_id, name, rides_history = driver
            if rides_history:
                rides = rides_history if isinstance(rides_history, list) else []
                print(f"\nDriver {name}: {len(rides)} corridas")
                
                for i, ride in enumerate(rides[:3]):
                    if isinstance(ride, dict) and 'date' in ride:
                        ride_date = ride.get('date')
                        ride_dates.append(ride_date)
                        print(f"  Corrida {i+1}: {ride_date}")
                        print(f"    Status: {ride.get('status', 'N/A')}")
                        print(f"    Valor: {ride.get('fare_amount', 'N/A')}")
                        
                        # Tentar parsear a data
                        try:
                            parsed_date = datetime.fromisoformat(ride_date.replace('Z', '+00:00'))
                            print(f"    Data parseada: {parsed_date}")
                        except Exception as e:
                            print(f"    ❌ Erro ao parsear data: {e}")
        
        # Analisar intervalo de datas
        if ride_dates:
            print(f"\n📅 ANÁLISE DE DATAS:")
            print(f"Total de corridas analisadas: {len(ride_dates)}")
            print(f"Primeira corrida: {min(ride_dates)}")
            print(f"Última corrida: {max(ride_dates)}")
            print(f"Data atual: {datetime.now().isoformat()}")
        
        cur.close()
        conn.close()
        return ride_dates
        
    except Exception as e:
        print(f"❌ Erro ao conectar ao banco: {e}")
        return []

def test_performance_endpoints():
    """Testa todos os endpoints de performance"""
    print("\n" + "=" * 50)
    print("TESTANDO ENDPOINTS DE PERFORMANCE")
    print("=" * 50)
    
    endpoints = [
        ("Overview 7 dias", "/api/analytics/performance/overview?period=7_days"),
        ("Overview 30 dias", "/api/analytics/performance/overview?period=30_days"),
        ("Overview 90 dias", "/api/analytics/performance/overview?period=90_days"),
        ("Trends", "/api/analytics/performance/trends?period=30_days"),
        ("Achievements", "/api/analytics/performance/achievements"),
        ("Alerts", "/api/analytics/performance/alerts"),
        ("Predictions", "/api/analytics/performance/predictions"),
        ("Detailed Metrics", "/api/analytics/performance/detailed-metrics?period=90_days")
    ]
    
    results = {}
    
    for name, endpoint in endpoints:
        try:
            print(f"\n🔍 Testando {name}...")
            url = f"{API_BASE}{endpoint}"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                results[name] = data
                print(f"✅ {name}: OK")
                
                # Mostrar dados resumidos
                if 'data' in data:
                    overview_data = data['data']
                    if isinstance(overview_data, dict):
                        print(f"   Total drivers: {overview_data.get('total_drivers', 'N/A')}")
                        print(f"   Active drivers: {overview_data.get('active_drivers', 'N/A')}")
                        print(f"   Performance score: {overview_data.get('performance_score', 'N/A')}")
                
                if 'achievements' in data:
                    achievements = data['achievements']
                    print(f"   Achievements: {len(achievements)} items")
                    
                if 'alerts' in data:
                    alerts = data['alerts']
                    print(f"   Alerts: {len(alerts)} items")
                    
                if 'predictions' in data:
                    predictions = data['predictions']
                    print(f"   Predictions: {len(predictions)} items")
                    
                if 'trends' in data:
                    trends = data['trends']
                    print(f"   Trends: {len(trends)} periods")
                    
                if 'metrics' in data:
                    metrics = data['metrics']
                    print(f"   Detailed metrics: {len(metrics)} drivers")
                    
            else:
                print(f"❌ {name}: HTTP {response.status_code}")
                print(f"   Response: {response.text[:200]}...")
                
        except Exception as e:
            print(f"❌ {name}: Erro - {e}")
    
    return results

def analyze_performance_data(results):
    """Analisa os dados de performance"""
    print("\n" + "=" * 50)
    print("ANÁLISE DOS DADOS DE PERFORMANCE")
    print("=" * 50)
    
    # Verificar se há dados reais
    overview_7d = results.get("Overview 7 dias", {})
    overview_30d = results.get("Overview 30 dias", {})
    overview_90d = results.get("Overview 90 dias", {})
    
    print("\n📊 COMPARAÇÃO POR PERÍODO:")
    periods = [
        ("7 dias", overview_7d),
        ("30 dias", overview_30d), 
        ("90 dias", overview_90d)
    ]
    
    for period_name, data in periods:
        if 'data' in data:
            period_data = data['data']
            print(f"\n{period_name}:")
            print(f"  ✅ Total drivers: {period_data.get('total_drivers', 0)}")
            print(f"  🟢 Active drivers: {period_data.get('active_drivers', 0)}")
            print(f"  📈 Performance score: {period_data.get('performance_score', 0)}")
            print(f"  ⚡ Efficiency score: {period_data.get('efficiency_score', 0)}")
            print(f"  ⭐ Quality score: {period_data.get('quality_score', 0)}")
            
            # Distribution
            dist = period_data.get('performance_distribution', {})
            print(f"  📊 Distribution:")
            print(f"    Excellent: {dist.get('excellent', 0)}")
            print(f"    Good: {dist.get('good', 0)}")
            print(f"    Average: {dist.get('average', 0)}")
            print(f"    Poor: {dist.get('poor', 0)}")

def recommend_fixes():
    """Recomenda correções baseadas nos testes"""
    print("\n" + "=" * 50)
    print("RECOMENDAÇÕES PARA CORREÇÃO")
    print("=" * 50)
    
    print("\n🔧 AÇÕES RECOMENDADAS:")
    print("1. Ajustar filtro de período para incluir todas as corridas (agosto-setembro 2025)")
    print("2. Modificar cálculo de active_drivers para não depender de período específico")
    print("3. Usar dados de personal_data para ratings mesmo sem corridas no período")
    print("4. Implementar fallback para dados quando período não tem corridas")
    print("5. Adicionar logs para debug de filtros de data")

def main():
    """Função principal"""
    print("🚀 INICIANDO TESTES DOS ENDPOINTS DE PERFORMANCE")
    print(f"Data/Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 1. Testar datas do banco
    ride_dates = test_database_dates()
    
    # 2. Testar endpoints
    results = test_performance_endpoints()
    
    # 3. Analisar dados
    analyze_performance_data(results)
    
    # 4. Recomendações
    recommend_fixes()
    
    print("\n✅ TESTES CONCLUÍDOS!")

if __name__ == "__main__":
    main()
