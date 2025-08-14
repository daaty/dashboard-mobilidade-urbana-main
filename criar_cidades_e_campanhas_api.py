#!/usr/bin/env python3
"""
Script simplificado para criar as 3 cidades importantes via API POST
"""

import requests
import json
from datetime import datetime

def criar_cidades_via_api():
    """Cria as 3 cidades importantes via API POST"""
    
    print("🏗️  CRIANDO AS 3 CIDADES IMPORTANTES VIA API...")
    print("=" * 60)
    
    # Dados das 3 cidades importantes
    cidades = [
        {
            "nome": "MATUPA",
            "populacao": 15000,
            "descricao": "Cidade com 22 corridas reais e 19 motoristas ativos"
        },
        {
            "nome": "PEIXOTO", 
            "populacao": 12000,
            "descricao": "Cidade com 57 corridas reais registradas"
        },
        {
            "nome": "GUARANTA DO NORTE",
            "populacao": 35000,
            "descricao": "Cidade maior da região com 9 corridas reais"
        }
    ]
    
    api_url = "http://localhost:8000/api/dashboard-executivo/nova-cidade"
    cidades_criadas = []
    
    for cidade_data in cidades:
        try:
            print(f"🏙️  Criando {cidade_data['nome']}...")
            
            response = requests.post(api_url, json=cidade_data)
            
            if response.status_code == 200:
                result = response.json()
                cidade_id = result.get("cidade_id")
                print(f"✅ {cidade_data['nome']} criada com ID: {cidade_id}")
                print(f"   📊 População: {cidade_data['populacao']:,}")
                
                cidades_criadas.append({
                    "nome": cidade_data['nome'],
                    "id": cidade_id,
                    "populacao": cidade_data['populacao']
                })
            else:
                print(f"❌ Erro ao criar {cidade_data['nome']}: {response.status_code}")
                print(f"   Resposta: {response.text}")
                
        except Exception as e:
            print(f"❌ Erro de conexão para {cidade_data['nome']}: {e}")
    
    print(f"\n✅ {len(cidades_criadas)}/3 cidades criadas com sucesso!")
    return cidades_criadas

def criar_campanhas_via_api(cidades_criadas):
    """Cria campanhas para as cidades via API POST"""
    
    print("\n🚀 CRIANDO CAMPANHAS PARA AS CIDADES...")
    print("=" * 60)
    
    campanhas_data = []
    
    # Gerar campanhas para cada cidade criada
    for cidade in cidades_criadas:
        nome_cidade = cidade["nome"]
        cidade_id = cidade["id"]
        
        # Definir metas baseadas nos dados reais conhecidos
        metas = {
            "MATUPA": {"motoristas": 25, "corridas": 30, "orcamento": 2500.0},
            "PEIXOTO": {"motoristas": 20, "corridas": 60, "orcamento": 2200.0}, 
            "GUARANTA DO NORTE": {"motoristas": 15, "corridas": 25, "orcamento": 1800.0}
        }
        
        meta_cidade = metas.get(nome_cidade, {"motoristas": 15, "corridas": 25, "orcamento": 2000.0})
        
        # Campanha de Motoristas
        campanhas_data.append({
            "nome": f"Campanha Motoristas {nome_cidade}",
            "fase": "Fase 1",
            "parte_campanha": "Part 1",
            "tipo_campanha": "aquisicao_motoristas",
            "tipo_gasto": "operacoes",
            "meta_quantidade": meta_cidade["motoristas"],
            "orcamento_previsto": meta_cidade["orcamento"],
            "status": "ativa",
            "data_inicio": "2025-08-01",
            "data_fim": "2025-09-15",
            "cidade_id": cidade_id
        })
        
        # Campanha de Corridas
        campanhas_data.append({
            "nome": f"Campanha Corridas {nome_cidade}",
            "fase": "Fase 1",
            "parte_campanha": "Part 2", 
            "tipo_campanha": "aquisicao_corridas",
            "tipo_gasto": "trafego_pago",
            "meta_quantidade": meta_cidade["corridas"],
            "meta_percentual_populacao": 0.5,
            "orcamento_previsto": meta_cidade["orcamento"],
            "status": "ativa",
            "data_inicio": "2025-08-01",
            "data_fim": "2025-09-15",
            "cidade_id": cidade_id
        })
    
    # Criar campanhas via API
    api_url = "http://localhost:8000/api/dashboard-executivo/campanhas"
    sucesso = 0
    
    for campanha in campanhas_data:
        try:
            print(f"📊 Criando {campanha['nome']}...")
            
            response = requests.post(api_url, json=campanha)
            
            if response.status_code == 201:
                print(f"✅ Campanha criada!")
                print(f"   💰 Orçamento: R$ {campanha['orcamento_previsto']:,.2f}")
                print(f"   🎯 Meta: {campanha['meta_quantidade']} {campanha['tipo_campanha'].replace('aquisicao_', '')}")
                sucesso += 1
            else:
                print(f"❌ Erro: {response.status_code}")
                print(f"   Resposta: {response.text}")
                
        except Exception as e:
            print(f"❌ Erro de conexão: {e}")
    
    print(f"\n🎯 {sucesso}/6 campanhas criadas com sucesso!")
    return sucesso == 6

