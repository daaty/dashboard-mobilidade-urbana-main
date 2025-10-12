"""
Script para investigar a estrutura real das cidades no banco de dados
"""
import requests
import json

API_URL = "http://localhost:8000"

print("="*70)
print("🔍 INVESTIGAÇÃO: CIDADES vs CAMPANHAS")
print("="*70)

# 1. Buscar todas as campanhas
print("\n📊 1. ANALISANDO CAMPANHAS...\n")
resp_campanhas = requests.get(f"{API_URL}/api/dashboard-executivo/campanhas")
if resp_campanhas.status_code == 200:
    data_campanhas = resp_campanhas.json()
    campanhas = data_campanhas.get('campanhas', [])
    
    print(f"Total de campanhas: {len(campanhas)}")
    
    # Analisar campos de cidade
    cidades_por_nome = set()
    cidades_por_id = set()
    campanhas_sem_cidade_id = 0
    campanhas_cidade_nao_encontrada = 0
    
    print("\n📋 PRIMEIRAS 10 CAMPANHAS - ANÁLISE DE CIDADE:\n")
    for i, camp in enumerate(campanhas[:10], 1):
        cidade_obj = camp.get('cidade', {})
        cidade_id = cidade_obj.get('id')
        cidade_nome = cidade_obj.get('nome')
        
        if cidade_id is None:
            campanhas_sem_cidade_id += 1
        if cidade_nome == "Cidade não encontrada":
            campanhas_cidade_nao_encontrada += 1
        
        if cidade_nome and cidade_nome != "Cidade não encontrada":
            cidades_por_nome.add(cidade_nome)
        if cidade_id:
            cidades_por_id.add(cidade_id)
            
        print(f"{i:2}. ID: {camp['id']:3} | Cidade ID: {cidade_id or 'NULL':6} | Nome: {cidade_nome}")
    
    print(f"\n📊 ESTATÍSTICAS:")
    print(f"   Campanhas SEM cidade_id (NULL): {campanhas_sem_cidade_id}/{len(campanhas)}")
    print(f"   Campanhas com 'Cidade não encontrada': {campanhas_cidade_nao_encontrada}/{len(campanhas)}")
    print(f"   Cidades únicas por NOME: {len(cidades_por_nome)}")
    print(f"   Cidades únicas por ID: {len(cidades_por_id)}")
    
    if cidades_por_nome:
        print(f"\n   🏙️ Nomes de cidades encontradas:")
        for nome in sorted(cidades_por_nome):
            print(f"      - {nome}")

# 2. Buscar cidades da tabela CidadesDemografia
print("\n" + "="*70)
print("🏙️ 2. ANALISANDO TABELA CIDADES_DEMOGRAFIA...\n")
resp_cidades = requests.get(f"{API_URL}/api/cidades")
if resp_cidades.status_code == 200:
    cidades_db = resp_cidades.json()
    
    if isinstance(cidades_db, list):
        cidades = cidades_db
    elif isinstance(cidades_db, dict):
        cidades = cidades_db.get('cidades', cidades_db.get('data', []))
    
    print(f"Total de cidades na tabela: {len(cidades)}")
    
    print(f"\n📋 PRIMEIRAS 15 CIDADES:\n")
    for i, cidade in enumerate(cidades[:15], 1):
        cidade_id = cidade.get('id')
        cidade_nome = cidade.get('cidade') or cidade.get('nome')
        populacao = cidade.get('populacao_estimada_2024') or cidade.get('populacao_censo_2022') or 0
        
        print(f"{i:2}. ID: {cidade_id:3} | Nome: {cidade_nome:30} | Pop: {populacao:,}")

# 3. Verificar Metas Progressivas
print("\n" + "="*70)
print("📈 3. VERIFICANDO METAS PROGRESSIVAS...\n")
resp_metas = requests.get(f"{API_URL}/api/metas-progressivas")
if resp_metas.status_code == 200:
    metas_data = resp_metas.json()
    
    if isinstance(metas_data, list):
        metas = metas_data
    elif isinstance(metas_data, dict):
        metas = metas_data.get('metas', metas_data.get('data', []))
    
    print(f"Total de metas progressivas: {len(metas)}")
    
    if metas:
        print(f"\n📋 PRIMEIRAS 5 METAS:\n")
        for i, meta in enumerate(metas[:5], 1):
            print(f"{i}. Cidade ID: {meta.get('cidade_id')} | "
                  f"Meta Motoristas: {meta.get('meta_motoristas')} | "
                  f"Meta Corridas: {meta.get('meta_corridas')} | "
                  f"Status: {meta.get('status')}")
    else:
        print("⚠️ Tabela de metas progressivas está VAZIA")

# 4. Conclusão
print("\n" + "="*70)
print("🎯 CONCLUSÃO:")
print("="*70)
print(f"""
PROBLEMA IDENTIFICADO:
- {campanhas_sem_cidade_id} de {len(campanhas)} campanhas têm cidade_id = NULL
- Isso causa o retorno "Cidade não encontrada" no endpoint

SOLUÇÕES POSSÍVEIS:
1. Popular cidade_id fazendo match com CidadesDemografia por nome
2. Modificar endpoint para usar campo 'cidade' (string) da tabela Campanha
3. Verificar se existe campo 'cidade' (string) na tabela Campanha

CIDADES REAIS:
- Tabela CidadesDemografia tem {len(cidades) if 'cidades' in locals() else '?'} cidades
- Campanhas referenciam {len(cidades_por_nome)} cidades únicas por nome
- Campanhas referenciam {len(cidades_por_id)} cidades únicas por ID
""")
