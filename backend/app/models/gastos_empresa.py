from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class GastosEmpresa(Base):
    __tablename__ = "gastos_empresa"
    
    id = Column(Integer, primary_key=True, index=True)
    data_despesa = Column(String(20))  # Tratado como string pois vem em formato texto
    valor_total = Column(String(20))   # Tratado como string pois vem em formato texto
    descricao_item = Column(String(255))
    tipo_documento = Column(String(100))
    fornecedor = Column(String(255))
    natureza_do_gasto = Column(String(100))
    descricao_imagem = Column(Text)
    arquivo_drive_url = Column(String(500))  # URL do documento/comprovante (Google Drive)
    possui_nota_fiscal = Column(Integer)  # 0 ou 1
    id_documento_vinculado = Column(Integer)
    status_documentacao = Column(String(100))
    observacoes = Column(Text)
    numero_nota_fiscal = Column(String(50))
    serie_nota_fiscal = Column(String(50))
    chave_acesso_nfe = Column(String(100))
    cnpj_emissor = Column(String(20))
    inscricao_estadual = Column(String(50))
    data_processamento = Column(String(50))  # Tratado como string
