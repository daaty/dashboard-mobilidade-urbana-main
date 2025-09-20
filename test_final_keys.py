import requests

def test_final_keys():
    """Teste final para garantir que a correção está funcionando"""
    
    for periodo in ['7d', '30d', '6m']:
        print(f"\n{'='*30} {periodo} {'='*30}")
        
        response = requests.get(f"http://localhost:8000/api/metrics/comparative-hourly?periodo={periodo}")
        data = response.json()
        
        print("📋 Periods Metadata:")
        for period in data['periods_metadata']:
            print(f"  Key: '{period['key']}' → Label: '{period['label']}'")
        
        # Simular a correção do frontend
        print("\n🔧 Simulando correção do frontend:")
        sample_keys = [
            f"{period['key']}_total",
            f"{period['key']}_concluidas"
        ]
        
        for sample_key in sample_keys:
            # Simular o que acontece no frontend
            period_key_extracted = sample_key.replace('_total', '').replace('_concluidas', '')
            period_data = next((p for p in data['periods_metadata'] if p['key'] == period_key_extracted), None)
            
            if period_data:
                print(f"  ✅ '{sample_key}' → '{period_key_extracted}' → '{period_data['label']}'")
            else:
                print(f"  ❌ '{sample_key}' → '{period_key_extracted}' → NÃO ENCONTRADO")

if __name__ == "__main__":
    test_final_keys()