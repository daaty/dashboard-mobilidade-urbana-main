"""
APIs para gerenciamento de Metas Progressivas
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.database.db import get_db
from app.models.metas_progressivas import MetasProgressivas
from app.models.cidades_demografia import CidadesDemografia
from pydantic import BaseModel

router = APIRouter()

# Schemas Pydantic
class MetasProgressivasCreate(BaseModel):
    cidade_id: int
    fase_id: Optional[int] = None
    mes: int
    percentual_publico: float
    tipo_meta: str
    meta_corridas: int
    meta_motoristas: int
    meta_usuarios_ativos: Optional[int] = 0
    meta_receita: Optional[float] = 0.0
    investimento_previsto: Optional[float] = 0.0
    estrategia: Optional[str] = None
    observacoes: Optional[str] = None

class MetasProgressivasUpdate(BaseModel):
    resultado_corridas: Optional[int] = None
    resultado_motoristas: Optional[int] = None
    resultado_usuarios_ativos: Optional[int] = None
    resultado_receita: Optional[float] = None
    resultado_satisfacao: Optional[float] = None
    resultado_tempo_resposta: Optional[float] = None
    resultado_taxa_cancelamento: Optional[float] = None
    investimento_realizado: Optional[float] = None
    status: Optional[str] = None
    observacoes: Optional[str] = None

class MetasProgressivasOut(BaseModel):
    id: int
    cidade_id: int
    mes: int
    percentual_publico: float
    tipo_meta: str
    meta_corridas: int
    meta_motoristas: int
    meta_usuarios_ativos: int
    meta_receita: float
    resultado_corridas: int
    resultado_motoristas: int
    resultado_usuarios_ativos: int
    resultado_receita: float
    status: str
    atingida: bool
    investimento_previsto: float
    investimento_realizado: float
    estrategia: Optional[str]
    observacoes: Optional[str]
    created_at: datetime
    
    # Propriedades calculadas
    percentual_atingido_corridas: float
    percentual_atingido_motoristas: float
    percentual_atingido_geral: float
    roi_meta: float
    
    # Dados da cidade
    cidade_nome: Optional[str] = None

    class Config:
        from_attributes = True

# Endpoints

@router.get("/metas-progressivas", response_model=List[MetasProgressivasOut])
async def listar_metas(
    cidade_id: Optional[int] = None,
    mes: Optional[int] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Lista metas progressivas com filtros opcionais"""
    try:
        query = db.query(MetasProgressivas).join(CidadesDemografia)
        
        if cidade_id:
            query = query.filter(MetasProgressivas.cidade_id == cidade_id)
        if mes:
            query = query.filter(MetasProgressivas.mes == mes)
        if status:
            query = query.filter(MetasProgressivas.status == status)
        
        metas = query.order_by(MetasProgressivas.cidade_id, MetasProgressivas.mes).all()
        
        # Adicionar apenas cidade_nome (propriedades calculadas são @property)
        for meta in metas:
            meta.cidade_nome = meta.cidade.cidade if meta.cidade else None
        return metas
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar metas: {str(e)}")

@router.get("/metas-progressivas/{meta_id}", response_model=MetasProgressivasOut)
async def buscar_meta(meta_id: int, db: Session = Depends(get_db)):
    """Busca uma meta específica por ID"""
    try:
        meta = db.query(MetasProgressivas).filter(MetasProgressivas.id == meta_id).first()
        
        if not meta:
            raise HTTPException(status_code=404, detail="Meta não encontrada")
        
        # Não atribuir propriedades calculadas diretamente (são @property)
        meta.cidade_nome = meta.cidade.cidade if meta.cidade else None
        
        return meta
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar meta: {str(e)}")

@router.post("/metas-progressivas", response_model=MetasProgressivasOut)
async def criar_meta(meta: MetasProgressivasCreate, db: Session = Depends(get_db)):
    """Cria uma nova meta progressiva"""
    try:
        # Verificar se a cidade existe
        cidade = db.query(CidadesDemografia).filter(CidadesDemografia.id == meta.cidade_id).first()
        if not cidade:
            raise HTTPException(status_code=404, detail="Cidade não encontrada")
        
        nova_meta = MetasProgressivas(**meta.dict())
        
        db.add(nova_meta)
        db.commit()
        db.refresh(nova_meta)
        
        # Não atribuir propriedades calculadas diretamente (são @property)
        # Apenas adicionar cidade_nome se necessário
        nova_meta.cidade_nome = cidade.cidade
        
        return nova_meta
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao criar meta: {str(e)}")

