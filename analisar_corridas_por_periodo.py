#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
import json

def analisar_corridas():
    """Analisa os dados de corridas por período no banco"""
    
    # Conectar ao banco
    conn = sqlite3.connect('drivers_data.db')
    cursor = conn.cursor()
    
    print("=== ANÁLISE DE CORRIDAS POR PERÍODO ===\n")
    
    # Query simples para começar
    query = """
    SELECT DISTINCT driver_id, name, additional_data, page_source
    FROM drivers_data
    WHERE page_source IN ('Active Drivers', 'Deactive Drivers', 'Driver Performance', 'Leaderboard', 'Drivers Enrollment')
    """
    
    cursor.execute(query)
    rows = cursor.fetchall()
    
    total_motoristas = 0
    total_rides_7 = 0
    total_rides_30 = 0
    motoristas_com_corridas_7 = 0
    motoristas_com_corridas_30 = 0
    
    print("Motoristas com corridas:")
    print("-" * 60)
    
    for row in rows:
        driver_id, name, additional_data_str, page_source = row
        total_motoristas += 1
        
        try:
            additional_data = json.loads(additional_data_str)
            rides_7 = int(additional_data.get('Rides in Last 7 Days', 0))
            rides_30 = int(additional_data.get('Rides in Last 30 Days', 0))
            status = additional_data.get('Status', 'N/A')
            
            total_rides_7 += rides_7
            total_rides_30 += rides_30
            
            if rides_7 > 0:
                motoristas_com_corridas_7 += 1
            if rides_30 > 0:
                motoristas_com_corridas_30 += 1
            
            # Mostrar apenas motoristas com corridas
            if rides_7 > 0 or rides_30 > 0:
                print(f"ID: {driver_id} | {name[:30]:30} | 7d: {rides_7:2} | 30d: {rides_30:2} | {page_source[:15]:15} | {status}")
                
        except Exception as e:
            print(f"Erro processando driver {driver_id}: {e}")
            continue
    
    print("\n" + "=" * 60)
    print("RESUMO:")
    print(f"Total de motoristas únicos: {total_motoristas}")
    print(f"Total corridas em 7 dias: {total_rides_7}")
    print(f"Total corridas em 30 dias: {total_rides_30}")
    print(f"Motoristas com corridas em 7 dias: {motoristas_com_corridas_7}")
    print(f"Motoristas com corridas em 30 dias: {motoristas_com_corridas_30}")
    print(f"Média corridas/motorista (7d): {total_rides_7/total_motoristas:.2f}")
    print(f"Média corridas/motorista (30d): {total_rides_30/total_motoristas:.2f}")
    
    conn.close()

if __name__ == "__main__":
    analisar_corridas()
