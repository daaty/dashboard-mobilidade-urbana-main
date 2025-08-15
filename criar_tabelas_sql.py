"""
Script SQL para criar as tabelas estratégicas
"""

CREATE_FASES_PLANEJAMENTO = """
CREATE TABLE IF NOT EXISTS fases_planejamento (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(200) NOT NULL,
    descricao TEXT,
    data_inicio TIMESTAMP WITH TIME ZONE NOT NULL,
    data_fim TIMESTAMP WITH TIME ZONE NOT NULL,
    data_inicio_real TIMESTAMP WITH TIME ZONE,
    data_fim_real TIMESTAMP WITH TIME ZONE,
    status VARCHAR(50) DEFAULT 'planejada',
    progresso_percentual DECIMAL(5,2) DEFAULT 0.00,
    orcamento_previsto DECIMAL(15,2) NOT NULL,
    orcamento_empenhado DECIMAL(15,2) DEFAULT 0.00,
    orcamento_pago DECIMAL(15,2) DEFAULT 0.00,
    orcamento_liquidado DECIMAL(15,2) DEFAULT 0.00,
    meta_cidades INTEGER NOT NULL,
    meta_motoristas INTEGER NOT NULL,
    meta_corridas INTEGER NOT NULL,
    meta_receita DECIMAL(15,2) DEFAULT 0.00,
    resultado_cidades INTEGER DEFAULT 0,
    resultado_motoristas INTEGER DEFAULT 0,
    resultado_corridas INTEGER DEFAULT 0,
    resultado_receita DECIMAL(15,2) DEFAULT 0.00,
    prazo_meses INTEGER NOT NULL,
    responsavel VARCHAR(100),
    observacoes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
"""

CREATE_METAS_PROGRESSIVAS = """
CREATE TABLE IF NOT EXISTS metas_progressivas (
    id SERIAL PRIMARY KEY,
    cidade_id INTEGER NOT NULL,
    fase_id INTEGER,
    mes INTEGER NOT NULL,
    percentual_publico DECIMAL(5,2) NOT NULL,
    tipo_meta VARCHAR(50) NOT NULL,
    meta_corridas INTEGER NOT NULL,
    meta_motoristas INTEGER NOT NULL,
    meta_usuarios_ativos INTEGER DEFAULT 0,
    meta_receita DECIMAL(15,2) DEFAULT 0.00,
    resultado_corridas INTEGER DEFAULT 0,
    resultado_motoristas INTEGER DEFAULT 0,
    resultado_usuarios_ativos INTEGER DEFAULT 0,
    resultado_receita DECIMAL(15,2) DEFAULT 0.00,
    resultado_satisfacao DECIMAL(3,2) DEFAULT 0.00,
    resultado_tempo_resposta DECIMAL(5,2) DEFAULT 0.00,
    resultado_taxa_cancelamento DECIMAL(5,2) DEFAULT 0.00,
    atingida BOOLEAN DEFAULT FALSE,
    status VARCHAR(50) DEFAULT 'pendente',
    investimento_previsto DECIMAL(15,2) DEFAULT 0.00,
    investimento_realizado DECIMAL(15,2) DEFAULT 0.00,
    estrategia TEXT,
    observacoes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (cidade_id) REFERENCES cidades_demografia(id),
    FOREIGN KEY (fase_id) REFERENCES fases_planejamento(id)
);
"""


import os
import psycopg2
from psycopg2 import sql
from dotenv import load_dotenv


def criar_tabelas_sql():
    """Cria as tabelas usando SQL direto e DATABASE_URL do .env"""
    print("🏗️ CRIANDO TABELAS ESTRATÉGICAS (SQL)")
    print("=" * 50)
    load_dotenv()
    DATABASE_URL = os.getenv("DATABASE_URL")
    if not DATABASE_URL:
        print("❌ DATABASE_URL não encontrada no .env!")
        return False
    if DATABASE_URL.startswith("postgresql+asyncpg"):
        DATABASE_URL = DATABASE_URL.replace("postgresql+asyncpg", "postgresql")
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        print("📊 Criando tabela fases_planejamento...")
        cur.execute(CREATE_FASES_PLANEJAMENTO)
        print("🎯 Criando tabela metas_progressivas...")
        cur.execute(CREATE_METAS_PROGRESSIVAS)
        conn.commit()
        cur.execute("SELECT COUNT(*) FROM fases_planejamento")
        fases_count = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM metas_progressivas")
        metas_count = cur.fetchone()[0]
        print("✅ Tabelas criadas com sucesso!")
        print(f"📈 Registros existentes:")
        print(f"   🏗️ Fases de planejamento: {fases_count}")
        print(f"   🎯 Metas progressivas: {metas_count}")
        cur.close()
        conn.close()
        return True
    except Exception as e:
        print(f"❌ Erro ao criar tabelas: {e}")
        return False

if __name__ == "__main__":
    sucesso = criar_tabelas_sql()
    
    if sucesso:
        print("\n🎉 PROCESSO CONCLUÍDO!")
        print("✅ Tabelas estratégicas prontas para uso")
        print("🔄 Agora pode executar o script de população")
    else:
        print("\n❌ PROCESSO FALHOU!")
        print("❌ Verificar configurações do banco de dados")
