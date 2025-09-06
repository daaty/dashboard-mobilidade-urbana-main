"""
Teste do endpoint expandido - imagem E interação
"""
import requests
import json

BASE_URL = "https://agno.rotadoscelulares.com"

def test_interaction():
    """Testa interação de texto"""
    print("🧪 TESTE 1: Interação de texto")
    
    data = {
        "userName": "Wesley",
        "userMessage": "Olá, acabei de enviar um comprovante de combustível. Precisa de mais alguma informação?"
    }
    
    response = requests.post(f"{BASE_URL}/financial/register", json=data)
    print(f"Status: {response.status_code}")
    print(f"Resposta: {response.json()}")
    print("=" * 50)

def test_image_data():
    """Testa dados de imagem"""
    print("🧪 TESTE 2: Dados de imagem")
    
    data = {
        "kind": "drive#file",
        "id": "test123",
        "name": "comprovante_teste.jpg",
        "mimeType": "text/html",
        "webContentLink": "https://exemplo.com/arquivo",
        "webViewLink": "https://exemplo.com/view",
        "content": {
            "parts": [
                {
                    "text": '```json\n{"dados_extraidos": {"data_despesa": "2025-09-05", "valor_total": 50.00, "descricao_item": "Teste endpoint expandido", "tipo_documento": "Comprovante", "fornecedor": "Empresa Teste"}, "descricao_imagem": "Teste de imagem"}\n```'
                }
            ],
            "role": "model"
        }
    }
    
    response = requests.post(f"{BASE_URL}/financial/register", json=data)
    print(f"Status: {response.status_code}")
    print(f"Resposta: {response.json()}")
    print("=" * 50)

def test_nf_response():
    """Testa resposta sobre nota fiscal"""
    print("🧪 TESTE 3: Resposta sobre NF")
    
    data = {
        "userName": "Wesley",
        "userMessage": "Sim, tenho nota fiscal deste comprovante"
    }
    
    response = requests.post(f"{BASE_URL}/financial/register", json=data)
    print(f"Status: {response.status_code}")
    print(f"Resposta: {response.json()}")
    print("=" * 50)

if __name__ == "__main__":
    test_interaction()
    test_image_data()
    test_nf_response()
