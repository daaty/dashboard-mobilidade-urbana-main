"""
🎮 PLAYGROUND CUSTOMIZADO PARA AGENTE DE MOBILIDADE URBANA
Baseado no padrão do Alice Agent com todas as melhorias
"""

import os
import sys
import json
import time
import logging
from datetime import datetime
from typing import Optional, Dict, List, Any
from dataclasses import dataclass
from functools import wraps
from dotenv import load_dotenv
from fastapi import Body, FastAPI, Request, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse, HTMLResponse
from pydantic import BaseModel, Field, validator
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from cachetools import TTLCache
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

# Adicionar o caminho da implementação local do AGNO
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "agno", "libs", "agno"))

from agno.playground import Playground
from agno.storage.postgres import PostgresStorage
from agno.memory.v2.db.postgres import PostgresMemoryDb
from agno.memory.v2.memory import Memory

# Importações do AGNO
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.playground import Playground

# Importação do endpoint financeiro específico
from financial_endpoint import router as financial_router

# Importações das nossas ferramentas
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), "dashboard_agent"))

from dashboard_agent.tools.dashboard_api_tools import DashboardAPITools
from dashboard_agent.tools.business_analysis_tools import BusinessAnalysisTools
from dashboard_agent.tools.financial_tools import FinancialTools  # ✅ NOVA FERRAMENTA FINANCEIRA

# Carrega as variáveis de ambiente
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

# --- Configuração de Logging ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('mobility_playground.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# --- Configuração de Rate Limiting ---
limiter = Limiter(key_func=get_remote_address)

# --- Configuração de Cache ---
dashboard_cache = TTLCache(maxsize=1000, ttl=300)  # 5 minutos
analysis_cache = TTLCache(maxsize=100, ttl=1800)   # 30 minutos

# --- Configurações da Aplicação ---
@dataclass
class MobilityConfig:
    """Configurações centralizadas do agente de mobilidade"""
    DASHBOARD_URL = os.getenv("DASHBOARD_URL", "https://fastapi.urbanmt.com.br")
    AGENT_STORAGE_PATH = "tmp/mobility_agents.db"
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# --- Decoradores para Resiliência ---
def circuit_breaker(max_failures=3, timeout=60):
    """Circuit breaker para APIs externas"""
    failures = []
    last_failure = 0

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            nonlocal failures, last_failure
            if len(failures) >= max_failures:
                time_since_last = time.time() - last_failure
                if time_since_last < timeout:
                    logger.error(f"[CIRCUIT BREAKER] Circuito aberto para {func.__name__}")
                    raise Exception("Circuit breaker está aberto - API temporariamente indisponível")
                else:
                    logger.info(f"[CIRCUIT BREAKER] Resetando circuito para {func.__name__}")
                    failures.clear()
            try:
                result = func(*args, **kwargs)
                if failures:
                    logger.info(f"[CIRCUIT BREAKER] Sucesso em {func.__name__}, resetando falhas")
                failures.clear()
                return result
            except Exception as e:
                failures.append(e)
                last_failure = time.time()
                logger.warning(f"[CIRCUIT BREAKER] Falha em {func.__name__}: {e}")
                raise
        return wrapper
    return decorator

