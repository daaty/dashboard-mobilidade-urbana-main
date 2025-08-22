from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from sqlalchemy.orm import Session
from app.database.db import get_db
from services.import_ridesdata_simple import ImportService
from services.import_service import ImportService as FullImportService
import os
import pandas as pd
import json
import hashlib
from datetime import datetime
import psycopg2

router = APIRouter()

@router.get("/import/history")
async def get_import_history():
    """Endpoint para histórico de importações"""
    return {"imports": []}

@router.post("/import/preview")
async def preview_import_data(
    filepath: str = Form(...),
    import_type: str = Form("corridas")
):
    """Endpoint para preview de dados"""
    return {"success": True, "preview": {"columns": [], "sample_data": []}}

@router.post("/import/ridesdata")
async def import_ridesdata_endpoint(
    file: UploadFile = File(...),
    table_name: str = Form(...),
    db: Session = Depends(get_db)
):
    """Endpoint para importar planilha direto para rides_data"""
    try:
        service = ImportService()
        # Salvar arquivo temporário
        filename = file.filename
        os.makedirs("uploads", exist_ok=True)  # Garantir que a pasta existe
        temp_path = os.path.join("uploads", filename)
        with open(temp_path, "wb") as f:
            f.write(await file.read())
        # Importar para rides_data
        result = service.import_ridesdata(temp_path, table_name, session=db)
        # Remover arquivo temporário
        if os.path.exists(temp_path):
            os.remove(temp_path)
        if not result['success']:
            raise HTTPException(status_code=400, detail=result['error'])
        return {"success": True, "imported": result['imported']}
    except Exception as e:
        # Log do erro para debug
        print(f"Erro no endpoint import_ridesdata: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/import/driversdata")
