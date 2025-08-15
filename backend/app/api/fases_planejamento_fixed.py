"""
APIs para gerenciamento de Fases de Planejamento
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.database.db import get_db
from app.models.fases_planejamento import FasesPlanejamento
from pydantic import BaseModel

router = APIRouter()

# Schemas Pydantic
class FasesPlanejamentoCreate(BaseModel):
    nome: str
    descricao: Optional[str] = None
    data_inicio: datetime
    data_fim: datetime
    orcamento_previsto: float
    meta_cidades: int
    meta_corridas: int
    meta_motoristas: int
    prazo_meses: int
    responsavel: Optional[str] = None
    observacoes: Optional[str] = None

class FasesPlanejamentoUpdate(BaseModel):
    nome: Optional[str] = None
    descricao: Optional[str] = None
    data_fim: Optional[datetime] = None
    orcamento_empenhado: Optional[float] = None
    orcamento_pago: Optional[float] = None
    resultado_corridas: Optional[int] = None
    resultado_motoristas: Optional[int] = None
    resultado_cidades: Optional[int] = None
    status: Optional[str] = None
    responsavel: Optional[str] = None
    observacoes: Optional[str] = None

class FasesPlanejamentoOut(BaseModel):
    id: int
    nome: str
    descricao: Optional[str]
    data_inicio: datetime
    data_fim: datetime
    orcamento_previsto: float
    orcamento_empenhado: float
    orcamento_pago: float
    meta_cidades: int
    meta_corridas: int
    meta_motoristas: int
    resultado_corridas: int
    resultado_motoristas: int
    resultado_cidades: int
    status: str
    prazo_meses: int
    progresso_percentual: float
    responsavel: Optional[str]
    observacoes: Optional[str]
    created_at: datetime
    
    # Propriedades calculadas
    percentual_orcamento_usado: float
    roi_fase: float
    esta_ativa: bool

    class Config:
        from_attributes = True

# Endpoints

@router.get("/fases-planejamento", response_model=List[FasesPlanejamentoOut])
async def listar_fases(
    status: Optional[str] = None,
    ativa_apenas: Optional[bool] = False,
    db: Session = Depends(get_db)
):
    """Lista fases de planejamento com filtros opcionais"""
    try:
        query = db.query(FasesPlanejamento)
        
        if status:
            query = query.filter(FasesPlanejamento.status == status)
        
        if ativa_apenas:
            query = query.filter(FasesPlanejamento.data_inicio <= datetime.utcnow())
            query = query.filter(FasesPlanejamento.data_fim >= datetime.utcnow())
        
        fases = query.order_by(FasesPlanejamento.data_inicio).all()
        
        # Adicionar propriedades calculadas
        for fase in fases:
            fase.percentual_orcamento_usado = fase.percentual_orcamento_usado
            fase.roi_fase = fase.roi_fase
            fase.esta_ativa = fase.esta_ativa
        
        return fases
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar fases: {str(e)}")

@router.get("/fases-planejamento/resumo")
async def resumo_fases_ativas(db: Session = Depends(get_db)):
    """Retorna resumo das fases ativas"""
    try:
        fases_ativas = db.query(FasesPlanejamento).filter(
            FasesPlanejamento.status.in_(["em_execucao", "planejada"])
        ).all()
        
        if not fases_ativas:
            return {"message": "Nenhuma fase ativa encontrada"}
        
        resumo = {
            "total_fases_ativas": len(fases_ativas),
            "orcamento_total_previsto": sum(f.orcamento_previsto for f in fases_ativas),
            "orcamento_total_empenhado": sum(f.orcamento_empenhado for f in fases_ativas),
            "orcamento_total_pago": sum(f.orcamento_pago for f in fases_ativas),
            "meta_total_cidades": sum(f.meta_cidades for f in fases_ativas),
            "meta_total_corridas": sum(f.meta_corridas for f in fases_ativas),
            "resultado_total_corridas": sum(f.resultado_corridas for f in fases_ativas),
            "progresso_medio": sum(f.progresso_percentual for f in fases_ativas) / len(fases_ativas) if fases_ativas else 0,
            "fases": [
                {
                    "id": f.id,
                    "nome": f.nome,
                    "status": f.status,
                    "progresso": f.progresso_percentual,
                    "orcamento_usado": f.percentual_orcamento_usado
                }
                for f in fases_ativas
            ]
        }
        
        return resumo
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao gerar resumo: {str(e)}")

@router.get("/fases-planejamento/{fase_id}", response_model=FasesPlanejamentoOut)
async def buscar_fase(fase_id: int, db: Session = Depends(get_db)):
    """Busca uma fase específica por ID"""
    try:
        fase = db.query(FasesPlanejamento).filter(FasesPlanejamento.id == fase_id).first()
        
        if not fase:
            raise HTTPException(status_code=404, detail="Fase não encontrada")
        
        # Adicionar propriedades calculadas
        fase.percentual_orcamento_usado = fase.percentual_orcamento_usado
        fase.roi_fase = fase.roi_fase
        fase.esta_ativa = fase.esta_ativa
        
        return fase
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar fase: {str(e)}")

@router.post("/fases-planejamento", response_model=FasesPlanejamentoOut)
async def criar_fase(fase: FasesPlanejamentoCreate, db: Session = Depends(get_db)):
    """Cria uma nova fase de planejamento"""
    try:
        nova_fase = FasesPlanejamento(**fase.dict())
        
        db.add(nova_fase)
        db.commit()
        db.refresh(nova_fase)
        
        # Adicionar propriedades calculadas
        nova_fase.percentual_orcamento_usado = nova_fase.percentual_orcamento_usado
        nova_fase.roi_fase = nova_fase.roi_fase
        nova_fase.esta_ativa = nova_fase.esta_ativa
        
        return nova_fase
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao criar fase: {str(e)}")

@router.put("/fases-planejamento/{fase_id}", response_model=FasesPlanejamentoOut)
async def atualizar_fase(fase_id: int, fase_update: FasesPlanejamentoUpdate, db: Session = Depends(get_db)):
    """Atualiza uma fase existente"""
    try:
        fase = db.query(FasesPlanejamento).filter(FasesPlanejamento.id == fase_id).first()
        
        if not fase:
            raise HTTPException(status_code=404, detail="Fase não encontrada")
        
        # Atualizar campos fornecidos
        update_data = fase_update.dict(exclude_unset=True)
        for campo, valor in update_data.items():
            setattr(fase, campo, valor)
        
        # Atualizar timestamp
        fase.updated_at = datetime.utcnow()
        
        # Recalcular progresso automático
        fase.progresso_percentual = fase.calcular_progresso_automatico()
        
        db.commit()
        db.refresh(fase)
        
        # Adicionar propriedades calculadas
        fase.percentual_orcamento_usado = fase.percentual_orcamento_usado
        fase.roi_fase = fase.roi_fase
        fase.esta_ativa = fase.esta_ativa
        
        return fase
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao atualizar fase: {str(e)}")

@router.delete("/fases-planejamento/{fase_id}")
async def deletar_fase(fase_id: int, db: Session = Depends(get_db)):
    """Deleta uma fase de planejamento"""
    try:
        fase = db.query(FasesPlanejamento).filter(FasesPlanejamento.id == fase_id).first()
        
        if not fase:
            raise HTTPException(status_code=404, detail="Fase não encontrada")
        
        db.delete(fase)
        db.commit()
        
        return {"message": f"Fase '{fase.nome}' deletada com sucesso"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao deletar fase: {str(e)}")
