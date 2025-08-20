"""
🧪 TESTE SIMPLES PARA DEBUG
"""

import requests

def teste_simples():
    # Testando a fase que está em execução (ID 10 ou 11)
    for fase_id in [10, 11]:
        print(f"\n🧪 Testando fase {fase_id}:")
        response = requests.post(
            f"http://localhost:8000/api/metas-estrategicas/fases-estrategicas/{fase_id}/calcular-progresso",
            params={'metodo': 'hibrido'}
        )
        
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Temporal: {data['detalhes']['temporal']:.1f}%")
            print(f"✅ Orçamentário: {data['detalhes']['orcamentario']:.1f}%")
            print(f"✅ Metas: {data['detalhes']['metas']:.1f}%")
            print(f"✅ Campanhas: {data['detalhes']['campanhas']:.1f}%")
            print(f"🔄 Híbrido: {data['progresso_novo']:.1f}%")
        else:
            print(f"❌ Erro: {response.text}")

if __name__ == "__main__":
    teste_simples()
