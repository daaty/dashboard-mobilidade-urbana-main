"""
Análise do agrupamento de cidades - Identificar duplicações e propor correções
"""
import requests
from collections import defaultdict

API_URL = "http://localhost:8000"

print("="*80)
print("🔍 ANÁLISE: AGRUPAMENTO DE CIDADES")
print("="*80)

# 1. Buscar campanhas
resp = requests.get(f"{API_URL}/api/dashboard-executivo/campanhas")
data = resp.json()
campanhas = data.get('campanhas', [])

print(f"\n📊 Total de campanhas: {len(campanhas)}\n")

# 2. Agrupar por cidade
cidades_map = defaultdict(list)

for camp in campanhas:
    cidade_nome = camp.get('cidade', {}).get('nome')
    cidade_id = camp.get('cidade', {}).get('id')
    
    if cidade_nome and cidade_nome != "Cidade não encontrada":
        key = f"{cidade_id}_{cidade_nome}"  # Usar ID + Nome como chave única
        cidades_map[key].append(camp)

print(f"🏙️ Total de cidades ÚNICAS: {len(cidades_map)}\n")

# 3. Mostrar cidades com suas campanhas
print("📋 DETALHAMENTO POR CIDADE:\n")

for cidade_key in sorted(cidades_map.keys()):
    campanhas_cidade = cidades_map[cidade_key]
    
    # Extrair ID e nome
    cidade_id, cidade_nome = cidade_key.split('_', 1)
    
    # Agrupar por fase
    fases = defaultdict(int)
    for camp in campanhas_cidade:
        fase = camp.get('fase', 'Sem fase')
        fases[fase] += 1
    
    # População (pegar do primeiro)
    populacao = campanhas_cidade[0].get('cidade', {}).get('populacao', 0)
    
    print(f"{'='*80}")
    print(f"🏙️  {cidade_nome} (ID: {cidade_id}) - Pop: {populacao:,}")
    print(f"{'='*80}")
    print(f"   Total de campanhas: {len(campanhas_cidade)}")
    print(f"   Distribuição por fase:")
    for fase, count in sorted(fases.items()):
        print(f"      {fase}: {count} campanha(s)")
    
    # Mostrar status
    status_list = [c.get('status', 'N/A') for c in campanhas_cidade]
    status_unique = set(status_list)
    print(f"   Status: {', '.join(status_unique)}")
    
    print()

# 4. Análise de duplicações
print("\n" + "="*80)
print("⚠️  ANÁLISE DE DUPLICAÇÕES:")
print("="*80)

# Verificar se alguma cidade tem múltiplas campanhas na mesma fase
duplicacoes = []
for cidade_key, campanhas_cidade in cidades_map.items():
    cidade_id, cidade_nome = cidade_key.split('_', 1)
    
    fases_contagem = defaultdict(int)
    for camp in campanhas_cidade:
        fase = camp.get('fase')
        fases_contagem[fase] += 1
    
    for fase, count in fases_contagem.items():
        if count > 1:
            duplicacoes.append({
                'cidade': cidade_nome,
                'fase': fase,
                'quantidade': count
            })

if duplicacoes:
    print("\n🚨 Cidades com MÚLTIPLAS campanhas na MESMA FASE:")
    for dup in duplicacoes:
        print(f"   - {dup['cidade']}: {dup['quantidade']} campanhas em '{dup['fase']}'")
else:
    print("\n✅ Não há duplicações de fase por cidade")

# 5. Sugestão de agrupamento correto
print("\n" + "="*80)
print("💡 SUGESTÃO DE AGRUPAMENTO CORRETO:")
print("="*80)

print("""
LÓGICA PROPOSTA:

1. Agrupar campanhas por CIDADE (cidade.id como chave única)
2. Para cada cidade, consolidar:
   - Fase principal (prioritária): Fase 1 > Fase 2 > Fase 3 > lançamento
   - Total de campanhas
   - Soma de corridas de todas as campanhas
   - Soma de motoristas de todas as campanhas
   - Status mais avançado

3. Classificação por categoria:
   - "Cidades Operacionais": status='ativa' E (fase='Fase 1' OU fase='lançamento')
   - "Expansão Fase 2": fase='Fase 2'
   - "Expansão Fase 3": fase='Fase 3'
   - "Em Planejamento": status='planejada' OU status='pendente'

4. Badge de atividade baseado em corridas:
   - 🚀 Muito Ativa: > 200 corridas
   - ⚡ Ativa: 20-200 corridas
   - 🌱 Iniciando: 1-19 corridas
   - ⏳ Aguardando: 0 corridas
""")

# 6. Contar por categoria usando lógica proposta
categorias = {
    'operacionais': [],
    'fase2': [],
    'fase3': [],
    'planejamento': []
}

for cidade_key, campanhas_cidade in cidades_map.items():
    cidade_id, cidade_nome = cidade_key.split('_', 1)
    
    # Determinar fase principal (priorizar Fase 1)
    fases = [c.get('fase') for c in campanhas_cidade]
    if 'Fase 1' in fases or 'lançamento' in fases:
        categorias['operacionais'].append(cidade_nome)
    elif 'Fase 2' in fases:
        categorias['fase2'].append(cidade_nome)
    elif 'Fase 3' in fases:
        categorias['fase3'].append(cidade_nome)
    else:
        categorias['planejamento'].append(cidade_nome)

print("\n📊 RESULTADO DO AGRUPAMENTO CORRIGIDO:\n")
print(f"🟢 Cidades Operacionais: {len(categorias['operacionais'])} cidades")
for cidade in sorted(categorias['operacionais']):
    print(f"   - {cidade}")

print(f"\n🔵 Expansão Fase 2: {len(categorias['fase2'])} cidades")
for cidade in sorted(categorias['fase2']):
    print(f"   - {cidade}")

print(f"\n🟣 Expansão Fase 3: {len(categorias['fase3'])} cidades")
for cidade in sorted(categorias['fase3']):
    print(f"   - {cidade}")

print(f"\n🟡 Em Planejamento: {len(categorias['planejamento'])} cidades")
for cidade in sorted(categorias['planejamento']):
    print(f"   - {cidade}")

print(f"\n{'='*80}")
print(f"📈 RESUMO:")
print(f"{'='*80}")
print(f"Total de cidades ÚNICAS: {len(cidades_map)}")
print(f"Total de campanhas: {len(campanhas)}")
print(f"Média de campanhas por cidade: {len(campanhas) / len(cidades_map):.1f}")
