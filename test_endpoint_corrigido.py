#!/usr/bin/env python3
import requests
import json

def test_endpoint():
    """Testar o endpoint comparative corrigido"""
    
    try:
        # Fazer requisição para o endpoint
        response = requests.get("http://localhost:8000/api/metrics/comparative?periodo=6")
        
        if response.status_code != 200:
            print(f"❌ Erro: {response.status_code}")
            print(response.text)
            return
        
        data = response.json()
        
        print("🎯 TESTANDO ENDPOINT COMPARATIVE CORRIGIDO")
        print("=" * 50)
        
        # Verificar estrutura básica
        if not data.get("success"):
            print("❌ Endpoint retornou success=false")
            return
        
        daily_data = data.get("daily_data", [])
        months_metadata = data.get("months_metadata", [])
        
        print(f"✅ Success: {data['success']}")
        print(f"📊 Dados diários: {len(daily_data)} dias")
        print(f"📅 Metadados meses: {len(months_metadata)} meses")
        
        # Encontrar dados de setembro
        setembro_meta = None
        for month in months_metadata:
            if "2025_09" in month.get("key", ""):
                setembro_meta = month
                break
        
        if setembro_meta:
            print(f"\n🎯 SETEMBRO 2025 - TOTAIS MENSAIS:")
            print(f"   ✅ Total Concluídas: {setembro_meta.get('total_concluidas', 0)}")
            print(f"   🟡 Total Canceladas: {setembro_meta.get('total_canceladas', 0)}")
            print(f"   🔴 Total Perdidas: {setembro_meta.get('total_perdidas', 0)}")
            print(f"   📈 TOTAL GERAL: {setembro_meta.get('total_geral', 0)}")
            
            # Verificar dia 13 especificamente
            dia_13 = None
            for day_data in daily_data:
                if day_data.get("day") == 13:
                    dia_13 = day_data
                    break
            
            if dia_13:
                print(f"\n🔍 DIA 13 DE SETEMBRO:")
                setembro_13_concluidas = dia_13.get("2025_09_concluidas", 0)
                setembro_13_canceladas = dia_13.get("2025_09_canceladas", 0) 
                setembro_13_perdidas = dia_13.get("2025_09_perdidas", 0)
                setembro_13_total = dia_13.get("2025_09_total", 0)
                
                print(f"   ✅ Concluídas: {setembro_13_concluidas}")
                print(f"   🟡 Canceladas: {setembro_13_canceladas}")
                print(f"   🔴 Perdidas: {setembro_13_perdidas}")
                print(f"   📈 TOTAL DIA 13: {setembro_13_total}")
                
                # Verificar se os números estão corretos
                if setembro_13_total > 50:
                    print(f"   ⚠️  ATENÇÃO: Dia 13 ainda tem {setembro_13_total} corridas!")
                else:
                    print(f"   ✅ Números parecem corretos agora!")
        else:
            print("❌ Não encontrou dados de setembro")
            
        # Mostrar top 5 dias de setembro
        print(f"\n🏆 TOP 5 DIAS DE SETEMBRO:")
        setembro_dias = []
        for day_data in daily_data:
            day = day_data.get("day")
            total_setembro = day_data.get("2025_09_total", 0)
            if total_setembro > 0:
                setembro_dias.append((day, total_setembro))
        
        setembro_dias.sort(key=lambda x: x[1], reverse=True)
        for i, (dia, total) in enumerate(setembro_dias[:5]):
            print(f"   {i+1}. Dia {dia:2d}: {total:2d} corridas")
            
    except Exception as e:
        print(f"❌ Erro ao testar endpoint: {e}")

if __name__ == "__main__":
    test_endpoint()