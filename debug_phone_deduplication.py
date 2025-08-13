#!/usr/bin/env python3

import sqlite3
import json
from collections import defaultdict

def debug_phone_deduplication():
    print("=== DEBUG: Phone Deduplication ===\n")
    
    # Conectar ao banco de dados
    conn = sqlite3.connect('instance/mobilidade_urbana_dev.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Buscar todos os drivers
    cursor.execute("SELECT * FROM drivers_data ORDER BY created_at DESC")
    drivers_data = cursor.fetchall()
    
    print(f"Total de registros no banco: {len(drivers_data)}\n")
    
    # Processamento com deduplicação
    drivers_processed = set()
    phones_processed = set()
    phone_to_drivers = defaultdict(list)
    online_drivers = []
    
    for driver_record in drivers_data:
        driver_id = driver_record['driver_id']
        driver_name = driver_record['name']
        
        # Pular IDs inválidos
        if not driver_id or driver_id in ['---', '0', 'Driver']:
            continue
            
        try:
            # Processar additional_data
            driver_data = driver_record['additional_data']
            if isinstance(driver_data, str):
                driver_data = json.loads(driver_data)
            elif not isinstance(driver_data, dict):
                driver_data = {}
            
            # Extrair telefone
            phone = None
            if driver_data and 'raw_row' in driver_data:
                raw_row = driver_data['raw_row']
                if isinstance(raw_row, list) and len(raw_row) > 4:
                    for item in raw_row[:6]:
                        if isinstance(item, str) and item.startswith('+556'):
                            phone = item
                            break
            
            # Se não encontrou telefone no raw_row, tentar no email
            if not phone and driver_record['email']:
                if driver_record['email'].startswith('+556'):
                    phone = driver_record['email']
            
            # Mapear telefone para drivers
            if phone:
                phone_to_drivers[phone].append({
                    'id': driver_id,
                    'name': driver_name,
                    'phone': phone
                })
            
            # Verificar status online
            driver_status = 'inativo'
            if driver_data:
                raw_row = driver_data.get('raw_row', [])
                if isinstance(raw_row, list):
                    for item in raw_row:
                        if isinstance(item, str) and item.lower() == 'online':
                            driver_status = 'ativo'
                            break
            
            if driver_status == 'ativo':
                online_drivers.append({
                    'id': driver_id,
                    'name': driver_name,
                    'phone': phone,
                    'already_processed_id': driver_id in drivers_processed,
                    'already_processed_phone': phone in phones_processed if phone else False
                })
            
            # Aplicar deduplicação
            if driver_id in drivers_processed:
                continue
            if phone and phone in phones_processed:
                continue
                
            drivers_processed.add(driver_id)
            if phone:
                phones_processed.add(phone)
                
        except Exception as e:
            print(f"Erro ao processar driver {driver_id}: {e}")
            continue
    
    print("=== TELEFONES DUPLICADOS ===")
    for phone, drivers in phone_to_drivers.items():
        if len(drivers) > 1:
            print(f"📱 Telefone: {phone}")
            for driver in drivers:
                print(f"   - ID: {driver['id']} | Nome: {driver['name']}")
            print()
    
    print("=== MOTORISTAS ONLINE ANTES DA DEDUPLICAÇÃO ===")
    for i, driver in enumerate(online_drivers, 1):
        print(f"{i}. ID: {driver['id']} | Nome: {driver['name']} | Telefone: {driver['phone']}")
        if driver['already_processed_id']:
            print("   ⚠️  ID já processado")
        if driver['already_processed_phone']:
            print("   ⚠️  Telefone já processado")
        print()
    
    print(f"Total de motoristas online antes da deduplicação: {len(online_drivers)}")
    print(f"Total de IDs únicos processados: {len(drivers_processed)}")
    print(f"Total de telefones únicos processados: {len(phones_processed)}")
    
    # Calcular motoristas online após deduplicação
    final_online = []
    drivers_seen = set()
    phones_seen = set()
    
    for driver in online_drivers:
        if driver['id'] in drivers_seen:
            continue
        if driver['phone'] and driver['phone'] in phones_seen:
            continue
            
        drivers_seen.add(driver['id'])
        if driver['phone']:
            phones_seen.add(driver['phone'])
        final_online.append(driver)
    
    print(f"\n=== RESULTADO FINAL ===")
    print(f"Motoristas online após deduplicação: {len(final_online)}")
    for i, driver in enumerate(final_online, 1):
        print(f"{i}. ID: {driver['id']} | Nome: {driver['name']} | Telefone: {driver['phone']}")
    
    conn.close()

if __name__ == "__main__":
    debug_phone_deduplication()
