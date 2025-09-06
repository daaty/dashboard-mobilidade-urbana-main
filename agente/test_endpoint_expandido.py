import requests
import json

# TESTE 1: Interação de texto (novo)
print("🧪 TESTE 1: Interação de texto")
data_interacao = {
    "userName": "Wesley",
    "userMessage": "Olá, acabei de enviar um comprovante de combustível. Precisa de mais alguma informação?"
}

try:
    response = requests.post(
        "http://localhost:8001/financial/register",
        json=data_interacao,
        headers={"Content-Type": "application/json"}
    )
    print(f"Status: {response.status_code}")
    print(f"Resposta: {response.json()}")
except Exception as e:
    print(f"Erro: {e}")

print("\n" + "="*50 + "\n")

# TESTE 2: Dados de imagem (existente)
print("🧪 TESTE 2: Dados de imagem")
data_imagem = {
    "kind": "drive#file",
    "id": "teste123",
    "name": "comprovante_teste.jpg",
    "mimeType": "image/jpeg",
    "webContentLink": "https://exemplo.com/arquivo",
    "webViewLink": "https://exemplo.com/view",
    "content": {
        "parts": [
            {
                "text": '```json\n{"dados_extraidos": {"data_despesa": "2025-09-05", "valor_total": 50.0, "descricao_item": "Teste endpoint expandido", "tipo_documento": "Comprovante", "fornecedor": "Empresa Teste"}}\n```'
            }
        ],
        "role": "model"
    }
}

try:
    response = requests.post(
        "http://localhost:8001/financial/register",
        json=data_imagem,
        headers={"Content-Type": "application/json"}
    )
    print(f"Status: {response.status_code}")
    print(f"Resposta: {response.json()}")
except Exception as e:
    print(f"Erro: {e}")
