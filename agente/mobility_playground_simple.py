"""
🎮 MOBILITY PLAYGROUND - VERSÃO COMPATÍVEL COM AGNO
Seguindo exatamente o padrão da documentação oficial do AGNO
"""

import os
import logging
from agno.playground import Playground
from agno.storage.sqlite import SqliteStorage

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Configurações
class MobilityConfig:
    DASHBOARD_URL = "https://fastapi.urbanmt.com.br"
    DATABASE_PATH = "tmp/agents.db"

# Import do agente
try:
    from main import mobility_agent
    if mobility_agent is None:
        logging.error("❌ mobility_agent importado como None")
        exit(1)
    logging.info("✅ Agente de mobilidade importado com sucesso!")
    logging.info(f"🔍 Tipo do agente: {type(mobility_agent)}")
except ImportError as e:
    logging.error(f"❌ Erro ao importar agente: {e}")
    exit(1)

# Configuração de storage para o agente (só se necessário)
agent_storage = SqliteStorage(
    table_name="mobility_agent", 
    db_file=MobilityConfig.DATABASE_PATH
)

# Atualiza o agente com storage se necessário
try:
    if not hasattr(mobility_agent, 'storage') or mobility_agent.storage is None:
        mobility_agent.storage = agent_storage
        logging.info("🗄️ Storage configurado para o agente")
except Exception as e:
    logging.warning(f"⚠️ Não foi possível configurar storage: {e}")
    # Continua sem storage - não é crítico

# Cria o playground seguindo o padrão AGNO
playground_app = Playground(agents=[mobility_agent])
app = playground_app.get_app()

if __name__ == "__main__":
    # Cria diretório para database
    os.makedirs("tmp", exist_ok=True)
    
    port = int(os.getenv("PORT", 7777))  # Porta padrão do AGNO
    
    logging.info(f"🚀 Iniciando Mobility Playground AGNO na porta {port}")
    logging.info(f"🔗 Dashboard URL: {MobilityConfig.DASHBOARD_URL}")
    logging.info(f"🎯 Endpoint AGNO: http://localhost:{port}/v1")
    logging.info(f"📊 Use no AGNO playground: localhost:{port}/v1")
    
    # Usa o método serve padrão do AGNO
    playground_app.serve("mobility_playground_simple:app", host="0.0.0.0", port=port, reload=False)