@router.put("/metas-progressivas/{meta_id}", response_model=MetasProgressivasOut)
async def atualizar_meta(meta_id: int, meta_update: MetasProgressivasUpdate, db: Session = Depends(get_db)):
    """Atualiza uma meta existente (principalmente resultados)"""
    try:
        meta = db.query(MetasProgressivas).filter(MetasProgressivas.id == meta_id).first()
        
        if not meta:
            raise HTTPException(status_code=404, detail="Meta não encontrada")
        
        # Atualizar campos fornecidos
        update_data = meta_update.dict(exclude_unset=True)
        for campo, valor in update_data.items():
            setattr(meta, campo, valor)
        
        # Atualizar timestamp
        meta.updated_at = datetime.utcnow()
        
        # Verificar automaticamente se meta foi atingida
        meta.verificar_se_atingida()
        
        db.commit()
        db.refresh(meta)
        
        # Não atribuir propriedades calculadas diretamente (são @property)
        meta.cidade_nome = meta.cidade.cidade if meta.cidade else None
        
        return meta
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao atualizar meta: {str(e)}")

@router.post("/metas-progressivas/cidade/{cidade_id}/automaticas")
async def criar_metas_automaticas(cidade_id: int, db: Session = Depends(get_db)):
    """Cria metas progressivas automáticas para uma cidade"""
    try:
        # Verificar se a cidade existe
        cidade = db.query(CidadesDemografia).filter(CidadesDemografia.id == cidade_id).first()
        if not cidade:
            raise HTTPException(status_code=404, detail="Cidade não encontrada")
        
        publico_alvo = cidade.publico_alvo_15_44_anos or int(cidade.populacao_estimada_2024 * 0.4)
        
        # Estratégias progressivas
        estrategias = [
            {"mes": 1, "percentual": 0.5},
            {"mes": 2, "percentual": 1.0},
            {"mes": 3, "percentual": 2.0},
            {"mes": 6, "percentual": 5.0},
            {"mes": 12, "percentual": 10.0}
        ]
        
        metas_criadas = []
        
        for estrategia in estrategias:
            # Verificar se já existe meta para este mês
            existe = db.query(MetasProgressivas).filter(
                MetasProgressivas.cidade_id == cidade_id,
                MetasProgressivas.mes == estrategia["mes"]
            ).first()
            
            if existe:
                continue  # Pular se já existe
            
            # Calcular metas automáticas
            metas_calc = MetasProgressivas.calcular_meta_automatica(
                publico_alvo, estrategia["percentual"], estrategia["mes"]
            )
            
            nova_meta = MetasProgressivas(
                cidade_id=cidade_id,
                mes=estrategia["mes"],
                percentual_publico=estrategia["percentual"],
                tipo_meta=metas_calc["tipo_meta"],
                meta_corridas=metas_calc["meta_corridas"],
                meta_motoristas=metas_calc["meta_motoristas"],
                meta_usuarios_ativos=metas_calc["meta_usuarios_ativos"],
                meta_receita=metas_calc["meta_receita"],
                investimento_previsto=metas_calc["meta_motoristas"] * 50 + metas_calc["meta_corridas"] * 0.5,
                estrategia=f"Meta automática para {estrategia['percentual']}% do público-alvo em {estrategia['mes']} mês(es)"
            )
            
            db.add(nova_meta)
            metas_criadas.append(nova_meta)
        
        db.commit()
        
        return {
            "message": f"Criadas {len(metas_criadas)} metas automáticas para {cidade.cidade}",
            "cidade": cidade.cidade,
            "publico_alvo": publico_alvo,
            "metas_criadas": len(metas_criadas)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao criar metas automáticas: {str(e)}")

@router.get("/metas-progressivas/cidade/{cidade_id}/resumo")
async def resumo_metas_cidade(cidade_id: int, db: Session = Depends(get_db)):
    """Retorna resumo das metas de uma cidade"""
    try:
        cidade = db.query(CidadesDemografia).filter(CidadesDemografia.id == cidade_id).first()
        if not cidade:
            raise HTTPException(status_code=404, detail="Cidade não encontrada")
        
        metas = db.query(MetasProgressivas).filter(MetasProgressivas.cidade_id == cidade_id).all()
        
        if not metas:
            return {
                "cidade": cidade.cidade,
                "total_metas": 0,
                "message": "Nenhuma meta configurada para esta cidade"
            }
        
        resumo = {
            "cidade": cidade.cidade,
            "total_metas": len(metas),
            "metas_atingidas": len([m for m in metas if m.atingida]),
            "total_investimento_previsto": sum(m.investimento_previsto for m in metas),
            "total_investimento_realizado": sum(m.investimento_realizado for m in metas),
            "total_meta_corridas": sum(m.meta_corridas for m in metas),
            "total_resultado_corridas": sum(m.resultado_corridas for m in metas),
            "progresso_medio": sum(m.percentual_atingido_geral for m in metas) / len(metas),
            "metas_por_tipo": {},
            "timeline": []
        }
        
        # Agrupar por tipo
        for meta in metas:
            tipo = meta.tipo_meta
            if tipo not in resumo["metas_por_tipo"]:
                resumo["metas_por_tipo"][tipo] = 0
            resumo["metas_por_tipo"][tipo] += 1
        
        # Timeline
        resumo["timeline"] = [
            {
                "mes": m.mes,
                "tipo": m.tipo_meta,
                "meta_corridas": m.meta_corridas,
                "resultado_corridas": m.resultado_corridas,
                "percentual_atingido": m.percentual_atingido_geral,
                "atingida": m.atingida
            }
            for m in sorted(metas, key=lambda x: x.mes)
        ]
        
        return resumo
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao gerar resumo: {str(e)}")

@router.delete("/metas-progressivas/{meta_id}")
async def deletar_meta(meta_id: int, db: Session = Depends(get_db)):
    """Deleta uma meta progressiva"""
    try:
        meta = db.query(MetasProgressivas).filter(MetasProgressivas.id == meta_id).first()
        
        if not meta:
            raise HTTPException(status_code=404, detail="Meta não encontrada")
        
        cidade_nome = meta.cidade.cidade if meta.cidade else "N/A"
        mes = meta.mes
        tipo = meta.tipo_meta
        
        db.delete(meta)
        db.commit()
        
        return {
            "message": f"Meta deletada com sucesso",
            "meta_deletada": {
                "id": meta_id,
                "cidade": cidade_nome,
                "mes": mes,
                "tipo": tipo
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao deletar meta: {str(e)}")

@router.delete("/metas-progressivas/cidade/{cidade_id}")
async def deletar_todas_metas_cidade(cidade_id: int, db: Session = Depends(get_db)):
    """Deleta todas as metas de uma cidade"""
    try:
        cidade = db.query(CidadesDemografia).filter(CidadesDemografia.id == cidade_id).first()
        if not cidade:
            raise HTTPException(status_code=404, detail="Cidade não encontrada")
        
        metas = db.query(MetasProgressivas).filter(MetasProgressivas.cidade_id == cidade_id).all()
        
        if not metas:
            return {
                "message": f"Nenhuma meta encontrada para {cidade.cidade}",
                "metas_deletadas": 0
            }
        
        quantidade = len(metas)
        
        # Deletar todas as metas da cidade
        db.query(MetasProgressivas).filter(MetasProgressivas.cidade_id == cidade_id).delete()
        db.commit()
        
        return {
            "message": f"Todas as metas de {cidade.cidade} foram deletadas",
            "cidade": cidade.cidade,
            "metas_deletadas": quantidade
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao deletar metas da cidade: {str(e)}")

@router.post("/metas-progressivas/bulk-create")
async def criar_metas_em_lote(metas: List[MetasProgressivasCreate], db: Session = Depends(get_db)):
    """Cria múltiplas metas de uma vez"""
    try:
        metas_criadas = []
        erros = []
        
        for meta_data in metas:
            try:
                # Verificar se a cidade existe
                cidade = db.query(CidadesDemografia).filter(CidadesDemografia.id == meta_data.cidade_id).first()
                if not cidade:
                    erros.append(f"Cidade ID {meta_data.cidade_id} não encontrada")
                    continue
                
                nova_meta = MetasProgressivas(**meta_data.dict())
                db.add(nova_meta)
                metas_criadas.append(nova_meta)
                
            except Exception as e:
                erros.append(f"Erro ao criar meta para cidade {meta_data.cidade_id}: {str(e)}")
        
        if metas_criadas:
            db.commit()
            
            # Refresh para obter os IDs
            for meta in metas_criadas:
                db.refresh(meta)
        
        return {
            "message": f"Processamento de lote concluído",
            "metas_criadas": len(metas_criadas),
            "erros": len(erros),
            "detalhes_erros": erros if erros else None,
            "ids_criados": [meta.id for meta in metas_criadas]
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro no processamento de lote: {str(e)}")

@router.put("/metas-progressivas/bulk-update")
async def atualizar_metas_em_lote(updates: List[dict], db: Session = Depends(get_db)):
    """Atualiza múltiplas metas de uma vez"""
    try:
        metas_atualizadas = []
        erros = []
        
        for update_data in updates:
            try:
                meta_id = update_data.get("id")
                if not meta_id:
                    erros.append("ID da meta não fornecido")
                    continue
                
                meta = db.query(MetasProgressivas).filter(MetasProgressivas.id == meta_id).first()
                if not meta:
                    erros.append(f"Meta ID {meta_id} não encontrada")
                    continue
                
                # Atualizar campos fornecidos (exceto ID)
                for campo, valor in update_data.items():
                    if campo != "id" and hasattr(meta, campo):
                        setattr(meta, campo, valor)
                
                meta.updated_at = datetime.utcnow()
                meta.verificar_se_atingida()
                metas_atualizadas.append(meta)
                
            except Exception as e:
                erros.append(f"Erro ao atualizar meta ID {update_data.get('id', 'N/A')}: {str(e)}")
        
        if metas_atualizadas:
            db.commit()
        
        return {
            "message": f"Atualização em lote concluída",
            "metas_atualizadas": len(metas_atualizadas),
            "erros": len(erros),
            "detalhes_erros": erros if erros else None
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro na atualização em lote: {str(e)}")
