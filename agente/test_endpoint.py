#!/usr/bin/env python3
"""
🧪 SCRIPT DE TESTE PARA ENDPOINT DO AGNO
Testa o endpoint /v1/playground/agents/{agent_id}/runs
"""

import requests
import json
import time

# Configurações
BASE_URL = "http://localhost:8001"
AGENT_ID = "test-agent-123"
ENDPOINT = f"{BASE_URL}/v1/playground/agents/{AGENT_ID}/runs"

def test_json_payload():
    """Testa com payload JSON (formato esperado)"""
    print("🧪 Testando com JSON payload...")
    
    payload = {
        "message": "Hello, what's your special skill?",
        "user_id": "test_user",
        "session_id": "test_session_123",
        "stream": False
    }
    
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    try:
        response = requests.post(ENDPOINT, json=payload, headers=headers, timeout=30)
        print(f"✅ Status Code: {response.status_code}")
        print(f"📄 Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            print(f"🎉 Sucesso! Resposta: {response.json()}")
        else:
            print(f"❌ Erro: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"🔌 Erro de conexão: {e}")

def test_form_data_payload():
    """Testa com form-data (formato do AGNO)"""
    print("\n🧪 Testando com Form Data (formato AGNO)...")
    
    form_data = {
        "message": "Hello, what's your special skill?",
        "user_id": "test_user_agno",
        "session_id": "test_session_agno_123",
        "stream": "true",
        "monitor": "true"
    }
    
    try:
        response = requests.post(ENDPOINT, data=form_data, timeout=30)
        print(f"✅ Status Code: {response.status_code}")
        print(f"📄 Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            print(f"🎉 Sucesso! Resposta: {response.json()}")
        else:
            print(f"❌ Erro: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"🔌 Erro de conexão: {e}")

def test_empty_payload():
    """Testa com payload vazio (deve dar erro 422)"""
    print("\n🧪 Testando com payload vazio...")
    
    try:
        response = requests.post(ENDPOINT, json={}, timeout=30)
        print(f"✅ Status Code: {response.status_code}")
        print(f"📄 Resposta: {response.text}")
        
    except requests.exceptions.RequestException as e:
        print(f"🔌 Erro de conexão: {e}")

def test_server_status():
    """Verifica se o servidor está rodando"""
    print("🔍 Verificando status do servidor...")
    
    try:
        response = requests.get(f"{BASE_URL}/v1/playground/status", timeout=5)
        if response.status_code == 200:
            print("✅ Servidor está rodando!")
            return True
        else:
            print(f"⚠️ Servidor respondeu com status {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Servidor não está acessível: {e}")
        return False

def main():
    print("🚀 INICIANDO TESTES DO ENDPOINT AGNO")
    print("=" * 50)
    
    # Verifica se o servidor está rodando
    if not test_server_status():
        print("❌ Servidor não está acessível. Execute primeiro: python mobility_playground.py")
        return
    
    print(f"\n🎯 Endpoint: {ENDPOINT}")
    print("=" * 50)
    
    # Teste 1: JSON
    test_json_payload()
    
    # Aguarda um pouco
    time.sleep(1)
    
    # Teste 2: Form Data (AGNO)
    test_form_data_payload()
    
    # Aguarda um pouco
    time.sleep(1)
    
    # Teste 3: Payload vazio
    test_empty_payload()
    
    print("\n🏁 TESTES CONCLUÍDOS!")

if __name__ == "__main__":
    main()
