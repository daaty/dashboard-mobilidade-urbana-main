import requests
import json

def test_comparative_hourly_endpoint():
    """Testa o novo endpoint de análise comparativa por horário"""
    
    base_url = "http://localhost:8000"
    endpoint = f"{base_url}/api/metrics/comparative-hourly"
    
    # Testar diferentes períodos
    periods_to_test = ['7d', '30d', '6m']
    
    for period in periods_to_test:
        print(f"\n{'='*50}")
        print(f"🕐 TESTANDO PERÍODO: {period}")
        print(f"{'='*50}")
        
        params = {
            'periodo': period,
            'tipo': 'horario'
        }
        
        try:
            response = requests.get(endpoint, params=params)
            print(f"📡 Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                
                print(f"✅ Sucesso: {data.get('success')}")
                print(f"📅 Período: {data.get('periodo')}")
                print(f"🏙️ Cidade: {data.get('cidade')}")
                print(f"📊 Total de registros: {data.get('total_records')}")
                
                # Mostrar metadados dos períodos
                if 'periods_metadata' in data:
                    print(f"\n📈 Períodos Analisados:")
                    for period_meta in data['periods_metadata']:
                        print(f"  - {period_meta['label']}: {period_meta['total_geral']} corridas totais")
                        print(f"    ✅ Concluídas: {period_meta['total_concluidas']}")
                        print(f"    ❌ Canceladas: {period_meta['total_canceladas']}")  
                        print(f"    ⏰ Perdidas: {period_meta['total_perdidas']}")
                
                # Mostrar algumas horas exemplo
                if 'hourly_data' in data and data['hourly_data']:
                    print(f"\n🕐 Exemplo de dados por horário (primeiras 5 horas):")
                    for hour_data in data['hourly_data'][:5]:
                        hour = hour_data.get('hour', 0)
                        hour_formatted = hour_data.get('hourFormatted', f'{hour:02d}:00')
                        print(f"  {hour_formatted}:")
                        
                        # Mostrar dados de cada período para esta hora
                        for period_meta in data['periods_metadata']:
                            period_key = period_meta['key']
                            total_key = f"{period_key}_total"
                            if total_key in hour_data:
                                total = hour_data[total_key]
                                if total > 0:
                                    concluidas_key = f"{period_key}_concluidas"
                                    canceladas_key = f"{period_key}_canceladas"
                                    perdidas_key = f"{period_key}_perdidas"
                                    
                                    concluidas = hour_data.get(concluidas_key, 0)
                                    canceladas = hour_data.get(canceladas_key, 0)
                                    perdidas = hour_data.get(perdidas_key, 0)
                                    
                                    print(f"    📊 {period_meta['label']}: {total} total ({concluidas}✅ {canceladas}❌ {perdidas}⏰)")
                
                # Encontrar horários de pico
                if 'hourly_data' in data and data['hourly_data']:
                    print(f"\n🔥 ANÁLISE DE HORÁRIOS DE PICO:")
                    
                    # Para cada período, encontrar hora de pico
                    for period_meta in data['periods_metadata']:
                        period_key = period_meta['key']
                        total_key = f"{period_key}_total"
                        
                        max_hour = 0
                        max_value = 0
                        
                        for hour_data in data['hourly_data']:
                            if total_key in hour_data and hour_data[total_key] > max_value:
                                max_value = hour_data[total_key]
                                max_hour = hour_data.get('hour', 0)
                        
                        if max_value > 0:
                            print(f"  🏆 {period_meta['label']}: Pico às {max_hour:02d}:00 com {max_value} corridas")
                        
            else:
                print(f"❌ Erro na requisição: {response.status_code}")
                print(f"📄 Resposta: {response.text}")
                
        except Exception as e:
            print(f"💥 Erro na requisição: {str(e)}")

if __name__ == "__main__":
    test_comparative_hourly_endpoint()