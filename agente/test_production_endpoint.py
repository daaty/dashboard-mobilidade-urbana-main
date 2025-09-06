#!/usr/bin/env python3
"""
Teste do endpoint financeiro em produção
"""
import requests
import json

# Endpoint de produção
ENDPOINT = "https://agno.rotadoscelulares.com/financial/register"
HEALTH_ENDPOINT = "https://agno.rotadoscelulares.com/financial/health"

# Dados de teste
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

def test_health():
    """Testa o health check"""
    print("🏥 TESTANDO HEALTH CHECK...")
    try:
        response = requests.get(HEALTH_ENDPOINT, timeout=10)
        if response.status_code == 200:
            print("✅ Health OK!")
            print(f"📨 {response.json()}")
            return True
        else:
            print(f"❌ Health Error: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health Error: {e}")
        return False

def test_financial():
    """Testa o endpoint financeiro"""
    print("\n💰 TESTANDO ENDPOINT FINANCEIRO...")
    print(f"📍 {ENDPOINT}")
    
    try:
        response = requests.post(
            ENDPOINT,
            json=test_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"📡 Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ SUCESSO!")
            print(f"📨 Resposta:")
            print(json.dumps(result, indent=2, ensure_ascii=False))
            
            if result.get("success"):
                print(f"\n🎯 Gasto registrado com ID: {result.get('gasto_id')}")
                print(f"💬 Mensagem: {result.get('message')}")
                return True
            else:
                print(f"❌ Erro: {result.get('error')}")
                return False
        else:
            print("❌ ERRO!")
            print(f"📨 Resposta: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

if __name__ == "__main__":
    print("🌐 TESTE DO ENDPOINT EM PRODUÇÃO")
    print("=" * 50)
    
    # Testar health
    health_ok = test_health()
    
    if health_ok:
        # Testar endpoint financeiro
        financial_ok = test_financial()
        
        if financial_ok:
            print("\n🎉 TODOS OS TESTES PASSARAM!")
            print("✅ Sistema pronto para usar em produção!")
        else:
            print("\n❌ Erro no teste financeiro")
    else:
        print("❌ Erro no health check - verifique se o servidor está rodando")
    
    print("\n" + "=" * 50)
    print("📝 CONFIGURAÇÃO DO N8N:")
    print(f"🔗 URL: {ENDPOINT}")
    print("📤 Method: POST")
    print("📋 Content-Type: application/json")
    print("💾 Body: Dados do Google Drive + content.parts[0].text")
