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
        
        # Não atribuir propriedades calculadas (são @property)
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
        
        # Não atribuir propriedades calculadas (são @property)
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
        # Não atribuir propriedades calculadas diretamente (são @property)
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
        
        # ✅ REMOVIDO: Não tentar setar propriedades calculadas (@property)
        # Elas já estão disponíveis automaticamente ao retornar o objeto
        
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
        
        nome_fase = fase.nome
        
        db.delete(fase)
        db.commit()
        
        return {
            "message": f"Fase '{nome_fase}' deletada com sucesso",
            "fase_deletada": {
                "id": fase_id,
                "nome": nome_fase
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao deletar fase: {str(e)}")

@router.get("/fases-planejamento/{fase_id}", response_model=FasesPlanejamentoOut)
async def buscar_fase(fase_id: int, db: Session = Depends(get_db)):
    """Busca uma fase específica por ID"""
    try:
        fase = db.query(FasesPlanejamento).filter(FasesPlanejamento.id == fase_id).first()
        
        if not fase:
            raise HTTPException(status_code=404, detail="Fase não encontrada")
        
        return fase
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar fase: {str(e)}")

@router.post("/fases-planejamento/bulk-create")
async def criar_fases_em_lote(fases: List[FasesPlanejamentoCreate], db: Session = Depends(get_db)):
    """Cria múltiplas fases de uma vez"""
    try:
        fases_criadas = []
        erros = []
        
        for fase_data in fases:
            try:
                nova_fase = FasesPlanejamento(**fase_data.dict())
                db.add(nova_fase)
                fases_criadas.append(nova_fase)
                
            except Exception as e:
                erros.append(f"Erro ao criar fase '{fase_data.nome}': {str(e)}")
        
        if fases_criadas:
            db.commit()
            
            # Refresh para obter os IDs
            for fase in fases_criadas:
                db.refresh(fase)
        
        return {
            "message": f"Processamento de lote concluído",
            "fases_criadas": len(fases_criadas),
            "erros": len(erros),
            "detalhes_erros": erros if erros else None,
            "ids_criados": [fase.id for fase in fases_criadas]
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro no processamento de lote: {str(e)}")

@router.put("/fases-planejamento/bulk-update")
async def atualizar_fases_em_lote(updates: List[dict], db: Session = Depends(get_db)):
    """Atualiza múltiplas fases de uma vez"""
    try:
        fases_atualizadas = []
        erros = []
        
        for update_data in updates:
            try:
                fase_id = update_data.get("id")
                if not fase_id:
                    erros.append("ID da fase não fornecido")
                    continue
                
                fase = db.query(FasesPlanejamento).filter(FasesPlanejamento.id == fase_id).first()
                if not fase:
                    erros.append(f"Fase ID {fase_id} não encontrada")
                    continue
                
                # Atualizar campos fornecidos (exceto ID)
                for campo, valor in update_data.items():
                    if campo != "id" and hasattr(fase, campo):
                        setattr(fase, campo, valor)
                
                fase.updated_at = datetime.utcnow()
                fase.progresso_percentual = fase.calcular_progresso_automatico()
                fases_atualizadas.append(fase)
                
            except Exception as e:
                erros.append(f"Erro ao atualizar fase ID {update_data.get('id', 'N/A')}: {str(e)}")
        
        if fases_atualizadas:
            db.commit()
        
        return {
            "message": f"Atualização em lote concluída",
            "fases_atualizadas": len(fases_atualizadas),
            "erros": len(erros),
            "detalhes_erros": erros if erros else None
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro na atualização em lote: {str(e)}")
