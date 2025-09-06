import requests

# Teste do JSON que você quer usar
url = "https://agno.rotadoscelulares.com/financial/register"

json_quebrado = {
    "kind": "[undefined]",
    "id": "[undefined]", 
    "name": "[undefined]",
    "mimeType": "[undefined]",
    "webContentLink": "[undefined]",
    "webViewLink": "[undefined]",
    "userName": "Wesley",
    "userMessage": "ola ola ola",
    "content": {
        "parts": [
            {
                "text": "[undefined]"
            }
        ],
        "role": "model"
    }
}

response = requests.post(url, json=json_quebrado)
print(f"Status: {response.status_code}")
print(f"Resposta: {response.json()}")
