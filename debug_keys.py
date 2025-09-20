import requests
import json

def debug_keys():
    """Debug para ver as chaves exatas que o endpoint está gerando"""
    
    response = requests.get("http://localhost:8000/api/metrics/comparative-hourly?periodo=6m&tipo=horario")
    
    if response.status_code == 200:
        data = response.json()
        
        print("🔍 DEBUGANDO CHAVES DOS PERÍODOS:")
        print("\n📋 Periods Metadata:")
        for period in data.get('periods_metadata', []):
            print(f"  - Key: '{period['key']}' | Label: '{period['label']}'")
        
        print("\n📊 Dados de exemplo (primeira hora):")
        if data.get('hourly_data'):
            first_hour = data['hourly_data'][0]
            print(f"Hora: {first_hour.get('hour')} ({first_hour.get('hourFormatted')})")
            
            for key, value in first_hour.items():
                if key not in ['hour', 'hourFormatted'] and value > 0:
                    print(f"  - '{key}': {value}")
                    
                    # Tentar extrair period key
                    for category in ['total', 'concluidas', 'canceladas', 'perdidas']:
                        if key.endswith(f'_{category}'):
                            period_key = key.replace(f'_{category}', '')
                            period_data = next((p for p in data['periods_metadata'] if p['key'] == period_key), None)
                            if period_data:
                                print(f"    → Period Key: '{period_key}' → Label: '{period_data['label']}'")
                            break
    else:
        print(f"Erro: {response.status_code} - {response.text}")

if __name__ == "__main__":
    debug_keys()