async def import_driversdata_endpoint(
    file: UploadFile = File(...),
    table_name: str = Form("drivers_data"),
    db: Session = Depends(get_db)
):
    """Endpoint para importar planilha direto para drivers_data usando lógica que funciona"""
    try:
        # Salvar arquivo temporário
        filename = file.filename
        os.makedirs("uploads", exist_ok=True)
        temp_path = os.path.join("uploads", filename)
        
        with open(temp_path, "wb") as f:
            f.write(await file.read())
        
        # Usar a lógica que funcionou no script psycopg2
        import pandas as pd
        import json
        import hashlib
        from datetime import datetime
        import psycopg2
        
        # Ler planilha
        df = pd.read_excel(temp_path)
        
        # Conectar diretamente ao PostgreSQL
        DATABASE_URL = "postgresql://n8n_user:n8n_pw@148.230.73.27:5432/n8n_db"
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        
        imported_count = 0
        errors = []
        
        # SQL de inserção simples (permitir dados duplicados por data)
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
                # Mapear dados usando mesma lógica do script
                driver_data = map_excel_to_driver_api(row.to_dict(), index)
                
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
                
            except Exception as e:
                error_msg = f"Linha {index + 1}: {str(e)}"
                errors.append(error_msg)
                continue
        
        # Commit final
        conn.commit()
        cursor.close()
        conn.close()
        
        # Remover arquivo temporário
        if os.path.exists(temp_path):
            os.remove(temp_path)
        
        return {
            "success": True, 
            "imported": imported_count,
            "total_rows": len(df),
            "errors": len(errors),
            "error_details": errors[:5] if errors else []
        }
        
    except Exception as e:
        # Log do erro para debug
        print(f"Erro no endpoint import_driversdata: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

def map_excel_to_driver_api(row, index):
    """Função para mapear linha da planilha - PRESERVANDO TODOS OS DADOS"""
    import pandas as pd
    import json
    import hashlib
    from datetime import datetime
    
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
            return float(value)  # Usar float para preservar decimais
        except:
            return default
    
    # Extrair dados principais para identificação
    driver_id = get_safe_value('Driver ID', f'DRV_{index + 1:04d}')
    name = get_safe_value('Driver Name', f'Motorista_{index + 1}')
    phone = get_safe_value('Phone Number', '')
    date = get_safe_value('Data', '')
    
    # Formatar telefone
    if phone and phone != '':
        try:
            phone_clean = str(int(float(phone)))
            if len(phone_clean) == 13:
                phone = phone_clean
            elif len(phone_clean) == 11:
                phone = f"+55{phone_clean}"
            else:
                phone = phone_clean
        except:
            phone = str(phone)
    
    # PRESERVAR TODOS OS DADOS DA PLANILHA
    all_data = {}
    for column, value in row.items():
        if pd.isna(value) or value is None:
            all_data[column] = None
        elif column in ['Driver ID']:
            all_data[column] = str(value)
        elif column in ['Request Sent', 'Requests Received', 'User Cancelled Rides', 
                       'User Cancelled Ride (cash)', 'User Cancelled Ride (wallet)',
                       'Driver Cancelled Rides', 'Driver Cancelled Ride (cash)', 
                       'Driver Cancelled Ride (wallet)', 'Rejected Rides', 'Success Rides',
                       'Missed Rides', 'Active Days', 'D2C Referral', 'D2D Referral',
                       'Start End Cheating Rides', 'Manual Start End Cheating Rides']:
            all_data[column] = get_numeric_value(column, 0)
        elif column in ['Online Hours']:
            all_data[column] = get_numeric_value(column, 0.0)
        else:
            all_data[column] = get_safe_value(column, '')
    
    # Dados estruturados para facilitar queries no frontend
    structured_data = {
        'raw_data': all_data,  # Todos os dados originais
        'metrics': {
            'requests_received': get_numeric_value('Requests Received', 0),
            'success_rides': get_numeric_value('Success Rides', 0),
            'user_cancelled': get_numeric_value('User Cancelled Rides', 0),
            'driver_cancelled': get_numeric_value('Driver Cancelled Rides', 0),
            'missed_rides': get_numeric_value('Missed Rides', 0),
            'rejected_rides': get_numeric_value('Rejected Rides', 0),
            'active_days': get_numeric_value('Active Days', 0),
            'online_hours': get_numeric_value('Online Hours', 0.0),
            'total_rides': get_numeric_value('Success Rides', 0) + get_numeric_value('User Cancelled Rides', 0) + get_numeric_value('Driver Cancelled Rides', 0),
            'success_rate': round((get_numeric_value('Success Rides', 0) / max(get_numeric_value('Requests Received', 1), 1)) * 100, 2)
        },
        'profile': {
            'city': get_safe_value('CITY', ''),
            'vehicle': get_safe_value('Vehicle', ''),
            'data_date': str(date)
        },
        'import_info': {
            'row_index': index,
            'import_timestamp': datetime.now().isoformat()
        }
    }
    
    # Hash único incluindo a data para permitir dados diários
    date_str = str(date) if date else 'no_date'
    hash_string = f"{driver_id}_{name}_{phone}_{date_str}"
    data_hash = hashlib.md5(hash_string.encode()).hexdigest()
    
    return {
        'driver_id': str(driver_id),
        'name': name,
        'email': '',
        'mobile': phone,
        'data_type': 'active',  # PADRONIZADO com o scraper que usa 'active'
        'page_source': 'excel_import',
        'additional_data': json.dumps(structured_data, ensure_ascii=False),
        'data_hash': data_hash,
        'scraped_at': datetime.now(),
        'session_info': json.dumps({'import_session': f'excel_import_{datetime.now().strftime("%Y%m%d_%H%M%S")}', 'data_date': str(date)}),
        'source': 'excel_import',
        'unique_id': f"{driver_id}_{data_hash[:8]}"
    }

@router.get("/drivers/analytics")
async def get_drivers_analytics():
    """Endpoint para obter dados agregados de motoristas para o dashboard"""
    try:
        DATABASE_URL = "postgresql://n8n_user:n8n_pw@148.230.73.27:5432/n8n_db"
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        
        # Query para buscar motoristas ativos - USANDO CAMPOS CORRETOS E FILTROS ESPECÍFICOS
        cursor.execute("""
            SELECT 
                driver_id, 
                name, 
                mobile,
                additional_data,
                scraped_at
            FROM drivers_data 
            WHERE data_type = 'active' 
            AND name IS NOT NULL 
            AND name != 'None'
            AND driver_id ~ '^[0-9]+$'  -- Apenas IDs numéricos
            AND LENGTH(driver_id) >= 8  -- IDs com pelo menos 8 dígitos
            ORDER BY driver_id
        """)
        
        rows = cursor.fetchall()
        drivers_data = []
        processed_drivers = set()  # Para evitar duplicatas por driver_id
        
        for row in rows:
            driver_id, name, mobile, additional_data, scraped_at = row
            
            # Evitar duplicatas pelo driver_id
            if driver_id in processed_drivers:
                continue
            processed_drivers.add(driver_id)
            
            # Parse do JSON - verificar se é string ou dict
            if isinstance(additional_data, str):
                data = json.loads(additional_data)
            elif isinstance(additional_data, dict):
                data = additional_data
            else:
                data = {}
            
            # USAR CAMPOS CORRETOS DA TABELA - Agora nome e mobile estão nos lugares certos
            try:
                # Extrair dados do raw_row se disponível para métricas adicionais
                headers = data.get('headers', [])
                raw_row = data.get('raw_row', [])
                
                # Dados principais da tabela (já corretos)
                real_driver_id = driver_id  # ID numérico único
                real_name = name  # Nome real do motorista 
                real_mobile = mobile  # Telefone correto
                
                # Extrair métricas do raw_row se disponível
                rides_last_30_days = 0
                rides_last_7_days = 0
                rating = 3.5
                last_login = ''
                status = 'inactive'
                city = 'Matupá'
                vehicle = ''
                email = ''
                
                if headers and raw_row and len(headers) == len(raw_row):
                    # Criar mapeamento header -> valor
                    mapped_data = {}
                    for i, header in enumerate(headers):
                        if i < len(raw_row):
                            mapped_data[header] = raw_row[i]
                    
                    # Extrair métricas se disponíveis
                    try:
                        rides_30d_str = mapped_data.get('Rides in Last 30 Days', '0')
                        rides_30d = int(rides_30d_str) if rides_30d_str and rides_30d_str.isdigit() else 0
                        rides_last_30_days = rides_30d
                    except:
                        rides_last_30_days = 0
                        
                    try:
                        rides_7d_str = mapped_data.get('Rides in Last 7 Days', '0')
                        rides_7d = int(rides_7d_str) if rides_7d_str and rides_7d_str.isdigit() else 0
                        rides_last_7_days = rides_7d
                    except:
                        rides_last_7_days = 0
                        
                    try:
                        rating_str = mapped_data.get('Driver Ratings', '35000')
                        rating_val = float(rating_str) if rating_str and rating_str.isdigit() else 35000
                        rating = min(5.0, max(1.0, rating_val / 10000))  # Converter para escala 1-5
                    except:
                        rating = 3.5
                    
                    # Outros campos
                    last_login = mapped_data.get('Last Login', '')
                    status_str = mapped_data.get('Status', 'Offline')
                    status = 'active' if status_str.lower() == 'online' else 'inactive'
                    city = mapped_data.get('Registered On', 'Matupá')
                    vehicle = mapped_data.get('Mobile', '')  # Veículo pode estar em Mobile
                    email = mapped_data.get('Email', '')
                
                # Determinar se está ativo baseado em corridas recentes
                total_rides = max(rides_last_30_days, rides_last_7_days)
                is_active = total_rides > 0 or status == 'active'
                
                drivers_data.append({
                    'driver_id': str(real_driver_id),  # ID numérico como string
                    'name': real_name,  # Nome real da tabela
                    'mobile': real_mobile,  # Telefone da tabela
                    'data': {
                        'profile': {
                            'city': city,
                            'vehicle': vehicle,
                            'email': email,
                            'status': 'active' if is_active else 'inactive',
                            'is_online': status == 'active'
                        },
                        'metrics': {
                            'rating': rating,
                            'rides_last_30_days': rides_last_30_days,
                            'rides_last_7_days': rides_last_7_days,
                            'total_rides': total_rides,
                            'last_login': last_login,
                            'success_rate': 85.0 if total_rides > 0 else 0.0  # Estimativa
                        },
                        'raw_data': mapped_data if headers and raw_row else {},
                        'original_data': data  # Manter dados originais para debug
                    },
                    'scraped_at': scraped_at.isoformat() if scraped_at else None
                })
                
            except Exception as e:
                print(f"Erro processando driver {driver_id}: {e}")
                # Fallback básico usando apenas dados da tabela
                drivers_data.append({
                    'driver_id': str(driver_id),
                    'name': name,
                    'mobile': mobile,
                    'data': {
                        'profile': {
                            'city': 'Matupá',
                            'status': 'active'
                        },
                        'metrics': {
                            'rating': 3.5,
                            'total_rides': 0
                        }
                    },
                    'scraped_at': scraped_at.isoformat() if scraped_at else None
                })
        
        conn.close()
        
        return {
            "success": True,
            "drivers": drivers_data,
            "total_records": len(drivers_data)
        }
        
    except Exception as e:
        print(f"Erro no endpoint drivers analytics: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
