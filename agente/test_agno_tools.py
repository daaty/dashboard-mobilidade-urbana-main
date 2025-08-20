"""
🧪 TESTE CRÍTICO: Verificar se AGNO está executando as ferramentas corretamente
"""

import os
import sys
sys.path.append('.')

from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools import Toolkit

# Configurar variáveis de ambiente  
openai_key = os.getenv("OPENAI_API_KEY")
if not openai_key:
    print("❌ ERRO: OPENAI_API_KEY não está configurada")
    sys.exit(1)
os.environ["OPENAI_API_KEY"] = openai_key

class SimpleTestTool(Toolkit):
    """Ferramenta simples para testar se AGNO executa corretamente"""
    
    def get_test_number(self) -> str:
        """
        Retorna um número específico para teste.
        
        Returns:
            O número 42 como string
        """
        print("🔥 [TEST_TOOL] get_test_number() FOI EXECUTADA!")
        return "42"
    
    def get_real_data(self) -> str:
        """
        Simula dados reais que o agente deveria usar.
        
        Returns:
            Dados específicos para teste
        """
        print("🔥 [TEST_TOOL] get_real_data() FOI EXECUTADA!")
        return "Dados reais: 18 motoristas ativos, 150 corridas este mês"

def test_agno_tools():
    """Teste para verificar se AGNO executa as ferramentas"""
    
    print("🧪 INICIANDO TESTE CRÍTICO DO AGNO")
    
    # Criar ferramenta de teste
    test_tool = SimpleTestTool()
    
    # Criar agente com instruções específicas
    agent = Agent(
        name="TestAgent",
        model=OpenAIChat(id="gpt-4o-mini"),
        tools=[test_tool],
        instructions="""
        Você DEVE usar suas ferramentas para responder perguntas.
        
        REGRAS OBRIGATÓRIAS:
        1. Para qualquer pergunta sobre números: use get_test_number()
        2. Para qualquer pergunta sobre dados: use get_real_data()
        3. JAMAIS invente respostas
        4. SEMPRE execute as ferramentas antes de responder
        """,
        show_tool_calls=True,
        markdown=False
    )
    
    print(f"✅ Agente criado com {len(agent.tools)} ferramenta(s)")
    
    # TESTE 1: Pergunta simples que deveria usar get_test_number()
    print("\n🔍 TESTE 1: Perguntando um número...")
    response1 = agent.run("Qual é o número de teste?")
    print(f"📤 Resposta: {response1}")
    
    # TESTE 2: Pergunta sobre dados que deveria usar get_real_data()
    print("\n🔍 TESTE 2: Perguntando sobre dados...")
    response2 = agent.run("Quantos motoristas temos?")
    print(f"📤 Resposta: {response2}")
    
    # TESTE 3: Verificar se o agente está realmente usando as ferramentas
    print("\n🔍 TESTE 3: Verificação direta...")
    response3 = agent.run("Use a ferramenta get_real_data e me diga exatamente o que ela retorna")
    print(f"📤 Resposta: {response3}")

if __name__ == "__main__":
    test_agno_tools()
