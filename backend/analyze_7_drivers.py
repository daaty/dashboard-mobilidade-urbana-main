#!/usr/bin/env python3
import sys
import os
sys.path.append('.')
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.drivers_data import DriversData
import json
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta

load_dotenv()

def analyze_online_drivers():
    print("=== ANÁLISE DOS 7 MOTORISTAS ONLINE ===\n")
    
    # Configurar conexão com PostgreSQL
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://n8n_user:n8n_pw@148.230.73.27:5432/n8n_db")
    DATABASE_URL = DATABASE_URL.replace("postgresql+asyncpg://", "postgresql+psycopg2://")
    
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    with SessionLocal() as session:
        # Buscar todos os drivers (mesmo lógica da API)
        data_limite = datetime.now() - timedelta(days=30)
        drivers_data = session.query(DriversData).filter(
            DriversData.scraped_at >= data_limite
        ).order_by(DriversData.scraped_at.desc()).all()
        
        print(f"Total de registros encontrados: {len(drivers_data)}\n")
        
        # Aplicar mesma lógica da API
        drivers_processed = set()
        online_drivers = []
        all_drivers_info = []
        
        for driver_record in drivers_data:
            # Filtro por data (mesmo da API)
            if hasattr(driver_record, 'scraped_at') and driver_record.scraped_at:
                if driver_record.scraped_at < data_limite:
                    continue
            
            try:
                driver_id = driver_record.driver_id
                driver_name = driver_record.name
                
                # DEDUPLICAÇÃO: mesmo da API
                if not driver_id or driver_id in drivers_processed or driver_id in ['---', '0', 'Driver']:
                    continue
                
                drivers_processed.add(driver_id)
                
                # Processar additional_data
                driver_data = driver_record.additional_data
                if isinstance(driver_data, str):
                    driver_data = json.loads(driver_data)
                elif not isinstance(driver_data, dict):
                    driver_data = {}
                
                # Determinar status (mesma lógica da API)
                driver_status = 'inativo'
                
                if driver_data:
                    # Procurar na raw_row pelo status "Online"
                    raw_row = driver_data.get('raw_row', [])
                    if isinstance(raw_row, list):
                        for item in raw_row:
                            if isinstance(item, str):
                                if item.lower() == 'online':
                                    driver_status = 'ativo'
                                    break
                                elif item.lower() == 'offline':
                                    driver_status = 'inativo'
                                    break
                    
                    # Fallback: verificar outros campos de status
                    if driver_status == 'inativo':
                        status_value = driver_data.get('status', '')
                        if isinstance(status_value, str) and status_value.lower() == 'online':
                            driver_status = 'ativo'
                        elif 'online' in str(driver_data).lower():
                            driver_status = 'ativo'
                
                # Extrair telefone
                phone = driver_record.email if hasattr(driver_record, 'email') else ''
                
                driver_info = {
                    'id': driver_id,
                    'name': driver_name,
                    'status': driver_status,
                    'phone': phone,
                    'data_type': driver_record.data_type,
                    'scraped_at': driver_record.scraped_at,
                    'raw_row': driver_data.get('raw_row', []) if driver_data else []
                }
                
                all_drivers_info.append(driver_info)
                
                if driver_status == 'ativo':
                    online_drivers.append(driver_info)
                    
            except Exception as e:
                print(f"Erro ao processar driver {driver_record.driver_id}: {e}")
                continue
        
        print(f"=== RESULTADO: {len(online_drivers)} MOTORISTAS ONLINE ===\n")
        
        for i, driver in enumerate(online_drivers, 1):
            print(f"🚗 {i}. MOTORISTA ONLINE:")
            print(f"   📋 ID: {driver['id']}")
            print(f"   👤 Nome: {driver['name']}")
            print(f"   📱 Telefone: {driver['phone']}")
            print(f"   📊 Tipo de Dados: {driver['data_type']}")
            print(f"   📅 Capturado em: {driver['scraped_at']}")
            print(f"   🔍 Raw Row: {driver['raw_row'][:10]}...")  # Primeiros 10 itens
            print()
        
        # Verificar duplicações por nome
        print("=== VERIFICAÇÃO DE DUPLICAÇÕES ===")
        names = [d['name'] for d in online_drivers]
        phones = [d['phone'] for d in online_drivers if d['phone']]
        
        # Verificar nomes duplicados
        name_counts = {}
        for name in names:
            name_counts[name] = name_counts.get(name, 0) + 1
        
        duplicated_names = {name: count for name, count in name_counts.items() if count > 1}
        if duplicated_names:
            print("⚠️  NOMES DUPLICADOS:")
            for name, count in duplicated_names.items():
                print(f"   - {name}: {count} vezes")
        else:
            print("✅ Nenhum nome duplicado encontrado")
        
        # Verificar telefones duplicados
        phone_counts = {}
        for phone in phones:
            if phone and phone.strip():
                phone_counts[phone] = phone_counts.get(phone, 0) + 1
        
        duplicated_phones = {phone: count for phone, count in phone_counts.items() if count > 1}
        if duplicated_phones:
            print("⚠️  TELEFONES DUPLICADOS:")
            for phone, count in duplicated_phones.items():
                print(f"   - {phone}: {count} vezes")
        else:
            print("✅ Nenhum telefone duplicado encontrado")
        
        # Mostrar todos os dados para análise manual
        print(f"\n=== ANÁLISE DETALHADA DOS {len(online_drivers)} MOTORISTAS ===")
        for i, driver in enumerate(online_drivers, 1):
            print(f"\n{i}. {driver['name']} (ID: {driver['id']})")
            print(f"   📱 Telefone: {driver['phone']}")
            print(f"   📊 Tipo: {driver['data_type']}")
            
            # Mostrar onde encontrou "Online" no raw_row
            raw_row = driver['raw_row']
            online_positions = []
            if isinstance(raw_row, list):
                for idx, item in enumerate(raw_row):
                    if isinstance(item, str) and item.lower() == 'online':
                        online_positions.append(idx)
            
            if online_positions:
                print(f"   🟢 'Online' encontrado nas posições: {online_positions}")
            else:
                print(f"   🔍 Status online detectado por fallback")

if __name__ == "__main__":
    analyze_online_drivers()
