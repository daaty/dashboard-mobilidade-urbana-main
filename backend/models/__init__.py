from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from enum import Enum
db = SQLAlchemy()
class StatusCorrida(Enum):
    """Enum para status das corridas"""
    CONCLUIDA = "concluida"
    CANCELADA = "cancelada"
    PERDIDA = "perdida"

class StatusMotorista(Enum):
    """Enum para status dos motoristas"""
    ATIVO = "ativo"
    INATIVO = "inativo"
    BLOQUEADO = "bloqueado"

class OrigemDado(Enum):
    """Enum para origem dos dados"""
    POSTGRES = "postgres"
    SHEETS = "sheets"
    IMPORT = "import"

class Corrida(db.Model):
    """Model para corridas"""
    __tablename__ = 'corridas'
    
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.DateTime, nullable=False, index=True)
    usuario_nome = db.Column(db.String(100), nullable=False)
    usuario_telefone = db.Column(db.String(20))
    motorista_nome = db.Column(db.String(100), nullable=False)
    municipio = db.Column(db.String(50), nullable=False, index=True)
    status = db.Column(db.Enum(StatusCorrida), nullable=False, index=True)
    valor = db.Column(db.Numeric(10, 2))
    distancia = db.Column(db.Float)  # em km
    tempo_corrida = db.Column(db.Integer)  # em minutos
    avaliacao = db.Column(db.Integer)  # 1-5 estrelas
    motivo_cancelamento = db.Column(db.String(100))
    origem_dado = db.Column(db.Enum(OrigemDado), nullable=False, default=OrigemDado.POSTGRES)
    
    # Campos de controle
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    motorista_id = db.Column(db.Integer, db.ForeignKey('motoristas.id'))
    motorista = db.relationship('Motorista', back_populates='corridas')
    
    def __repr__(self):
        return f'<Corrida {self.id}: {self.usuario_nome} - {self.status.value}>'
    
    def to_dict(self):
        """Converte o objeto para dicionário"""
        return {
            'id': self.id,
            'data': self.data.isoformat() if self.data else None,
            'usuario_nome': self.usuario_nome,
            'usuario_telefone': self.usuario_telefone,
            'motorista_nome': self.motorista_nome,
            'municipio': self.municipio,
            'status': self.status.value if self.status else None,
            'valor': float(self.valor) if self.valor else None,
            'distancia': self.distancia,
            'tempo_corrida': self.tempo_corrida,
            'avaliacao': self.avaliacao,
            'motivo_cancelamento': self.motivo_cancelamento,
            'origem_dado': self.origem_dado.value if self.origem_dado else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class Motorista(db.Model):
    """Model para motoristas"""
    __tablename__ = 'motoristas'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    telefone = db.Column(db.String(20), unique=True)
    municipio = db.Column(db.String(50), nullable=False, index=True)
    status = db.Column(db.Enum(StatusMotorista), nullable=False, default=StatusMotorista.ATIVO)
    data_cadastro = db.Column(db.DateTime, default=datetime.utcnow)
    total_corridas = db.Column(db.Integer, default=0)
    avaliacao_media = db.Column(db.Float)
    ultima_corrida = db.Column(db.DateTime)
    
    # Campos de controle
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    corridas = db.relationship('Corrida', back_populates='motorista')
    
    def __repr__(self):
        return f'<Motorista {self.id}: {self.nome} - {self.status.value}>'
    
    def to_dict(self):
        """Converte o objeto para dicionário"""
        return {
            'id': self.id,
            'nome': self.nome,
            'telefone': self.telefone,
            'municipio': self.municipio,
            'status': self.status.value if self.status else None,
            'data_cadastro': self.data_cadastro.isoformat() if self.data_cadastro else None,
            'total_corridas': self.total_corridas,
            'avaliacao_media': self.avaliacao_media,
            'ultima_corrida': self.ultima_corrida.isoformat() if self.ultima_corrida else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class Meta(db.Model):
    """Model para metas mensais"""
    __tablename__ = 'metas'
    
    id = db.Column(db.Integer, primary_key=True)
    municipio = db.Column(db.String(50), nullable=False, index=True)
    mes = db.Column(db.Date, nullable=False, index=True)
    meta_corridas = db.Column(db.Integer, nullable=False)
    meta_receita = db.Column(db.Numeric(10, 2))
    meta_motoristas = db.Column(db.Integer)
    
    # Campos de controle
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Índice único para evitar duplicação
    __table_args__ = (db.UniqueConstraint('municipio', 'mes', name='unique_meta_municipio_mes'),)
    
    def __repr__(self):
        return f'<Meta {self.id}: {self.municipio} - {self.mes}>'
    
    def to_dict(self):
        """Converte o objeto para dicionário"""
        return {
            'id': self.id,
            'municipio': self.municipio,
            'mes': self.mes.isoformat() if self.mes else None,
            'meta_corridas': self.meta_corridas,
            'meta_receita': float(self.meta_receita) if self.meta_receita else None,
            'meta_motoristas': self.meta_motoristas,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class MetricaDiaria(db.Model):
    """Model para métricas consolidadas diárias"""
    __tablename__ = 'metricas_diarias'
    
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.Date, nullable=False, index=True)
    municipio = db.Column(db.String(50), nullable=False, index=True)
    corridas_concluidas = db.Column(db.Integer, default=0)
    corridas_canceladas = db.Column(db.Integer, default=0)
    corridas_perdidas = db.Column(db.Integer, default=0)
    receita_total = db.Column(db.Numeric(10, 2), default=0)
    motoristas_ativos = db.Column(db.Integer, default=0)
    avaliacao_media = db.Column(db.Float)
    tempo_medio_corrida = db.Column(db.Float)
    distancia_media = db.Column(db.Float)
    
    # Campos calculados
    total_corridas = db.Column(db.Integer, default=0)
    taxa_conclusao = db.Column(db.Float)  # percentual
    ticket_medio = db.Column(db.Numeric(10, 2))
    
    # Campos de controle
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Índice único para evitar duplicação
    __table_args__ = (db.UniqueConstraint('data', 'municipio', name='unique_metrica_data_municipio'),)
    
    def __repr__(self):
        return f'<MetricaDiaria {self.id}: {self.municipio} - {self.data}>'
    
    def to_dict(self):
        """Converte o objeto para dicionário"""
        return {
            'id': self.id,
            'data': self.data.isoformat() if self.data else None,
            'municipio': self.municipio,
            'corridas_concluidas': self.corridas_concluidas,
            'corridas_canceladas': self.corridas_canceladas,
            'corridas_perdidas': self.corridas_perdidas,
            'receita_total': float(self.receita_total) if self.receita_total else None,
            'motoristas_ativos': self.motoristas_ativos,
            'avaliacao_media': self.avaliacao_media,
            'tempo_medio_corrida': self.tempo_medio_corrida,
            'distancia_media': self.distancia_media,
            'total_corridas': self.total_corridas,
            'taxa_conclusao': self.taxa_conclusao,
            'ticket_medio': float(self.ticket_medio) if self.ticket_medio else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class ImportLog(db.Model):
    """Model para log de importações"""
    __tablename__ = 'import_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    file_size = db.Column(db.Integer)
    total_rows = db.Column(db.Integer)
    success_rows = db.Column(db.Integer)
    error_rows = db.Column(db.Integer)
    import_type = db.Column(db.String(50))  # 'corridas', 'metas', etc.
    status = db.Column(db.String(20))  # 'processing', 'completed', 'failed'
    error_message = db.Column(db.Text)
    
    # Campos de controle
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    
    def __repr__(self):
        return f'<ImportLog {self.id}: {self.filename} - {self.status}>'
    
    def to_dict(self):
        """Converte o objeto para dicionário"""
        return {
            'id': self.id,
            'filename': self.filename,
            'file_size': self.file_size,
            'total_rows': self.total_rows,
            'success_rows': self.success_rows,
            'error_rows': self.error_rows,
            'import_type': self.import_type,
            'status': self.status,
            'error_message': self.error_message,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }
