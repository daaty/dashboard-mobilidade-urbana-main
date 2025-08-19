#!/usr/bin/env python3
"""
Teste completo do dashboard com dados reais
"""

import requests
import time

def test_complete_flow():
    """Testa o fluxo completo: dados na DB -> API -> Frontend"""
    
    print("🔄 Testando fluxo completo do dashboard...")
    print("=" * 60)
    
    # 1. Verificar dados na API
    print("1️⃣ Verificando API de Analytics...")
    try:
        response = requests.get("http://localhost:8000/api/drivers/analytics")
        if response.status_code == 200:
            data = response.json()
            total_records = data.get('total_records', 0)
            print(f"   ✅ API funcionando - {total_records} registros encontrados")
            
            if total_records > 0:
                # Mostrar algumas estatísticas dos dados
                drivers = data.get('drivers', [])
                unique_drivers = len(set(d['driver_id'] for d in drivers))
                dates = set()
                total_hours = 0
                
                for driver in drivers:
                    driver_data = driver.get('data', {})
                    metrics = driver_data.get('metrics', {})
                    profile = driver_data.get('profile', {})
                    
                    if profile.get('data_date'):
                        dates.add(profile['data_date'][:10])  # Só a data
                    
                    total_hours += metrics.get('online_hours', 0)
                
                print(f"   📊 Estatísticas dos dados:")
                print(f"      - Motoristas únicos: {unique_drivers}")
                print(f"      - Registros diários: {total_records}")
                print(f"      - Datas diferentes: {len(dates)}")
                print(f"      - Total horas online: {total_hours:.1f}h")
                print(f"      - Média horas/motorista: {(total_hours/unique_drivers):.1f}h" if unique_drivers > 0 else "")
                
                # Mostrar algumas datas
                if dates:
                    sorted_dates = sorted(list(dates))
                    print(f"      - Período: {sorted_dates[0]} até {sorted_dates[-1]}")
                
            else:
                print("   ⚠️ Nenhum dado encontrado na API")
        else:
            print(f"   ❌ Erro na API: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Erro ao conectar API: {e}")
        return False
    
    # 2. Verificar frontend
    print("\n2️⃣ Verificando Frontend...")
    try:
        response = requests.get("http://localhost:3000")
        if response.status_code == 200:
            print("   ✅ Frontend rodando")
        else:
            print(f"   ⚠️ Frontend resposta: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Frontend não acessível: {e}")
    
    # 3. Simular análise temporal
    if total_records > 0:
        print("\n3️⃣ Simulando análise temporal...")
        
        # Agrupar por motorista
        driver_analysis = {}
        for driver in drivers:
            driver_id = driver['driver_id']
            name = driver['name']
            driver_data = driver.get('data', {})
            metrics = driver_data.get('metrics', {})
            profile = driver_data.get('profile', {})
            
            if driver_id not in driver_analysis:
                driver_analysis[driver_id] = {
                    'name': name,
                    'total_hours': 0,
                    'total_rides': 0,
                    'days_count': 0,
                    'dates': set()
                }
            
            analysis = driver_analysis[driver_id]
            analysis['total_hours'] += metrics.get('online_hours', 0)
            analysis['total_rides'] += metrics.get('success_rides', 0)
            analysis['days_count'] += 1
            
            if profile.get('data_date'):
                analysis['dates'].add(profile['data_date'][:10])
        
        # Top 5 motoristas por horas online
        top_drivers = sorted(
            driver_analysis.items(), 
            key=lambda x: x[1]['total_hours'], 
            reverse=True
        )[:5]
        
        print("   🏆 Top 5 Motoristas por Horas Online:")
        for i, (driver_id, data) in enumerate(top_drivers, 1):
            print(f"      {i}. {data['name']} (ID: {driver_id})")
            print(f"         - {data['total_hours']:.1f}h online")
            print(f"         - {data['total_rides']} corridas")
            print(f"         - {len(data['dates'])} dias diferentes")
    
    print("\n" + "=" * 60)
    print("✅ Teste completo finalizado!")
    print(f"💡 Acesse: http://localhost:3000 para ver o dashboard")
    print(f"📊 API: http://localhost:8000/api/drivers/analytics")

if __name__ == "__main__":
    test_complete_flow()
