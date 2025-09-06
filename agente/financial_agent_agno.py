"""
🤖 ALICE-FINANCEIRA AGNO - Agente Inteligente usando Framework AGNO
Inspirado no cookbook do AGNO para agentes conversacionais com ferramentas
"""

import os
import sys
from pathlib import Path
from typing import Dict, Any, Optional, List
import logging
import json

# Adicionar caminho do AGNO
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "agno", "libs", "agno"))

from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.storage.postgres import PostgresStorage
from agno.memory.v2.db.postgres import PostgresMemoryDb
from agno.memory.v2.memory import Memory
from agno.tools.reasoning import ReasoningTools

# Nossas ferramentas financeiras
sys.path.append(os.path.join(os.path.dirname(__file__), "dashboard_agent"))
from dashboard_agent.tools.financial_tools import FinancialTools

from dotenv import load_dotenv
load_dotenv()

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FinancialAgentAGNO:
    """🧠 Alice-Financeira - Agente AGNO Inteligente"""
    
    def __init__(self):
        """Inicializa o agente AGNO com todas as capacidades"""
        logger.info("🚀 Inicializando Alice-Financeira AGNO...")
        
        # Configurar storage e memória PostgreSQL
        self.setup_storage()
        
        # Criar agente AGNO com capabilities avançadas
        self.agent = Agent(
            model=OpenAIChat(
                id="gpt-4o-mini",
                api_key=os.getenv("OPENAI_API_KEY")
            ),
            
            # 🧰 FERRAMENTAS INTELIGENTES
            tools=[
                ReasoningTools(add_instructions=True),  # Raciocínio estruturado
                FinancialTools(),  # Nossas ferramentas financeiras
            ],
            
            # 🧠 INSTRUÇÕES INTELIGENTES
            instructions=self.get_intelligent_instructions(),
            
            # 💾 MEMÓRIA PERSISTENTE
            storage=self.storage,
            memory=self.memory,
            
            # 🎯 CONFIGURAÇÕES AVANÇADAS
            reasoning=True,  # Habilita raciocínio estruturado
            markdown=True,   # Respostas em markdown
            show_tool_calls=True,  # Mostra processo de pensamento
            use_json_mode=False,   # Respostas conversacionais
            
            # 🔧 META-DADOS
            name="Alice-Financeira",
            role="Assistente Financeira Inteligente",
            
            # 📝 CONFIGURAÇÕES DE CONVERSA
            add_history_to_messages=True,
            num_history_responses=10,
        )
        
        logger.info("✅ Alice-Financeira AGNO inicializada com sucesso!")
    
    def setup_storage(self):
        """Configura storage PostgreSQL para memória persistente"""
        try:
            # Configurar PostgreSQL Storage para dados do agente
            self.storage = PostgresStorage(
                table_name="financial_agent_storage",
                db_url="postgresql://n8n_user:n8n_pw@148.230.73.27:5432/n8n_db"
            )
            
            # Configurar Memória PostgreSQL
            memory_db = PostgresMemoryDb(
                db_url="postgresql://n8n_user:n8n_pw@148.230.73.27:5432/n8n_db",
                schema_name="agno_financial_memory"
            )
            
            self.memory = Memory(
                db=memory_db,
                create_user_memories=True,
                create_session_memories=True,
                update_memories_after_run=True,
            )
            
            logger.info("✅ Storage e memória PostgreSQL configurados")
            
        except Exception as e:
            logger.warning(f"⚠️ Erro no PostgreSQL, usando memória local: {e}")
            self.storage = None
            self.memory = None
    
    def get_intelligent_instructions(self) -> List[str]:
        """📋 Instruções inteligentes para o agente AGNO"""
        return [
            # 🎯 IDENTIDADE E PERSONALIDADE
            "🤖 Você é Alice-Financeira, uma assistente inteligente especializada em gestão financeira empresarial.",
            "💡 Seja natural, conversacional e proativa. Nunca robótica ou seguindo scripts.",
            "🧠 Use seu raciocínio estruturado para analisar situações antes de agir.",
            "",
            
            # 🔄 FLUXOS INTELIGENTES
            "📊 ANÁLISE DE CONTEXTO (sempre usar reasoning_tools):",
            "- Antes de qualquer ação, ANALISE o contexto usando think()",
            "- Identifique se é: cumprimento, pergunta, registro de gasto, ou conversa geral",
            "- Determine a melhor abordagem baseada no contexto e histórico",
            "",
            
            # 💰 GESTÃO FINANCEIRA INTELIGENTE
            "💰 PARA CONSULTAS FINANCEIRAS:",
            "- Use analyze() para entender exatamente o que o usuário quer",
            "- Execute as ferramentas financeiras apropriadas",
            "- Formate respostas de forma clara e acionável",
            "- Ofereça insights e próximos passos",
            "",
            
            # 📸 REGISTRO DE DOCUMENTOS
            "📸 PARA REGISTRO DE GASTOS:",
            "- Quando receber dados de imagem (JSON com webContentLink), use think() primeiro",
            "- Processe automaticamente usando FinancialTools.inserir_gasto_empresa",
            "- Colete informações adicionais de forma conversacional",
            "- Mantenha contexto durante todo o processo",
            "",
            
            # 🗣️ CONVERSAÇÃO NATURAL
            "🗣️ CONVERSAÇÃO INTELIGENTE:",
            "- Cumprimentos: seja calorosa e apresente suas capacidades",
            "- Perguntas: entenda o contexto antes de responder",
            "- Confirmações: seja positiva e ofereça próximos passos",
            "- Despedidas: seja gentil e lembre das suas capacidades",
            "",
            
            # 🧠 RACIOCÍNIO ESTRUTURADO
            "🧠 SEMPRE USE REASONING:",
            "- think() antes de ações importantes",
            "- analyze() para processar dados complexos",
            "- plan() para fluxos multi-etapa",
            "- reflect() após completar tarefas",
            "",
            
            # 📈 VALOR AGREGADO
            "📈 SEJA PROATIVA:",
            "- Ofereça insights baseados nos dados",
            "- Sugira melhorias nos processos",
            "- Antecipe necessidades do usuário",
            "- Eduque sobre melhores práticas financeiras",
            "",
            
            # ⚡ EFICIÊNCIA
            "⚡ OTIMIZAÇÃO:",
            "- Use memória para lembrar preferências do usuário",
            "- Evite perguntas repetitivas",
            "- Mantenha contexto entre interações",
            "- Aprenda com cada conversa",
        ]
    
    async def process_message(self, user_name: str, user_message: str, 
                            previous_gasto_id: Optional[str] = None) -> Dict[str, Any]:
        """🎯 Processa mensagem usando inteligência AGNO"""
        
        try:
            # Criar contexto estruturado para o agente
            context = {
                "user_name": user_name,
                "message": user_message,
                "previous_gasto_id": previous_gasto_id,
                "timestamp": "now"
            }
            
            # Construir prompt contextual para o agente AGNO
            if previous_gasto_id:
                prompt = f"""
💬 **Continuação de Registro Financeiro**

👤 **Usuário:** {user_name}
🆔 **Gasto ID:** {previous_gasto_id}
💭 **Mensagem:** {user_message}

**Contexto:** O usuário está respondendo sobre um registro de gasto em andamento.
"""
            else:
                prompt = f"""
💬 **Nova Interação Financeira**

👤 **Usuário:** {user_name}
💭 **Mensagem:** {user_message}

**Contexto:** Nova conversa ou consulta financeira.
"""
            
            # Processar com o agente AGNO
            logger.info(f"🧠 Alice-AGNO processando: {user_name} disse '{user_message}'")
            
            response = self.agent.run(
                prompt,
                session_id=f"financial_session_{user_name}",
                user_id=user_name
            )
            
            # Extrair resposta do agente
            agent_response = response.content if hasattr(response, 'content') else str(response)
            
            # Estruturar resposta para o endpoint
            return {
                "success": True,
                "message": agent_response,
                "gasto_id": self._extract_gasto_id_from_response(agent_response),
                "data": {
                    "user": user_name,
                    "agent_type": "agno_intelligent",
                    "reasoning_used": True,
                    "session_id": f"financial_session_{user_name}"
                },
                "error": None
            }
            
        except Exception as e:
            logger.error(f"❌ Erro no agente AGNO: {e}")
            return {
                "success": False,
                "message": f"Desculpe {user_name}, tive um problema técnico. Pode tentar novamente?",
                "error": str(e)
            }
    
    def _extract_gasto_id_from_response(self, response: str) -> Optional[str]:
        """Extrai ID do gasto da resposta do agente"""
        import re
        match = re.search(r'ID:?\s*(\d+)', response)
        return match.group(1) if match else None

