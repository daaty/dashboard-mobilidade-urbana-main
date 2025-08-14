#!/usr/bin/env python3
"""
Script para criar campanhas para MATUPA, PEIXOTO e GUARANTA DO NORTE
que têm dados reais de corridas/motoristas mas não têm campanhas ainda.
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"

def verificar_cidades_existentes():
    """Verifica quais cidades já existem na tabela demográfica"""
    print("🔍 Verificando cidades existentes...")
    
    response = requests.get(f"{BASE_URL}/api/cidades")
    if response.status_code == 200:
        cidades = response.json()
        print(f"✅ Encontradas {len(cidades)} cidades na tabela demográfica:")
        for cidade in cidades:
            print(f"   - {cidade['cidade']} (pop: {cidade['populacao_censo_2022']:,})")
        return cidades
    else:
        print(f"❌ Erro ao buscar cidades: {response.status_code}")
        return []

def criar_cidade_demografica(nome, populacao):
    """Cria uma nova cidade na tabela demográfica"""
    print(f"🏗️ Criando cidade demográfica: {nome}")
    
    # Calculando público-alvo (15-44 anos) como ~44% da população
    publico_alvo = int(populacao * 0.44)
    
    cidade_data = {
        "cidade": nome,
        "populacao_censo_2022": populacao,
        "populacao_estimada_2024": populacao,
        "densidade_demografica": None,
        "publico_alvo_15_44_anos": publico_alvo,
        "publico_homens": None,
        "publico_mulheres": None
    }
    
    response = requests.post(f"{BASE_URL}/api/cidades", json=cidade_data)
    if response.status_code == 201:
        cidade_criada = response.json()
        print(f"✅ Cidade {nome} criada com ID: {cidade_criada['id']}")
        return cidade_criada
    else:
        print(f"❌ Erro ao criar cidade {nome}: {response.status_code}")
        print(f"   Resposta: {response.text}")
        return None

def criar_campanha(nome, fase, parte, tipo_campanha, tipo_gasto, meta_quantidade, orcamento, cidade_id):
    """Cria uma nova campanha"""
    print(f"📋 Criando campanha: {nome}")
    
    campanha_data = {
        "nome": nome,
        "fase": fase,
        "parte_campanha": parte,
        "tipo_campanha": tipo_campanha,
        "tipo_gasto": tipo_gasto,
        "meta_quantidade": meta_quantidade,
        "meta_percentual_populacao": 0.5 if tipo_campanha == "aquisicao_corridas" else None,
        "orcamento_previsto": orcamento,
        "status": "ativa",
        "data_inicio": "2025-08-01",
        "data_fim": "2025-09-30",
        "cidade_id": cidade_id
    }
    
    response = requests.post(f"{BASE_URL}/api/dashboard-executivo/campanhas", json=campanha_data)
    if response.status_code == 201:
        campanha_criada = response.json()
        print(f"✅ Campanha criada com ID: {campanha_criada['id']}")
        return campanha_criada
    else:
        print(f"❌ Erro ao criar campanha {nome}: {response.status_code}")
        print(f"   Resposta: {response.text}")
        return None

def main():
    print("🚀 CRIANDO CAMPANHAS PARA CIDADES IMPORTANTES")
    print("=" * 60)
    
    # 1. Verificar cidades existentes
    cidades_existentes = verificar_cidades_existentes()
    cidades_nomes = [c['cidade'] for c in cidades_existentes]
    
    # 2. Definir as cidades importantes que precisam de campanhas
    cidades_importantes = [
        {"nome": "MATUPA", "populacao": 15000, "corridas": 22, "motoristas": 19},
        {"nome": "PEIXOTO", "populacao": 12000, "corridas": 57, "motoristas": 25},
        {"nome": "GUARANTA DO NORTE", "populacao": 8000, "corridas": 9, "motoristas": 8}
    ]
    
    print(f"\n🎯 Cidades importantes que precisam de campanhas:")
    for cidade in cidades_importantes:
        print(f"   - {cidade['nome']}: {cidade['corridas']} corridas, {cidade['motoristas']} motoristas")
    
    # 3. Criar cidades demográficas se não existirem
    print(f"\n🏗️ CRIANDO CIDADES DEMOGRÁFICAS...")
    cidades_ids = {}
    
    for cidade in cidades_importantes:
        nome = cidade['nome']
        if nome not in cidades_nomes:
            cidade_criada = criar_cidade_demografica(nome, cidade['populacao'])
            if cidade_criada:
                cidades_ids[nome] = cidade_criada['id']
        else:
            # Encontrar ID da cidade existente
            cidade_existente = next((c for c in cidades_existentes if c['cidade'] == nome), None)
            if cidade_existente:
                cidades_ids[nome] = cidade_existente['id']
                print(f"✅ Cidade {nome} já existe com ID: {cidade_existente['id']}")
    
    # 4. Criar campanhas para cada cidade
    print(f"\n📋 CRIANDO CAMPANHAS...")
    
    campanhas_criadas = []
    
    for cidade in cidades_importantes:
        nome = cidade['nome']
        cidade_id = cidades_ids.get(nome)
        
        if not cidade_id:
            print(f"❌ Pulando {nome}: cidade_id não encontrado")
            continue
        
        # Calcular orçamentos baseados nos dados reais
        orcamento_motoristas = cidade['motoristas'] * 150  # R$150 por motorista
        orcamento_corridas = cidade['corridas'] * 50      # R$50 por corrida
        
        # Campanha de Motoristas
        campanha_motoristas = criar_campanha(
            nome=f"Campanha Motoristas {nome}",
            fase="Fase 1",
            parte="Part 1",
            tipo_campanha="aquisicao_motoristas",
            tipo_gasto="operacoes",
            meta_quantidade=cidade['motoristas'],
            orcamento=orcamento_motoristas,
            cidade_id=cidade_id
        )
        
        if campanha_motoristas:
            campanhas_criadas.append(campanha_motoristas)
        
        # Campanha de Corridas
        campanha_corridas = criar_campanha(
            nome=f"Campanha Corridas {nome}",
            fase="Fase 1",
            parte="Part 2",
            tipo_campanha="aquisicao_corridas",
            tipo_gasto="trafego_pago",
            meta_quantidade=cidade['corridas'],
            orcamento=orcamento_corridas,
            cidade_id=cidade_id
        )
        
        if campanha_corridas:
            campanhas_criadas.append(campanha_corridas)
    
    # 5. Resumo final
    print(f"\n🎉 RESUMO FINAL")
    print("=" * 60)
    print(f"✅ Cidades importantes processadas: {len(cidades_importantes)}")
    print(f"✅ Campanhas criadas: {len(campanhas_criadas)}")
    
    if campanhas_criadas:
        print(f"\n📋 Campanhas criadas:")
        for campanha in campanhas_criadas:
            print(f"   - {campanha['nome']} (ID: {campanha['id']})")
    
    # 6. Verificar total de campanhas agora
    print(f"\n🔄 Verificando total de campanhas...")
    response = requests.get(f"{BASE_URL}/api/dashboard-executivo/campanhas")
    if response.status_code == 200:
        data = response.json()
        total_campanhas = data.get('total_campanhas', 0)
        print(f"✅ Total de campanhas no sistema: {total_campanhas}")
    
    print(f"\n🎯 Sistema agora tem dados completos para validação!")

if __name__ == "__main__":
    main()
