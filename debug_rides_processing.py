#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
import json

def debug_rides_processing():
    """Debug do processamento de corridas por período"""
    
    # Dados de exemplo do arquivo RIDESHISTORY
    sample_rides = [
        {"fare":"10","s_no":"1","duration":"5","drop_time":"03/09/2025 : 6:37 pm","customer_id":"18395675","driver_rating":"--"},
        {"fare":"10","s_no":"2","duration":"2","drop_time":"03/09/2025 : 1:44 pm","customer_id":"18411476","driver_rating":"--"},
        {"fare":"10.65","s_no":"3","duration":"5","drop_time":"01/09/2025 : 3:55 pm","customer_id":"18326537","driver_rating":"5/5"},
        {"fare":"10","s_no":"4","duration":"3","drop_time":"28/08/2025 : 3:40 pm","customer_id":"18318166","driver_rating":"1/5"},
        {"fare":"10","s_no":"5","duration":"4","drop_time":"28/08/2025 : 2:15 pm","customer_id":"18318166","driver_rating":"1/5"},
        {"fare":"13.91","s_no":"6","duration":"6","drop_time":"21/08/2025 : 6:18 pm","customer_id":"18326537","driver_rating":"5/5"},
        {"fare":"10","s_no":"7","duration":"3","drop_time":"20/08/2025 : 2:23 pm","customer_id":"18318166","driver_rating":"5/5"},
        {"fare":"10.8","s_no":"8","duration":"2","drop_time":"20/08/2025 : 1:40 pm","customer_id":"18318209","driver_rating":"5/5"},
        {"fare":"15","s_no":"1","duration":"0","drop_time":"28/08/2025 : 10:48 am","customer_id":"18036120","driver_rating":"5/5"},
        {"fare":"17.6","s_no":"2","duration":"0","drop_time":"22/08/2025 : 9:36 am","customer_id":"18156580","driver_rating":"--"},
        {"fare":"15","s_no":"3","duration":"1","drop_time":"22/08/2025 : 9:09 am","customer_id":"18156580","driver_rating":"5/5"},
        {"fare":"7","s_no":"1","duration":"1","drop_time":"23/08/2025 : 12:41 pm","customer_id":"18339877","driver_rating":"5/5"}
    ]
    
    # Calcular datas (com correção - início do dia)
    today = datetime.now()
    start_7 = (today - timedelta(days=7)).replace(hour=0, minute=0, second=0, microsecond=0)
    start_30 = (today - timedelta(days=30)).replace(hour=0, minute=0, second=0, microsecond=0)
    
    print(f"Data atual: {today.strftime('%d/%m/%Y %H:%M')}")
    print(f"Range 7 dias: {start_7.strftime('%d/%m/%Y %H:%M')} até {today.strftime('%d/%m/%Y %H:%M')}")
    print(f"Range 30 dias: {start_30.strftime('%d/%m/%Y %H:%M')} até {today.strftime('%d/%m/%Y %H:%M')}")
    print("\n" + "="*80)
    
    # Processar cada corrida
    total_7_days = 0
    total_30_days = 0
    
    for ride in sample_rides:
        try:
            date_str = ride['drop_time']
            date_part = date_str.split(' : ')[0]
            ride_date = datetime.strptime(date_part, '%d/%m/%Y')
            
            in_7_days = start_7 <= ride_date <= today
            in_30_days = start_30 <= ride_date <= today
            
            if in_7_days:
                total_7_days += 1
            if in_30_days:
                total_30_days += 1
            
            status_7 = "✅ SIM" if in_7_days else "❌ NÃO"
            status_30 = "✅ SIM" if in_30_days else "❌ NÃO"
            
            print(f"{date_part:12} | Fare: R$ {ride['fare']:>6} | 7d: {status_7} | 30d: {status_30}")
            
        except Exception as e:
            print(f"ERRO processando {ride.get('drop_time', 'N/A')}: {e}")
    
    print("\n" + "="*80)
    print(f"TOTAL corridas 7 dias: {total_7_days}")
    print(f"TOTAL corridas 30 dias: {total_30_days}")
    print(f"Receita estimada 7d: R$ {total_7_days * 2.50}")
    print(f"Receita estimada 30d: R$ {total_30_days * 2.50}")

if __name__ == "__main__":
    debug_rides_processing()
