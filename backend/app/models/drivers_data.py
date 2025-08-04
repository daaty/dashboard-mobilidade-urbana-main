from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class DriversData(Base):
    __tablename__ = "drivers_data"
    
    id = Column(Integer, primary_key=True, index=True)
    driver_id = Column(String, nullable=False)
    name = Column(String, nullable=False)
    email = Column(String)
    mobile = Column(String)
    data_type = Column(String, nullable=False)
    page_source = Column(String, nullable=False)
    additional_data = Column(Text, nullable=False)  # JSON data
    data_hash = Column(String, nullable=False)
    scraped_at = Column(DateTime, nullable=False)
    session_info = Column(String)
    source = Column(String)
    unique_id = Column(String)
