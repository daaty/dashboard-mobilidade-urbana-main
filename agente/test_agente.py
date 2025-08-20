"""
🧪 TESTE DO AGENTE INTELIGENTE
Script para testar a API do agente localmente e em produção
"""

import requests
import json
import os
from datetime import datetime

def testar_agente_local():
    """Testa agente rodando localmente"""
    print("🏠 TESTANDO AGENTE LOCAL")
    print("=" * 40)
    
    base_url = "http://localhost:8001"
    
    # Teste de health check
    try:
        response = requests.get(f"{base_url}/health", timeout=10)
        if response.status_code == 200:
            print("✅ Health check OK")
            print(f"   Status: {response.json()}")
        else:
            print(f"❌ Health check falhou: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Erro de conexão: {e}")
        print("💡 Certifique-se que o agente está rodando: python main.py")
        return False
    
    # Teste de análise rápida
    try:
        print("\n📊 Testando análise de performance...")
        response = requests.post(f"{base_url}/analyze", 
            json={"analysis_type": "performance", "parameters": {}},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Análise executada com sucesso!")
            print(f"   Resultado: {result['result'][:100]}...")
        else:
            print(f"❌ Análise falhou: {response.status_code}")
            print(f"   Erro: {response.text}")
    except requests.exceptions.Timeout:
        print("⏱️ Timeout na análise (normal para primeira execução)")
    except Exception as e:
        print(f"❌ Erro na análise: {e}")
    
    # Teste de pergunta interativa
    try:
        print("\n🤔 Testando pergunta interativa...")
        response = requests.post(f"{base_url}/ask",
            json={"question": "Qual é o status atual do sistema?"},
            timeout=20
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Pergunta processada com sucesso!")
            print(f"   Resposta: {result['result'][:100]}...")
        else:
            print(f"❌ Pergunta falhou: {response.status_code}")
    except requests.exceptions.Timeout:
        print("⏱️ Timeout na pergunta (normal para primeira execução)")
    except Exception as e:
        print(f"❌ Erro na pergunta: {e}")
    
    return True

def testar_agente_producao():
    """Testa agente em produção no Heroku"""
    print("\n🌐 TESTANDO AGENTE EM PRODUÇÃO")
    print("=" * 40)
    
    base_url = "https://dashboard-mobility-agent.herokuapp.com"
    
    # Teste de health check
    try:
        response = requests.get(f"{base_url}/health", timeout=30)
        if response.status_code == 200:
            print("✅ Health check OK")
            data = response.json()
            print(f"   Status: {data.get('status')}")
            print(f"   Agent Ready: {data.get('agent_ready')}")
        else:
            print(f"❌ Health check falhou: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Erro de conexão: {e}")
        print("💡 Verifique se o app está deployado e ativo")
        return False
    
    # Teste de status detalhado
    try:
        print("\n🔍 Verificando status detalhado...")
        response = requests.get(f"{base_url}/status", timeout=15)
        if response.status_code == 200:
            status = response.json()
            print("✅ Status obtido:")
            print(f"   Agente inicializado: {status.get('agent_initialized')}")
            env = status.get('environment', {})
            print(f"   Dashboard URL: {env.get('dashboard_url')}")
            print(f"   OpenAI configurado: {env.get('openai_configured')}")
            print(f"   Memória configurada: {env.get('memory_configured')}")
        else:
            print(f"❌ Status falhou: {response.status_code}")
    except Exception as e:
        print(f"❌ Erro no status: {e}")
    
    # Teste de análises disponíveis
    try:
        print("\n📋 Verificando análises disponíveis...")
        response = requests.get(f"{base_url}/available-analyses", timeout=10)
        if response.status_code == 200:
            analyses = response.json()
            print("✅ Análises disponíveis:")
            for key, info in analyses.items():
                print(f"   - {key}: {info['name']}")
        else:
            print(f"❌ Lista de análises falhou: {response.status_code}")
    except Exception as e:
        print(f"❌ Erro na lista: {e}")
    
    return True

def testar_integracao_dashboard():
    """Testa integração com dashboard principal"""
    print("\n🔗 TESTANDO INTEGRAÇÃO COM DASHBOARD")
    print("=" * 40)
    
    # Testar endpoint local do dashboard
    dashboard_url = "http://localhost:8000"
    
    try:
        response = requests.get(f"{dashboard_url}/api/rides/overview", timeout=10)
        if response.status_code == 200:
            print("✅ Dashboard local acessível")
            data = response.json()
            print(f"   Total corridas: {data.get('total_rides', 'N/A')}")
        else:
            print(f"⚠️ Dashboard local não acessível: {response.status_code}")
    except Exception as e:
        print(f"⚠️ Dashboard local não disponível: {e}")
    
    # Testar endpoint de produção
    dashboard_prod = "https://dashboard-mobilidade-urbana-main-4e5d29b0c6cb.herokuapp.com"
    
    try:
        response = requests.get(f"{dashboard_prod}/api/rides/overview", timeout=15)
        if response.status_code == 200:
            print("✅ Dashboard produção acessível")
            data = response.json()
            print(f"   Total corridas: {data.get('total_rides', 'N/A')}")
        else:
            print(f"⚠️ Dashboard produção não acessível: {response.status_code}")
    except Exception as e:
        print(f"⚠️ Dashboard produção não disponível: {e}")

def main():
    """Função principal de teste"""
    print("🧪 TESTE COMPLETO DO AGENTE INTELIGENTE")
    print("=" * 50)
    print(f"⏰ Timestamp: {datetime.now()}")
    print()
    
    # Menu de opções
    print("Escolha o que testar:")
    print("1. 🏠 Agente Local (localhost:8001)")
    print("2. 🌐 Agente Produção (Heroku)")
    print("3. 🔗 Integração com Dashboard")
    print("4. 🧪 Todos os testes")
    print("5. 🚪 Sair")
    
    opcao = input("\nDigite sua escolha (1-5): ").strip()
    
    if opcao == "1":
        testar_agente_local()
    elif opcao == "2":
        testar_agente_producao()
    elif opcao == "3":
        testar_integracao_dashboard()
    elif opcao == "4":
        testar_agente_local()
        testar_agente_producao()
        testar_integracao_dashboard()
    elif opcao == "5":
        print("👋 Teste cancelado!")
        return
    else:
        print("❌ Opção inválida!")
        return
    
    print("\n🎯 TESTE CONCLUÍDO!")
    print("💡 Para mais detalhes, consulte os logs dos serviços")

if __name__ == "__main__":
    main()
