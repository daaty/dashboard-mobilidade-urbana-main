import requests

cidades = ['PEIXOTO', 'Matupa', 'Nova Monte Verde', 'GUARANTA DO NORTE', 'Nova Bandeirantes']

print("=" * 60)
print("🧪 TESTE: Endpoint /api/drivers/by-city")
print("=" * 60)

for cidade in cidades:
    try:
        r = requests.get(f'http://localhost:8000/api/drivers/by-city?cidade={cidade}')
        data = r.json()
        
        if data.get('success'):
            total = data.get('total', 0)
            cidade_norm = data.get('cidade_normalizada', cidade)
            print(f"✅ {cidade:20} → {cidade_norm:25} | {total:3} motoristas")
        else:
            print(f"❌ {cidade:20} → Erro: {data.get('error', 'N/A')[:40]}")
    except Exception as e:
        print(f"❌ {cidade:20} → Exception: {str(e)[:40]}")

print("=" * 60)
