#!/usr/bin/env python3
"""
Teste do Reconhecimento de Usuário no Agente
Verifica se o agente consegue identificar e personalizar respostas com o nome do usuário
"""

import json
import requests
import time

# URL do endpoint
BASE_URL = "http://localhost:8001"
ENDPOINT = f"{BASE_URL}/v1/playground/agents/mobility-agent/runs"

def test_user_recognition():
    """Testa o reconhecimento do usuário pelo agente"""
    
    print("🧪 TESTE: Reconhecimento de Usuário no Chat")
    print("=" * 50)
    
    # Casos de teste
    test_cases = [
        {
            "name": "Usuário Identificado - João",
            "payload": {
                "message": "Olá, como você está?",
                "user_id": "joao123",
                "user_name": "João Silva",
                "session_id": f"test_session_joao_{int(time.time())}"
            },
            "expected_keywords": ["João", "joão silva", "olá joão"]
        },
        {
            "name": "Usuária Identificada - Maria",
            "payload": {
                "message": "Preciso de uma análise de dados",
                "user_id": "maria456", 
                "user_name": "Maria Santos",
                "session_id": f"test_session_maria_{int(time.time())}"
            },
            "expected_keywords": ["Maria", "maria santos", "olá maria"]
        },
        {
            "name": "Usuário Sem Nome",
            "payload": {
                "message": "Como está o desempenho da empresa?",
                "user_id": "anonymous789",
                "session_id": f"test_session_anon_{int(time.time())}"
            },
            "expected_keywords": ["olá", "como posso ajudar"]
        }
    ]
    
    results = []
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📋 Teste {i}: {test_case['name']}")
        print(f"💬 Mensagem: {test_case['payload']['message']}")
        print(f"👤 Usuário: {test_case['payload'].get('user_name', 'Sem nome')}")
        
        try:
            # Fazer requisição
            response = requests.post(ENDPOINT, json=test_case['payload'], timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                agent_response = data.get('content', data.get('result', data.get('message', '')))
                
                print(f"✅ Status: {response.status_code}")
                print(f"🤖 Resposta do Agente:")
                print(f"   {agent_response[:200]}...")
                
                # Verificar se resposta contém personalização esperada
                response_lower = agent_response.lower()
                personalized = any(keyword.lower() in response_lower 
                                 for keyword in test_case.get('expected_keywords', []))
                
                if test_case.get('user_name') and personalized:
                    print("🎯 ✅ PERSONALIZAÇÃO DETECTADA!")
                    result_status = "SUCESSO - Personalizado"
                elif not test_case.get('user_name'):
                    print("🔍 ✅ RESPOSTA GENÉRICA (Esperado)")
                    result_status = "SUCESSO - Genérico"
                else:
                    print("⚠️  PERSONALIZAÇÃO NÃO DETECTADA")
                    result_status = "FALHA - Não personalizado"
                
                results.append({
                    "test": test_case['name'],
                    "status": result_status,
                    "response_preview": agent_response[:100]
                })
                
            else:
                print(f"❌ Erro HTTP: {response.status_code}")
                print(f"   {response.text}")
                results.append({
                    "test": test_case['name'],
                    "status": f"ERRO HTTP {response.status_code}",
                    "response_preview": response.text[:100]
                })
                
        except Exception as e:
            print(f"❌ Erro na requisição: {e}")
            results.append({
                "test": test_case['name'],
                "status": f"ERRO: {str(e)}",
                "response_preview": ""
            })
        
        # Aguardar entre testes
        time.sleep(2)
    
    # Sumário dos resultados
    print("\n" + "="*50)
    print("📊 RESUMO DOS TESTES")
    print("="*50)
    
    success_count = sum(1 for r in results if "SUCESSO" in r['status'])
    
    for result in results:
        status_emoji = "✅" if "SUCESSO" in result['status'] else "❌"
        print(f"{status_emoji} {result['test']}: {result['status']}")
    
    print(f"\n🎯 Taxa de Sucesso: {success_count}/{len(results)} ({success_count/len(results)*100:.1f}%)")
    
    return results

def test_endpoint_health():
    """Testa se o endpoint está funcionando"""
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Endpoint saudável!")
            return True
        else:
            print(f"⚠️ Endpoint retornou: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erro ao conectar: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Iniciando Teste de Reconhecimento de Usuário")
    print(f"🔗 URL: {ENDPOINT}")
    
    # Verificar saúde do endpoint
    if not test_endpoint_health():
        print("💡 Certifique-se de que o servidor esteja rodando:")
        print("   cd agente && python mobility_playground.py")
        exit(1)
    
    # Executar testes
    results = test_user_recognition()
    
    print("\n🏁 Teste concluído!")
