import requests
import json

print("🔍 VERIFICANDO NOMES EXATOS DAS CIDADES")
print("=" * 60)

# 1. Buscar campanhas
response = requests.get('http://localhost:8000/api/dashboard-executivo/campanhas')
campanhas_data = response.json()

# Verificar se é lista ou objeto
if isinstance(campanhas_data, dict):
    campanhas = campanhas_data.get('campanhas', [])
elif isinstance(campanhas_data, list):
    campanhas = campanhas_data
else:
    print(f"⚠️  Tipo inesperado: {type(campanhas_data)}")
    campanhas = []

print(f"Total de campanhas retornadas: {len(campanhas)}")

# 2. Extrair nomes únicos
nomes_unicos = set()
for campanha in campanhas:
    if isinstance(campanha, dict):
        cidade = campanha.get('cidade')
        if cidade:
            # cidade pode ser string ou objeto
            if isinstance(cidade, dict):
                nome = cidade.get('nome')
            else:
                nome = cidade
            
            if nome:
                nomes_unicos.add(nome)

print(f"\n📋 Total de cidades únicas: {len(nomes_unicos)}")
print("\n🏙️ NOMES EXATOS das cidades:")
for nome in sorted(nomes_unicos):
    print(f"  - '{nome}'")

# 3. Testar endpoint de motoristas para cada cidade
print("\n\n👨‍💼 TESTANDO ENDPOINT DE MOTORISTAS:")
print("=" * 60)

for cidade in sorted(nomes_unicos):
    try:
        # Testar com nome original
        response_drivers = requests.get(f'http://localhost:8000/api/drivers/by-city?cidade={cidade}')
        dados = response_drivers.json()
        
        total = dados.get('total', 0)
        success = dados.get('success', False)
        
        if success and total > 0:
            # Calcular ativos
            motoristas = dados.get('motoristas', [])
            ativos = len([m for m in motoristas if (m.get('total_rides', 0) > 0)])
            print(f"✅ {cidade:30s} -> Total: {total:3d}, Ativos: {ativos:3d}")
        else:
            print(f"❌ {cidade:30s} -> SEM DADOS")
            
    except Exception as e:
        print(f"⚠️  {cidade:30s} -> ERRO: {e}")

print("\n\n🚕 TESTANDO ENDPOINT DE CORRIDAS:")
print("=" * 60)

for cidade in sorted(nomes_unicos):
    try:
        response_metrics = requests.get(f'http://localhost:8000/api/metrics/overview?cidade={cidade}')
        dados = response_metrics.json()
        
        metricas = dados.get('metricas_principais', {})
        corridas = metricas.get('corridas_concluidas', 0)
        
        if corridas > 0:
            print(f"✅ {cidade:30s} -> Corridas: {corridas:4d}")
        else:
            print(f"❌ {cidade:30s} -> SEM CORRIDAS")
            
    except Exception as e:
        print(f"⚠️  {cidade:30s} -> ERRO: {e}")

print("\n" + "=" * 60)
print("✅ ANÁLISE COMPLETA!")
