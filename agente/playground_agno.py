"""
🎮 PLAYGROUND OFICIAL DO AGNO
Usa o CLI nativo do framework AGNO para interagir com o agente
"""

import os
import sys
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

# Adicionar o diretório dashboard_agent ao path
sys.path.append(os.path.join(os.path.dirname(__file__), "dashboard_agent"))

try:
    from dashboard_agent.mobility_agent import MobilityDashboardAgent
    
    print("🚀 PLAYGROUND OFICIAL DO AGNO")
    print("=" * 40)
    print("📋 Comandos disponíveis:")
    print("  - Digite suas perguntas normalmente")
    print("  - 'exit' ou 'quit' para sair")
    print("  - 'help' para ver comandos do agente")
    print("=" * 40)
    
    # Criar agente
    dashboard_url = os.getenv("DASHBOARD_URL", "https://fastapi.urbanmt.com.br")
    print(f"🔗 Dashboard URL: {dashboard_url}")
    
    agente = MobilityDashboardAgent(
        dashboard_url=dashboard_url,
        openai_api_key=os.getenv("OPENAI_API_KEY"),
        memory_db_url=os.getenv("MEMORY_DB_URL")
    )
    
    print("✅ Agente inicializado com sucesso!")
    
    # Verificar ferramentas disponíveis de forma segura
    try:
        tools_count = len(agente.tools) if hasattr(agente, 'tools') and agente.tools else 0
        print(f"🛠️ Ferramentas disponíveis: {tools_count} tools")
    except:
        print("🛠️ Ferramentas: Carregadas via toolkits")
    
    print("\n🎯 Iniciando playground oficial do AGNO...\n")
    
    # Usar o playground oficial do AGNO
    agente.agent.cli_app(
        user="Admin",
        emoji="🚗",
        stream=True,
        markdown=True
    )
    
except ImportError as e:
    print(f"❌ Erro ao importar agente: {e}")
    print("Certifique-se de que o AGNO está instalado: pip install agno")
except Exception as e:
    print(f"❌ Erro: {e}")
