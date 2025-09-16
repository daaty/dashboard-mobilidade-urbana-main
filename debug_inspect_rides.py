import os
import sys
import json
from datetime import datetime

ROOT = os.path.dirname(os.path.abspath(__file__))
# Garantir que o diretório 'backend' esteja no PYTHONPATH para importar o pacote 'app'
BACKEND_DIR = os.path.join(ROOT, 'backend')
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

try:
    # Import session and model
    from backend.app.database.db import SyncSessionLocal
    from backend.app.models.rides_data import RidesData
except Exception as e:
    print('Erro ao importar módulos do projeto:', e)
    sys.exit(1)

def main(limit=10):
    session = SyncSessionLocal()
    try:
        q = session.query(RidesData).order_by(RidesData.id.desc()).limit(limit).all()
        for r in q:
            print('='*80)
            print('id:', r.id)
            print('table_name:', r.table_name)
            rd = r.ride_data
            if rd is None:
                print('ride_data: None')
                continue
            # try parse JSON
            try:
                data = json.loads(rd) if isinstance(rd, str) else rd
            except Exception:
                data = rd
            # show keys and sample
            if isinstance(data, dict):
                print('keys:', list(data.keys()))
                print('tableName:', data.get('tableName'))
                new_records = data.get('newRecords', [])
                print('newRecords count:', len(new_records))
                if len(new_records) > 0:
                    print('sample record (first):')
                    rec = new_records[0]
                    try:
                        print(json.dumps(rec, ensure_ascii=False)[:1000])
                    except Exception:
                        print(str(rec)[:1000])
            else:
                print('ride_data (non-dict) sample:', str(data)[:1000])
    finally:
        session.close()

if __name__ == '__main__':
    main(10)