def cache_result(cache_obj, key_func):
    """Decorator para cache de resultados"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            cache_key = key_func(*args, **kwargs)
            try:
                if cache_key in cache_obj:
                    logger.debug(f"Cache hit para: {cache_key}")
                    return cache_obj[cache_key]
            except Exception as e:
                logger.warning(f"Erro ao acessar cache: {e}")
            
            try:
                result = func(*args, **kwargs)
                try:
                    cache_obj[cache_key] = result
                    logger.debug(f"Resultado cacheado: {cache_key}")
                except Exception as e:
                    logger.warning(f"Erro ao salvar no cache: {e}")
                return result
            except Exception as e:
                logger.error(f"Erro na função: {e}")
                raise
        return wrapper
    return decorator

# --- Classes de Erro ---
class DashboardAPIError(Exception):
    """Erro relacionado à API do dashboard"""
    pass

class AnalysisError(Exception):
    """Erro de análise de dados"""
    pass

# --- Agente com Memória Otimizada ---
class MobilityMemoryAgent(Agent):
    """Agente de mobilidade com memória persistente"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.session_memory = {}  # Memória por sessão
        self.dashboard_cache = {}  # Cache de dados do dashboard
        
    def extract_business_context(self, message: str, session_id: str) -> Dict[str, Any]:
        """Extrai contexto de negócio da mensagem"""
        import re
        context = {}
        
        # Padrões para extração
        patterns = {
            "cidade": r"(?:cidade|em|de) ([\w\s]+)",
            "periodo": r"(?:últimos?|nos) (\d+) (?:dias?|meses?|semanas?)",
            "metrica": r"(?:motoristas?|corridas?|kpis?|financeiro|gastos?)",
            "analise": r"(?:análise|relatório|performance|tendência)"
        }
        
        for key, pattern in patterns.items():
            matches = re.findall(pattern, message.lower())
            if matches:
                context[key] = matches[0] if len(matches) == 1 else matches
                
        return context
    
    def update_session_memory(self, message: str, session_id: str, context: dict = None):
        """Atualiza memória da sessão"""
        if session_id not in self.session_memory:
            self.session_memory[session_id] = {
                "business_context": {},
                "last_queries": [],
                "preferred_metrics": [],
                "timestamp": datetime.now()
            }
        
        # Extrai contexto de negócio
        business_context = self.extract_business_context(message, session_id)
        self.session_memory[session_id]["business_context"].update(business_context)
        
        # Mantém histórico de consultas
        self.session_memory[session_id]["last_queries"].append({
            "message": message,
            "timestamp": datetime.now(),
            "context": context
        })
        
        # Mantém apenas as últimas 5 consultas
        if len(self.session_memory[session_id]["last_queries"]) > 5:
            self.session_memory[session_id]["last_queries"] = \
                self.session_memory[session_id]["last_queries"][-5:]
    
    def get_session_context(self, session_id: str) -> str:
        """Recupera contexto da sessão"""
        if session_id not in self.session_memory:
            return ""
        
        memory = self.session_memory[session_id]
        context_parts = []
        
        if memory["business_context"]:
            context_parts.append("Contexto de negócio conhecido:")
            for key, value in memory["business_context"].items():
                context_parts.append(f"- {key}: {value}")
        
        if memory["last_queries"]:
            context_parts.append("Consultas recentes:")
            for query in memory["last_queries"][-3:]:  # Últimas 3
                context_parts.append(f"- {query['message'][:50]}...")
        
        return "\n".join(context_parts)
    
    def run(self, message, session_id=None, context=None, **kwargs):
        """Override com memória otimizada"""
        if session_id:
            self.update_session_memory(message, session_id, context)
            
        # Adiciona contexto da sessão
        session_context = self.get_session_context(session_id or "default")
        enhanced_context = context.copy() if context else {}
        if session_context:
            enhanced_context["session_memory"] = session_context
            
        return super().run(message=message, session_id=session_id, context=enhanced_context, **kwargs)

