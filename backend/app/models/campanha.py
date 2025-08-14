
from sqlalchemy import Column, Integer, String, Date, DECIMAL, TIMESTAMP, Float, ForeignKey
from sqlalchemy.orm import relationship
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

    # Novos campos estratégicos
    parte_campanha = Column(String(20))  # "Part 1" ou "Part 2"
    tipo_gasto = Column(String(30))  # "trafego_pago", "operacoes", "outros"
    pagamento_programado = Column(Date)
    status_financeiro = Column(String(20))  # "empenhado", "pago", "liquidado"
    meta_percentual_populacao = Column(Float)  # 0.5, 1, 2, 10

    # Relacionamento com dados demográficos
    cidade_id = Column(Integer, ForeignKey('cidades_demografia.id'))
    cidade_dados = relationship("CidadesDemografia", back_populates="campanhas")
    cidade_dados = relationship("CidadesDemografia")
