from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.orm import relationship
from app.database.db import Base
from datetime import datetime

class CidadesDemografia(Base):
    __tablename__ = "cidades_demografia"

    id = Column(Integer, primary_key=True)
    cidade = Column(String, unique=True, nullable=False)
    populacao_censo_2022 = Column(Integer)
    populacao_estimada_2024 = Column(Integer)
    densidade_demografica = Column(Float)
    publico_alvo_15_44_anos = Column(Integer)
    publico_homens = Column(Integer)
    publico_mulheres = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relacionamentos
    campanhas = relationship("Campanha", back_populates="cidade_dados")
    metas_progressivas = relationship("MetasProgressivas", back_populates="cidade")

# Exemplo de script de inserção (para usar em migration ou seed)
cidades = [
    {
        "cidade": "Colíder",
        "populacao_censo_2022": 31370,
        "populacao_estimada_2024": 32010,
        "densidade_demografica": 10.08,
        "publico_alvo_15_44_anos": 14045,
        "publico_homens": 6975,
        "publico_mulheres": 7070
    },
    {
        "cidade": "Alta Floresta",
        "populacao_censo_2022": 58613,
        "populacao_estimada_2024": 61291,
        "densidade_demografica": 6.54,
        "publico_alvo_15_44_anos": 27522,
        "publico_homens": 13845,
        "publico_mulheres": 14037
    },
    {
        "cidade": "Nova Canaã do Norte",
        "populacao_censo_2022": 11707,
        "populacao_estimada_2024": 11771,
        "densidade_demografica": 1.97,
        "publico_alvo_15_44_anos": 5091,
        "publico_homens": 2587,
        "publico_mulheres": 2504
    },
    {
        "cidade": "Carlinda",
        "populacao_censo_2022": 10332,
        "populacao_estimada_2024": 10324,
        "densidade_demografica": 4.27,
        "publico_alvo_15_44_anos": 4171,
        "publico_homens": 2073,
        "publico_mulheres": 2098
    },
    {
        "cidade": "Paranaíta",
        "populacao_censo_2022": 11671,
        "populacao_estimada_2024": 11989,
        "densidade_demografica": 2.42,
        "publico_alvo_15_44_anos": 5032,
        "publico_homens": 2561,
        "publico_mulheres": 2471
    },
    {
        "cidade": "Monte Verde",
        "populacao_censo_2022": 8313,
        "populacao_estimada_2024": 8451,
        "densidade_demografica": 1.62,
        "publico_alvo_15_44_anos": 3844,
        "publico_homens": 1993,
        "publico_mulheres": 1851
    },
    {
        "cidade": "Nova Bandeirantes",
        "populacao_censo_2022": 13635,
        "populacao_estimada_2024": 14160,
        "densidade_demografica": 1.43,
        "publico_alvo_15_44_anos": 6115,
        "publico_homens": 3246,
        "publico_mulheres": 2869
    }
]

# Exemplo de uso:
# for c in cidades:
#     db.add(CidadesDemografia(**c))
# db.commit()
