import requests
import json

API_URL = "http://localhost:8000"

print("Analisando endpoint /api/metas-progressivas")

response = requests.get(f"{API_URL}/api/metas-progressivas")

if response.status_code == 200:
    data = response.json()
    print(f"Status: {response.status_code}")
    
    if isinstance(data, list):
        metas = data
    elif isinstance(data, dict):
        metas = data.get('metas', data.get('data', []))
    
    print(f"Total metas: {len(metas)}")
    
    if metas:
        print("\nPrimeiras 3 metas:")
        for i, meta in enumerate(metas[:3], 1):
            print(f"\n=== META {i} ===")
            print(f"ID: {meta.get('id')}")
            print(f"Cidade ID: {meta.get('cidade_id')}")
            print(f"Meta Motoristas: {meta.get('meta_motoristas')}")
            print(f"Meta Corridas: {meta.get('meta_corridas')}")
            print(f"Resultado Motoristas: {meta.get('resultado_motoristas')}")
            print(f"Resultado Corridas: {meta.get('resultado_corridas')}")
            print(f"Status: {meta.get('status')}")
        
        print(f"\nCampos disponiveis:")
        print(json.dumps(list(metas[0].keys()), indent=2))
    else:
        print("Nenhuma meta encontrada")
else:
    print(f"Erro {response.status_code}: {response.text}")
