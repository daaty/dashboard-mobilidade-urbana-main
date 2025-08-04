#!/usr/bin/env python3
import requests

def test_simpler_api():
    """Testa endpoint overview que já está funcionando"""
    
    url = "http://localhost:5000/api/dashboard/overview"
    
    try:
        print("🔍 Testando endpoint overview...")
        response = requests.get(url)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Dados recebidos do overview:")
            
            metricas = data['data']['metricas_principais']
            print(f"  📊 Total de corridas: {metricas['total_corridas']}")
            print(f"  💰 Receita total: R$ {metricas['receita_total']:.2f}")
            print(f"  🚗 Corridas concluídas: {metricas['corridas_concluidas']}")
            print(f"  ⭐ Avaliação média: {metricas['avaliacao_media']}")
            print(f"  👥 Motoristas ativos: {metricas['motoristas_ativos']}")
            
            por_municipio = data['data']['por_municipio']
            print(f"\n🏙️ Por município:")
            for municipio in por_municipio:
                print(f"  {municipio['municipio']}: {municipio['total_corridas']} corridas - R$ {municipio['receita_total']:.2f}")
                
        else:
            print(f"❌ Erro: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    test_simpler_api()