# Instância global do agente
_financial_agent_instance = None

def get_financial_agent() -> FinancialAgentAGNO:
    """🔧 Factory para obter instância do agente (singleton)"""
    global _financial_agent_instance
    
    if _financial_agent_instance is None:
        _financial_agent_instance = FinancialAgentAGNO()
    
    return _financial_agent_instance

# Função principal para usar no endpoint
async def process_with_agno_agent(user_name: str, user_message: str, 
                                 previous_gasto_id: Optional[str] = None) -> Dict[str, Any]:
    """🎯 Interface principal para o endpoint financeiro"""
    agent = get_financial_agent()
    return await agent.process_message(user_name, user_message, previous_gasto_id)


if __name__ == "__main__":
    """🧪 Teste do agente AGNO"""
    import asyncio
    
    async def test_agent():
        print("🧪 Testando Alice-Financeira AGNO...")
        
        # Teste 1: Cumprimento
        result1 = await process_with_agno_agent("Wesley", "ola!")
        print(f"✅ Cumprimento: {result1['message'][:100]}...")
        
        # Teste 2: Consulta financeira
        result2 = await process_with_agno_agent("Wesley", "quais foram meus últimos gastos?")
        print(f"✅ Consulta: {result2['message'][:100]}...")
        
        print("🎯 Testes concluídos!")
    
    asyncio.run(test_agent())
