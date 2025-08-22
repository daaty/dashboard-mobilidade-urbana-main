from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class DriverPersonalDetails(Base):
    __tablename__ = "driver_personal_details"
    
    id = Column(Integer, primary_key=True, index=True)
    driver_id = Column(String, nullable=False, index=True)
    city = Column(String, nullable=False)
    personal_data = Column(JSONB, nullable=False)
    rides_history = Column(JSONB, nullable=True)
    wallet_transactions = Column(JSONB, nullable=True)
    subscription_history = Column(JSONB, nullable=True)
    additional_info = Column(JSONB, nullable=True)
    extracted_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, nullable=True)
    extraction_source = Column(String, nullable=True)
    data_hash = Column(String, nullable=False)