# --- Instruções do Agente ---
# --- Instruções do Agente ---
mobility_instructions = [
    "Você é um agente especialista em análise de dados de mobilidade urbana da empresa Urban.",
    "Você tem DUAS FUNÇÕES PRINCIPAIS:",
    "",
    "🔧 1) ANÁLISE DE MOBILIDADE URBANA:",
    "- Consultar dados em tempo real de motoristas, corridas e KPIs financeiros",
    "- SEMPRE consulte os dados do dashboard PRIMEIRO antes de fazer análises",
    "- Use: get_drivers_overview, get_drivers_list, get_rides_overview, calculate_business_kpis, financial_health_check",
    "",
    "💰 2) GESTÃO FINANCEIRA DA EMPRESA:",
    "SUA FUNÇÃO É INSERIR E ATUALIZAR O BANCO DE DADOS DA EMPRESA quando receber dados de documentos.",
    "Use o REASONING antes de usar qualquer ferramenta financeira para analisar a situação.",
    "",
    "📄 RECONHECIMENTO DE DADOS FINANCEIROS:",
    "Quando receber dados no formato JSON com 'webContentLink' e 'content.parts[0].text', você está recebendo:",
    "- DESCRIÇÃO DO ARQUIVO: content.parts[0].text (dados extraídos da imagem)",
    "- LINK DO ARQUIVO: webContentLink (URL do Google Drive)",
    "- NOME DO ARQUIVO: name (indica se é comprovante ou nota fiscal)",
    "",
    "IMEDIATAMENTE ao identificar estes dados, EXECUTE o fluxo financeiro:",
    "",
    "🔄 FLUXO OBRIGATÓRIO PARA GASTOS:",
    "",
    "ETAPA 1 - INSERÇÃO INICIAL:",
    "- ASSIM QUE receber 'DESCRIÇÃO DO ARQUIVO' e 'LINK DO ARQUIVO'",
    "- Execute 'inserir_gasto_empresa' COM OS DADOS EXTRAÍDOS",
    "- Use IDs aleatórios (100000-999999)",
    "- Se erro de ID duplicado, tente novamente com ID diferente (máximo 5 tentativas)",
    "- SEMPRE retorne SUCESSO ou FALHA",
    "",
    "ETAPA 2 - COLETA DE INFORMAÇÕES:",
    "Após inserir com sucesso, informe o ID usado e pergunte EXATAMENTE:",
    "\"✅ Dados inseridos com sucesso! ID: [id_usado]\"",
    "\"\"",
    "\"Agora preciso de mais informações:\"",
    "\"1) Este comprovante possui Nota Fiscal correspondente? (Sim/Não)\"",
    "\"2) Qual a natureza deste gasto? (Alimentação, Transporte, Material de Escritório, Serviços, Marketing, Viagem, Outros)\"",
    "\"3) Confirme se o nome do fornecedor extraído está correto: [fornecedor_extraido]\"",
    "",
    "ETAPA 3 - ATUALIZAÇÃO COM DADOS DO USUÁRIO:",
    "Com base na resposta do usuário:",
    "",
    "3.1) Se responder \"SIM\" para Nota Fiscal:",
    "- Solicite: \"Envie os dados da Nota Fiscal (descrição + link)\"",
    "- Quando receber: faça novo INSERT da NF com novo ID",
    "- Depois: atualize o comprovante vinculando à NF (id_documento_vinculado)",
    "",
    "3.2) Se responder \"NÃO\" para Nota Fiscal:",
    "- Apenas atualize o comprovante com: natureza_do_gasto, fornecedor, possui_nota_fiscal=false",
    "",
    "Use 'atualizar_gasto_empresa' APENAS nestas colunas específicas:",
    "- possui_nota_fiscal, id_documento_vinculado, status_documentacao",
    "- observacoes, numero_nota_fiscal, serie_nota_fiscal",
    "- chave_acesso_nfe, cnpj_emissor, inscricao_estadual, data_processamento",
    "",
    "ETAPA 4 - RELATÓRIO FINAL:",
    "Envie relatório resumido: ID inserido, fornecedor, valor, natureza, status NF",
    "",
    "⚠️ REGRAS IMPORTANTES:",
    "- SEMPRE distinguir: 'COMPROVANTE DE PAGAMENTO' vs 'NOTA FISCAL'",
    "- Para COMPROVANTE: INSERT + UPDATE com dados do usuário",
    "- Para NOTA FISCAL: INSERT + vinculação ao comprovante existente",
    "- NÃO confundir ferramentas de inserção e update",
    "- Use o ID da inserção original para todos os updates",
    "",
    "📊 FORMATO DE RESPOSTA:",
    "- Seja objetivo e use dados específicos",
    "- Inclua números e percentuais quando disponível", 
    "- Use emojis: 📊 📈 📉 ⚠️ ✅ 💰 📄",
    "- Para mobilidade: insights estratégicos e recomendações",
    "- Para financeiro: status claro de cada etapa",
    "",
    "CONTEXTO: A Urban é uma empresa de transporte urbano que opera em múltiplas cidades.",
    "Use a memória da sessão para personalizar análises e lembrar IDs de gastos inseridos."
]

