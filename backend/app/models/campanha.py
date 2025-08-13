from sqlalchemy import Column, Integer, String, Date, DECIMAL, TIMESTAMP
from app.database.db import Base

class Campanha(Base):
    __tablename__ = "campanhas"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False)
    fase = Column(String(20), nullable=False)
    cidade = Column(String(50), nullable=False)
    data_inicio = Column(Date, nullable=False)
    data_fim = Column(Date, nullable=False)
    tipo_campanha = Column(String(50), nullable=False)
    meta_quantidade = Column(Integer, nullable=False)
    orcamento_previsto = Column(DECIMAL(10,2), nullable=False)
    custo_real = Column(DECIMAL(10,2), default=0)
    status = Column(String(20), default='ativa')
    created_at = Column(TIMESTAMP, nullable=False)
