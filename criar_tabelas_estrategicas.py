"""
Script para criar as tabelas dos novos modelos
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from app.database.db import engine, SessionLocal
from app.models.fases_planejamento import FasesPlanejamento
from app.models.metas_progressivas import MetasProgressivas
from app.models.cidades_demografia import CidadesDemografia
from app.models.campanha import Campanha

def criar_tabelas_estrategicas():
    """Cria as tabelas para os modelos estratégicos"""
    print("🏗️ CRIANDO TABELAS ESTRATÉGICAS")
    print("=" * 50)
    
    try:
        # Criar todas as tabelas (apenas as que não existem)
        print("📊 Criando tabela fases_planejamento...")
        FasesPlanejamento.metadata.create_all(bind=engine)
        
        print("🎯 Criando tabela metas_progressivas...")  
        MetasProgressivas.metadata.create_all(bind=engine)
        
        print("✅ Tabelas criadas com sucesso!")
        
        # Verificar se as tabelas foram criadas
        db = SessionLocal()
        
        try:
            # Testar consulta básica
            fases_count = db.query(FasesPlanejamento).count()
            metas_count = db.query(MetasProgressivas).count()
            
            print(f"📈 Registros existentes:")
            print(f"   🏗️ Fases de planejamento: {fases_count}")
            print(f"   🎯 Metas progressivas: {metas_count}")
            
            return True
            
        except Exception as e:
            print(f"❌ Erro ao verificar tabelas: {e}")
            return False
        finally:
            db.close()
            
    except Exception as e:
        print(f"❌ Erro ao criar tabelas: {e}")
        return False

if __name__ == "__main__":
    sucesso = criar_tabelas_estrategicas()
    
    if sucesso:
        print("\n🎉 PROCESSO CONCLUÍDO!")
        print("✅ Tabelas estratégicas prontas para uso")
    else:
        print("\n❌ PROCESSO FALHOU!")
        print("❌ Verificar logs de erro acima")
