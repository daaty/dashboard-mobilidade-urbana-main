import os
import sys
import json
from collections import defaultdict

ROOT = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.join(ROOT, 'backend')
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

try:
    from backend.app.database.db import SyncSessionLocal
    from backend.app.models.rides_data import RidesData
except Exception as e:
    print('Erro ao importar módulos:', e)
    sys.exit(1)

def short(v):
    try:
        s = str(v)
        return s if len(s) < 60 else s[:57] + '...'
    except Exception:
        return repr(v)

def inspect(limit=50):
    session = SyncSessionLocal()
    try:
        rows = session.query(RidesData).order_by(RidesData.id.desc()).limit(limit).all()
        grouped = defaultdict(list)
        for r in rows:
            rd = r.ride_data
            if isinstance(rd, str):
                try:
                    rd = json.loads(rd)
                except Exception:
                    pass
            if not isinstance(rd, dict):
                continue
            table = rd.get('tableName', 'unknown')
            for rec in rd.get('newRecords', [])[:3]:
                grouped[table].append(rec)

        for table, recs in grouped.items():
            print('\n' + '='*80)
            print('Table:', table, ' - samples:', len(recs))
            # show up to 3 samples and per-index values
            for i, rec in enumerate(recs[:3]):
                print('\n-- sample', i+1)
                for idx, val in enumerate(rec):
                    print(f'[{idx:02d}]', short(val))
    finally:
        session.close()

if __name__ == '__main__':
    inspect(100)
