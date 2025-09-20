#!/usr/bin/env python3
"""
Análise crítica dos dados de taxa de aceitação
"""

import requests
import json
from collections import Counter

def analyze_acceptance_rate_data():
    """Analisa criticamente os dados retornados pelo endpoint"""
    
    try:
        response = requests.get('http://localhost:8000/api/drivers/acceptance-rate')
        
        if response.status_code == 200:
            data = response.json()
            
            print("ANALISE CRITICA DOS DADOS DE TAXA DE ACEITACAO:")
            print("=" * 60)
            
            # Verificar IDs duplicados
            driver_ids = []
            for driver in data['data']['drivers_details']:
                driver_ids.append(driver['driver_id'])
            
            unique_ids = set(driver_ids)
            total_entries = len(driver_ids)
            unique_entries = len(unique_ids)
            
            print(f"Total de entradas no drivers_details: {total_entries}")
            print(f"IDs unicos encontrados: {unique_entries}")
            print(f"Duplicados identificados: {total_entries - unique_entries}")
            
            if total_entries != unique_entries:
                print(f"\nPROBLEMA CONFIRMADO: Ha {total_entries - unique_entries} registros duplicados!")
                
                # Contar duplicados por ID
                id_counts = Counter(driver_ids)
                duplicated_ids = {id_: count for id_, count in id_counts.items() if count > 1}
                
                print(f"\nIDs com multiplas entradas (primeiros 15):")
                for i, (driver_id, count) in enumerate(list(duplicated_ids.items())[:15]):
                    print(f"  - ID {driver_id}: {count} registros")
                
                if len(duplicated_ids) > 15:
                    print(f"  ... e mais {len(duplicated_ids) - 15} IDs duplicados")
                
                print(f"\nTotal de IDs que aparecem duplicados: {len(duplicated_ids)}")
            
            # Verificar distribuição por cidade
            print(f"\nVERIFICACAO POR CIDADE:")
            total_by_city_sum = 0
            for city, stats in data['data']['city_breakdown'].items():
                print(f"  {city}: {stats['drivers_count']} motoristas")
                total_by_city_sum += stats['drivers_count']
            
            print(f"\nCOMPARACAO DE TOTAIS:")
            print(f"Total por soma das cidades: {total_by_city_sum}")
            print(f"Total reportado pelo endpoint: {data['data']['total_drivers']}")
            print(f"Total de entradas em drivers_details: {total_entries}")
            print(f"Total de IDs unicos: {unique_entries}")
            
            if total_by_city_sum != data['data']['total_drivers']:
                print(f"\nINCONSISTENCIA: Soma das cidades ({total_by_city_sum}) != Total reportado ({data['data']['total_drivers']})")
            
            # Verificar alguns detalhes dos primeiros registros
            print(f"\nAMOSTRA DOS PRIMEIROS 10 MOTORISTAS:")
            for i, driver in enumerate(data['data']['drivers_details'][:10]):
                print(f"  {i+1}. ID: {driver['driver_id']}, Cidade: {driver['city']}, Requests: {driver['total_requests']}")
            
            # Análise das queries SQL
            print(f"\nANALISE TECNICA:")
            print(f"- O endpoint pode estar fazendo LEFT JOIN incorreto")
            print(f"- Pode haver multiplos registros em drivers_data para o mesmo driver_id")
            print(f"- Precisa verificar se a query esta usando DISTINCT ou GROUP BY")
            
        else:
            print(f"Erro na requisicao: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"Erro inesperado: {e}")

if __name__ == "__main__":
    analyze_acceptance_rate_data()