# --- Função para formatar contexto ---
def format_context(context: dict) -> str:
    """Formata contexto para o prompt"""
    lines = ["[MOBILITY_CONTEXT]"]
    
    if context.get("session_id"):
        lines.append(f"Sessão: {context.get('session_id')}")
    
    if context.get("dashboard_url"):
        lines.append(f"Dashboard: {context.get('dashboard_url')}")
    
    if context.get("session_memory"):
        lines.append("[SESSION_MEMORY]")
        lines.append(context.get("session_memory"))
        lines.append("[/SESSION_MEMORY]")
    
    lines.append("[/MOBILITY_CONTEXT]\n")
    return "\n".join(lines)

# --- Agente Principal ---
class MobilityAgentWithContext(MobilityMemoryAgent):
    """Agente de mobilidade com contexto formatado"""
    
    def run(self, message, session_id=None, context=None, **kwargs):
        context = context or {}
        context["dashboard_url"] = MobilityConfig.DASHBOARD_URL
        
        context_text = format_context(context)
        prompt = f"{context_text}\n" + "\n".join(mobility_instructions) + f"\n\nUsuário: {message}"
        
        return super().run(message=prompt, session_id=session_id, context=context, **kwargs)

# --- Inicialização das Ferramentas ---
try:
    print("🔧 Inicializando ferramentas do dashboard...")
    dashboard_tools = DashboardAPITools(base_url=MobilityConfig.DASHBOARD_URL)
    print(f"✅ DashboardAPITools: {len(dashboard_tools.tools)} ferramentas")
    
    business_tools = BusinessAnalysisTools()
    print(f"✅ BusinessAnalysisTools: {len(business_tools.tools)} ferramentas")
    
    financial_tools = FinancialTools()  # ✅ NOVA FERRAMENTA FINANCEIRA
    print(f"✅ FinancialTools: {len(financial_tools.tools)} ferramentas")
    
    # Configurar storage PostgreSQL do AGNO
    postgres_storage = None
    postgres_memory = None
    try:
        postgres_url = os.getenv("DATABASE_URL")
        if postgres_url:
            # Converter formato asyncpg para psycopg2 se necessário
            if "postgresql+asyncpg://" in postgres_url:
                postgres_url = postgres_url.replace("postgresql+asyncpg://", "postgresql://")
            
            # Configurar storage para sessões
            postgres_storage = PostgresStorage(
                table_name="agno_mobility_sessions",
                db_url=postgres_url,
                auto_upgrade_schema=True
            )
            print(f"✅ PostgreSQL Storage configurado: {postgres_url[:50]}...")
            
            # Configurar memória PostgreSQL para lembrar contexto
            postgres_memory_db = PostgresMemoryDb(
                table_name="agno_mobility_memories",
                db_url=postgres_url
            )
            postgres_memory_db.create()  # Criar tabela explicitamente
            postgres_memory = Memory(
                db=postgres_memory_db,
                model=OpenAIChat(id="gpt-4o-mini", api_key=api_key)  # Modelo para processar memórias
            )
            print(f"✅ PostgreSQL Memory configurado: agno_mobility_memories")
            
        else:
            print("⚠️ DATABASE_URL não encontrada, usando storage local")
    except Exception as e:
        print(f"⚠️ Erro ao configurar PostgreSQL storage: {e}")
        print("💡 Continuando com storage local")
    
    # Criar agente AGNO padrão (sem customizações que possam interferir na memória)
    mobility_agent = Agent(
        name="MobilityAgent",
        model=OpenAIChat(id="gpt-4o", api_key=api_key),
        tools=[dashboard_tools, business_tools, financial_tools],  # ✅ INCLUIR FERRAMENTAS FINANCEIRAS
        instructions=mobility_instructions,
        storage=postgres_storage,  # Storage PostgreSQL do AGNO
        memory=postgres_memory,    # Memória PostgreSQL do AGNO 
        add_history_to_messages=True,
        num_history_runs=3,  # Usar num_history_runs ao invés de num_history_responses
        enable_user_memories=True,      # Ativar memórias de usuário
        enable_session_summaries=True,  # Ativar resumos de sessão
        reasoning=True,  # ✅ ATIVAR REASONING (substitui a ferramenta THINK do n8n)
        reasoning_model=OpenAIChat(id="gpt-4o-mini", api_key=api_key),  # Modelo para reasoning
        reasoning_min_steps=1,
        reasoning_max_steps=5,
        markdown=True,
        show_tool_calls=True,
        description="Agente especialista em análise de dados de mobilidade urbana da empresa Urban",
        add_datetime_to_instructions=True  # Adicionar timestamp
    )
    
    print("✅ Agente de mobilidade criado com sucesso!")
    
