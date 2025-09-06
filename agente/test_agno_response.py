#!/usr/bin/env python3
"""
Teste específico para o formato de resposta do AGNO
"""
import requests
import json
import time

def test_agno_endpoint():
    """Testa o endpoint do AGNO e mostra a resposta completa"""
    
    url = "http://localhost:8001/v1/playground/agents/test-agent-123/runs"
    
    # Teste 1: JSON simples
    print("=== TESTE 1: JSON ===")
    try:
        json_data = {
            "message": "Hello, test response",
            "user_id": "test_user",
            "session_id": "test_session"
        }
        
        response = requests.post(
            url,
            json=json_data,
            headers={"Content-Type": "application/json"},
            timeout=15
        )
        
        print(f"Status: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            result = response.json()
            print("=== RESPOSTA JSON ===")
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            print(f"Erro: {response.text}")
            
    except Exception as e:
        print(f"Erro no teste JSON: {e}")
    
    print("\n" + "="*50 + "\n")
    
    # Teste 2: Form data (como AGNO envia)
    print("=== TESTE 2: FORM DATA ===")
    try:
        form_data = {
            "message": "Hello, form test",
            "user_id": "test_user",
            "session_id": "test_session",
            "stream": "false",
            "monitor": "false"
        }
        
        response = requests.post(
            url,
            data=form_data,
            timeout=15
        )
        
        print(f"Status: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            try:
                result = response.json()
                print("=== RESPOSTA JSON ===")
                print(json.dumps(result, indent=2, ensure_ascii=False))
            except:
                print("=== RESPOSTA TEXT ===")
                print(response.text)
        else:
            print(f"Erro: {response.text}")
            
    except Exception as e:
        print(f"Erro no teste form: {e}")

if __name__ == "__main__":
    print("🧪 Testando endpoint AGNO...")
    test_agno_endpoint()
    print("\n✅ Teste concluído!")
