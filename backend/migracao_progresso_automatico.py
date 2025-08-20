"""
🔧 MIGRAÇÃO: Adicionar campos de progresso manual e método de cálculo

Adiciona as colunas:
- progresso_manual: Boolean (padrão False)
- metodo_calculo: String (padrão 'hibrido')
"""

import psycopg2
from psycopg2 import sql
import os
from dotenv import load_dotenv

load_dotenv()

def executar_migracao():
    """Executa a migração para adicionar as novas colunas"""
    
    # Configuração do banco
    DATABASE_URL = os.getenv('DATABASE_URL')
    
    # Se a URL contém asyncpg, converter para psycopg2
    if DATABASE_URL and 'asyncpg' in DATABASE_URL:
        DATABASE_URL = DATABASE_URL.replace('postgresql+asyncpg://', 'postgresql://')
    
    if not DATABASE_URL:
        DATABASE_URL = "postgresql://postgres:123456@localhost:5432/dashboard_mobilidade"
    
    print(f"🔗 Conectando em: {DATABASE_URL.split('@')[1] if '@' in DATABASE_URL else 'local'}")
    
    print("🔧 INICIANDO MIGRAÇÃO - PROGRESSO AUTOMÁTICO")
    print("=" * 60)
    
    try:
        # Conectar ao banco
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        
        print("✅ Conectado ao banco de dados")
        
        # 1️⃣ Verificar se as colunas já existem
        print("\n1️⃣ Verificando colunas existentes...")
        
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'fases_planejamento'
            AND column_name IN ('progresso_manual', 'metodo_calculo')
        """)
        
        colunas_existentes = [row[0] for row in cursor.fetchall()]
        print(f"   Colunas existentes: {colunas_existentes}")
        
        # 2️⃣ Adicionar coluna progresso_manual se não existir
        if 'progresso_manual' not in colunas_existentes:
            print("\n2️⃣ Adicionando coluna progresso_manual...")
            cursor.execute("""
                ALTER TABLE fases_planejamento 
                ADD COLUMN progresso_manual BOOLEAN DEFAULT FALSE
            """)
            print("   ✅ Coluna progresso_manual adicionada")
        else:
            print("\n2️⃣ Coluna progresso_manual já existe")
        
        # 3️⃣ Adicionar coluna metodo_calculo se não existir
        if 'metodo_calculo' not in colunas_existentes:
            print("\n3️⃣ Adicionando coluna metodo_calculo...")
            cursor.execute("""
                ALTER TABLE fases_planejamento 
                ADD COLUMN metodo_calculo VARCHAR(20) DEFAULT 'hibrido'
            """)
            print("   ✅ Coluna metodo_calculo adicionada")
        else:
            print("\n3️⃣ Coluna metodo_calculo já existe")
        
        # 4️⃣ Atualizar registros existentes para ter progresso automático
        print("\n4️⃣ Configurando fases existentes para progresso automático...")
        cursor.execute("""
            UPDATE fases_planejamento 
            SET progresso_manual = FALSE, 
                metodo_calculo = 'hibrido'
            WHERE progresso_manual IS NULL 
               OR metodo_calculo IS NULL
        """)
        
        linhas_atualizadas = cursor.rowcount
        print(f"   ✅ {linhas_atualizadas} registros configurados para automático")
        
        # Commit das mudanças
        conn.commit()
        
        # 5️⃣ Verificar resultado final
        print("\n5️⃣ Verificando estrutura final...")
        cursor.execute("""
            SELECT column_name, data_type, column_default
            FROM information_schema.columns 
            WHERE table_name = 'fases_planejamento'
            AND column_name IN ('progresso_manual', 'metodo_calculo', 'progresso_percentual')
            ORDER BY column_name
        """)
        
        for row in cursor.fetchall():
            print(f"   📋 {row[0]}: {row[1]} (padrão: {row[2]})")
        
        print("\n✅ MIGRAÇÃO CONCLUÍDA COM SUCESSO!")
        
    except Exception as e:
        print(f"\n❌ ERRO NA MIGRAÇÃO: {e}")
        if 'conn' in locals():
            conn.rollback()
    
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    executar_migracao()
