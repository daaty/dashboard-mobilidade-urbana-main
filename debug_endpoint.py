import requests
import json

# Teste direto do endpoint com debug
response = requests.get('http://localhost:8000/api/drivers/kpis?period=30_days&city=all&status=all')
print("Status:", response.status_code)
print("Response:", response.text)

# Verificar se há logs no terminal do backend