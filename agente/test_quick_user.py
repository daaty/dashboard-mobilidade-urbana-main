#!/usr/bin/env python3
"""
Teste rápido do reconhecimento de usuário
"""

import json
import requests

# URL do endpoint
ENDPOINT = "http://localhost:8001/v1/playground/agents/mobility-agent/runs"

def test_user_recognition_simple():
    """Teste simples do reconhecimento"""
    
    print("=== TESTE RECONHECIMENTO DE USUÁRIO ===")
    
    payload = {
        "message": "ola",
        "user_id": "daath1",
        "user_name": "daath1",
        "session_id": "test_session_123"
    }
    
    print(f"Enviando: {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(ENDPOINT, json=payload, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            agent_response = data.get('content', data.get('result', data.get('message', '')))
            
            print(f"\nStatus: {response.status_code}")
            print(f"Resposta do agente:")
            print(f"'{agent_response}'")
            
            # Verificar se contém o nome
            if 'daath1' in agent_response.lower():
                print("\n✅ RECONHECIMENTO FUNCIONANDO!")
            else:
                print("\n❌ Nome não encontrado na resposta")
                
        else:
            print(f"❌ Erro HTTP: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    test_user_recognition_simple()
