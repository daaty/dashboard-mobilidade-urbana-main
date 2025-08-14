#!/usr/bin/env python3
"""Script simplificado para inserir as cidades importantes via SQL"""

import requests
import json

BASE_URL = "http://localhost:8000"

def inserir_cidades_sql():
    """Inserir as cidades via SQL direto"""
    print("🏗️ INSERINDO CIDADES IMPORTANTES VIA SQL")
    print("=" * 50)
    
    # Comandos SQL para inserir as cidades
    sql_commands = [
        """
        INSERT INTO cidades_demografia (
            cidade, populacao_censo_2022, populacao_estimada_2024, 
            densidade_demografica, publico_alvo_15_44_anos, 
            publico_homens, publico_mulheres, created_at
        ) VALUES 
        ('MATUPA', 15000, 15000, NULL, 6600, NULL, NULL, NOW()),
        ('PEIXOTO', 12000, 12000, NULL, 5280, NULL, NULL, NOW()),
        ('GUARANTA DO NORTE', 8000, 8000, NULL, 3520, NULL, NULL, NOW())
        ON CONFLICT (cidade) DO NOTHING;
        """
    ]
    
    print("📝 SQL para executar no banco:")
    for cmd in sql_commands:
        print(cmd.strip())
    
    return sql_commands

def verificar_cidades_criadas():
    """Verificar se as cidades foram criadas"""
    print("\n🔍 VERIFICANDO CIDADES CRIADAS...")
    
    try:
        response = requests.get(f"{BASE_URL}/api/cidades")
        if response.status_code == 200:
            cidades = response.json()
            print(f"✅ Total de cidades: {len(cidades)}")
            
            # Procurar pelas nossas cidades importantes
            cidades_importantes = ['MATUPA', 'PEIXOTO', 'GUARANTA DO NORTE']
            cidades_encontradas = {}
            
            for cidade in cidades:
                nome = cidade['cidade']
                if nome in cidades_importantes:
                    cidades_encontradas[nome] = cidade['id']
                    print(f"   ✅ {nome} (ID: {cidade['id']}) - Pop: {cidade['populacao_censo_2022']:,}")
            
            # Verificar quais estão faltando
            faltando = set(cidades_importantes) - set(cidades_encontradas.keys())
            if faltando:
                print(f"❌ Cidades faltando: {', '.join(faltando)}")
                return None
            else:
                print("🎉 Todas as cidades importantes foram encontradas!")
                return cidades_encontradas
        else:
            print(f"❌ Erro ao verificar cidades: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Erro na verificação: {e}")
        return None

def criar_campanhas_para_cidade(nome_cidade, cidade_id, dados):
    """Criar campanhas para uma cidade específica"""
    print(f"\n📋 Criando campanhas para {nome_cidade}...")
    
    campanhas_criadas = []
    
    # Calcular orçamentos baseados nos dados reais
    orcamento_motoristas = dados['motoristas'] * 150  # R$150 por motorista
    orcamento_corridas = dados['corridas'] * 50      # R$50 por corrida
    
    # Campanha de Motoristas
    campanha_motoristas = {
        "nome": f"Campanha Motoristas {nome_cidade}",
        "fase": "Fase 1",
        "parte_campanha": "Part 1",
        "tipo_campanha": "aquisicao_motoristas",
        "tipo_gasto": "operacoes",
        "meta_quantidade": dados['motoristas'],
        "meta_percentual_populacao": None,
        "orcamento_previsto": float(orcamento_motoristas),
        "status": "ativa",
        "data_inicio": "2025-08-01",
        "data_fim": "2025-09-30",
        "cidade_id": cidade_id
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/dashboard-executivo/campanhas", json=campanha_motoristas)
        if response.status_code == 201:
            campanha_criada = response.json()
            print(f"   ✅ Campanha Motoristas criada (ID: {campanha_criada['id']})")
            campanhas_criadas.append(campanha_criada)
        else:
            print(f"   ❌ Erro ao criar campanha motoristas: {response.status_code}")
            print(f"      Resposta: {response.text}")
    except Exception as e:
        print(f"   ❌ Erro ao criar campanha motoristas: {e}")
    
    # Campanha de Corridas
    campanha_corridas = {
        "nome": f"Campanha Corridas {nome_cidade}",
        "fase": "Fase 1",
        "parte_campanha": "Part 2",
        "tipo_campanha": "aquisicao_corridas",
        "tipo_gasto": "trafego_pago",
        "meta_quantidade": dados['corridas'],
        "meta_percentual_populacao": 0.5,
        "orcamento_previsto": float(orcamento_corridas),
        "status": "ativa",
        "data_inicio": "2025-08-01",
        "data_fim": "2025-09-30",
        "cidade_id": cidade_id
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/dashboard-executivo/campanhas", json=campanha_corridas)
        if response.status_code == 201:
            campanha_criada = response.json()
            print(f"   ✅ Campanha Corridas criada (ID: {campanha_criada['id']})")
            campanhas_criadas.append(campanha_criada)
        else:
            print(f"   ❌ Erro ao criar campanha corridas: {response.status_code}")
            print(f"      Resposta: {response.text}")
    except Exception as e:
        print(f"   ❌ Erro ao criar campanha corridas: {e}")
    
    return campanhas_criadas

def main():
    print("🚀 PROCESSO COMPLETO: CIDADES + CAMPANHAS")
    print("=" * 60)
    
    # Etapa 1: Mostrar SQL para inserir cidades
    sql_commands = inserir_cidades_sql()
    
    print("\n" + "="*50)
    print("⚠️  AÇÃO MANUAL NECESSÁRIA:")
    print("1. Execute o SQL acima no seu banco PostgreSQL")
    print("2. Pressione ENTER quando concluído")
    print("="*50)
    input("Pressione ENTER após executar o SQL...")
    
    # Etapa 2: Verificar se as cidades foram criadas
    cidades_encontradas = verificar_cidades_criadas()
    
    if not cidades_encontradas:
        print("❌ Não foi possível encontrar as cidades. Verifique se o SQL foi executado.")
        return
    
    # Etapa 3: Criar campanhas
    print("\n🎯 CRIANDO CAMPANHAS...")
    dados_cidades = {
        'MATUPA': {'corridas': 22, 'motoristas': 19},
        'PEIXOTO': {'corridas': 57, 'motoristas': 25},
        'GUARANTA DO NORTE': {'corridas': 9, 'motoristas': 8}
    }
    
    total_campanhas_criadas = 0
    
    for nome_cidade, cidade_id in cidades_encontradas.items():
        dados = dados_cidades[nome_cidade]
        campanhas = criar_campanhas_para_cidade(nome_cidade, cidade_id, dados)
        total_campanhas_criadas += len(campanhas)
    
    # Etapa 4: Verificar resultado final
    print(f"\n🎉 RESUMO FINAL")
    print("=" * 50)
    print(f"✅ Cidades criadas: {len(cidades_encontradas)}")
    print(f"✅ Campanhas criadas: {total_campanhas_criadas}")
    
    # Verificar total de campanhas no sistema
    try:
        response = requests.get(f"{BASE_URL}/api/dashboard-executivo/campanhas")
        if response.status_code == 200:
            data = response.json()
            total_campanhas = data.get('total_campanhas', 0)
            print(f"📊 Total de campanhas no sistema: {total_campanhas}")
        
        print("\n🎯 Sistema pronto para validação!")
    except Exception as e:
        print(f"⚠️ Erro ao verificar total de campanhas: {e}")

if __name__ == "__main__":
    main()
