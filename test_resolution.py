import requests
import json

# Teste específico para verificar se o frontend consegue acessar o backend corretamente
print("=== TESTE DE RESOLUÇÃO DO PROBLEMA ===")
print()

# 1. Verificar se o backend responde ao health check
print("1. Testando health check do backend:")
try:
    health_response = requests.get("https://fastapi.urbanmt.com.br/health", timeout=10)
    print(f"   Status: {health_response.status_code}")
    if health_response.status_code == 200:
        print(f"   Response: {health_response.json()}")
        print("   ✅ Backend está funcionando")
    else:
        print("   ❌ Backend não está respondendo corretamente")
except Exception as e:
    print(f"   ❌ Erro ao acessar backend: {e}")

print()

# 2. Testar CORS preflight para requisições do frontend
print("2. Testando CORS preflight (OPTIONS):")
cors_headers = {
    "Origin": "https://dashbord.urbanmt.com.br",
    "Access-Control-Request-Method": "DELETE",
    "Access-Control-Request-Headers": "content-type"
}

try:
    options_response = requests.options(
        "https://fastapi.urbanmt.com.br/api/financeiro/gastos/123456",
        headers=cors_headers,
        timeout=10
    )
    print(f"   Status: {options_response.status_code}")
    
    cors_headers_response = {}
    for key, value in options_response.headers.items():
        if 'access-control' in key.lower():
            cors_headers_response[key] = value
    
    if cors_headers_response:
        print("   Headers CORS na resposta:")
        for key, value in cors_headers_response.items():
            print(f"     {key}: {value}")
        
        # Verificar se permite o domínio do frontend
        allowed_origin = cors_headers_response.get('Access-Control-Allow-Origin', '')
        if 'dashbord.urbanmt.com.br' in allowed_origin or allowed_origin == '*':
            print("   ✅ CORS configurado corretamente para o frontend")
        else:
            print(f"   ⚠️  CORS pode ter problema - Origin permitida: {allowed_origin}")
    else:
        print("   ❌ Nenhum header CORS encontrado")
        
except Exception as e:
    print(f"   ❌ Erro no teste CORS: {e}")

print()

# 3. Testar uma requisição DELETE real (simular o que o frontend faria)
print("3. Testando requisição DELETE (simulando frontend):")
delete_headers = {
    "Content-Type": "application/json",
    "Origin": "https://dashbord.urbanmt.com.br"
}

try:
    # Usar um ID que provavelmente não existe para não afetar dados reais
    delete_response = requests.delete(
        "https://fastapi.urbanmt.com.br/api/financeiro/gastos/999999999",
        headers=delete_headers,
        timeout=10
    )
    print(f"   Status: {delete_response.status_code}")
    print(f"   Response: {delete_response.text[:200]}...")
    
    if delete_response.status_code == 404:
        print("   ✅ Endpoint funcionando (404 = gasto não encontrado é esperado)")
    elif delete_response.status_code == 200:
        print("   ✅ Endpoint funcionando (deletou com sucesso)")
    elif delete_response.status_code >= 500:
        print("   ❌ Erro interno do servidor")
    else:
        print(f"   ⚠️  Status inesperado: {delete_response.status_code}")
        
except Exception as e:
    print(f"   ❌ Erro na requisição DELETE: {e}")

print()
print("=== DIAGNÓSTICO ===")
print("✅ Se todos os testes passaram, o problema foi resolvido!")
print("❌ Se algum teste falhou, ainda há configurações a ajustar.")
print()
print("PRÓXIMOS PASSOS:")
print("1. Deploy do frontend com as correções de API_URL")
print("2. Teste no ambiente real do usuário")
print("3. Verificação dos logs de produção se ainda houver problemas")