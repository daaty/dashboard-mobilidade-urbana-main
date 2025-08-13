#!/usr/bin/env python3
import sys
import os
sys.path.append('.')
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.drivers_data import DriversData
import json
from collections import Counter
from dotenv import load_dotenv

load_dotenv()

def analyze_drivers_status():
    # Usar a string de conexão PostgreSQL correta
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://n8n_user:n8n_pw@148.230.73.27:5432/n8n_db")
    DATABASE_URL = DATABASE_URL.replace("postgresql+asyncpg://", "postgresql+psycopg2://")
    
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    with SessionLocal() as session:
        drivers = session.query(DriversData).all()
        print(f'🔍 Total de registros drivers_data: {len(drivers)}')
        
        if len(drivers) == 0:
            print("❌ Nenhum registro encontrado na tabela drivers_data")
            return
        
        # Analisar por data_type
        data_types = Counter([d.data_type for d in drivers])
        print(f'\n📊 CONTAGEM POR DATA_TYPE:')
        for data_type, count in data_types.items():
            print(f'  {data_type}: {count}')
        
        # Analisar motoristas únicos
        unique_drivers = {}
        
        for driver in drivers:
            driver_id = driver.driver_id
            
            # Pular IDs inválidos
            if not driver_id or driver_id in ['---', '0', 'Driver']:
                continue
                
            # Se já temos esse driver, manter o registro mais recente
            if driver_id in unique_drivers:
                if hasattr(driver, 'scraped_at') and hasattr(unique_drivers[driver_id], 'scraped_at'):
                    if driver.scraped_at > unique_drivers[driver_id].scraped_at:
                        unique_drivers[driver_id] = driver
            else:
                unique_drivers[driver_id] = driver
        
        print(f'\n👥 MOTORISTAS ÚNICOS: {len(unique_drivers)}')
        
        # Analisar por status
        status_counts = {'active': 0, 'leaderboard': 0, 'enrollment': 0, 'unknown': 0}
        active_drivers = []
        
        for driver_id, driver in unique_drivers.items():
            status = driver.data_type
            
            if status == 'active':
                status_counts['active'] += 1
                active_drivers.append(driver)
            elif status == 'leaderboard':
                status_counts['leaderboard'] += 1
            elif status == 'enrollment':
                status_counts['enrollment'] += 1
            else:
                status_counts['unknown'] += 1
        
        print(f'\n📈 ANÁLISE DE STATUS:')
        print(f'  🟢 Active: {status_counts["active"]} motoristas')
        print(f'  🏆 Leaderboard: {status_counts["leaderboard"]} motoristas')
        print(f'  📝 Enrollment: {status_counts["enrollment"]} motoristas')
        print(f'  ❓ Unknown: {status_counts["unknown"]} motoristas')
        
        print(f'\n🚗 MOTORISTAS ATIVOS DETALHADOS:')
        for i, driver in enumerate(active_drivers, 1):
            name = driver.name if driver.name and driver.name not in ['None', '0'] else driver.driver_id
            phone = driver.email if hasattr(driver, 'email') else 'N/A'
            vehicle = driver.mobile if hasattr(driver, 'mobile') else 'N/A'
            
            print(f'  {i}. {name}')
            print(f'     📞 Phone: {phone}')
            print(f'     🚙 Vehicle: {vehicle}')
            print(f'     📅 Updated: {driver.scraped_at}')
            print()
        
        # Verificar se realmente são apenas 3 únicos
        print(f'🎯 CONCLUSÃO:')
        print(f'  Total de registros na tabela: {len(drivers)}')
        print(f'  Motoristas únicos (sem duplicatas): {len(unique_drivers)}')
        print(f'  Motoristas com status "active": {status_counts["active"]}')
        print(f'  Motoristas no "leaderboard": {status_counts["leaderboard"]} (também considerados ativos)')
        
        # Total de motoristas considerados "online/ativos"
        total_active = status_counts["active"] + status_counts["leaderboard"]
        print(f'  🟢 TOTAL DE MOTORISTAS ONLINE/ATIVOS: {total_active}')
        
        # Listar todos os IDs únicos para verificação
        print(f'\n📋 TODOS OS IDs ÚNICOS DE MOTORISTAS:')
        for i, driver_id in enumerate(sorted(unique_drivers.keys()), 1):
            driver = unique_drivers[driver_id]
            print(f'  {i}. {driver_id} ({driver.data_type})')

if __name__ == "__main__":
    analyze_drivers_status()
