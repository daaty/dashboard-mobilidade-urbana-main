import requests

# Teste do novo fluxo de workflow
url = "https://agno.rotadoscelulares.com/financial/register"

print("🧪 TESTE DO NOVO FLUXO DE WORKFLOW")
print("="*50)

# TESTE 1: Enviar dados de imagem (deve fazer ETAPA 1 e perguntar sobre NF)
print("🧪 TESTE 1: Dados de imagem (deve perguntar sobre NF)")
json_imagem = {
    "kind": "drive#file",
    "id": "test_id",
    "name": "comprovante_teste.jpg",
    "mimeType": "text/html",
    "webContentLink": "https://exemplo.com/arquivo",
    "webViewLink": "https://exemplo.com/view",
    "content": {
        "parts": [
            {
                "text": '```json\n{"dados_extraidos":{"data_despesa":"2025-09-05","valor_total":50.0,"descricao_item":"Teste workflow","tipo_documento":"Comprovante","fornecedor":"Empresa Teste"},"descricao_imagem":"Teste"}\n```'
            }
        ],
        "role": "model"
    }
}

response = requests.post(url, json=json_imagem)
print(f"Status: {response.status_code}")
print(f"Resposta: {response.json()}")
print("="*50)

# TESTE 2: Resposta "SIM" para NF
print("🧪 TESTE 2: Resposta 'Sim, tenho nota fiscal'")
json_sim_nf = {
    "userName": "Wesley",
    "userMessage": "Sim, tenho nota fiscal"
}

response = requests.post(url, json=json_sim_nf)
print(f"Status: {response.status_code}")
print(f"Resposta: {response.json()}")
print("="*50)

# TESTE 3: Resposta "NÃO" para NF
print("🧪 TESTE 3: Resposta 'Não tenho nota fiscal'")
json_nao_nf = {
    "userName": "Wesley", 
    "userMessage": "Não tenho nota fiscal"
}

response = requests.post(url, json=json_nao_nf)
print(f"Status: {response.status_code}")
print(f"Resposta: {response.json()}")
print("="*50)

# TESTE 4: Categoria do gasto
print("🧪 TESTE 4: Categoria 'Alimentação'")
json_categoria = {
    "userName": "Wesley",
    "userMessage": "Alimentação"
}

response = requests.post(url, json=json_categoria)
print(f"Status: {response.status_code}")
print(f"Resposta: {response.json()}")
print("="*50)
