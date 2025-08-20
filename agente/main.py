"""
🤖 API DO AGENTE INTELIGENTE - DASHBOARD MOBILIDADE URBANA
Serve o agente como uma API REST para deploy no Heroku
"""

import os
import sys
from typing import Dict, Any, Optional
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import asyncio
from datetime import datetime
from dotenv import load_dotenv

# Carregar variáveis de ambiente do arquivo .env na raiz do projeto
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

# Adicionar o diretório dashboard_agent ao path
sys.path.append(os.path.join(os.path.dirname(__file__), "dashboard_agent"))

try:
    from dashboard_agent.mobility_agent import MobilityDashboardAgent
except ImportError:
    print("⚠️ Agente não encontrado. Criando versão mock para deploy...")
    
    class MobilityDashboardAgent:
        def __init__(self, **kwargs):
            self.dashboard_url = kwargs.get('dashboard_url', 'http://localhost:8000')
        
        def analyze_overall_performance(self):
            return "🚧 Agente em configuração inicial..."
        
        def interactive_analysis(self, question):
            return f"🚧 Processando: {question}"

# Inicializar FastAPI
app = FastAPI(
    title="🤖 Agente Inteligente - Mobilidade Urbana",
    description="API do agente inteligente para análise de dados de mobilidade urbana",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Modelos de request/response
class AnalysisRequest(BaseModel):
    analysis_type: str
    parameters: Optional[Dict[str, Any]] = {}

class QuestionRequest(BaseModel):
    question: str
    context: Optional[Dict[str, Any]] = {}

class AnalysisResponse(BaseModel):
    success: bool
    result: str
    timestamp: datetime
    analysis_type: str
    metadata: Optional[Dict[str, Any]] = {}

# Instância global do agente
agente = None

@app.on_event("startup")
async def startup_event():
    """Inicializar agente na startup"""
    global agente
    
    try:
        print("🚀 Inicializando Agente Inteligente...")
        
        agente = MobilityDashboardAgent(
            dashboard_url=os.getenv("DASHBOARD_URL", "http://localhost:8000"),
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            memory_db_url=os.getenv("MEMORY_DB_URL")
        )
        
        print("✅ Agente inicializado com sucesso!")
        
    except Exception as e:
        print(f"❌ Erro ao inicializar agente: {e}")
        # Criar versão mock para não quebrar o deploy
        agente = MobilityDashboardAgent()

@app.get("/")
async def root():
    """Endpoint raiz"""
    return {
        "message": "🤖 Agente Inteligente - Dashboard Mobilidade Urbana",
        "status": "online",
        "timestamp": datetime.now(),
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    """Health check para deploy"""
    return {
        "status": "healthy",
        "timestamp": datetime.now(),
        "agent_ready": agente is not None
    }

@app.post("/analyze", response_model=AnalysisResponse)
async def analyze(request: AnalysisRequest):
    """Executar análise específica"""
    
    if not agente:
        raise HTTPException(status_code=503, detail="Agente não inicializado")
    
    try:
        print(f"📊 Executando análise: {request.analysis_type}")
        
        # Mapear tipos de análise
        analysis_methods = {
            "performance": agente.analyze_overall_performance,
            "financial": agente.financial_health_assessment,
            "drivers": agente.driver_performance_analysis,
            "expansion": agente.city_expansion_analysis,
            "trends": agente.market_trends_forecast,
            "executive": agente.generate_executive_report
        }
        
        if request.analysis_type not in analysis_methods:
            raise HTTPException(
                status_code=400, 
                detail=f"Tipo de análise inválido. Disponíveis: {list(analysis_methods.keys())}"
            )
        
        # Executar análise
        method = analysis_methods[request.analysis_type]
        
        # Para expansão, passar parâmetros se houver
        if request.analysis_type == "expansion" and "cities" in request.parameters:
            result = method(request.parameters["cities"])
        else:
            result = method()
        
        # Extrair conteúdo se for RunResponse
        if hasattr(result, 'content'):
            result_content = result.content
        else:
            result_content = str(result)
        
        return AnalysisResponse(
            success=True,
            result=result_content,
            timestamp=datetime.now(),
            analysis_type=request.analysis_type,
            metadata=request.parameters
        )
        
    except Exception as e:
        print(f"❌ Erro na análise: {e}")
        raise HTTPException(status_code=500, detail=f"Erro na análise: {str(e)}")

@app.post("/ask", response_model=AnalysisResponse)
async def ask_question(request: QuestionRequest):
    """Fazer pergunta específica ao agente"""
    
    if not agente:
        raise HTTPException(status_code=503, detail="Agente não inicializado")
    
    try:
        print(f"🤔 Pergunta recebida: {request.question[:50]}...")
        
        result = agente.interactive_analysis(request.question)
        
        # Extrair conteúdo se for RunResponse
        if hasattr(result, 'content'):
            result_content = result.content
        else:
            result_content = str(result)
        
        return AnalysisResponse(
            success=True,
            result=result_content,
            timestamp=datetime.now(),
            analysis_type="interactive",
            metadata={"question": request.question, "context": request.context}
        )
        
    except Exception as e:
        print(f"❌ Erro ao processar pergunta: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao processar pergunta: {str(e)}")

@app.get("/status")
async def get_status():
    """Status detalhado do agente"""
    
    status = {
        "agent_initialized": agente is not None,
        "timestamp": datetime.now(),
        "environment": {
            "dashboard_url": os.getenv("DASHBOARD_URL", "não configurado"),
            "openai_configured": bool(os.getenv("OPENAI_API_KEY")),
            "memory_configured": bool(os.getenv("MEMORY_DB_URL"))
        }
    }
    
    return status

@app.get("/available-analyses")
async def get_available_analyses():
    """Lista de análises disponíveis"""
    
    analyses = {
        "performance": {
            "name": "Análise de Performance",
            "description": "Análise completa da operação atual",
            "parameters": []
        },
        "financial": {
            "name": "Saúde Financeira", 
            "description": "Avaliação financeira e ROI",
            "parameters": []
        },
        "drivers": {
            "name": "Performance de Motoristas",
            "description": "Análise de produtividade dos motoristas",
            "parameters": []
        },
        "expansion": {
            "name": "Expansão Geográfica",
            "description": "Estratégia para novas cidades",
            "parameters": ["cities (opcional)"]
        },
        "trends": {
            "name": "Tendências de Mercado",
            "description": "Análise de tendências e projeções",
            "parameters": []
        },
        "executive": {
            "name": "Relatório Executivo",
            "description": "Relatório completo para liderança",
            "parameters": []
        }
    }
    
    return analyses

if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("PORT", 8001))
    
    print(f"🚀 Iniciando API do Agente na porta {port}")
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=False
    )
