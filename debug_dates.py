#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
import json

def debug_dates():
    """Debug das datas para entender o problema"""
    
    today = datetime.now()
    print(f"Data atual: {today.strftime('%d/%m/%Y')}")
    
    # Calcular ranges
    start_7 = today - timedelta(days=7)
    start_30 = today - timedelta(days=30)
    start_90 = today - timedelta(days=90)
    
    print(f"Range 7 dias: {start_7.strftime('%d/%m/%Y')} até {today.strftime('%d/%m/%Y')}")
    print(f"Range 30 dias: {start_30.strftime('%d/%m/%Y')} até {today.strftime('%d/%m/%Y')}")
    print(f"Range 90 dias: {start_90.strftime('%d/%m/%Y')} até {today.strftime('%d/%m/%Y')}")
    
    # Exemplos de datas dos dados
    sample_dates = [
        "20/08/2025 : 5:01 pm",
        "28/08/2025 : 10:48 am", 
        "22/08/2025 : 9:36 am",
        "03/09/2025 : 6:37 pm",
        "29/07/2025 : 6:00 pm",
        "13/07/2025 : 9:24 pm",
        "24/07/2025 : 6:36 pm"
    ]
    
    print("\n=== TESTE DE DATAS DOS DADOS ===")
    for date_str in sample_dates:
        try:
            date_part = date_str.split(' : ')[0]
            ride_date = datetime.strptime(date_part, '%d/%m/%Y')
            
            in_7_days = start_7 <= ride_date <= today
            in_30_days = start_30 <= ride_date <= today
            in_90_days = start_90 <= ride_date <= today
            
            print(f"{date_part}: 7d={in_7_days}, 30d={in_30_days}, 90d={in_90_days}")
        except Exception as e:
            print(f"Erro parsing {date_str}: {e}")

if __name__ == "__main__":
    debug_dates()
