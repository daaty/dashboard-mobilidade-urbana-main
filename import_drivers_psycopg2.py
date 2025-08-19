#!/usr/bin/env python3
"""
Script corrigido para importar motoristas usando sessão síncrona
"""

import sys
import os
import pandas as pd
import json
import hashlib
from datetime import datetime
import psycopg2
from urllib.parse import urlparse

def map_excel_to_driver(row, index):
    """Mapeia linha da planilha para dados do motorista"""
    
    # Função auxiliar para obter valor seguro
    def get_safe_value(column_name, default=''):
        try:
            value = row.get(column_name, default)
            if pd.isna(value) or value is None:
                return default
            return str(value).strip()
        except:
            return default
    
    def get_numeric_value(column_name, default=0):
        try:
            value = row.get(column_name, default)
            if pd.isna(value) or value is None:
                return default
            return int(float(value))
        except:
            return default
    
    # Extrair dados principais
    driver_id = get_safe_value('Driver ID', f'DRV_{index + 1:04d}')
    name = get_safe_value('Driver Name', f'Motorista_{index + 1}')
    phone = get_safe_value('Phone Number', '')
    city = get_safe_value('CITY', 'GUARANTA')  # Default baseado nos dados
    vehicle = get_safe_value('Vehicle', 'POPULAR')
    
    # Formatar telefone
    if phone and phone != '':
        try:
            phone_clean = str(int(float(phone)))
            if len(phone_clean) == 13:  # Já tem +55
                phone = phone_clean
            elif len(phone_clean) == 11:  # Só número
                phone = f"+55{phone_clean}"
            else:
                phone = phone_clean
        except:
            phone = str(phone)
    
    # Métricas de corridas
    success_rides = get_numeric_value('Success Rides', 0)
    requests_received = get_numeric_value('Requests Received', 0)
    user_cancelled = get_numeric_value('User Cancelled Rides', 0)
    driver_cancelled = get_numeric_value('Driver Cancelled Rides', 0)
    total_rides = success_rides + user_cancelled + driver_cancelled
    
    # Calcular rating baseado na performance
    if requests_received > 0:
        success_rate = (success_rides / requests_received) * 100
        rating = round(min(5.0, max(1.0, success_rate / 20)), 1)
    else:
        rating = 3.0
    
    # Dados adicionais
    additional_data = {
        'row_index': index,
        'import_timestamp': datetime.now().isoformat(),
        'performance': {
            'success_rides': success_rides,
            'total_rides': total_rides,
            'success_rate': round((success_rides / max(requests_received, 1)) * 100, 2),
            'requests_received': requests_received,
            'user_cancelled': user_cancelled,
            'driver_cancelled': driver_cancelled
        },
        'profile': {
            'city': city,
            'vehicle_type': vehicle,
            'rating': rating,
            'status': 'active' if total_rides > 0 else 'inactive'
        }
    }
    
    # Hash único
    hash_string = f"{driver_id}_{name}_{phone}"
    data_hash = hashlib.md5(hash_string.encode()).hexdigest()
    
    return {
        'driver_id': str(driver_id),
        'name': name,
        'email': '',  # Não disponível
        'mobile': phone,
        'data_type': 'driver_profile',
        'page_source': 'excel_import',
        'additional_data': json.dumps(additional_data, ensure_ascii=False),
        'data_hash': data_hash,
        'scraped_at': datetime.now(),
        'session_info': json.dumps({'import_session': f'excel_import_{datetime.now().strftime("%Y%m%d_%H%M%S")}'}),
        'source': 'excel_import',
        'unique_id': f"{driver_id}_{data_hash[:8]}"
    }

def main():
    print("🚀 IMPORTAÇÃO PSYCOPG2 DE MOTORISTAS")
    print("=" * 40)
    
    try:
        # Ler planilha
        excel_file = "Dados Completos Motoristas.xlsx"
        df = pd.read_excel(excel_file)
        print(f"📊 Planilha lida: {len(df)} linhas")
        
        # Conectar diretamente ao PostgreSQL
        DATABASE_URL = "postgresql://n8n_user:n8n_pw@148.230.73.27:5432/n8n_db"
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        
        print("🔗 Conectado ao PostgreSQL")
        
        imported_count = 0
        errors = []
        
        # Preparar SQL de inserção
        insert_sql = """
        INSERT INTO drivers_data (
            driver_id, name, email, mobile, data_type, page_source, 
            additional_data, data_hash, scraped_at, session_info, 
            source, unique_id
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        # Processar cada linha
        for index, row in df.iterrows():
            try:
                # Mapear dados
                driver_data = map_excel_to_driver(row.to_dict(), index)
                
                # Executar inserção
                cursor.execute(insert_sql, (
                    driver_data['driver_id'],
                    driver_data['name'],
                    driver_data['email'],
                    driver_data['mobile'],
                    driver_data['data_type'],
                    driver_data['page_source'],
                    driver_data['additional_data'],
                    driver_data['data_hash'],
                    driver_data['scraped_at'],
                    driver_data['session_info'],
                    driver_data['source'],
                    driver_data['unique_id']
                ))
                
                imported_count += 1
                if imported_count % 50 == 0:
                    print(f"✅ {imported_count} motoristas importados...")
                    conn.commit()  # Commit a cada 50 registros
                
            except Exception as e:
                error_msg = f"Erro na linha {index + 1}: {str(e)}"
                errors.append(error_msg)
                print(f"❌ {error_msg}")
                conn.rollback()
                continue
        
        # Commit final
        conn.commit()
        
        print(f"\n🎉 IMPORTAÇÃO CONCLUÍDA!")
        print(f"✅ Motoristas importados: {imported_count}")
        print(f"❌ Erros: {len(errors)}")
        
        if errors:
            print("\n⚠️ PRIMEIROS ERROS:")
            for error in errors[:3]:
                print(f"   - {error}")
        
        # Verificar quantos foram realmente inseridos
        cursor.execute("SELECT COUNT(*) FROM drivers_data WHERE source = 'excel_import'")
        count = cursor.fetchone()[0]
        print(f"\n📊 Registros salvos no banco: {count}")
        
        cursor.close()
        conn.close()
        print("🔒 Conexão fechada")
        
    except Exception as e:
        print(f"💥 Erro geral: {str(e)}")

if __name__ == "__main__":
    main()
