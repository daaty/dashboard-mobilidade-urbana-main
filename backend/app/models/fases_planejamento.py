"""
Model para gerenciar fases de planejamento do projeto de expansão
"""

from sqlalchemy import Column, Integer, String, Date, Float, DateTime, Text
from sqlalchemy.orm import relationship
from app.database.db import Base
from datetime import datetime

class FasesPlanejamento(Base):
    __tablename__ = "fases_planejamento"
    
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)  # "Fase 1", "Fase 2", "Fase 3"
    descricao = Column(Text)  # Descrição detalhada da fase
    
    # Datas de planejamento
    data_inicio = Column(Date, nullable=False)
    data_fim = Column(Date, nullable=False)
    data_inicio_real = Column(Date)  # Data real de início
    data_fim_real = Column(Date)     # Data real de conclusão
    
    # Status da fase
    status = Column(String, default="planejada")  # "planejada", "em_execucao", "concluida", "suspensa"
    progresso_percentual = Column(Float, default=0.0)  # 0.0 a 100.0
    
    # Orçamento e finanças
    orcamento_previsto = Column(Float, nullable=False)
    orcamento_empenhado = Column(Float, default=0.0)
    orcamento_pago = Column(Float, default=0.0)
    orcamento_liquidado = Column(Float, default=0.0)
    
    # Metas da fase
    meta_cidades = Column(Integer, default=0)  # Quantas cidades serão ativadas
    meta_motoristas = Column(Integer, default=0)  # Total de motoristas esperados
    meta_corridas = Column(Integer, default=0)   # Total de corridas esperadas
    meta_receita = Column(Float, default=0.0)    # Receita esperada da fase

    # Prazo em meses (novo campo)
    prazo_meses = Column(Integer, default=1)

    # Resultados reais
    resultado_cidades = Column(Integer, default=0)
    resultado_motoristas = Column(Integer, default=0)
    resultado_corridas = Column(Integer, default=0)
    resultado_receita = Column(Float, default=0.0)

    # Responsável e observações
    responsavel = Column(String)  # Nome do responsável pela fase
    observacoes = Column(Text)    # Observações e notas importantes
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<FasesPlanejamento(nome='{self.nome}', status='{self.status}')>"
    
    @property
    def esta_ativa(self):
        """Verifica se a fase está atualmente ativa"""
        return self.status == "em_execucao"
    
    @property
    def percentual_orcamento_usado(self):
        """Calcula percentual do orçamento já utilizado"""
        if self.orcamento_previsto > 0:
            return (self.orcamento_empenhado / self.orcamento_previsto) * 100
        return 0.0
    
    @property
    def roi_fase(self):
        """Calcula ROI da fase baseado em receita vs investimento"""
        if self.orcamento_pago > 0 and self.resultado_receita > 0:
            return ((self.resultado_receita - self.orcamento_pago) / self.orcamento_pago) * 100
        return 0.0
    
    def calcular_progresso_automatico(self):
        """Calcula progresso baseado nas metas vs resultados"""
        progressos = []
        
        if self.meta_cidades > 0:
            progressos.append((self.resultado_cidades / self.meta_cidades) * 100)
        if self.meta_motoristas > 0:
            progressos.append((self.resultado_motoristas / self.meta_motoristas) * 100)
        if self.meta_corridas > 0:
            progressos.append((self.resultado_corridas / self.meta_corridas) * 100)
        
        if progressos:
            self.progresso_percentual = min(100.0, sum(progressos) / len(progressos))
        
        return self.progresso_percentual
