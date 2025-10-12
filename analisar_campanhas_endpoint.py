"""
Script para analisar o que está retornando do endpoint de campanhas
"""
import requests
import json

API_URL = "http://localhost:8000"

print("🔍 ANALISANDO ENDPOINT /api/dashboard-executivo/campanhas\n")

response = requests.get(f"{API_URL}/api/dashboard-executivo/campanhas")

if response.status_code == 200:
    data = response.json()
    print(f"✅ Status: {response.status_code}")
    print(f"📊 Total de campanhas: {data.get('total_campanhas', 0)}\n")
    
    campanhas = data.get('campanhas', [])
    
    if campanhas:
        print("🎯 PRIMEIRAS 3 CAMPANHAS:\n")
        for i, camp in enumerate(campanhas[:3], 1):
            print(f"{'='*60}")
            print(f"CAMPANHA {i}:")
            print(f"{'='*60}")
            print(f"  ID: {camp.get('id')}")
            print(f"  Nome: {camp.get('nome')}")
            print(f"  Fase: {camp.get('fase')}")
            print(f"  Status: {camp.get('status')}")
            print(f"  Meta Quantidade: {camp.get('meta_quantidade')}")
            print(f"  Meta Motoristas: {camp.get('meta_motoristas', 'NÃO EXISTE')}")
            print(f"  Meta Corridas: {camp.get('meta_corridas', 'NÃO EXISTE')}")
            print(f"  Motoristas Total: {camp.get('motoristas_total', 'NÃO EXISTE')}")
            print(f"  Corridas Total: {camp.get('corridas_total', 'NÃO EXISTE')}")
            
            cidade = camp.get('cidade', {})
            print(f"\n  CIDADE:")
            print(f"    ID: {cidade.get('id')}")
            print(f"    Nome: {cidade.get('nome')}")
            print(f"    População: {cidade.get('populacao')}")
            print()
        
        print(f"\n📋 CAMPOS DISPONÍVEIS NA PRIMEIRA CAMPANHA:")
        print(json.dumps(list(campanhas[0].keys()), indent=2))
        
    else:
        print("❌ Nenhuma campanha encontrada")
else:
    print(f"❌ Erro {response.status_code}: {response.text}")
