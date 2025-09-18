#!/usr/bin/env python3
"""
Script para analisar dados reais da tabela passenger_personal_details
e identificar que métricas podemos extrair para o dashboard
"""
import psycopg2
from psycopg2.extras import RealDictCursor
import json
from datetime import datetime

# Configuração do banco PostgreSQL
DATABASE_CONFIG = {
    'host': '148.230.73.27',
    'port': 5432,
    'database': 'n8n_db',
    'user': 'n8n_user',
    'password': 'n8n_pw'
}

def analyze_passenger_data_for_dashboard():
    """Analisa os dados dos passageiros para identificar métricas úteis para dashboard"""
    try:
        conn = psycopg2.connect(**DATABASE_CONFIG)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        print("📊 ANÁLISE DOS DADOS PARA DASHBOARD - PASSAGEIROS")
        print("=" * 60)
        
        # 1. Análise básica dos dados
        cursor.execute("SELECT COUNT(*) as total FROM passenger_personal_details;")
        total = cursor.fetchone()['total']
        print(f"🔢 Total de passageiros: {total}")
        
        # 2. Análise por cidade
        cursor.execute("""
            SELECT city, COUNT(*) as count 
            FROM passenger_personal_details 
            WHERE city IS NOT NULL 
            GROUP BY city 
            ORDER BY count DESC;
        """)
        cities_data = cursor.fetchall()
        print(f"\n🏙️ DISTRIBUIÇÃO POR CIDADE ({len(cities_data)} cidades):")
        for city in cities_data:
            print(f"  • {city['city']}: {city['count']} passageiros")
        
        # 3. Análise de corridas e gastos
        cursor.execute("""
            SELECT 
                AVG(total_rides) as avg_rides,
                SUM(total_rides) as total_rides,
                MAX(total_rides) as max_rides,
                AVG(total_spent) as avg_spent,
                SUM(total_spent) as total_spent,
                MAX(total_spent) as max_spent,
                AVG(average_rating) as avg_rating,
                COUNT(CASE WHEN total_rides > 0 THEN 1 END) as active_passengers
            FROM passenger_personal_details;
        """)
        metrics = cursor.fetchone()
        
        print(f"\n💰 MÉTRICAS DE NEGÓCIO:")
        print(f"  • Total de corridas: {metrics['total_rides'] or 0}")
        print(f"  • Média de corridas por passageiro: {metrics['avg_rides'] or 0:.1f}")
        print(f"  • Passageiro mais ativo: {metrics['max_rides'] or 0} corridas")
        print(f"  • Total gasto pelos passageiros: R$ {metrics['total_spent'] or 0:.2f}")
        print(f"  • Média de gasto por passageiro: R$ {metrics['avg_spent'] or 0:.2f}")
        print(f"  • Maior gasto individual: R$ {metrics['max_spent'] or 0:.2f}")
        print(f"  • Avaliação média: {metrics['avg_rating'] or 0:.2f}/5.0")
        print(f"  • Passageiros ativos: {metrics['active_passengers'] or 0}")
        
        # 4. Análise dos dados JSONB (personal_data e rides_history)
        print(f"\n🔍 ANÁLISE DOS DADOS JSON:")
        
        # Examinar structure do personal_data
        cursor.execute("""
            SELECT personal_data 
            FROM passenger_personal_details 
            WHERE personal_data IS NOT NULL 
            LIMIT 3;
        """)
        personal_samples = cursor.fetchall()
        
        if personal_samples:
            print("  📝 Estrutura do personal_data:")
            for i, sample in enumerate(personal_samples, 1):
                data = sample['personal_data']
                print(f"    Amostra {i}: {list(data.keys()) if data else 'Vazio'}")
        
        # Examinar rides_history
        cursor.execute("""
            SELECT rides_history 
            FROM passenger_personal_details 
            WHERE rides_history IS NOT NULL 
            AND jsonb_array_length(rides_history) > 0
            LIMIT 2;
        """)
        rides_samples = cursor.fetchall()
        
        if rides_samples:
            print("  🚗 Estrutura do rides_history:")
            for i, sample in enumerate(rides_samples, 1):
                rides = sample['rides_history']
                if rides and len(rides) > 0:
                    first_ride = rides[0]
                    print(f"    Amostra {i} - Campos da corrida: {list(first_ride.keys())}")
                    print(f"    Exemplo: {first_ride}")
        
        # 5. Análise temporal (se tivermos datas)
        cursor.execute("""
            SELECT 
                COUNT(CASE WHEN registration_date >= CURRENT_DATE - INTERVAL '30 days' THEN 1 END) as new_30_days,
                COUNT(CASE WHEN last_activity_date >= CURRENT_DATE - INTERVAL '7 days' THEN 1 END) as active_7_days,
                COUNT(CASE WHEN registration_date IS NOT NULL THEN 1 END) as with_registration_date,
                COUNT(CASE WHEN last_activity_date IS NOT NULL THEN 1 END) as with_activity_date
            FROM passenger_personal_details;
        """)
        temporal = cursor.fetchone()
        
        print(f"\n📅 ANÁLISE TEMPORAL:")
        print(f"  • Novos passageiros (30 dias): {temporal['new_30_days']}")
        print(f"  • Ativos nos últimos 7 dias: {temporal['active_7_days']}")
        print(f"  • Com data de registro: {temporal['with_registration_date']}")
        print(f"  • Com última atividade: {temporal['with_activity_date']}")
        
        # 6. Análise de preferências
        cursor.execute("""
            SELECT 
                favorite_payment_method, COUNT(*) as count
            FROM passenger_personal_details 
            WHERE favorite_payment_method IS NOT NULL
            GROUP BY favorite_payment_method
            ORDER BY count DESC;
        """)
        payment_methods = cursor.fetchall()
        
        if payment_methods:
            print(f"\n💳 MÉTODOS DE PAGAMENTO PREFERIDOS:")
            for method in payment_methods:
                print(f"  • {method['favorite_payment_method']}: {method['count']} passageiros")
        
        # 7. Sugerir endpoints baseados nos dados reais
        print(f"\n🎯 ENDPOINTS SUGERIDOS BASEADOS NOS DADOS REAIS:")
        print("=" * 50)
        
        endpoints = [
            {
                "endpoint": "/api/passengers/kpis",
                "description": f"KPIs gerais: {total} passageiros, {metrics['total_rides'] or 0} corridas, R$ {metrics['total_spent'] or 0:.2f} receita"
            },
            {
                "endpoint": "/api/passengers/by-city", 
                "description": f"Distribuição por cidade ({len(cities_data)} cidades ativas)"
            },
            {
                "endpoint": "/api/passengers/activity",
                "description": f"Análise de atividade: {temporal['active_7_days']} ativos recentes"
            },
            {
                "endpoint": "/api/passengers/revenue-analysis",
                "description": f"Análise financeira: ticket médio R$ {metrics['avg_spent'] or 0:.2f}"
            },
            {
                "endpoint": "/api/passengers/rides-analytics",
                "description": f"Analytics de corridas: {metrics['avg_rides'] or 0:.1f} corridas/passageiro"
            },
            {
                "endpoint": "/api/passengers/top-passengers",
                "description": "Top passageiros por corridas e gastos"
            }
        ]
        
        for ep in endpoints:
            print(f"📍 {ep['endpoint']}")
            print(f"   └─ {ep['description']}")
        
        cursor.close()
        conn.close()
        
        return {
            'total_passengers': total,
            'cities_count': len(cities_data),
            'metrics': dict(metrics),
            'has_rides_data': len(rides_samples) > 0,
            'has_personal_data': len(personal_samples) > 0
        }
        
    except Exception as e:
        print(f"❌ Erro na análise: {e}")
        return None

if __name__ == "__main__":
    print("🔄 Analisando dados dos passageiros para dashboard...")
    result = analyze_passenger_data_for_dashboard()
    
    if result:
        print(f"\n✅ Análise concluída!")
        print(f"📊 Pronto para criar {6} endpoints úteis para o dashboard")
    else:
        print(f"\n❌ Falha na análise.")