"""
🧪 TESTE DAS FERRAMENTAS ATUALIZADAS
Script para testar todas as ferramentas do agente
"""

import requests
import json
import sys
import os

# Adicionar o diretório dashboard_agent ao path
sys.path.append(os.path.join(os.path.dirname(__file__), "dashboard_agent"))

from dashboard_agent.tools.dashboard_api_tools import DashboardAPITools
from dashboard_agent.tools.business_analysis_tools import BusinessAnalysisTools

def test_dashboard_tools():
    """Testa as ferramentas de API do dashboard"""
    print("🔧 TESTANDO DASHBOARD TOOLS")
    print("=" * 40)
    
    tools = DashboardAPITools(base_url="https://fastapi.urbanmt.com.br")
    
    # Teste 1: KPIs de motoristas
    print("🚗 Testando get_drivers_overview...")
    try:
        result = tools.get_drivers_overview()
        if "error" not in result.lower():
            print("✅ get_drivers_overview: OK")
            print(f"   Resultado: {result[:100]}...")
        else:
            print(f"❌ get_drivers_overview: {result}")
    except Exception as e:
        print(f"❌ get_drivers_overview: {e}")
    
    # Teste 2: Lista de motoristas
    print("\n📋 Testando get_drivers_list...")
    try:
        result = tools.get_drivers_list()
        if "error" not in result.lower():
            print("✅ get_drivers_list: OK")
            print(f"   Resultado: {result[:100]}...")
        else:
            print(f"❌ get_drivers_list: {result}")
    except Exception as e:
        print(f"❌ get_drivers_list: {e}")
    
    # Teste 3: Cidades disponíveis
    print("\n🏙️ Testando get_drivers_by_city (cidades)...")
    try:
        result = tools.get_drivers_by_city()  # Sem parâmetro = cidades
        if "error" not in result.lower():
            print("✅ get_drivers_by_city: OK")
            print(f"   Resultado: {result[:100]}...")
        else:
            print(f"❌ get_drivers_by_city: {result}")
    except Exception as e:
        print(f"❌ get_drivers_by_city: {e}")
    
    print(f"\n📊 RESUMO: DashboardAPITools tem {len(tools.tools)} ferramentas")
    for i, tool in enumerate(tools.tools):
        print(f"   🔧 {i+1}. {tool.__name__}")

def test_business_tools():
    """Testa as ferramentas de análise de negócio"""
    print("\n🧠 TESTANDO BUSINESS ANALYSIS TOOLS")
    print("=" * 40)
    
    tools = BusinessAnalysisTools()
    
    # Dados de teste
    test_data = {
        "metricas_principais": {
            "corridas_concluidas": 150,
            "corridas_canceladas": 25,
            "total_drivers": 50
        },
        "total_gastos": 5000,
        "media_gastos_dia": 166.67
    }
    
    # Teste 1: Cálculo de KPIs
    print("📊 Testando calculate_business_kpis...")
    try:
        result = tools.calculate_business_kpis(json.dumps(test_data))
        if "kpis_calculados" in result:
            print("✅ calculate_business_kpis: OK")
            kpis = json.loads(result)
            print(f"   KPIs calculados: {len(kpis.get('kpis_calculados', {}))}")
            print(f"   Alertas: {len(kpis.get('alertas_criticos', []))}")
        else:
            print(f"❌ calculate_business_kpis: {result}")
    except Exception as e:
        print(f"❌ calculate_business_kpis: {e}")
    
    # Teste 2: Análise financeira
    print("\n💰 Testando financial_health_check...")
    try:
        result = tools.financial_health_check(json.dumps(test_data))
        if "score_saude_financeira" in result:
            print("✅ financial_health_check: OK")
            health = json.loads(result)
            print(f"   Score: {health.get('score_saude_financeira', 'N/A')}")
        else:
            print(f"❌ financial_health_check: {result}")
    except Exception as e:
        print(f"❌ financial_health_check: {e}")
    
    print(f"\n📊 RESUMO: BusinessAnalysisTools tem {len(tools.tools)} ferramentas")
    for i, tool in enumerate(tools.tools):
        print(f"   🧠 {i+1}. {tool.__name__}")

def test_playground_connection():
    """Testa se o playground está respondendo"""
    print("\n🎮 TESTANDO CONEXÃO COM PLAYGROUND")
    print("=" * 40)
    
    try:
        response = requests.get("http://localhost:8002/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("✅ Playground online")
            print(f"   Status: {data.get('status', 'N/A')}")
            print(f"   Agent ready: {data.get('agent_ready', 'N/A')}")
        else:
            print(f"❌ Playground não está respondendo: {response.status_code}")
    except Exception as e:
        print(f"❌ Erro ao conectar com playground: {e}")

if __name__ == "__main__":
    print("🧪 TESTE COMPLETO DAS FERRAMENTAS")
    print("=" * 50)
    
    test_dashboard_tools()
    test_business_tools()
    test_playground_connection()
    
    print("\n✅ Teste concluído!")
