from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Dict, Any, Optional
from app.database.db import get_db
from app.models.cidades_demografia import CidadesDemografia
from app.models.campanha import Campanha
import json
from datetime import datetime, timedelta

router = APIRouter()

@router.get("/dashboard-executivo/overview")
async def get_dashboard_executivo_overview(db: Session = Depends(get_db)):
    """
    Retorna dados consolidados para o dashboard executivo integrado
    """
    try:
        # 1. Resumo das cidades estratégicas
        cidades_query = db.query(CidadesDemografia).all()
        cidades_estrategicas = []
        
        for cidade in cidades_query:
            # Verificar se tem dados de corridas (simulação para cidades ativas)
            cidades_ativas = ['Cuiabá', 'Várzea Grande', 'Rondonópolis']
            is_active = cidade.cidade in cidades_ativas
            
            cidades_estrategicas.append({
                "nome": cidade.cidade,
                "uf": "MT",  # Assumindo MT para todas as cidades
                "populacao": cidade.populacao_estimada_2024 or cidade.populacao_censo_2022,
                "status": "ativa" if is_active else "planejamento",
                "penetracao_estimada": round((10000 / (cidade.populacao_estimada_2024 or cidade.populacao_censo_2022)) * 100, 2) if (cidade.populacao_estimada_2024 or cidade.populacao_censo_2022) > 0 else 0,
                "frota_estimada": 10000,  # Valor simulado
                "receita_potencial": 50000.0,  # Valor simulado
                "investimento_necessario": 100000.0,  # Valor simulado
                "roi_projetado": 25.0  # Valor simulado
            })
        
        # 2. KPIs Consolidados
        total_populacao = sum([c["populacao"] for c in cidades_estrategicas])
        total_receita_potencial = sum([c["receita_potencial"] for c in cidades_estrategicas])
        total_investimento = sum([c["investimento_necessario"] for c in cidades_estrategicas])
        
        # ROI médio ponderado
        roi_medio = sum([c["roi_projetado"] * c["receita_potencial"] for c in cidades_estrategicas]) / total_receita_potencial if total_receita_potencial > 0 else 0
        
        # 3. Campanhas ativas por cidade
        campanhas_query = db.query(Campanha).all()
        campanhas_por_cidade = {}
        
        for campanha in campanhas_query:
            cidade_nome = "Desconhecida"
            if campanha.cidade_id:
                cidade_obj = db.query(CidadesDemografia).filter(CidadesDemografia.id == campanha.cidade_id).first()
                if cidade_obj:
                    cidade_nome = cidade_obj.cidade
            
            if cidade_nome not in campanhas_por_cidade:
                campanhas_por_cidade[cidade_nome] = []
            
            campanhas_por_cidade[cidade_nome].append({
                "id": campanha.id,
                "tipo": campanha.tipo_campanha or "Campanha",
                "descricao": campanha.nome or "Sem descrição",
                "status": campanha.status or "ativa",
                "investimento": float(campanha.orcamento_previsto or 0),
                "roi_esperado": 15.0,  # Valor simulado
                "data_inicio": campanha.data_inicio.isoformat() if campanha.data_inicio else None,
                "data_fim": campanha.data_fim.isoformat() if campanha.data_fim else None
            })
        
        # 4. Simulação de dados operacionais para cidades ativas
        dados_operacionais = {}
        for cidade_ativa in ['Cuiabá', 'Várzea Grande', 'Rondonópolis']:
            # Simular dados baseados em padrões reais
            base_corridas = {"Cuiabá": 1200, "Várzea Grande": 800, "Rondonópolis": 600}
            
            dados_operacionais[cidade_ativa] = {
                "corridas_mes": base_corridas.get(cidade_ativa, 500),
                "receita_mes": base_corridas.get(cidade_ativa, 500) * 15.5,  # Ticket médio R$ 15,50
                "motoristas_ativos": int(base_corridas.get(cidade_ativa, 500) / 40),  # ~40 corridas/motorista/mês
                "crescimento_mensal": round(abs(hash(cidade_ativa) % 15) + 5, 1),  # 5-20%
                "satisfacao_cliente": round(4.2 + (abs(hash(cidade_ativa) % 8) / 10), 1),  # 4.2-4.9
                "ultima_atualizacao": datetime.now().isoformat()
            }
        
        # 5. Métricas de expansão
        cidades_planejamento = [c for c in cidades_estrategicas if c["status"] == "planejamento"]
        metricas_expansao = {
            "cidades_ativas": len([c for c in cidades_estrategicas if c["status"] == "ativa"]),
            "cidades_planejamento": len(cidades_planejamento),
            "proxima_expansao": sorted(cidades_planejamento, key=lambda x: x["roi_projetado"], reverse=True)[:3],
            "investimento_total_expansao": sum([c["investimento_necessario"] for c in cidades_planejamento]),
            "receita_potencial_expansao": sum([c["receita_potencial"] for c in cidades_planejamento])
        }
        
        return {
            "timestamp": datetime.now().isoformat(),
            "resumo_geral": {
                "total_cidades": len(cidades_estrategicas),
                "cidades_ativas": len([c for c in cidades_estrategicas if c["status"] == "ativa"]),
                "total_populacao": total_populacao,
                "receita_potencial_total": total_receita_potencial,
                "investimento_total": total_investimento,
                "roi_medio": round(roi_medio, 2)
            },
            "cidades_estrategicas": cidades_estrategicas,
            "dados_operacionais": dados_operacionais,
            "campanhas_por_cidade": campanhas_por_cidade,
            "metricas_expansao": metricas_expansao
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar dados do dashboard executivo: {str(e)}")

@router.get("/dashboard-executivo/kpis-comparativos")
async def get_kpis_comparativos(db: Session = Depends(get_db)):
    """
    Retorna KPIs comparativos entre cidades ativas e planejamento
    """
    try:
        cidades_query = db.query(CidadesDemografia).all()
        
        kpis_ativos = {"receita": 0, "corridas": 0, "motoristas": 0, "cidades": 0}
        kpis_planejamento = {"receita_potencial": 0, "investimento": 0, "roi_medio": 0, "cidades": 0}
        
        cidades_ativas = ['Cuiabá', 'Várzea Grande', 'Rondonópolis']
        
        for cidade in cidades_query:
            if cidade.cidade in cidades_ativas:
                # Simular dados operacionais
                base_corridas = {"Cuiabá": 1200, "Várzea Grande": 800, "Rondonópolis": 600}
                corridas = base_corridas.get(cidade.cidade, 500)
                
                kpis_ativos["receita"] += corridas * 15.5
                kpis_ativos["corridas"] += corridas
                kpis_ativos["motoristas"] += int(corridas / 40)
                kpis_ativos["cidades"] += 1
            else:
                # Valores simulados para cidades em planejamento
                populacao = cidade.populacao_estimada_2024 or cidade.populacao_censo_2022 or 0
                kpis_planejamento["receita_potencial"] += 50000.0  # Valor simulado
                kpis_planejamento["investimento"] += 100000.0  # Valor simulado  
                kpis_planejamento["roi_medio"] += 25.0  # Valor simulado
                kpis_planejamento["cidades"] += 1
        
        # Calcular ROI médio
        if kpis_planejamento["cidades"] > 0:
            kpis_planejamento["roi_medio"] = kpis_planejamento["roi_medio"] / kpis_planejamento["cidades"]
        
        return {
            "operacao_atual": kpis_ativos,
            "expansao_planejada": kpis_planejamento,
            "projecao_crescimento": {
                "receita_total_projetada": kpis_ativos["receita"] + kpis_planejamento["receita_potencial"],
                "crescimento_percentual": round((kpis_planejamento["receita_potencial"] / kpis_ativos["receita"]) * 100, 1) if kpis_ativos["receita"] > 0 else 0,
                "payback_medio_meses": round(kpis_planejamento["investimento"] / (kpis_planejamento["receita_potencial"] / 12), 1) if kpis_planejamento["receita_potencial"] > 0 else 0
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar KPIs comparativos: {str(e)}")

@router.post("/dashboard-executivo/nova-cidade")
async def criar_nova_cidade_estrategica(
    dados_cidade: Dict[str, Any],
    db: Session = Depends(get_db)
):
    """
    Adiciona uma nova cidade ao planejamento estratégico
    """
    try:
        nova_cidade = CidadesDemografia(
            cidade=dados_cidade["nome"],
            populacao_estimada_2024=int(dados_cidade["populacao"]),
            populacao_censo_2022=int(dados_cidade["populacao"]),
            publico_alvo_15_44_anos=int(int(dados_cidade["populacao"]) * 0.4),  # Estimativa
            publico_homens=int(int(dados_cidade["populacao"]) * 0.5),
            publico_mulheres=int(int(dados_cidade["populacao"]) * 0.5),
            densidade_demografica=10.0  # Valor padrão
        )
        
        db.add(nova_cidade)
        db.commit()
        db.refresh(nova_cidade)
        
        return {
            "success": True,
            "message": f"Cidade {dados_cidade['nome']} adicionada ao planejamento estratégico",
            "cidade_id": nova_cidade.id
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao criar nova cidade: {str(e)}")

@router.put("/dashboard-executivo/atualizar-cidade/{cidade_id}")
async def atualizar_cidade_estrategica(
    cidade_id: int,
    dados_atualizacao: Dict[str, Any],
    db: Session = Depends(get_db)
):
    """
    Atualiza dados de uma cidade estratégica
    """
    try:
        cidade = db.query(CidadesDemografia).filter(CidadesDemografia.id == cidade_id).first()
        
        if not cidade:
            raise HTTPException(status_code=404, detail="Cidade não encontrada")
        
        # Atualizar campos fornecidos
        for campo, valor in dados_atualizacao.items():
            if hasattr(cidade, campo):
                setattr(cidade, campo, valor)
        
        db.commit()
        db.refresh(cidade)
        
        return {
            "success": True,
            "message": f"Cidade {cidade.cidade} atualizada com sucesso"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao atualizar cidade: {str(e)}")

@router.get("/dashboard-executivo/campanhas")
async def get_campanhas(db: Session = Depends(get_db)):
    """
    Retorna todas as campanhas com informações das cidades
    """
    try:
        # Query para buscar campanhas com informações das cidades
        campanhas = db.query(Campanha).all()
        
        campanhas_list = []
        for campanha in campanhas:
            # Buscar informações da cidade
            cidade = db.query(CidadesDemografia).filter(CidadesDemografia.id == campanha.cidade_id).first()
            
            campanha_data = {
                "id": campanha.id,
                "nome": campanha.nome,
                "fase": campanha.fase,
                "parte_campanha": campanha.parte_campanha,
                "tipo_campanha": campanha.tipo_campanha,
                "tipo_gasto": campanha.tipo_gasto,
                "meta_quantidade": campanha.meta_quantidade,
                "meta_percentual_populacao": campanha.meta_percentual_populacao,
                "orcamento_previsto": float(campanha.orcamento_previsto) if campanha.orcamento_previsto else 0,
                "status": campanha.status,
                "data_inicio": campanha.data_inicio.isoformat() if campanha.data_inicio else None,
                "data_fim": campanha.data_fim.isoformat() if campanha.data_fim else None,
                "created_at": campanha.created_at.isoformat() if campanha.created_at else None,
                "cidade": {
                    "id": cidade.id if cidade else None,
                    "nome": cidade.cidade if cidade else "Cidade não encontrada",
                    "populacao": cidade.populacao_estimada_2024 or cidade.populacao_censo_2022 if cidade else 0
                }
            }
            campanhas_list.append(campanha_data)
        
        return {
            "timestamp": datetime.now().isoformat(),
            "total_campanhas": len(campanhas_list),
            "campanhas": campanhas_list
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar campanhas: {str(e)}")

@router.post("/dashboard-executivo/nova-campanha")
async def criar_nova_campanha(
    campanha_data: Dict[str, Any],
    db: Session = Depends(get_db)
):
    """
    Cria uma nova campanha
    """
    try:
        nova_campanha = Campanha(
            nome=campanha_data.get("nome"),
            fase=campanha_data.get("fase"),
            parte_campanha=campanha_data.get("parte_campanha"),
            tipo_campanha=campanha_data.get("tipo_campanha"),
            tipo_gasto=campanha_data.get("tipo_gasto"),
            meta_quantidade=campanha_data.get("meta_quantidade"),
            meta_percentual_populacao=campanha_data.get("meta_percentual_populacao"),
            orcamento_previsto=campanha_data.get("orcamento_previsto"),
            status=campanha_data.get("status", "ativa"),
            cidade_id=campanha_data.get("cidade_id"),
            data_inicio=datetime.fromisoformat(campanha_data["data_inicio"]) if campanha_data.get("data_inicio") else None,
            data_fim=datetime.fromisoformat(campanha_data["data_fim"]) if campanha_data.get("data_fim") else None,
            created_at=datetime.now()
        )
        
        db.add(nova_campanha)
        db.commit()
        db.refresh(nova_campanha)
        
        return {
            "success": True,
            "message": "Campanha criada com sucesso",
            "campanha_id": nova_campanha.id
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao criar campanha: {str(e)}")
