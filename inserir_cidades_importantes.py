#!/usr/bin/env python3
"""Script para criar as 3 cidades importantes na tabela de demografia"""

import sys
import os
import requests

def main():
    print("🏗️ VERIFICANDO CIDADES IMPORTANTES")
    print("=" * 50)
    
    # Dados das 3 cidades importantes
    cidades_importantes = [
        {
            'cidade': 'MATUPA', 
            'populacao_censo_2022': 15000, 
            'populacao_estimada_2024': 15000, 
            'publico_alvo_15_44_anos': 6600
        },
        {
            'cidade': 'PEIXOTO', 
            'populacao_censo_2022': 12000, 
            'populacao_estimada_2024': 12000, 
            'publico_alvo_15_44_anos': 5280
        },
        {
            'cidade': 'GUARANTA DO NORTE', 
            'populacao_censo_2022': 8000, 
            'populacao_estimada_2024': 8000, 
            'publico_alvo_15_44_anos': 3520
        }
    ]

    # Sempre usar método via API HTTP (mais confiável)
    verificar_via_api(cidades_importantes)

def verificar_via_api(cidades_importantes):
    """Verificar cidades via API HTTP"""
    try:
        print("🌐 Verificando cidades via API...")
        
        # Verificar se a API está rodando
        response = requests.get("http://localhost:8000/api/cidades")
        if response.status_code == 200:
            cidades_existentes = response.json()
            print(f"✅ API funcionando - {len(cidades_existentes)} cidades encontradas")
            
            # Verificar se as 3 cidades importantes estão lá
            nomes_existentes = [c['cidade'] for c in cidades_existentes]
            
            print("\n🔍 VERIFICANDO CIDADES IMPORTANTES:")
            for cidade_data in cidades_importantes:
                nome = cidade_data['cidade']
                if nome in nomes_existentes:
                    cidade_info = next(c for c in cidades_existentes if c['cidade'] == nome)
                    print(f"✅ {nome} já existe (ID: {cidade_info['id']}, pop: {cidade_info['populacao_estimada_2024']:,})")
                else:
                    print(f"❌ {nome} NÃO encontrada - precisa ser criada")
            
            print(f"\n📊 TODAS AS CIDADES NA API:")
            for c in cidades_existentes:
                pop = c.get('populacao_estimada_2024', c.get('populacao_censo_2022', 0))
                print(f"   {c['id']}: {c['cidade']} (pop: {pop:,})")
                
            # Verificar campanhas das cidades importantes
            print(f"\n🚀 VERIFICANDO CAMPANHAS DAS CIDADES IMPORTANTES:")
            response_campanhas = requests.get("http://localhost:8000/api/dashboard-executivo/campanhas")
            if response_campanhas.status_code == 200:
                campanhas_data = response_campanhas.json()
                campanhas = campanhas_data.get('campanhas', [])
                
                for cidade_data in cidades_importantes:
                    nome = cidade_data['cidade']
                    campanhas_cidade = [c for c in campanhas if nome in c['nome']]
                    print(f"   📊 {nome}: {len(campanhas_cidade)} campanhas")
                    
                    # Verificar dados reais de corridas
                    try:
                        metrics_response = requests.get(f"http://localhost:8000/api/metrics/overview?cidade={nome}")
                        if metrics_response.status_code == 200:
                            metrics = metrics_response.json()
                            corridas = metrics.get('metricas_principais', {}).get('corridas_concluidas', 0)
                            print(f"       🚗 Corridas reais: {corridas}")
                        else:
                            print(f"       ⚠️  Sem dados de corridas")
                    except:
                        print(f"       ❌ Erro ao buscar métricas")
                
        else:
            print(f"❌ Erro na API: {response.status_code}")
            
    except requests.ConnectionError:
        print("❌ Não foi possível conectar à API. Verifique se o backend está rodando em http://localhost:8000")
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    main()
