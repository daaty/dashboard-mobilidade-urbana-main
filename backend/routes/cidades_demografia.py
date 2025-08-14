from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database.db import get_db
from app.models.cidades_demografia import CidadesDemografia
from app.models.campanha import Campanha
from sqlalchemy import func

router = APIRouter()

@router.get("/cidades")
async def get_all_cidades(db: Session = Depends(get_db)):
    """Retorna todas as cidades com dados demográficos"""
    cidades = db.query(CidadesDemografia).all()
    return cidades

@router.get("/cidades/{cidade_id}")
async def get_cidade_by_id(cidade_id: int, db: Session = Depends(get_db)):
    """Retorna dados demográficos de uma cidade específica"""
    cidade = db.query(CidadesDemografia).filter(CidadesDemografia.id == cidade_id).first()
    if not cidade:
        raise HTTPException(status_code=404, detail="Cidade não encontrada")
    return cidade

@router.get("/cidades/{cidade_id}/campanhas")
async def get_campanhas_por_cidade(cidade_id: int, db: Session = Depends(get_db)):
    """Retorna todas as campanhas de uma cidade específica"""
    cidade = db.query(CidadesDemografia).filter(CidadesDemografia.id == cidade_id).first()
    if not cidade:
        raise HTTPException(status_code=404, detail="Cidade não encontrada")
    
    campanhas = db.query(Campanha).filter(Campanha.cidade_id == cidade_id).all()
    return {
        "cidade": cidade.cidade,
        "populacao": cidade.populacao_censo_2022,
        "publico_alvo": cidade.publico_alvo_15_44_anos,
        "campanhas": campanhas
    }

@router.get("/kpis/penetracao-mercado")
async def get_kpis_penetracao_mercado(db: Session = Depends(get_db)):
    """Calcula KPIs de penetração de mercado por cidade"""
    try:
        # Query para buscar dados combinados de cidades e campanhas
        results = db.query(
            CidadesDemografia.cidade,
            CidadesDemografia.populacao_censo_2022,
            CidadesDemografia.publico_alvo_15_44_anos,
            func.sum(Campanha.meta_quantidade).label('meta_total'),
            func.sum(Campanha.orcamento_previsto).label('orcamento_total'),
            func.count(Campanha.id).label('total_campanhas')
        ).outerjoin(
            Campanha, CidadesDemografia.id == Campanha.cidade_id
        ).group_by(
            CidadesDemografia.id,
            CidadesDemografia.cidade,
            CidadesDemografia.populacao_censo_2022,
            CidadesDemografia.publico_alvo_15_44_anos
        ).all()
        
        kpis = []
        for result in results:
            meta_total = result.meta_total or 0
            orcamento_total = float(result.orcamento_total or 0)
            penetracao_percentual = (meta_total / result.publico_alvo_15_44_anos * 100) if result.publico_alvo_15_44_anos else 0
            receita_estimada = meta_total * 2.50  # R$ 2,50 por corrida
            roi_estimado = (receita_estimada / orcamento_total * 100) if orcamento_total > 0 else 0
            
            kpis.append({
                "cidade": result.cidade,
                "populacao": result.populacao_censo_2022,
                "publico_alvo": result.publico_alvo_15_44_anos,
                "meta_total_corridas": meta_total,
                "penetracao_percentual": round(penetracao_percentual, 2),
                "orcamento_total": orcamento_total,
                "receita_estimada": round(receita_estimada, 2),
                "roi_estimado": round(roi_estimado, 2),
                "total_campanhas": result.total_campanhas
            })
        
        return kpis
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao calcular KPIs: {str(e)}")

@router.get("/metas/progressao-temporal")
async def get_progressao_temporal(cidade_id: Optional[int] = None, db: Session = Depends(get_db)):
    """Retorna progressão de metas baseada nos percentuais: 0.5%, 1%, 2%, 10%"""
    query = db.query(CidadesDemografia)
    if cidade_id:
        query = query.filter(CidadesDemografia.id == cidade_id)
    
    cidades = query.all()
    progressao = []
    
    for cidade in cidades:
        if cidade.publico_alvo_15_44_anos:
            metas_progressivas = {
                "cidade": cidade.cidade,
                "publico_alvo": cidade.publico_alvo_15_44_anos,
                "metas": {
                    "mes_1": round(cidade.publico_alvo_15_44_anos * 0.005),  # 0.5%
                    "mes_2": round(cidade.publico_alvo_15_44_anos * 0.01),   # 1%
                    "mes_3": round(cidade.publico_alvo_15_44_anos * 0.02),   # 2%
                    "mes_6": round(cidade.publico_alvo_15_44_anos * 0.10)    # 10%
                },
                "receita_estimada": {
                    "mes_1": round(cidade.publico_alvo_15_44_anos * 0.005 * 2.50, 2),
                    "mes_2": round(cidade.publico_alvo_15_44_anos * 0.01 * 2.50, 2),
                    "mes_3": round(cidade.publico_alvo_15_44_anos * 0.02 * 2.50, 2),
                    "mes_6": round(cidade.publico_alvo_15_44_anos * 0.10 * 2.50, 2)
                }
            }
            progressao.append(metas_progressivas)
    
    return progressao
