"""
🔥 TESTE FINAL: Verificar se a correção do Toolkit funcionou
"""

import os
import sys
sys.path.append('.')

# Testar importação das ferramentas corrigidas
try:
    from agente.dashboard_agent.tools.dashboard_api_tools import DashboardAPITools
    from agente.dashboard_agent.tools.business_analysis_tools import BusinessAnalysisTools
    print("✅ Importação das ferramentas: SUCESSO")
except Exception as e:
    print(f"❌ Erro na importação: {e}")
    # Tentar caminho alternativo
    try:
        sys.path.append('./agente')
        from dashboard_agent.tools.dashboard_api_tools import DashboardAPITools
        from dashboard_agent.tools.business_analysis_tools import BusinessAnalysisTools
        print("✅ Importação das ferramentas (caminho alternativo): SUCESSO")
    except Exception as e2:
        print(f"❌ Erro na importação alternativa: {e2}")
        sys.exit(1)

def test_corrected_tools():
    """Testa se as ferramentas agora são detectadas corretamente"""
    
    print("🧪 TESTE DAS FERRAMENTAS CORRIGIDAS")
    
    # Criar instâncias das ferramentas
    print("\n1. Criando DashboardAPITools...")
    dashboard_tools = DashboardAPITools(base_url="https://fastapi.urbanmt.com.br")
    
    print("\n2. Criando BusinessAnalysisTools...")
    business_tools = BusinessAnalysisTools()
    
    # Verificar se as ferramentas foram registradas corretamente
    print(f"\n3. DashboardAPITools tem {len(dashboard_tools.tools)} ferramentas registradas")
    for tool in dashboard_tools.tools:
        print(f"   - {tool.__name__}")
    
    print(f"\n4. BusinessAnalysisTools tem {len(business_tools.tools)} ferramentas registradas")
    for tool in business_tools.tools:
        print(f"   - {tool.__name__}")
    
    # Teste rápido de uma ferramenta
    print(f"\n5. Testando get_drivers_overview diretamente...")
    try:
        result = dashboard_tools.get_drivers_overview()
        if "active_drivers" in result:
            print("   ✅ Ferramenta funciona corretamente!")
            print(f"   📊 Resultado: {result[:100]}...")
        else:
            print("   ⚠️ Resultado inesperado")
    except Exception as e:
        print(f"   ❌ Erro: {e}")

if __name__ == "__main__":
    test_corrected_tools()