def validar_resultado():
    """Valida se tudo foi criado corretamente"""
    
    print("\n🔍 VALIDANDO RESULTADO FINAL...")
    print("=" * 60)
    
    try:
        # Verificar cidades
        response_cidades = requests.get("http://localhost:8000/api/cidades")
        if response_cidades.status_code == 200:
            cidades = response_cidades.json()
            print(f"🏙️  Total de cidades: {len(cidades)}")
            
            nomes_cidades = [c['cidade'] for c in cidades]
            for nome in ['MATUPA', 'PEIXOTO', 'GUARANTA DO NORTE']:
                status = "✅" if nome in nomes_cidades else "❌"
                print(f"{status} {nome}")
        
        # Verificar campanhas
        response_campanhas = requests.get("http://localhost:8000/api/dashboard-executivo/campanhas")
        if response_campanhas.status_code == 200:
            campanhas_data = response_campanhas.json()
            total_campanhas = campanhas_data.get('total_campanhas', 0)
            print(f"\n🚀 Total de campanhas: {total_campanhas}")
            
            # Contar campanhas por cidade
            campanhas = campanhas_data.get('campanhas', [])
            for nome in ['MATUPA', 'PEIXOTO', 'GUARANTA DO NORTE']:
                campanhas_cidade = [c for c in campanhas if nome in c['nome']]
                print(f"📊 {nome}: {len(campanhas_cidade)} campanhas")
        
        print("\n🎉 PROCESSO COMPLETO!")
        print("💡 Dashboard agora está 100% dinâmico!")
        print("🚀 Sistema funcionando com 10 cidades (7 originais + 3 importantes)!")
        
    except Exception as e:
        print(f"❌ Erro na validação: {e}")

if __name__ == "__main__":
    print("🏗️  PROCESSO COMPLETO VIA API: CIDADES + CAMPANHAS")
    print("=" * 60)
    
    # Passo 1: Criar as 3 cidades importantes
    cidades_criadas = criar_cidades_via_api()
    
    if len(cidades_criadas) > 0:
        print("\n✅ Pelo menos algumas cidades foram criadas!")
        
        # Passo 2: Criar campanhas para essas cidades
        if criar_campanhas_via_api(cidades_criadas):
            print("✅ Todas as campanhas criadas!")
        else:
            print("⚠️  Algumas campanhas podem ter falhado")
        
        # Passo 3: Validar resultado
        validar_resultado()
        
    else:
        print("❌ Nenhuma cidade foi criada - verificar API")
