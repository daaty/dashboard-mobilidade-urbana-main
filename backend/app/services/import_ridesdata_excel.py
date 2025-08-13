import pandas as pd
import json
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.rides_data import RidesData
from app.database.db import SessionLocal

# Função utilitária para converter uma planilha em registros RidesData
# table_name: 'Completed Rides', 'Cancelled Rides', 'Missed Rides'
def import_excel_to_ridesdata(filepath, table_name, session: Session, source="import_excel"):
    df = pd.read_excel(filepath)
    records = df.values.tolist()
    ride_data = {
        "tableName": table_name,
        "newRecords": records
    }
    now = datetime.now()
    entry = RidesData(
        table_name=table_name,
        data_hash=None,  # pode ser calculado se necessário
        ride_data=json.dumps(ride_data, ensure_ascii=False),
        scraped_at=now,
        session_info=None,
        source=source
    )
    session.add(entry)
    session.commit()
    print(f"Importado {len(records)} registros para {table_name} em rides_data.")

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 3:
        print("Uso: python import_ridesdata_excel.py <arquivo.xlsx> <table_name>")
        print("table_name: 'Completed Rides', 'Cancelled Rides', 'Missed Rides'")
        exit(1)
    filepath = sys.argv[1]
    table_name = sys.argv[2]
    with SessionLocal() as session:
        import_excel_to_ridesdata(filepath, table_name, session)
