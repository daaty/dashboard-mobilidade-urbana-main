"""
🎮 PLAYGROUND SIMPLIFICADO PARA TESTE - SEM LOOPS
Versão minimalista para corrigir o problema de chamadas múltiplas
"""

import os
import sys
import json
import time
import logging
from datetime import datetime
from typing import Optional, Dict, List, Any
from dotenv import load_dotenv
from fastapi import Body, FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.util import get_remote_address

# Adicionar o caminho da implementação local do AGNO
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "agno", "libs", "agno"))

from agno.playground import Playground
from agno.agent import Agent
from agno.models.openai import OpenAIChat

# Carrega as variáveis de ambiente
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

# --- Configuração de Logging ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- Rate Limiting ---
limiter = Limiter(key_func=get_remote_address)

# --- Instruções SUPER SIMPLES ---
simple_instructions = [
    "Você é um assistente amigável e simples.",
    "Para cumprimentos (oi, olá, hello): apenas cumprimente de volta.",
    "Seja conciso e direto.",
    "NÃO use ferramentas para cumprimentos simples.",
    "Use emojis: 👋 😊"
]

# --- Agente MINIMALISTA ---
try:
    print("🔧 Criando agente MINIMALISTA...")
    mobility_agent = Agent(
        name="SimpleAgent",
        model=OpenAIChat(id="gpt-4o-mini", api_key=api_key),
        tools=[],  # ❌ ZERO FERRAMENTAS
        instructions=simple_instructions,
        storage=None,  # ❌ SEM STORAGE
        memory=None,   # ❌ SEM MEMORY
        reasoning=False,  # ❌ SEM REASONING
        markdown=True,
        show_tool_calls=False,
        description="Agente minimalista para teste"
    )
    print("✅ Agente MINIMALISTA criado com sucesso!")
    
except Exception as e:
    print(f"❌ Erro ao criar agente: {e}")
    mobility_agent = None

# --- Playground SIMPLES ---
class SimplePlayground(Playground):
    async def run_agent(self, message: str, session_id: str = None, user_id: str = None) -> str:
        """Executa o agente de forma SUPER SIMPLES"""
        try:
            logging.info(f"🤖 Executando SimpleAgent - Mensagem: {message}")
            
            if not mobility_agent:
                return "❌ Agente não disponível"
            
            # Execução DIRETA sem complicações
            result = mobility_agent.run(message=message)
            
            logging.info(f"✅ Resposta gerada com sucesso")
            return str(result)
            
        except Exception as e:
            logging.error(f"❌ Erro: {e}")
            return f"❌ Erro: {str(e)}"
    
    def get_app(self):
        """Aplicação FastAPI SIMPLIFICADA"""
        app = FastAPI(title="Simple Mobility Playground", version="1.0.0")
        
        # CORS básico
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        # ENDPOINT PRINCIPAL - SIMPLIFICADO
        @app.post("/v1/playground/agents/{agent_id}/runs")
        @limiter.limit("60/minute")
        async def run_simple_agent(agent_id: str, request: Request, payload: Dict[str, Any] = Body(...)):
            start_time = time.time()
            
            try:
                logging.info(f"🎯 Request recebido - Agent ID: {agent_id}")
                logging.info(f"📦 Payload: {payload}")
                
                # Extrai mensagem
                message = payload.get("message", "")
                if not message:
                    raise HTTPException(status_code=400, detail="Mensagem é obrigatória")
                
                logging.info(f"📝 Mensagem: {message}")
                
                # Executa agente
                result = await self.run_agent(message)
                
                # Resposta SIMPLES
                response = {
                    "id": f"run_{int(time.time())}",
                    "agent_id": agent_id,
                    "status": "completed",
                    "result": result,
                    "timestamp": datetime.now().isoformat(),
                    "execution_time": round(time.time() - start_time, 2)
                }
                
                logging.info(f"✅ Sucesso em {response['execution_time']}s")
                return response
                
            except Exception as e:
                logging.error(f"❌ Erro: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        # Health check
        @app.get("/health")
        def health_check():
            return {
                "status": "healthy",
                "agent": "SimpleAgent",
                "version": "1.0.0",
                "timestamp": datetime.now().isoformat()
            }
        
        # Root
        @app.get("/")
        def root():
            return {"message": "Simple Mobility Playground", "status": "online"}
        
        return app

# --- Inicialização ---
if mobility_agent:
    playground_app = SimplePlayground(agents=[mobility_agent])
    app = playground_app.get_app()
else:
    # Fallback app
    app = FastAPI()
    
    @app.get("/")
    def fallback_root():
        return {"error": "Agente não disponível", "status": "error"}

if __name__ == "__main__":
    port = int(os.getenv("PORT", 7777))
    logging.info(f"🚀 Iniciando Simple Playground na porta {port}")
    logging.info(f"🎯 Endpoints:")
    logging.info(f"   - Health: http://localhost:{port}/health")
    logging.info(f"   - Main: POST http://localhost:{port}/v1/playground/agents/{{agent_id}}/runs")
    
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=port, reload=False)
