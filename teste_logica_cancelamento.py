#!/usr/bin/env python3
"""Teste DIRETO da lógica de cancelamento do endpoint"""

import psycopg2
from datetime import datetime, timedelta
import json

def test_endpoint_cancellation_logic():
    """Testa exatamente a mesma lógica que implementamos no endpoint"""
    
    DATABASE_URL = "postgresql://postgres:n8nmtcuiaba@localhost:5432/n8n_db"
    
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        
        # Período de 30 dias (mesma lógica do endpoint)
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=30)
        
        print(f"🔍 TESTANDO LÓGICA DO ENDPOINT")
        print(f"📅 Período: {start_date} até {end_date}")
        print("="*50)
        
        # EXATAMENTE a mesma query do endpoint
        query = """
        SELECT driver_id, rides_cancelled
        FROM driver_personal_details 
        WHERE rides_cancelled IS NOT NULL 
        AND rides_cancelled::text LIKE '%cancelled_rides%'
        AND rides_cancelled::text != 'null'
        """
        
        cursor.execute(query)
        results = cursor.fetchall()
        
        print(f"📊 Drivers com dados de cancelamento: {len(results)}")
        
        total_cancelled_rides = 0
        
        for driver_id, rides_cancelled_raw in results:
            try:
                # MESMA LÓGICA DO ENDPOINT
                if isinstance(rides_cancelled_raw, dict):
                    rides_cancelled_data = rides_cancelled_raw
                else:
                    rides_cancelled_data = json.loads(rides_cancelled_raw)
                
                if not rides_cancelled_data.get('cancelled_rides'):
                    continue
                    
                cancelled_rides_list = rides_cancelled_data['cancelled_rides']
                driver_cancelled_in_period = 0
                
                # Filtrar por período (MESMA LÓGICA DO ENDPOINT)
                for ride in cancelled_rides_list:
                    cancelled_date_str = ride.get('cancelled_on')
                    if not cancelled_date_str:
                        continue
                        
                    try:
                        cancelled_date = datetime.strptime(cancelled_date_str, '%Y-%m-%d %H:%M:%S')
                        
                        if start_date <= cancelled_date.date() <= end_date:
                            total_cancelled_rides += 1
                            driver_cancelled_in_period += 1
                            
                    except (ValueError, TypeError):
                        continue
                
                if driver_cancelled_in_period > 0:
                    print(f"✅ Driver {driver_id}: {driver_cancelled_in_period} cancelamentos no período")
                        
            except (json.JSONDecodeError, ValueError, TypeError):
                continue
        
        print(f"\n🎯 RESULTADO FINAL: {total_cancelled_rides} cancelamentos")
        
        if total_cancelled_rides == 22:
            print("✅ PERFEITO! Este é o resultado esperado (22 cancelamentos)")
        elif total_cancelled_rides == 0:
            print("❌ PROBLEMA: Resultado 0 (mesmo problema do endpoint)")
        else:
            print(f"⚠️  INESPERADO: {total_cancelled_rides} (esperávamos 22)")
        
        cursor.close()
        conn.close()
        
        return total_cancelled_rides
        
    except Exception as e:
        print(f"❌ ERRO: {e}")
        return 0

if __name__ == "__main__":
    result = test_endpoint_cancellation_logic()