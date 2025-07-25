from sqlalchemy import Column, Integer, String, DateTime, Text
from app.database.db import Base
import os
from dotenv import load_dotenv

# Garante que o .env seja carregado
load_dotenv()

RIDES_TABLE_NAME = os.getenv("RIDES_TABLE_NAME", "rides_data")

class RidesData(Base):
    __tablename__ = RIDES_TABLE_NAME

    id = Column(Integer, primary_key=True, index=True)
    table_name = Column(String)
    data_hash = Column(String)
    ride_data = Column(Text)  # campo JSON armazenado como texto
    scraped_at = Column(DateTime)
    session_info = Column(String)
    source = Column(String)
