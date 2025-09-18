import requests
import json

# Teste do endpoint DELETE que está falhando
url = "https://fastapi.urbanmt.com.br/api/financeiro/gastos/425581"

# Headers que simulam uma requisição do frontend
headers = {
    "Content-Type": "application/json",
    "Origin": "https://dashbord.urbanmt.com.br",  # Domínio do frontend
    "Access-Control-Request-Method": "DELETE",
    "Access-Control-Request-Headers": "content-type"
}

print("Testando endpoint DELETE em produção...")
print(f"URL: {url}")
print(f"Headers: {json.dumps(headers, indent=2)}")

try:
    # Primeiro, teste um OPTIONS request (preflight CORS)
    print("\n1. Testando OPTIONS request (CORS preflight):")
    options_response = requests.options(url, headers=headers, timeout=10)
    print(f"Status: {options_response.status_code}")
    print(f"Headers de resposta:")
    for key, value in options_response.headers.items():
        if 'cors' in key.lower() or 'access-control' in key.lower():
            print(f"  {key}: {value}")
    
    # Agora teste o DELETE real
    print("\n2. Testando DELETE request:")
    delete_headers = {
        "Content-Type": "application/json",
        "Origin": "https://dashbord.urbanmt.com.br"
    }
    
    delete_response = requests.delete(url, headers=delete_headers, timeout=10)
    print(f"Status: {delete_response.status_code}")
    print(f"Response headers:")
    for key, value in delete_response.headers.items():
        if 'cors' in key.lower() or 'access-control' in key.lower() or 'content-type' in key.lower():
            print(f"  {key}: {value}")
    
    print(f"Response content: {delete_response.text[:500]}...")
    
    # Teste também um GET para verificar se o servidor está respondendo
    print("\n3. Testando GET na mesma base URL:")
    get_response = requests.get("https://fastapi.urbanmt.com.br/health", timeout=10)
    print(f"Health check status: {get_response.status_code}")
    print(f"Health check response: {get_response.text}")
    
except requests.exceptions.RequestException as e:
    print(f"Erro na requisição: {e}")
except Exception as e:
    print(f"Erro geral: {e}")

print("\n" + "="*50)
print("DIAGNÓSTICO:")
print("Se o OPTIONS retornar 200 mas o DELETE retornar 500, o problema está no servidor.")
print("Se o OPTIONS retornar erro, o problema é CORS.")
print("Se ambos derem erro de conexão, o servidor não está acessível.")