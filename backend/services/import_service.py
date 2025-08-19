from app.models.rides_data import RidesData as AsyncRidesData
from app.models.drivers_data import DriversData as AsyncDriversData
from app.database.db import SessionLocal as AsyncSessionLocal
import json
import pandas as pd
import os
import hashlib
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from werkzeug.utils import secure_filename
# from models import db, Corrida, Motorista, Meta, ImportLog, StatusCorrida, StatusMotorista, OrigemDado  # Removido temporariamente

class ImportService:

    def import_ridesdata(self, filepath: str, table_name: str, session=None, source="import_excel") -> Dict:
        """Importa planilha para rides_data, igual ao scraper"""
        import_result = {
            'success': False,
            'imported': 0,
            'error': None
        }
        try:
            print(f"Tentando ler arquivo: {filepath}")
            df = pd.read_excel(filepath)
            print(f"Arquivo lido com sucesso. Linhas: {len(df)}")
            
            # Converter dados para formatos serializáveis em JSON
            df_serializable = df.copy()
            for col in df_serializable.columns:
                if df_serializable[col].dtype == 'datetime64[ns]':
                    df_serializable[col] = df_serializable[col].dt.strftime('%Y-%m-%d %H:%M:%S')
                elif df_serializable[col].dtype == 'object':
                    # Converter timestamps para string se houver
                    df_serializable[col] = df_serializable[col].astype(str)
            
            records = df_serializable.values.tolist()
            ride_data = {
                "tableName": table_name,
                "newRecords": records
            }
            
            # Gerar hash dos dados
            data_string = json.dumps(ride_data, sort_keys=True, ensure_ascii=False)
            data_hash = hashlib.md5(data_string.encode('utf-8')).hexdigest()
            
            now = datetime.now()
            
            # Para sessão síncrona do FastAPI
            if session is not None:
                print(f"Usando sessão fornecida para inserir {len(records)} registros")
                # Usar o modelo síncrono correto
                from app.models.rides_data import RidesData as SyncRidesData
                entry = SyncRidesData(
                    table_name=table_name,
                    data_hash=data_hash,
                    ride_data=json.dumps(ride_data, ensure_ascii=False),
                    scraped_at=now,
                    session_info=None,
                    source=source
                )
                session.add(entry)
                session.commit()
                print("Commit realizado com sucesso")
            else:
                print("Nenhuma sessão fornecida")
                import_result['error'] = "Sessão de banco não fornecida"
                return import_result
                
            import_result['success'] = True
            import_result['imported'] = len(records)
            print(f"Importação concluída: {len(records)} registros")
        except Exception as e:
            print(f"Erro na importação: {str(e)}")
            import_result['error'] = str(e)
        return import_result

    def import_driversdata(self, filepath: str, table_name: str, session=None, source="import_excel") -> Dict:
        """Importa planilha para drivers_data"""
        import_result = {
            'success': False,
            'imported': 0,
            'errors': [],
            'total_rows': 0
        }
        
        try:
            # Ler planilha
            df = pd.read_excel(filepath)
            import_result['total_rows'] = len(df)
            
            # Log do que foi encontrado na planilha
            print(f"📊 Encontradas {len(df)} linhas na planilha")
            print(f"📋 Colunas encontradas: {list(df.columns)}")
            
            # Processar cada linha da planilha
            imported_count = 0
            
            for index, row in df.iterrows():
                try:
                    # Mapear dados do motorista usando padrões comuns de colunas
                    driver_data = self.map_row_to_driver(row, index)
                    
                    if session is not None:
                        # Usar sessão síncrona fornecida
                        from app.models.drivers_data import DriversData as SyncDriversData
                        entry = SyncDriversData(
                            driver_id=driver_data['driver_id'],
                            name=driver_data['name'],
                            email=driver_data.get('email', ''),
                            mobile=driver_data.get('mobile', ''),
                            data_type=driver_data['data_type'],
                            page_source=driver_data['page_source'],
                            additional_data=driver_data['additional_data'],
                            data_hash=driver_data['data_hash'],
                            scraped_at=driver_data['scraped_at'],
                            session_info=driver_data.get('session_info'),
                            source=source,
                            unique_id=driver_data.get('unique_id')
                        )
                        session.add(entry)
                        session.commit()
                        imported_count += 1
                        print(f"✅ Motorista {driver_data['name']} importado com sucesso")
                    else:
                        import_result['error'] = "Sessão de banco não fornecida"
                        return import_result
                        
                except Exception as e:
                    error_msg = f"Erro na linha {index + 2}: {str(e)}"
                    import_result['errors'].append(error_msg)
                    print(f"❌ {error_msg}")
                    continue
            
            import_result['imported'] = imported_count
            import_result['success'] = imported_count > 0
            
            print(f"🎉 Importação concluída: {imported_count} motoristas importados")
            
        except Exception as e:
            import_result['error'] = f"Erro geral na importação: {str(e)}"
            print(f"💥 Erro geral: {str(e)}")
            
        return import_result

    def map_row_to_driver(self, row: pd.Series, index: int) -> Dict:
        """Mapeia uma linha da planilha para os campos da tabela drivers_data usando o esquema específico da planilha"""
        import hashlib
        from datetime import datetime
        
        # Converter para dicionário
        row_dict = row.to_dict()
        
        # Função auxiliar para obter valor seguro
        def get_safe_value(column_name, default=''):
            try:
                value = row_dict.get(column_name, default)
                if pd.isna(value) or value is None:
                    return default
                return str(value).strip()
            except:
                return default
        
        def get_numeric_value(column_name, default=0):
            try:
                value = row_dict.get(column_name, default)
                if pd.isna(value) or value is None:
                    return default
                return int(float(value))
            except:
                return default
        
        # Extrair dados principais baseado na estrutura real da planilha
        driver_id = get_safe_value('Driver ID', f'DRV_{index + 1:04d}')
        name = get_safe_value('Driver Name', f'Motorista_{index + 1}')
        phone = get_safe_value('Phone Number', '')
        city = get_safe_value('CITY', '')
        vehicle = get_safe_value('Vehicle', '')
        
        # Converter phone number para string formatada
        if phone and phone != '':
            try:
                # Converter para string limpa
                phone_clean = str(int(float(phone)))
                if len(phone_clean) == 11:  # Formato brasileiro
                    phone = f"+55{phone_clean}"
                else:
                    phone = phone_clean
            except:
                phone = str(phone)
        
        # Coletar métricas de corridas
        request_sent = get_numeric_value('Request Sent', 0)
        requests_received = get_numeric_value('Requests Received', 0)
        success_rides = get_numeric_value('Success Rides', 0)
        user_cancelled = get_numeric_value('User Cancelled Rides', 0)
        driver_cancelled = get_numeric_value('Driver Cancelled Rides', 0)
        rejected_rides = get_numeric_value('Rejected Rides', 0)
        missed_rides = get_numeric_value('Missed Rides', 0)
        active_days = get_safe_value('Active Days', '0')
        online_hours = get_safe_value('Online Hours', '0')
        
        # Calcular total de corridas (successful + cancelled)
        total_rides = success_rides + user_cancelled + driver_cancelled
        
        # Calcular rating baseado na performance
        if requests_received > 0:
            success_rate = (success_rides / requests_received) * 100
            rating = round(min(5.0, max(1.0, success_rate / 20)), 1)  # Converte % para escala 1-5
        else:
            rating = 3.0
        
        # Determinar status baseado na atividade
        status = 'active' if success_rides > 0 or requests_received > 0 else 'inactive'
        
        # Criar dados adicionais detalhados
        additional_data = {
            'row_index': index,
            'import_timestamp': datetime.now().isoformat(),
            'performance_metrics': {
                'request_sent': request_sent,
                'requests_received': requests_received,
                'success_rides': success_rides,
                'user_cancelled_rides': user_cancelled,
                'driver_cancelled_rides': driver_cancelled,
                'rejected_rides': rejected_rides,
                'missed_rides': missed_rides,
                'success_rate': round((success_rides / max(requests_received, 1)) * 100, 2),
                'acceptance_rate': round((requests_received / max(request_sent, 1)) * 100, 2)
            },
            'activity_info': {
                'active_days': active_days,
                'online_hours': online_hours,
                'total_rides': total_rides,
                'avg_rides_per_day': round(total_rides / max(1, get_numeric_value('Active Days', 1)), 2) if active_days != '0' else 0
            },
            'profile_info': {
                'city': city,
                'vehicle_type': vehicle,
                'phone': phone,
                'rating': rating,
                'status': status
            },
            'import_info': {
                'source_file': 'Dados Completos Motoristas.xlsx',
                'original_data': {k: str(v) if pd.notna(v) else '' for k, v in row_dict.items()}
            }
        }
        
        # Criar hash único baseado nos dados principais
        hash_string = f"{driver_id}_{name}_{phone}_{city}"
        data_hash = hashlib.md5(hash_string.encode()).hexdigest()
        
        return {
            'driver_id': str(driver_id),
            'name': name,
            'email': '',  # Não disponível na planilha
            'mobile': phone,
            'data_type': 'driver_profile',
            'page_source': 'excel_import',
            'additional_data': json.dumps(additional_data, ensure_ascii=False),
            'data_hash': data_hash,
            'scraped_at': datetime.now(),
            'session_info': f'excel_import_{datetime.now().strftime("%Y%m%d_%H%M%S")}',
            'unique_id': f"{driver_id}_{data_hash[:8]}"
        }
    """Serviço para importação de planilhas locais"""
    
    SUPPORTED_FORMATS = ['.xlsx', '.xls', '.csv']
    MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB
    
    def __init__(self, upload_folder: str = 'uploads'):
        self.upload_folder = upload_folder
        self.ensure_upload_folder()
    
    def ensure_upload_folder(self):
        """Garante que a pasta de upload existe"""
        if not os.path.exists(self.upload_folder):
            os.makedirs(self.upload_folder)
    
    def validate_file(self, file) -> Dict:
        """Valida o arquivo enviado"""
        if not file or not file.filename:
            return {
                'valid': False,
                'error': 'Nenhum arquivo selecionado'
            }
        
        # Verificar extensão
        filename = secure_filename(file.filename)
        file_ext = os.path.splitext(filename)[1].lower()
        
        if file_ext not in self.SUPPORTED_FORMATS:
            return {
                'valid': False,
                'error': f'Formato não suportado. Use: {", ".join(self.SUPPORTED_FORMATS)}'
            }
        
        # Verificar tamanho do arquivo
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)
        
        if file_size > self.MAX_FILE_SIZE:
            return {
                'valid': False,
                'error': f'Arquivo muito grande. Máximo: {self.MAX_FILE_SIZE // (1024*1024)}MB'
            }
        
        return {
            'valid': True,
            'filename': filename,
            'size': file_size,
            'extension': file_ext
        }
    
    def save_uploaded_file(self, file, filename: str) -> str:
        """Salva o arquivo enviado"""
        filepath = os.path.join(self.upload_folder, filename)
        file.save(filepath)
        return filepath
    
    def read_file_data(self, filepath: str) -> Tuple[pd.DataFrame, Dict]:
        """Lê dados do arquivo"""
        try:
            file_ext = os.path.splitext(filepath)[1].lower()
            
            if file_ext == '.csv':
                # Tentar diferentes encodings para CSV
                encodings = ['utf-8', 'latin-1', 'iso-8859-1', 'cp1252']
                df = None
                
                for encoding in encodings:
                    try:
                        df = pd.read_csv(filepath, encoding=encoding)
                        break
                    except UnicodeDecodeError:
                        continue
                
                if df is None:
                    raise Exception("Não foi possível decodificar o arquivo CSV")
                    
            elif file_ext in ['.xlsx', '.xls']:
                df = pd.read_excel(filepath)
            else:
                raise Exception(f"Formato não suportado: {file_ext}")
            
            return df, {
                'success': True,
                'rows': len(df),
                'columns': list(df.columns)
            }
            
        except Exception as e:
            return None, {
                'success': False,
                'error': str(e)
            }
    
    def preview_import(self, filepath: str, import_type: str) -> Dict:
        """Gera preview dos dados antes da importação"""
        df, read_result = self.read_file_data(filepath)
        
        if not read_result['success']:
            return read_result
        
        # Mapear colunas baseado no tipo de importação
        column_mapping = self.get_column_mapping(import_type)
        
        # Detectar possível mapeamento automático
        detected_mapping = self.detect_column_mapping(df.columns, column_mapping)
        
        # Amostra dos dados (primeiras 5 linhas)
        sample_data = df.head(5).to_dict('records')
        
        return {
            'success': True,
            'total_rows': len(df),
            'columns': list(df.columns),
            'sample_data': sample_data,
            'detected_mapping': detected_mapping,
            'required_fields': column_mapping['required'],
            'optional_fields': column_mapping['optional']
        }
    
    def get_column_mapping(self, import_type: str) -> Dict:
        """Retorna mapeamento de colunas para cada tipo de importação"""
        mappings = {
            'corridas': {
                'required': {
                    'data': ['data', 'date', 'Data', 'Date'],
                    'usuario_nome': ['usuario_nome', 'usuario', 'cliente', 'nome_usuario', 'Nome Usuário', 'Cliente'],
                    'motorista_nome': ['motorista_nome', 'motorista', 'driver', 'Nome Motorista', 'Motorista'],
                    'municipio': ['municipio', 'cidade', 'city', 'Municipio', 'Cidade'],
                    'status': ['status', 'situacao', 'Status', 'Situação']
                },
                'optional': {
                    'usuario_telefone': ['usuario_telefone', 'telefone_usuario', 'tel_usuario', 'Tel Usuário'],
                    'valor': ['valor', 'preco', 'price', 'Valor', 'Preço'],
                    'distancia': ['distancia', 'distance', 'Distância', 'Distancia'],
                    'tempo_corrida': ['tempo_corrida', 'tempo', 'duration', 'Tempo', 'Duração'],
                    'avaliacao': ['avaliacao', 'rating', 'nota', 'Avaliação', 'Nota'],
                    'motivo_cancelamento': ['motivo_cancelamento', 'motivo', 'reason', 'Motivo']
                }
            },
            'motoristas': {
                'required': {
                    'nome': ['nome', 'name', 'Nome', 'Name'],
                    'municipio': ['municipio', 'cidade', 'city', 'Municipio', 'Cidade']
                },
                'optional': {
                    'telefone': ['telefone', 'phone', 'tel', 'Telefone'],
                    'status': ['status', 'situacao', 'Status', 'Situação'],
                    'data_cadastro': ['data_cadastro', 'cadastro', 'registration_date', 'Data Cadastro']
                }
            },
            'metas': {
                'required': {
                    'municipio': ['municipio', 'cidade', 'city', 'Municipio', 'Cidade'],
                    'mes': ['mes', 'month', 'data', 'Mês', 'Data'],
                    'meta_corridas': ['meta_corridas', 'meta', 'target_rides', 'Meta Corridas']
                },
                'optional': {
                    'meta_receita': ['meta_receita', 'receita', 'target_revenue', 'Meta Receita'],
                    'meta_motoristas': ['meta_motoristas', 'motoristas', 'target_drivers', 'Meta Motoristas']
                }
            }
        }
        
        return mappings.get(import_type, {'required': {}, 'optional': {}})
    
    def detect_column_mapping(self, file_columns: List[str], mapping_config: Dict) -> Dict:
        """Detecta automaticamente o mapeamento de colunas"""
        detected = {}
        
        for field, possible_names in {**mapping_config['required'], **mapping_config['optional']}.items():
            for col in file_columns:
                if col.lower() in [name.lower() for name in possible_names]:
                    detected[field] = col
                    break
        
        return detected
    
    def import_corridas(self, filepath: str, column_mapping: Dict) -> Dict:
        """Importa corridas do arquivo"""
        # Criar log de importação
        import_log = ImportLog(
            filename=os.path.basename(filepath),
            file_size=os.path.getsize(filepath),
            import_type='corridas',
            status='processing'
        )
        db.session.add(import_log)
        db.session.commit()
        
        try:
            df, read_result = self.read_file_data(filepath)
            
            if not read_result['success']:
                import_log.status = 'failed'
                import_log.error_message = read_result['error']
                import_log.completed_at = datetime.utcnow()
                db.session.commit()
                return read_result
            
            import_log.total_rows = len(df)
            db.session.commit()
            
            success_count = 0
            error_count = 0
            errors = []
            
            for index, row in df.iterrows():
                try:
                    # Mapear dados da linha
                    corrida_data = self.map_row_to_corrida(row, column_mapping)
                    
                    # Criar corrida
                    corrida = Corrida(**corrida_data)
                    db.session.add(corrida)
                    
                    success_count += 1
                    
                except Exception as e:
                    error_count += 1
                    errors.append(f"Linha {index + 2}: {str(e)}")
                    
                    # Limitar número de erros reportados
                    if len(errors) > 10:
                        errors.append(f"... e mais {error_count - 10} erros")
                        break
            
            # Commit das corridas
            db.session.commit()
            
            # Atualizar log
            import_log.success_rows = success_count
            import_log.error_rows = error_count
            import_log.status = 'completed' if error_count == 0 else 'completed_with_errors'
            import_log.completed_at = datetime.utcnow()
            
            if errors:
                import_log.error_message = '\n'.join(errors[:10])
            
            db.session.commit()
            
            # Recalcular métricas após importação bem-sucedida
            if success_count > 0:
                try:
                    from backend.services.sync_service import DataSyncService
                    sync_service = DataSyncService()
                    sync_service.recalculate_daily_metrics()
                    print(f"✅ Métricas recalculadas após importação de {success_count} corridas")
                except Exception as sync_error:
                    print(f"⚠️ Erro ao recalcular métricas: {sync_error}")
            
            return {
                'success': True,
                'imported': success_count,
                'errors': error_count,
                'error_details': errors[:10],
                'import_log_id': import_log.id
            }
            
        except Exception as e:
            db.session.rollback()
            import_log.status = 'failed'
            import_log.error_message = str(e)
            import_log.completed_at = datetime.utcnow()
            db.session.commit()
            
            return {
                'success': False,
                'error': str(e),
                'import_log_id': import_log.id
            }
    
    def map_row_to_corrida(self, row: pd.Series, column_mapping: Dict) -> Dict:
        """Mapeia uma linha do DataFrame para dados de Corrida"""
        data = {}
        
        # Campos obrigatórios
        data['data'] = self.parse_datetime(row.get(column_mapping.get('data')))
        data['usuario_nome'] = str(row.get(column_mapping.get('usuario_nome', ''), '')).strip()
        data['motorista_nome'] = str(row.get(column_mapping.get('motorista_nome', ''), '')).strip()
        data['municipio'] = str(row.get(column_mapping.get('municipio', ''), '')).strip()
        
        # Status
        status_value = str(row.get(column_mapping.get('status', ''), '')).strip().lower()
        if status_value in ['concluida', 'concluída', 'completed']:
            data['status'] = StatusCorrida.CONCLUIDA
        elif status_value in ['cancelada', 'cancelled']:
            data['status'] = StatusCorrida.CANCELADA
        elif status_value in ['perdida', 'lost']:
            data['status'] = StatusCorrida.PERDIDA
        else:
            data['status'] = StatusCorrida.CONCLUIDA  # Default
        
        # Campos opcionais
        if 'usuario_telefone' in column_mapping:
            data['usuario_telefone'] = str(row.get(column_mapping['usuario_telefone'], '')).strip()
        
        if 'valor' in column_mapping:
            data['valor'] = self.parse_decimal(row.get(column_mapping['valor']))
        
        if 'distancia' in column_mapping:
            data['distancia'] = self.parse_float(row.get(column_mapping['distancia']))
        
        if 'tempo_corrida' in column_mapping:
            data['tempo_corrida'] = self.parse_int(row.get(column_mapping['tempo_corrida']))
        
        if 'avaliacao' in column_mapping:
            data['avaliacao'] = self.parse_int(row.get(column_mapping['avaliacao']))
        
        if 'motivo_cancelamento' in column_mapping:
            data['motivo_cancelamento'] = str(row.get(column_mapping['motivo_cancelamento'], '')).strip()
        
        # Origem do dado
        data['origem_dado'] = OrigemDado.IMPORT
        
        return data
    
    def parse_datetime(self, value) -> datetime:
        """Converte valor para datetime"""
        if pd.isna(value):
            raise ValueError("Data é obrigatória")
        
        if isinstance(value, datetime):
            return value
        
        # Tentar diferentes formatos
        formats = [
            '%Y-%m-%d %H:%M:%S',
            '%Y-%m-%d',
            '%d/%m/%Y %H:%M:%S',
            '%d/%m/%Y',
            '%m/%d/%Y',
            '%d-%m-%Y'
        ]
        
        value_str = str(value).strip()
        
        for fmt in formats:
            try:
                return datetime.strptime(value_str, fmt)
            except ValueError:
                continue
        
        raise ValueError(f"Formato de data inválido: {value}")
    
    def parse_decimal(self, value) -> Optional[float]:
        """Converte valor para decimal"""
        if pd.isna(value) or value == '':
            return None
        
        try:
            # Remover caracteres não numéricos (exceto . e ,)
            clean_value = str(value).replace('R$', '').replace(' ', '').replace(',', '.')
            return float(clean_value)
        except (ValueError, TypeError):
            return None
    
    def parse_float(self, value) -> Optional[float]:
        """Converte valor para float"""
        if pd.isna(value) or value == '':
            return None
        
        try:
            return float(str(value).replace(',', '.'))
        except (ValueError, TypeError):
            return None
    
    def parse_int(self, value) -> Optional[int]:
        """Converte valor para int"""
        if pd.isna(value) or value == '':
            return None
        
        try:
            return int(float(str(value)))
        except (ValueError, TypeError):
            return None
    
    def get_import_history(self, limit: int = 50) -> List[Dict]:
        """Retorna histórico de importações"""
        logs = ImportLog.query.order_by(ImportLog.started_at.desc()).limit(limit).all()
        return [log.to_dict() for log in logs]
    
    def cleanup_old_files(self, days: int = 7):
        """Remove arquivos antigos da pasta de upload"""
        cutoff_date = datetime.now() - timedelta(days=days)
        
        for filename in os.listdir(self.upload_folder):
            filepath = os.path.join(self.upload_folder, filename)
            
            if os.path.isfile(filepath):
                file_time = datetime.fromtimestamp(os.path.getmtime(filepath))
                
                if file_time < cutoff_date:
                    try:
                        os.remove(filepath)
                        print(f"Arquivo removido: {filename}")
                    except Exception as e:
                        print(f"Erro ao remover {filename}: {e}")
