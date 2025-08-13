#!/usr/bin/env python3
import sys
import os
sys.path.append('.')
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.drivers_data import DriversData
import json
from dotenv import load_dotenv

load_dotenv()

def debug_online_drivers():
    # Usar a string de conexão PostgreSQL correta
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://n8n_user:n8n_pw@148.230.73.27:5432/n8n_db")
    DATABASE_URL = DATABASE_URL.replace("postgresql+asyncpg://", "postgresql+psycopg2://")
    
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    with SessionLocal() as session:
        drivers = session.query(DriversData).all()
        print(f'🔍 Analisando motoristas ONLINE específicos...')
        
        drivers_processed = set()
        online_drivers_detail = []
        
        for driver_record in drivers:
            driver_id = driver_record.driver_id
            
            # DEDUPLICAÇÃO: Pular se ID já foi processado ou é inválido
            if not driver_id or driver_id in drivers_processed or driver_id in ['---', '0', 'Driver']:
                continue
                
            try:
                # Processar additional_data
                driver_data = driver_record.additional_data
                if isinstance(driver_data, str):
                    driver_data = json.loads(driver_data)
                elif not isinstance(driver_data, dict):
                    driver_data = {}
                
                # Verificar se tem "Online" no raw_row
                has_online = False
                raw_row = driver_data.get('raw_row', [])
                if isinstance(raw_row, list):
                    for item in raw_row:
                        if isinstance(item, str) and item.lower() == 'online':
                            has_online = True
                            break
                
                if has_online:
                    drivers_processed.add(driver_id)
                    online_drivers_detail.append({
                        'id': driver_id,
                        'name': driver_record.name if driver_record.name and driver_record.name not in ['None', '0'] else driver_id,
                        'data_type': driver_record.data_type,
                        'raw_row': raw_row,
                        'scraped_at': driver_record.scraped_at
                    })
                    
            except Exception as e:
                print(f"❌ Erro ao processar {driver_id}: {e}")
                continue
        
        print(f'\n🟢 MOTORISTAS COM STATUS "Online" (total: {len(online_drivers_detail)}):')
        for i, driver in enumerate(online_drivers_detail, 1):
            print(f'\n{i}. ID: {driver["id"]}')
            print(f'   Nome: {driver["name"]}')
            print(f'   Data Type: {driver["data_type"]}')
            print(f'   Scraped At: {driver["scraped_at"]}')
            print(f'   Raw Row (primeiros 5): {driver["raw_row"][:5] if len(driver["raw_row"]) > 5 else driver["raw_row"]}')
        
        # Verificar se há duplicatas por nome
        names = [d['name'] for d in online_drivers_detail]
        print(f'\n🔍 VERIFICAÇÃO DE DUPLICATAS POR NOME:')
        unique_names = set(names)
        print(f'   Total de nomes: {len(names)}')
        print(f'   Nomes únicos: {len(unique_names)}')
        
        if len(names) != len(unique_names):
            print('   ⚠️ Há duplicatas de nomes!')
            for name in unique_names:
                count = names.count(name)
                if count > 1:
                    print(f'   - "{name}" aparece {count} vezes')
        else:
            print('   ✅ Não há duplicatas de nomes')

if __name__ == "__main__":
    debug_online_drivers()
