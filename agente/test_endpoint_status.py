#!/usr/bin/env python3
"""
Teste para verificar se o endpoint está funcionando após restart
"""
import requests
import json

def test_endpoint_status():
    """Verifica se o endpoint está funcionando"""
    
    print("🏥 TESTANDO STATUS DO ENDPOINT...")
    
    try:
        # Teste de health primeiro
        health_response = requests.get("https://agno.rotadoscelulares.com/financial/health", timeout=10)
        
        if health_response.status_code == 200:
            print("✅ Health endpoint funcionando!")
            print(f"📨 {health_response.json()}")
        else:
            print(f"❌ Health endpoint com problema: {health_response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Erro no health check: {e}")
        return False
    
    # Teste com dados simples para validar JSON
    simple_test_data = {
        "kind": "drive#file",
        "id": "test123",
        "name": "teste.jpg",
        "mimeType": "text/html",
        "webContentLink": "https://example.com/test",
        "webViewLink": "https://example.com/view",
        "content": {
            "parts": [
                {
                    "text": """```json
{
  "dados_extraidos": {
    "data_despesa": "2025-09-05",
    "valor_total": 100.50,
    "descricao_item": "Teste de funcionamento",
    "tipo_documento": "Comprovante",
    "fornecedor": "Fornecedor Teste"
  },
  "descricao_imagem": "Imagem de teste para validar funcionamento"
}
```"""
                }
            ],
            "role": "model"
        }
    }
    
    print("\n💰 TESTANDO ENDPOINT FINANCEIRO COM DADOS SIMPLES...")
    
    try:
        response = requests.post(
            "https://agno.rotadoscelulares.com/financial/register",
            json=simple_test_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"📡 Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ ENDPOINT FUNCIONANDO!")
            print(json.dumps(result, indent=2, ensure_ascii=False))
            
            if result.get("success"):
                print(f"\n🎯 Gasto registrado com sucesso!")
                print(f"💾 ID: {result.get('gasto_id')}")
                return True
            else:
                print(f"\n❌ Erro na resposta: {result.get('error')}")
                return False
        else:
            print(f"❌ Erro HTTP: {response.status_code}")
            print(f"📨 Resposta: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")
        return False

if __name__ == "__main__":
    print("🧪 VERIFICAÇÃO DO STATUS DO ENDPOINT")
    print("=" * 50)
    
    if test_endpoint_status():
        print("\n🎉 ENDPOINT FUNCIONANDO PERFEITAMENTE!")
        print("\n📝 N8N PODE USAR:")
        print("🔗 URL: https://agno.rotadoscelulares.com/financial/register")
        print("📤 Method: POST")
        print("📋 Content-Type: application/json")
        print("\n✅ Dados do JSON válidos - pode configurar no N8N!")
    else:
        print("\n❌ ENDPOINT COM PROBLEMAS")
        print("🔧 Verifique se o servidor está rodando:")
        print("   python mobility_playground.py")
