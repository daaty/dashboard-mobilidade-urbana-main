import psycopg2
import json
from datetime import datetime, timedelta

# Configuração do banco
DB_CONFIG = {
    'host': '148.230.73.27',
    'port': 5432,
    'database': 'n8n_db',
    'user': 'n8n_user',
    'password': 'n8n_pw'
}

def analyze_real_data_for_predictions():
    """Analisa dados reais para gerar predições realistas"""
    print("=" * 60)
    print("ANALISANDO DADOS REAIS PARA PREDIÇÕES")
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
        ''')
        
        drivers = cur.fetchall()
        
        # Análise por período
        now = datetime.now()
        periods = {
            'last_7_days': now - timedelta(days=7),
            'last_30_days': now - timedelta(days=30),
            'last_90_days': now - timedelta(days=90)
        }
        
        stats = {}
        
        for period_name, start_date in periods.items():
            print(f"\n📊 ANÁLISE - {period_name.upper()}:")
            
            total_rides = 0
            total_revenue = 0
            active_drivers = 0
            completed_rides = 0
            
            for driver in drivers:
                driver_id, name, rides_history = driver
                
                if rides_history:
                    rides = rides_history if isinstance(rides_history, list) else []
                    period_rides = []
                    
                    for ride in rides:
                        if isinstance(ride, dict) and 'drop_time' in ride:
                            try:
                                drop_time_str = ride['drop_time'].strip().replace(' : ', ' ')
                                ride_date = datetime.strptime(drop_time_str, '%d/%m/%Y %I:%M %p')
                                
                                if start_date <= ride_date <= now:
                                    period_rides.append(ride)
                            except:
                                continue
                    
                    if period_rides:
                        active_drivers += 1
                        total_rides += len(period_rides)
                        
                        for ride in period_rides:
                            if ride.get('fare'):
                                try:
                                    fare = float(ride['fare'])
                                    total_revenue += fare
                                    if fare > 0:
                                        completed_rides += 1
                                except:
                                    continue
            
            # Calcular médias por dia
            days_in_period = (now - start_date).days
            if days_in_period > 0:
                avg_rides_per_day = total_rides / days_in_period
                avg_revenue_per_day = total_revenue / days_in_period
                completion_rate = (completed_rides / total_rides * 100) if total_rides > 0 else 0
            else:
                avg_rides_per_day = 0
                avg_revenue_per_day = 0
                completion_rate = 0
            
            stats[period_name] = {
                'total_rides': total_rides,
                'total_revenue': total_revenue,
                'active_drivers': active_drivers,
                'completed_rides': completed_rides,
                'days': days_in_period,
                'avg_rides_per_day': avg_rides_per_day,
                'avg_revenue_per_day': avg_revenue_per_day,
                'completion_rate': completion_rate
            }
            
            print(f"   Total corridas: {total_rides}")
            print(f"   Receita total: R$ {total_revenue:.2f}")
            print(f"   Motoristas ativos: {active_drivers}")
            print(f"   Corridas por dia: {avg_rides_per_day:.1f}")
            print(f"   Receita por dia: R$ {avg_revenue_per_day:.2f}")
            print(f"   Taxa conclusão: {completion_rate:.1f}%")
        
        # Calcular predições realistas
        print(f"\n🔮 PREDIÇÕES REALISTAS:")
        
        # Usar dados de 7 dias para predição de amanhã
        if stats['last_7_days']['avg_rides_per_day'] > 0:
            predicted_rides_tomorrow = int(stats['last_7_days']['avg_rides_per_day'])
            print(f"   Corridas amanhã: ~{predicted_rides_tomorrow} corridas")
        
        # Usar dados de 30 dias para predição de próxima semana
        if stats['last_30_days']['avg_revenue_per_day'] > 0:
            predicted_revenue_week = stats['last_30_days']['avg_revenue_per_day'] * 7
            print(f"   Receita próxima semana: R$ {predicted_revenue_week:.2f}")
        
        # Taxa de conversão baseada em dados reais
        current_completion = stats['last_30_days']['completion_rate']
        print(f"   Taxa de conclusão atual: {current_completion:.1f}%")
        
        cur.close()
        conn.close()
        
        return stats
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        return {}

if __name__ == "__main__":
    analyze_real_data_for_predictions()
