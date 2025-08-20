"""
🧪 TESTE SIMPLES PARA VERIFICAR SE O AGENTE USA FERRAMENTAS
"""

import os
import sys
sys.path.append('.')

from dashboard_agent import MobilityDashboardAgent

def test_agent_tools():
    print("🧪 Testando se o agente usa ferramentas...")
    
    # Configurar agente local com debug
    agent = MobilityDashboardAgent(
        dashboard_url="https://fastapi.urbanmt.com.br",
        openai_api_key=os.getenv("OPENAI_API_KEY", "fake-key-for-test")
    )
    
    print("\n📋 Pergunta de teste: 'quantos motoristas temos?'")
    
    try:
        # Esta deveria FORÇAR o uso de get_drivers_overview()
        response = agent.interactive_analysis("quantos motoristas temos?")
        print(f"\n📤 Resposta do agente:")
        print(response)
        
        # Verificar se a resposta contém dados reais
        if "18" in response or "20" in response:
            print("\n✅ SUCESSO: Agente usou dados reais!")
        elif "150" in response or "não tenho acesso" in response:
            print("\n❌ FALHA: Agente ainda está inventando ou não usando ferramentas")
        else:
            print("\n⚠️ INCERTO: Resposta inesperada")
            
    except Exception as e:
        print(f"\n❌ ERRO: {e}")
        
    print("\n" + "="*50)

if __name__ == "__main__":
    test_agent_tools()
