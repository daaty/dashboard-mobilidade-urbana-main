"""
Model para metas progressivas por cidade baseadas em tempo e população
"""

from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey, Boolean, Text
from sqlalchemy.orm import relationship
from app.database.db import Base
from datetime import datetime

class MetasProgressivas(Base):
    __tablename__ = "metas_progressivas"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Relacionamento com cidade
    cidade_id = Column(Integer, ForeignKey('cidades_demografia.id'), nullable=False)
    cidade = relationship("CidadesDemografia", back_populates="metas_progressivas")
    
    # Relacionamento com fase (opcional)
    fase_id = Column(Integer, ForeignKey('fases_planejamento.id'))
    fase = relationship("FasesPlanejamento")
    
    # Período da meta
    mes = Column(Integer, nullable=False)  # 1, 2, 3, 6, 12 (meses desde início)
    
    # Percentual do público-alvo
    percentual_publico = Column(Float, nullable=False)  # 0.5, 1.0, 2.0, 10.0 (%)
    tipo_meta = Column(String, nullable=False)  # "muito_baixa", "baixa", "media", "alta", "agressiva"
    
    # Metas numéricas
    meta_corridas = Column(Integer, nullable=False)
    meta_motoristas = Column(Integer, nullable=False)
    meta_usuarios_ativos = Column(Integer, default=0)
    meta_receita = Column(Float, default=0.0)
    
    # Metas de qualidade
    
    # Resultados reais
    resultado_corridas = Column(Integer, default=0)
    resultado_motoristas = Column(Integer, default=0)
    resultado_usuarios_ativos = Column(Integer, default=0)
    resultado_receita = Column(Float, default=0.0)
    resultado_satisfacao = Column(Float, default=0.0)
    resultado_tempo_resposta = Column(Float, default=0.0)
    resultado_taxa_cancelamento = Column(Float, default=0.0)
    
    # Status e controle
    status = Column(String, default="ativa")  # "ativa", "pausada", "concluida", "cancelada"
    atingida = Column(Boolean, default=False)
    
    # Investimento para atingir meta
    investimento_previsto = Column(Float, default=0.0)
    investimento_realizado = Column(Float, default=0.0)
    
    # Observações e estratégia
    estrategia = Column(Text)  # Como atingir esta meta
    observacoes = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<MetasProgressivas(cidade_id={self.cidade_id}, mes={self.mes}, tipo='{self.tipo_meta}')>"
    
    @property
    def percentual_atingido_corridas(self):
        """Percentual atingido da meta de corridas"""
        if self.meta_corridas > 0:
            return min(100.0, (self.resultado_corridas / self.meta_corridas) * 100)
        return 0.0
    
    @property
    def percentual_atingido_motoristas(self):
        """Percentual atingido da meta de motoristas"""
        if self.meta_motoristas > 0:
            return min(100.0, (self.resultado_motoristas / self.meta_motoristas) * 100)
        return 0.0
    
    @property
    def percentual_atingido_geral(self):
        """Percentual geral atingido (média das metas principais)"""
        percentuais = [
            self.percentual_atingido_corridas,
            self.percentual_atingido_motoristas
        ]
        
        if self.meta_receita > 0:
            percentual_receita = min(100.0, (self.resultado_receita / self.meta_receita) * 100)
            percentuais.append(percentual_receita)
        
        return sum(percentuais) / len(percentuais) if percentuais else 0.0
    
    @property
    def roi_meta(self):
        """ROI da meta específica"""
        if self.investimento_realizado > 0 and self.resultado_receita > 0:
            return ((self.resultado_receita - self.investimento_realizado) / self.investimento_realizado) * 100
        return 0.0
    
    def verificar_se_atingida(self):
        """Verifica automaticamente se a meta foi atingida"""
        percentual_geral = self.percentual_atingido_geral
        
        if percentual_geral >= 100.0 and not self.atingida:
            self.atingida = True
            self.data_atingida = datetime.utcnow()
            self.status = "concluida"
        elif percentual_geral < 100.0 and self.atingida:
            self.atingida = False
            self.data_atingida = None
            self.status = "ativa"
        
        return self.atingida
    
    @classmethod
    def calcular_meta_automatica(cls, publico_alvo, percentual, mes):
        """
        Calcula metas automáticas baseadas no público-alvo e percentual desejado
        """
        usuarios_meta = int(publico_alvo * (percentual / 100))
        
        # Estimativas baseadas em padrões da indústria
        corridas_por_usuario_mes = 2.5  # Média de corridas por usuário ativo por mês
        motoristas_por_100_corridas = 2.5  # Relação motoristas/corridas
        receita_por_corrida = 2.50  # Ticket médio
        
        meta_corridas = int(usuarios_meta * corridas_por_usuario_mes * mes)
        meta_motoristas = max(1, int(meta_corridas * (motoristas_por_100_corridas / 100)))
        meta_receita = meta_corridas * receita_por_corrida
        
        # Classificar tipo de meta baseado no percentual
        if percentual <= 0.5:
            tipo_meta = "muito_baixa"
        elif percentual <= 1.0:
            tipo_meta = "baixa"
        elif percentual <= 2.0:
            tipo_meta = "media"
        elif percentual <= 5.0:
            tipo_meta = "alta"
        else:
            tipo_meta = "agressiva"
        
        return {
            'meta_corridas': meta_corridas,
            'meta_motoristas': meta_motoristas,
            'meta_usuarios_ativos': usuarios_meta,
            'meta_receita': meta_receita,
            'tipo_meta': tipo_meta
        }
