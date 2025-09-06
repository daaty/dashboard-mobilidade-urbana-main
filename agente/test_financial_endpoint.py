#!/usr/bin/env python3
"""
Script para testar o endpoint financeiro específico do N8N
"""
import requests
import json

# Dados de teste simulando o que vem do N8N
test_data = {
    "kind": "drive#file",
    "id": "1OY3GUVQ_DQFg6FSzadSNFRDlKXBHB1y8",
    "name": "comprovante_combustivel_20250905.jpg",
    "mimeType": "text/html",
    "webContentLink": "https://drive.google.com/uc?id=1OY3GUVQ_DQFg6FSzadSNFRDlKXBHB1y8&export=download",
    "webViewLink": "https://drive.google.com/file/d/1OY3GUVQ_DQFg6FSzadSNFRDlKXBHB1y8/view?usp=drivesdk",
    "content": {
        "parts": [
            {
                "text": '''```json
{
  "dados_extraidos": {
    "data_despesa": "2025-09-05",
    "valor_total": 150.75,
    "descricao_item": "Combustível para veículo da empresa",
    "tipo_documento": "Comprovante",
    "fornecedor": "Posto Shell"
  },
  "descricao_imagem": "Comprovante de pagamento de combustível no Posto Shell. Data: 05/09/2025. Valor: R$ 150,75. Produto: Gasolina comum. Placa do veículo: ABC-1234."
}
```'''
            }
        ],
        "role": "model"
    }
}

def test_financial_endpoint():
    """Testa o endpoint financeiro"""
    
    endpoint = "http://localhost:8001/financial/register"
    
    print("🧪 TESTE DO ENDPOINT FINANCEIRO")
    print("=" * 50)
    print(f"📍 Endpoint: {endpoint}")
    print(f"📋 Arquivo: {test_data['name']}")
    print(f"💰 Valor: R$ {test_data['content']['parts'][0]['text']}")
    print()
    
    try:
        # Enviar requisição
        response = requests.post(
            endpoint,
            json=test_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"📡 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ SUCESSO!")
            print(f"📨 Resposta: {json.dumps(result, indent=2, ensure_ascii=False)}")
            
            if result.get("success"):
                print(f"🎯 Gasto ID: {result.get('gasto_id')}")
                print(f"💬 Mensagem: {result.get('message')}")
            else:
                print(f"❌ Erro: {result.get('error')}")
                
        else:
            print("❌ ERRO!")
            print(f"📨 Resposta: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ ERRO: Não foi possível conectar ao servidor")
        print("🔧 Certifique-se de que o mobility_playground.py está rodando")
        print("🚀 Execute: python mobility_playground.py")
        
    except Exception as e:
        print(f"❌ ERRO INESPERADO: {e}")

def test_health_endpoint():
    """Testa o endpoint de health"""
    
    endpoint = "http://localhost:8001/financial/health"
    
    print("\n🏥 TESTE DO HEALTH CHECK")
    print("=" * 30)
    
    try:
        response = requests.get(endpoint, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Health OK!")
            print(f"📨 Status: {result.get('status')}")
            print(f"🔧 Serviço: {result.get('service')}")
        else:
            print(f"❌ Health Error: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Health Error: {e}")

if __name__ == "__main__":
    print("🧪 TESTANDO ENDPOINTS FINANCEIROS")
    print("=" * 60)
    
    # Testar health primeiro
    test_health_endpoint()
    
    # Testar endpoint principal
    test_financial_endpoint()
    
    print("\n" + "=" * 60)
    print("🏁 TESTE CONCLUÍDO!")
    print("\n📝 COMO USAR:")
    print("1. 🎯 Dashboard → POST /v1/playground/agents/{agent_id}/runs")
    print("2. 💰 N8N → POST /financial/register")
    print("3. 🏥 Health → GET /financial/health")
