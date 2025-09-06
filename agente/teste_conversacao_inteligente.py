import requests

# Teste das novas respostas inteligentes
url = "https://agno.rotadoscelulares.com/financial/register"

# Teste 1: Cumprimento
print("🧪 TESTE 1: Cumprimento")
response = requests.post(url, json={"userName": "Wesley", "userMessage": "Ola"})
print(f"Resposta: {response.json()['message']}")
print("=" * 50)

# Teste 2: Pergunta sobre funcionalidade
print("🧪 TESTE 2: Pergunta sobre funcionalidade")
response = requests.post(url, json={"userName": "Wesley", "userMessage": "o que você faz?"})
print(f"Resposta: {response.json()['message']}")
print("=" * 50)

# Teste 3: Menção de comprovante
print("🧪 TESTE 3: Menção de comprovante")
response = requests.post(url, json={"userName": "Wesley", "userMessage": "tenho um comprovante para registrar"})
print(f"Resposta: {response.json()['message']}")
print("=" * 50)

# Teste 4: Resposta positiva sobre NF
print("🧪 TESTE 4: Resposta positiva sobre NF")
response = requests.post(url, json={"userName": "Wesley", "userMessage": "sim, tenho nota fiscal"})
print(f"Resposta: {response.json()['message']}")
print("=" * 50)

# Teste 5: Mensagem aleatória
print("🧪 TESTE 5: Mensagem aleatória")
response = requests.post(url, json={"userName": "Wesley", "userMessage": "blz, vamos conversar!"})
print(f"Resposta: {response.json()['message']}")
print("=" * 50)