except Exception as e:
    print(f"❌ Erro ao inicializar agente: {e}")
    # Agente mock para não quebrar
    mobility_agent = Agent(
        name="MobilityAgent",
        model=OpenAIChat(id="gpt-4o", api_key=api_key),
        instructions=["Agente em modo de manutenção"],
        storage=postgres_storage if 'postgres_storage' in locals() else None,
        memory=postgres_memory if 'postgres_memory' in locals() else None
    )

# --- Modelos Pydantic ---
class MobilityRunPayload(BaseModel):
    message: str
    session_id: str = "default"
    analysis_type: Optional[str] = None
    city_filter: Optional[str] = None
    period: Optional[str] = "30d"

# --- Playground Customizado ---
class MobilityPlayground(Playground):
    async def run_agent(self, message: str, session_id: str = None, user_id: str = None) -> str:
        """Executa o agente de mobilidade com uma mensagem"""
        try:
            # Usa o agente global de forma síncrona
            session_id = session_id or f"session_{int(time.time())}"
            user_id = user_id or "mobility_user"
            logging.info(f"🤖 Executando MobilityAgent com sessão: {session_id}, usuário: {user_id}")
            
            # O método run do agente é síncrono com memória AGNO
            result = mobility_agent.run(
                message=message,
                session_id=session_id,
                user_id=user_id  # Adicionar user_id para memórias
            )
            
            logging.info(f"✅ Execução concluída com sucesso")
            return str(result)
            
        except Exception as e:
            logging.error(f"❌ Erro ao executar agente: {e}", exc_info=True)
            raise e
        app = super().get_app()
        
        # Middlewares
        app.add_middleware(GZipMiddleware)
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["https://app.agno.com", "http://localhost:8001", "http://127.0.0.1:8001"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        app.state.agents = {agent.name: agent for agent in self.agents}
        app.state.limiter = limiter
        
        # Remove rota padrão
        routes_to_keep = [
            route for route in app.routes 
            if getattr(route, "path", "") != "/v1/playground/agents/{agent_id}/runs"
        ]
        app.router.routes = routes_to_keep
        
        # Exception handlers
        @app.exception_handler(RateLimitExceeded)
        async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
            return JSONResponse(
                status_code=429,
                content={"detail": "Rate limit exceeded", "message": "Muitas requisições"}
            )
        
        @app.exception_handler(DashboardAPIError)
        async def dashboard_api_error_handler(request: Request, exc: DashboardAPIError):
            return JSONResponse(
                status_code=502,
                content={"detail": "Dashboard API Error", "message": str(exc)}
            )
        
        # ROTAS NECESSÁRIAS PARA O AGNO PLAYGROUND
        @app.get("/v1", tags=["AGNO Compatibility"])
        def agno_v1_root():
            """Rota raiz v1 necessária para o playground do AGNO"""
            return {"message": "AGNO Mobility Playground v1", "version": "1.0"}
        
        @app.get("/v1/playground", tags=["AGNO Compatibility"])
        def agno_playground_root():
            """Rota playground necessária para o AGNO"""
            return {"message": "Mobility Playground", "endpoints": ["/agents", "/health"]}
        
        @app.get("/v1/playground/agents", tags=["AGNO Compatibility"])
        def agno_list_agents():
            """Lista agentes no formato esperado pelo AGNO playground"""
            return [
                {
                    "id": "MobilityAgent",
                    "name": "Mobility Agent",
                    "description": "Agente especializado em análise de dados de mobilidade urbana com 24 ferramentas especializadas",
                    "model": "gpt-4o",
                    "tools_count": 24,
                    "capabilities": [
                        "Dashboard API Integration",
                        "Business Analysis",
                        "KPI Calculation",
                        "Driver Analytics",
                        "City Metrics"
                    ],
                    "status": "active"
                }
            ]
        
        @app.get("/v1/playground/status", tags=["AGNO Compatibility"])
        def agno_playground_status():
            """Status do playground no formato esperado pelo AGNO"""
            return {
                "status": "online",
                "version": "1.0",
                "agents_count": 1,
                "available": True,
                "timestamp": datetime.now().isoformat()
            }
        
        # Rota customizada - Compatível com AGNO
        @app.post("/v1/playground/agents/{agent_id}/runs", tags=["AGNO Compatibility"])
        @limiter.limit("60/minute")
        async def run_mobility_agent(agent_id: str, request: Request, payload: Dict[str, Any] = Body(...)):
            start_time = time.time()
            
            try:
                # Log detalhado do que está chegando
                logging.info(f"🎯 AGNO Request - Agent ID: {agent_id}")
                logging.info(f"📦 Payload recebido: {payload}")
                logging.info(f"📋 Headers: {dict(request.headers)}")
                
                # Extrai a mensagem do payload (formato AGNO)
                message = payload.get("message", "")
                user_id = payload.get("user_id", "agno_user")  # Extrair user_id se disponível
                session_id = payload.get("session_id")  # Extrair session_id se disponível
                
                if not message:
                    logging.error(f"❌ Mensagem vazia no payload: {payload}")
                    raise HTTPException(status_code=400, detail="Mensagem é obrigatória")
                
                logging.info(f"📝 Mensagem extraída: {message}")
                logging.info(f"👤 User ID: {user_id}, Session ID: {session_id}")
                
                # SEMPRE usa nosso MobilityAgent independente do agent_id
                # O AGNO pode gerar IDs aleatórios, mas sempre executamos nosso agente
                result = await self.run_agent(message, session_id=session_id, user_id=user_id)
                
                # Formato de resposta compatível com AGNO
                response = {
                    "id": f"run_{int(time.time())}",
                    "agent_id": agent_id,  # Retorna o ID que o AGNO enviou
                    "status": "completed",
                    "result": result,
                    "timestamp": datetime.now().isoformat(),
                    "execution_time": round(time.time() - start_time, 2)
                }
                
                logging.info(f"✅ Agente executado via AGNO em {response['execution_time']}s")
                return response
                
            except HTTPException:
                raise
            except Exception as e:
                logging.error(f"❌ Erro interno ao executar agente via AGNO: {e}", exc_info=True)
                raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")
        
        # Endpoint alternativo para capturar diferentes formatos do AGNO
        @app.post("/v1/playground/agents/{agent_id}/runs/{run_id}", tags=["AGNO Debug"])
        async def run_mobility_agent_alt(agent_id: str, run_id: str, request: Request, payload: Dict[str, Any] = Body(...)):
            """Endpoint alternativo caso o AGNO use formato diferente"""
            logging.info(f"🔍 AGNO Alt Format - Agent: {agent_id}, Run: {run_id}")
            logging.info(f"📦 Alt Payload: {payload}")
            return {"message": "Alternative endpoint detected", "agent_id": agent_id, "run_id": run_id}
        
        # 🎮 Interface Web Local
        @app.get("/", response_class=HTMLResponse, tags=["Interface"])
        def get_playground_interface():
            """Interface web do playground"""
            return self.get_interface_html()
        
        # Debug endpoint para testar agente
        @app.post("/debug/test-agent", tags=["Debug"])
        async def debug_test_agent(payload: Dict[str, Any] = Body(...)):
            """Endpoint de debug para testar o agente"""
            try:
                message = payload.get("message", "Hello")
                logging.info(f"🔍 Debug: testando agente com mensagem: {message}")
                
                # Testa execução direta
                result = mobility_agent.run(message=message, session_id="debug")
                
                return {
                    "status": "success",
                    "message": message,
                    "result": str(result),
                    "timestamp": datetime.now().isoformat()
                }
            except Exception as e:
                logging.error(f"🔍 Debug: erro no teste: {e}", exc_info=True)
                return {
                    "status": "error",
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                }
        
        # Health check
        @app.get("/health", tags=["Health"])
        def health_check():
            return {
                "status": "healthy",
                "agent": "MobilityAgent",
                "dashboard_url": MobilityConfig.DASHBOARD_URL,
                "tools": {
                    "dashboard_tools": 19,
                    "business_tools": 5
                },
                "version": "1.0",
                "timestamp": datetime.now().isoformat()
            }
        
        # List available agents
        @app.get("/agents", tags=["Agents"])
        def list_agents():
            """Lista todos os agentes disponíveis"""
            return [
                {
                    "id": "MobilityAgent",
                    "name": "Mobility Agent",
                    "description": "Agente especializado em análise de dados de mobilidade urbana",
                    "model": "gpt-4o",
                    "tools_count": 24,
                    "status": "active"
                }
            ]
        
        return app

# --- Inicialização ---
os.makedirs("tmp", exist_ok=True)

playground_app = MobilityPlayground(agents=[mobility_agent])
app = playground_app.get_app()

# Adicionar endpoint específico para N8N
app.include_router(financial_router)

if __name__ == "__main__":
    port = int(os.getenv("PORT", 7777))  # Porta padrão do AGNO
    logging.info(f"🚀 Iniciando Mobility Playground na porta {port}")
    logging.info(f"🔗 Dashboard URL: {MobilityConfig.DASHBOARD_URL}")
    logging.info(f"🎯 Endpoints principais:")
    logging.info(f"   - Health: http://localhost:{port}/health")
    logging.info(f"   - Docs: http://localhost:{port}/docs")
    logging.info(f"   - Playground: http://localhost:{port}")
    logging.info(f"   - AGNO Status: http://localhost:{port}/v1/playground/status")
    logging.info(f"   - AGNO Agents: http://localhost:{port}/v1/playground/agents")
    logging.info(f"   - Dashboard Chat: POST http://localhost:{port}/v1/playground/agents/{{agent_id}}/runs")
    logging.info(f"   - N8N Financial: POST http://localhost:{port}/financial/register")
    logging.info(f"   - Financial Health: GET http://localhost:{port}/financial/health")
    
    # Nota: O AGNO espera porta 7777 por padrão
    if port != 7777:
        logging.warning(f"⚠️  ATENÇÃO: AGNO espera porta 7777 por padrão, você está usando {port}")
        logging.warning(f"   Configure no AGNO playground: http://localhost:{port}/v1")
    
    # Usa o método serve do AGNO que é o padrão recomendado
    playground_app.serve("mobility_playground:app", host="0.0.0.0", port=port, reload=False)
