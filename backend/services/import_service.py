import pandas as pd
import os
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from werkzeug.utils import secure_filename
from backend.models import db, Corrida, Motorista, Meta, ImportLog, StatusCorrida, StatusMotorista, OrigemDado

class ImportService:
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
