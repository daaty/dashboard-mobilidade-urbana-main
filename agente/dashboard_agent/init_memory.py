"""
🗄️ INICIALIZAÇÃO DAS TABELAS DE MEMÓRIA DO AGENTE
Script para criar as tabelas necessárias no PostgreSQL para memória persistente
"""

import os
import sys
import psycopg2
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

def criar_tabelas_agente():
    """Cria as tabelas necessárias para a memória do agente"""
    
    # String de conexão (mesma da API)
    database_url = os.getenv("MEMORY_DB_URL", "postgresql://n8n_user:n8n_pw@148.230.73.27:5432/n8n_db")
    table_prefix = os.getenv("AGENT_MEMORY_TABLE_PREFIX", "agente_")
    
    print(f"🔗 Conectando ao PostgreSQL...")
    print(f"📊 Prefixo das tabelas: {table_prefix}")
    
    try:
        # Conectar ao banco
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        # SQL para criar tabela de memória do agente
        create_memory_table = f"""
        CREATE TABLE IF NOT EXISTS {table_prefix}memory (
            id SERIAL PRIMARY KEY,
            session_id VARCHAR(255) NOT NULL,
            agent_id VARCHAR(255) NOT NULL,
            memory_type VARCHAR(100) NOT NULL,
            content JSONB NOT NULL,
            metadata JSONB DEFAULT '{{}}',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        
        # SQL para criar índices
        create_indexes = f"""
        CREATE INDEX IF NOT EXISTS idx_{table_prefix}memory_session 
        ON {table_prefix}memory (session_id);
        
        CREATE INDEX IF NOT EXISTS idx_{table_prefix}memory_agent 
        ON {table_prefix}memory (agent_id);
        
        CREATE INDEX IF NOT EXISTS idx_{table_prefix}memory_type 
        ON {table_prefix}memory (memory_type);
        
        CREATE INDEX IF NOT EXISTS idx_{table_prefix}memory_created 
        ON {table_prefix}memory (created_at);
        """
        
        # SQL para criar tabela de conversas do agente
        create_conversations_table = f"""
        CREATE TABLE IF NOT EXISTS {table_prefix}conversations (
            id SERIAL PRIMARY KEY,
            session_id VARCHAR(255) NOT NULL,
            agent_id VARCHAR(255) NOT NULL,
            user_message TEXT,
            agent_response TEXT,
            reasoning_steps JSONB DEFAULT '[]',
            tools_used JSONB DEFAULT '[]',
            metadata JSONB DEFAULT '{{}}',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        
        # SQL para criar índices de conversas
        create_conversation_indexes = f"""
        CREATE INDEX IF NOT EXISTS idx_{table_prefix}conversations_session 
        ON {table_prefix}conversations (session_id);
        
        CREATE INDEX IF NOT EXISTS idx_{table_prefix}conversations_agent 
        ON {table_prefix}conversations (agent_id);
        
        CREATE INDEX IF NOT EXISTS idx_{table_prefix}conversations_created 
        ON {table_prefix}conversations (created_at);
        """
        
        # SQL para criar tabela de insights do agente
        create_insights_table = f"""
        CREATE TABLE IF NOT EXISTS {table_prefix}insights (
            id SERIAL PRIMARY KEY,
            insight_type VARCHAR(100) NOT NULL,
            title VARCHAR(255) NOT NULL,
            content TEXT NOT NULL,
            kpis JSONB DEFAULT '{{}}',
            recommendations JSONB DEFAULT '[]',
            confidence_score DECIMAL(3,2) DEFAULT 0.0,
            data_sources JSONB DEFAULT '[]',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            expires_at TIMESTAMP
        );
        """
        
        # SQL para criar índices de insights
        create_insight_indexes = f"""
        CREATE INDEX IF NOT EXISTS idx_{table_prefix}insights_type 
        ON {table_prefix}insights (insight_type);
        
        CREATE INDEX IF NOT EXISTS idx_{table_prefix}insights_created 
        ON {table_prefix}insights (created_at);
        
        CREATE INDEX IF NOT EXISTS idx_{table_prefix}insights_confidence 
        ON {table_prefix}insights (confidence_score);
        """
        
        # Executar criação das tabelas
        print("📊 Criando tabela de memória...")
        cursor.execute(create_memory_table)
        
        print("🔍 Criando índices de memória...")
        cursor.execute(create_indexes)
        
        print("💬 Criando tabela de conversas...")
        cursor.execute(create_conversations_table)
        
        print("🔍 Criando índices de conversas...")
        cursor.execute(create_conversation_indexes)
        
        print("💡 Criando tabela de insights...")
        cursor.execute(create_insights_table)
        
        print("🔍 Criando índices de insights...")
        cursor.execute(create_insight_indexes)
        
        # Commit das alterações
        conn.commit()
        
        print("✅ Tabelas de memória criadas com sucesso!")
        
        # Verificar se as tabelas foram criadas
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name LIKE %s
            ORDER BY table_name;
        """, (f"{table_prefix}%",))
        
        tabelas = cursor.fetchall()
        print(f"\n📋 Tabelas criadas:")
        for tabela in tabelas:
            print(f"   - {tabela[0]}")
        
        cursor.close()
        conn.close()
        
        return True
        
    except psycopg2.Error as e:
        print(f"❌ Erro ao conectar/criar tabelas no PostgreSQL: {e}")
        return False
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        return False


def verificar_tabelas():
    """Verifica se as tabelas do agente existem"""
    
    database_url = os.getenv("MEMORY_DB_URL", "postgresql://n8n_user:n8n_pw@148.230.73.27:5432/n8n_db")
    table_prefix = os.getenv("AGENT_MEMORY_TABLE_PREFIX", "agente_")
    
    try:
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        # Verificar tabelas existentes
        cursor.execute("""
            SELECT table_name, 
                   (SELECT COUNT(*) FROM information_schema.columns 
                    WHERE table_name = t.table_name AND table_schema = 'public') as column_count
            FROM information_schema.tables t
            WHERE table_schema = 'public' 
            AND table_name LIKE %s
            ORDER BY table_name;
        """, (f"{table_prefix}%",))
        
        tabelas = cursor.fetchall()
        
        if tabelas:
            print(f"✅ Tabelas do agente encontradas:")
            for nome, colunas in tabelas:
                print(f"   - {nome} ({colunas} colunas)")
        else:
            print(f"⚠️ Nenhuma tabela do agente encontrada com prefixo '{table_prefix}'")
        
        cursor.close()
        conn.close()
        
        return len(tabelas) > 0
        
    except Exception as e:
        print(f"❌ Erro ao verificar tabelas: {e}")
        return False


def limpar_memoria_agente():
    """Limpa a memória do agente (cuidado!)"""
    
    resposta = input("⚠️ Deseja realmente limpar TODA a memória do agente? (digite 'CONFIRMO'): ")
    if resposta != "CONFIRMO":
        print("❌ Operação cancelada")
        return
    
    database_url = os.getenv("MEMORY_DB_URL", "postgresql://n8n_user:n8n_pw@148.230.73.27:5432/n8n_db")
    table_prefix = os.getenv("AGENT_MEMORY_TABLE_PREFIX", "agente_")
    
    try:
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        # Limpar dados das tabelas
        tabelas = [f"{table_prefix}memory", f"{table_prefix}conversations", f"{table_prefix}insights"]
        
        for tabela in tabelas:
            try:
                cursor.execute(f"DELETE FROM {tabela};")
                print(f"🗑️ Tabela {tabela} limpa")
            except psycopg2.Error:
                print(f"⚠️ Tabela {tabela} não existe ou não pôde ser limpa")
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print("✅ Memória do agente limpa com sucesso!")
        
    except Exception as e:
        print(f"❌ Erro ao limpar memória: {e}")


def main():
    """Função principal"""
    print("🗄️ CONFIGURAÇÃO DE MEMÓRIA DO AGENTE")
    print("=" * 50)
    
    if len(sys.argv) > 1:
        comando = sys.argv[1]
        
        if comando == "criar":
            criar_tabelas_agente()
        elif comando == "verificar":
            verificar_tabelas()
        elif comando == "limpar":
            limpar_memoria_agente()
        else:
            print("❌ Comando inválido!")
            print("Uso: python init_memory.py [criar|verificar|limpar]")
    else:
        # Menu interativo
        print("Escolha uma opção:")
        print("1. 🆕 Criar tabelas de memória")
        print("2. 🔍 Verificar tabelas existentes")
        print("3. 🗑️ Limpar memória do agente")
        print("4. 🚪 Sair")
        
        escolha = input("\nDigite sua escolha (1-4): ").strip()
        
        if escolha == "1":
            criar_tabelas_agente()
        elif escolha == "2":
            verificar_tabelas()
        elif escolha == "3":
            limpar_memoria_agente()
        elif escolha == "4":
            print("👋 Até logo!")
        else:
            print("❌ Escolha inválida!")


if __name__ == "__main__":
    main()
