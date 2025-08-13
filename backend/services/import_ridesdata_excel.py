import pandas as pd
import json
from datetime import datetime
from sqlalchemy.orm import sessionmaker
from app.database.db import engine
from app.models.rides_data import RidesData
import os

# Config
EXCEL_FILES = [
    'CorridasConcluidas.xlsx',
    'CorridasCanceladas.xlsx',
    'CorridasMissed.xlsx'
]
TABLE_NAME_MAP = {
    'CorridasConcluidas.xlsx': 'Completed Rides',
    'CorridasCanceladas.xlsx': 'Cancelled Rides',
    'CorridasMissed.xlsx': 'Missed Rides',
}

Session = sessionmaker(bind=engine)
session = Session()

def excel_to_ridesdata(filepath, table_name):
    df = pd.read_excel(filepath)
    # Ajuste conforme o cabeçalho real da planilha
    new_records = df.values.tolist()
    ride_data = {
        'tableName': table_name,
        'newRecords': new_records
    }
    rd = RidesData(
        table_name=table_name,
        data_hash=None,
        ride_data=json.dumps(ride_data, ensure_ascii=False),
        scraped_at=datetime.now(),
        session_info=None,
        source='import_excel'
    )
    session.add(rd)
    session.commit()
    print(f"Importado {filepath} para rides_data com {len(new_records)} registros.")

if __name__ == "__main__":
    for file in EXCEL_FILES:
        if os.path.exists(file):
            excel_to_ridesdata(file, TABLE_NAME_MAP[file])
        else:
            print(f"Arquivo não encontrado: {file}")
