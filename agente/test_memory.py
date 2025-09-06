#!/usr/bin/env python3
"""
Script para testar a configuração de memória PostgreSQL do AGNO
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
    from agno.memory.v2.db.postgres import PostgresMemoryDb
    from agno.memory.v2.memory import Memory
    from agno.models.openai import OpenAIChat
    print("✅ Imports AGNO funcionaram!")
except ImportError as e:
    print(f"❌ Erro nos imports: {e}")
    sys.exit(1)

def test_memory_config():
    """Testa configuração de memória"""
    
    # Configurações
    db_url = os.getenv('DATABASE_URL', 'postgresql://n8n_user:n8n_pw@148.230.73.27:5432/n8n_db')
    api_key = os.getenv('OPENAI_API_KEY')
    
    if not api_key:
        print("❌ OPENAI_API_KEY não encontrada")
        return False
        
    print(f"🔧 Testando PostgreSQL: {db_url[:50]}...")
    
    try:
        # 1. Criar PostgresMemoryDb
        print("🔧 Criando PostgresMemoryDb...")
        memory_db = PostgresMemoryDb(
            table_name='agno_mobility_memories',
            db_url=db_url
        )
        print("✅ PostgresMemoryDb criado")
        
        # 2. Criar tabela se não existir
        print("🔧 Criando/verificando tabela...")
        memory_db.create()
        print("✅ Tabela de memória ok")
        
        # 3. Criar Memory com modelo
        print("🔧 Configurando Memory...")
        memory = Memory(
            db=memory_db,
            model=OpenAIChat(id='gpt-4o-mini', api_key=api_key)
        )
        print("✅ Memory configurado!")
        
        # 4. Verificar configuração
        print("\n📊 Status da Memória:")
        print(f"  - DB: {memory.db.__class__.__name__}")
        print(f"  - Model: {memory.model.__class__.__name__} ({memory.model.id})")
        print(f"  - Tabela: {memory_db.table_name}")
        
        # 5. Testar leitura de memórias
        print("\n🔧 Testando leitura de memórias...")
        memories = memory_db.read_memories()
        print(f"✅ Memórias encontradas: {len(memories)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 Testando configuração de memória AGNO...")
    success = test_memory_config()
    
    if success:
        print("\n✅ Configuração de memória OK!")
    else:
        print("\n❌ Problemas na configuração de memória!")
        sys.exit(1)
