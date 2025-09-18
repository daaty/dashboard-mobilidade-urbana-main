import os
import sys
import json
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Adicionar o diretório raiz ao path para importar módulos locais
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Usar a URL do banco real
DATABASE_URL = "postgresql://n8n_user:n8n_pw@148.230.73.27:5432/n8n_db"

def check_halef_data():
    """Verifica os dados do passageiro Halef no banco de dados"""
    
    # Conectar com o banco
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = SessionLocal()
    
    try:
        print("=== BUSCANDO PASSAGEIRO 'HALEF' ===")
        
        # Buscar todos os passageiros que contenham "halef" no nome
        query = text("""
            SELECT 
                passenger_id,
                city,
                personal_data,
                extraction_source,
                extracted_at,
                updated_at
            FROM passenger_personal_details 
            WHERE LOWER(personal_data::text) LIKE '%halef%'
            ORDER BY updated_at DESC NULLS LAST
        """)
        
        results = session.execute(query).fetchall()
        
        if not results:
            print("❌ NENHUM PASSAGEIRO 'HALEF' ENCONTRADO!")
            
            # Vamos buscar pelo ID que poderia ter sido usado
            print("\n=== TENTANDO BUSCAR POR IDs CONHECIDOS ===")
            common_ids = ['17147322', '18354678']  # IDs que apareceram nos logs anteriores
            
            for passenger_id in common_ids:
                query_by_id = text("""
                    SELECT 
                        passenger_id,
                        city,
                        personal_data,
                        extraction_source,
                        extracted_at,
                        updated_at
                    FROM passenger_personal_details 
                    WHERE passenger_id = :passenger_id
                """)
                
                result = session.execute(query_by_id, {"passenger_id": passenger_id}).fetchone()
                if result:
                    print(f"\n📋 PASSAGEIRO ID: {passenger_id}")
                    print(f"🏙️  Cidade: {result.city}")
                    print(f"📅 Extraído em: {result.extracted_at}")
                    print(f"📅 Atualizado em: {result.updated_at}")
                    
                    # Parse dos dados pessoais
                    personal_data = result.personal_data
                    if isinstance(personal_data, str):
                        try:
                            personal_data = json.loads(personal_data)
                        except json.JSONDecodeError as e:
                            print(f"❌ ERRO ao parsear personal_data: {e}")
                            print(f"📄 Dados brutos: {result.personal_data}")
                            continue
                    
                    print(f"👤 Nome: {personal_data.get('user_name', 'N/A')}")
                    print(f"📧 Email: {personal_data.get('user_email', 'N/A')}")
                    print(f"📱 Telefone: {personal_data.get('user_phone', 'N/A')}")
                    print(f"📄 Dados completos: {json.dumps(personal_data, indent=2, ensure_ascii=False)}")
                    print("-" * 50)
        else:
            print(f"✅ ENCONTRADOS {len(results)} REGISTROS:")
            
            for i, result in enumerate(results, 1):
                print(f"\n📋 REGISTRO #{i} - ID: {result.passenger_id}")
                print(f"🏙️  Cidade: {result.city}")
                print(f"📅 Extraído em: {result.extracted_at}")
                print(f"📅 Atualizado em: {result.updated_at}")
                
                # Parse dos dados pessoais
                personal_data = result.personal_data
                if isinstance(personal_data, str):
                    try:
                        personal_data = json.loads(personal_data)
                    except json.JSONDecodeError as e:
                        print(f"❌ ERRO ao parsear personal_data: {e}")
                        print(f"📄 Dados brutos: {result.personal_data}")
                        continue
                
                print(f"👤 Nome: {personal_data.get('user_name', 'N/A')}")
                print(f"📧 Email: {personal_data.get('user_email', 'N/A')}")
                print(f"📱 Telefone: {personal_data.get('user_phone', 'N/A')}")
                print(f"🚫 Bloqueado: {personal_data.get('blocked', 'N/A')}")
                
                # Mostrar estrutura completa para debug
                print(f"📄 Estrutura completa do personal_data:")
                print(json.dumps(personal_data, indent=2, ensure_ascii=False))
                print("-" * 50)
    
    except Exception as e:
        print(f"❌ ERRO: {str(e)}")
    
    finally:
        session.close()

if __name__ == "__main__":
    check_halef_data()