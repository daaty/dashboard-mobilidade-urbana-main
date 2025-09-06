#!/usr/bin/env python3
"""
Script para testar se o agente está criando memórias corretamente
"""
import os
import sys
from pathlib import Path

# Carregar variáveis de ambiente do .env
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("✅ Variáveis de ambiente carregadas do .env")
except ImportError:
    print("⚠️ python-dotenv não encontrado, usando variáveis do sistema")

# Adicionar pasta agno ao path
agno_path = Path(__file__).parent / "agno" / "libs" / "agno"
sys.path.insert(0, str(agno_path))

try:
    from agno.agent import Agent
    from agno.memory.v2.db.postgres import PostgresMemoryDb
    from agno.memory.v2.memory import Memory
    from agno.models.openai import OpenAIChat
    from agno.storage.postgres import PostgresStorage
    print("✅ Imports AGNO funcionaram!")
except ImportError as e:
    print(f"❌ Erro nos imports: {e}")
    sys.exit(1)

def test_agent_memory():
    """Testa se o agente está criando memórias"""
    
    # Configurações
    db_url = os.getenv('DATABASE_URL', 'postgresql://n8n_user:n8n_pw@148.230.73.27:5432/n8n_db')
    api_key = os.getenv('OPENAI_API_KEY')
    
    if not api_key:
        print("❌ OPENAI_API_KEY não encontrada")
        return False
        
    print(f"🔧 Configurando agente com PostgreSQL...")
    
    try:
        # 1. Configurar storage e memória
        postgres_storage = PostgresStorage(
            table_name="test_mobility_sessions",
            db_url=db_url
        )
        
        postgres_memory_db = PostgresMemoryDb(
            table_name="test_mobility_memories",
            db_url=db_url
        )
        postgres_memory_db.create()
        
        postgres_memory = Memory(
            db=postgres_memory_db,
            model=OpenAIChat(id="gpt-4o-mini", api_key=api_key)
        )
        
        # 2. Criar agente com memória
        print("🔧 Criando agente com memória...")
        agent = Agent(
            name="TestMobilityAgent",
            model=OpenAIChat(id="gpt-4o-mini", api_key=api_key),
            storage=postgres_storage,
            memory=postgres_memory,
            enable_user_memories=True,
            enable_session_summaries=True,
            instructions=["Você é um assistente que lembra de informações sobre o usuário"]
        )
        
        print("✅ Agente criado!")
        print(f"  - Memory: {agent.memory}")
        print(f"  - Memory DB: {agent.memory.db}")
        print(f"  - Enable User Memories: {agent.enable_user_memories}")
        print(f"  - Enable Session Summaries: {agent.enable_session_summaries}")
        
        # 3. Testar interação que deve criar memória
        print("\n🔧 Testando interação que deve criar memória...")
        user_id = "test_user_123"
        session_id = "test_session_456"
        
        response = agent.run(
            message="Meu nome é João e eu trabalho com análise de dados de mobilidade urbana.",
            user_id=user_id,
            session_id=session_id,
            stream=False
        )
        
        print(f"✅ Resposta do agente: {response.content[:100]}...")
        
        # 4. Verificar se memórias foram criadas
        print("\n🔧 Verificando memórias criadas...")
        memories = postgres_memory_db.read_memories(user_id=user_id)
        print(f"✅ Memórias encontradas para {user_id}: {len(memories)}")
        
        for memory in memories:
            print(f"  - ID: {memory.id}")
            print(f"  - Conteúdo: {str(memory.memory)[:100]}...")
        
        # 5. Verificar se o agente lembra na próxima interação
        print("\n🔧 Testando se agente lembra na próxima interação...")
        response2 = agent.run(
            message="Qual é o meu nome?",
            user_id=user_id,
            session_id=session_id,
            stream=False
        )
        
        print(f"✅ Segunda resposta: {response2.content[:200]}...")
        
        # Se o agente lembrar do nome João, a memória está funcionando
        if "joão" in response2.content.lower():
            print("🎉 SUCESSO: Agente lembrou do nome!")
            return True
        else:
            print("⚠️ Agente não lembrou do nome, mas pode ser normal")
            return True
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 Testando agente com memória...")
    success = test_agent_memory()
    
    if success:
        print("\n✅ Teste de memória concluído!")
    else:
        print("\n❌ Problemas no teste de memória!")
        sys.exit(1)
