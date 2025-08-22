#!/usr/bin/env python3
"""
Script para analisar e extrair todos os driver_ids dos motoristas na base
"""
import psycopg2
import json
from collections import Counter, defaultdict

# Conectar na base
DATABASE_URL = "postgresql://n8n_user:n8n_pw@148.230.73.27:5432/n8n_db"

try:
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    
    # Buscar todos os registros de motoristas
    cursor.execute("""
        SELECT 
            driver_id, 
            name, 
            mobile,
            additional_data,
            data_type,
            scraped_at
        FROM drivers_data 
        WHERE data_type = 'active'
        ORDER BY driver_id, scraped_at DESC
    """)
    
    rows = cursor.fetchall()
    print(f"🔍 ANÁLISE DE DRIVER_IDs - Total de registros: {len(rows)}")
    print("=" * 80)
    
    # Análises
    driver_ids = []
    driver_names = []
    driver_mobiles = []
    real_names = []
    real_phones = []
    driver_details = []
    
    for i, row in enumerate(rows):
        driver_id, name, mobile, additional_data, data_type, scraped_at = row
        
        # Parse do JSON
        try:
            if isinstance(additional_data, str):
                data = json.loads(additional_data)
            else:
                data = additional_data or {}
        except:
            data = {}
        
        # Extrair dados dos headers/raw_row
        headers = data.get('headers', [])
        raw_row = data.get('raw_row', [])
        
        # Mapear dados corretamente
        mapped_data = {}
        if headers and raw_row and len(headers) == len(raw_row):
            for j, header in enumerate(headers):
                if j < len(raw_row):
                    mapped_data[header] = raw_row[j]
        
        # Extrair nome e telefone reais
        real_name = mapped_data.get('OTP', name) if mapped_data.get('OTP') != 'View OTP' else name
        real_phone = mapped_data.get('City', mobile) if mapped_data.get('City', '').startswith('+556') else mobile
        vehicle = mapped_data.get('Mobile', '')
        city = mapped_data.get('Registered On', '')
        rides_30d = mapped_data.get('Rides in Last 30 Days', '0')
        rides_7d = mapped_data.get('Rides in Last 7 Days', '0')
        
        driver_ids.append(driver_id)
        driver_names.append(name)
        driver_mobiles.append(mobile)
        real_names.append(real_name)
        real_phones.append(real_phone)
        
        driver_details.append({
            'registro': i + 1,
            'driver_id': driver_id,
            'name_campo': name,
            'mobile_campo': mobile,
            'real_name': real_name,
            'real_phone': real_phone,
            'vehicle': vehicle,
            'city': city,
            'rides_30d': rides_30d,
            'rides_7d': rides_7d,
            'data_type': data_type,
            'scraped_at': scraped_at.strftime('%Y-%m-%d %H:%M:%S') if scraped_at else 'N/A'
        })
    
    # Estatísticas dos driver_ids
    print("📊 ESTATÍSTICAS DOS DRIVER_IDs:")
    driver_id_counts = Counter(driver_ids)
    print(f"   Total de registros: {len(driver_ids)}")
    print(f"   Driver IDs únicos: {len(driver_id_counts)}")
    print(f"   Driver IDs mais frequentes:")
    for driver_id, count in driver_id_counts.most_common(10):
        print(f"     - {driver_id}: {count} vezes")
    
    print("\n📱 ESTATÍSTICAS DOS TELEFONES REAIS:")
    phone_counts = Counter([p for p in real_phones if p and p.startswith('+556')])
    print(f"   Telefones válidos únicos: {len(phone_counts)}")
    print(f"   Telefones mais frequentes:")
    for phone, count in phone_counts.most_common(5):
        print(f"     - {phone}: {count} vezes")
    
    print("\n👤 ESTATÍSTICAS DOS NOMES REAIS:")
    name_counts = Counter([n for n in real_names if n and n not in ['0', '1', 'None', 'View OTP']])
    print(f"   Nomes válidos únicos: {len(name_counts)}")
    print(f"   Nomes mais frequentes:")
    for name, count in name_counts.most_common(5):
        print(f"     - {name}: {count} vezes")
    
    print("\n" + "=" * 80)
    print("📋 DETALHAMENTO COMPLETO DOS REGISTROS:")
    print("=" * 80)
    
    for detail in driver_details:
        print(f"#{detail['registro']:2d} | ID: {detail['driver_id']:12s} | Nome DB: {detail['name_campo']:20s} | Nome Real: {detail['real_name']:25s}")
        print(f"     | Tel DB: {detail['mobile_campo']:20s} | Tel Real: {detail['real_phone']:18s} | Veículo: {detail['vehicle']}")
        print(f"     | Cidade: {detail['city']:15s} | Corridas 30d: {detail['rides_30d']:4s} | Corridas 7d: {detail['rides_7d']:8s} | Data: {detail['scraped_at']}")
        print("-" * 120)
    
    # Agrupar por telefone único
    print("\n🔍 AGRUPAMENTO POR TELEFONE ÚNICO:")
    print("=" * 80)
    
    by_phone = defaultdict(list)
    for detail in driver_details:
        if detail['real_phone'] and detail['real_phone'].startswith('+556'):
            by_phone[detail['real_phone']].append(detail)
    
    print(f"Total de motoristas únicos por telefone: {len(by_phone)}")
    
    for i, (phone, records) in enumerate(by_phone.items(), 1):
        print(f"\n📱 MOTORISTA #{i} - Telefone: {phone}")
        for record in records:
            print(f"   - {record['real_name']} (ID: {record['driver_id']}) - {record['rides_30d']} corridas 30d")
    
    conn.close()
    
except Exception as e:
    print(f"❌ Erro: {e}")
