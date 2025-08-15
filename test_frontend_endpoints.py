#!/usr/bin/env python3
"""Script para testar os novos endpoints do frontend"""

import requests
import json

# URL base da API
API_URL = "http://localhost:8000"

def test_endpoint(endpoint, description):
    """Testa um endpoint e exibe o resultado"""
    try:
        print(f"\n🧪 TESTANDO: {description}")
        print(f"📡 Endpoint: {endpoint}")
        
        response = requests.get(f"{API_URL}{endpoint}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Sucesso! Status: {response.status_code}")
            
            # Exibir informações resumidas dos dados
            if isinstance(data, list):
                print(f"📊 Retornou {len(data)} itens")
                if len(data) > 0:
                    print(f"🔍 Exemplo do primeiro item:")
                    print(f"   {json.dumps(data[0], indent=2, ensure_ascii=False)[:200]}...")
            elif isinstance(data, dict):
                print(f"📊 Retornou objeto com {len(data)} propriedades")
                print(f"🔍 Propriedades: {list(data.keys())}")
                
        else:
            print(f"❌ Erro! Status: {response.status_code}")
            print(f"💬 Resposta: {response.text}")
            
    except requests.ConnectionError:
        print(f"❌ Erro de conexão! Verifique se o backend está rodando em {API_URL}")
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")

def main():
    print("🚀 TESTE DOS NOVOS ENDPOINTS")
    print("=" * 50)
    
    # Testar todos os endpoints principais
    endpoints = [
        ("/api/fases-planejamento", "Fases de Planejamento"),
        ("/api/fases-planejamento/resumo", "Resumo das Fases"),
        ("/api/metas-progressivas", "Metas Progressivas"),
        ("/api/metas-progressivas?cidade_id=8", "Metas da cidade MATUPA"),
        ("/api/metas-progressivas?mes=1", "Metas de 1 mês"),
        ("/api/cidades", "Lista de Cidades"),
        ("/api/dashboard-executivo/campanhas", "Campanhas Executivas"),
    ]
    
    for endpoint, description in endpoints:
        test_endpoint(endpoint, description)
    
    print(f"\n🎉 TESTE CONCLUÍDO!")
    print("=" * 50)
    print("💡 Se todos os endpoints retornaram ✅, o frontend deve funcionar perfeitamente!")
    print("🌐 Acesse: http://localhost:3000")

if __name__ == "__main__":
    main()
