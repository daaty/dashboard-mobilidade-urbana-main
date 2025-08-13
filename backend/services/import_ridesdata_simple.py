from app.models.rides_data import RidesData
import json
import pandas as pd
import os
import hashlib
from typing import Dict
from datetime import datetime

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
                entry = RidesData(
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
