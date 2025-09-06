"""
🎮 PLAYGROUND DO AGENTE INTELIGENTE
Interface web para monitorar e interagir com o agente AGNO em tempo real
"""

import os
import sys
import json
import asyncio
import threading
import time
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from queue import Queue

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

# Adicionar o diretório dashboard_agent ao path
sys.path.append(os.path.join(os.path.dirname(__file__), "dashboard_agent"))

from dashboard_agent.mobility_agent import MobilityDashboardAgent
from monitor import MonitoredAgent, DebugLogger
from dotenv import load_dotenv

load_dotenv()

@dataclass
class ToolCall:
    """Registro de chamada de ferramenta"""
    timestamp: datetime
    tool_name: str
    method: str
    args: Dict[str, Any]
    result: Any
    duration: float
    success: bool
    error: Optional[str] = None

@dataclass
class AgentInteraction:
    """Registro de interação com o agente"""
    timestamp: datetime
    user_input: str
    agent_response: str
    tool_calls: List[ToolCall]
    duration: float
    tokens_used: Optional[int] = None

class PlaygroundMonitor:
    """Monitor para capturar dados do agente em tempo real"""
    
    def __init__(self):
        self.tool_calls: List[ToolCall] = []
        self.interactions: List[AgentInteraction] = []
        self.active_websockets: List[WebSocket] = []
        self.logs_queue = Queue()
        
    def log_tool_call(self, tool_call: ToolCall):
        """Registra uma chamada de ferramenta"""
        self.tool_calls.append(tool_call)
        self._broadcast({
            "type": "tool_call",
            "data": asdict(tool_call)
        })
        
    def log_interaction(self, interaction: AgentInteraction):
        """Registra uma interação completa"""
        self.interactions.append(interaction)
        self._broadcast({
            "type": "interaction",
            "data": asdict(interaction)
        })
        
    def log_message(self, level: str, message: str):
        """Registra uma mensagem de log"""
        log_entry = {
            "timestamp": datetime.now(),
            "level": level,
            "message": message
        }
        self.logs_queue.put(log_entry)
        self._broadcast({
            "type": "log",
            "data": log_entry
        })
        
    def _broadcast(self, message: Dict[str, Any]):
        """Envia mensagem para todos os websockets conectados"""
        if self.active_websockets:
            for websocket in self.active_websockets.copy():
                try:
                    asyncio.create_task(websocket.send_json(message))
                except:
                    self.active_websockets.remove(websocket)

# Instância global do monitor e logger
monitor = PlaygroundMonitor()
logger = DebugLogger("playground.log")

# Criar aplicação FastAPI
app = FastAPI(
    title="🎮 Playground do Agente Inteligente",
    description="Interface para monitorar e interagir com o agente AGNO",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Modelos Pydantic
class ChatMessage(BaseModel):
    message: str
    analysis_type: Optional[str] = "interactive"

class AgentResponse(BaseModel):
    response: str
    tool_calls: List[Dict[str, Any]]
    duration: float
    timestamp: datetime

# Instância global do agente
agente: Optional[MobilityDashboardAgent] = None

@app.on_event("startup")
async def startup_event():
    """Inicializar o agente"""
    global agente
    
    try:
        monitor.log_message("INFO", "🚀 Inicializando agente...")
        
        agente = MobilityDashboardAgent(
            dashboard_url=os.getenv("DASHBOARD_URL", "https://fastapi.urbanmt.com.br"),
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            memory_db_url=os.getenv("MEMORY_DB_URL")
        )
        
        monitor.log_message("SUCCESS", "✅ Agente inicializado com sucesso!")
        
    except Exception as e:
        monitor.log_message("ERROR", f"❌ Erro ao inicializar agente: {e}")
        agente = None

@app.get("/", response_class=HTMLResponse)
async def get_playground():
    """Página principal do playground"""
    return HTMLResponse(content=PLAYGROUND_HTML)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket para comunicação em tempo real"""
    await websocket.accept()
    monitor.active_websockets.append(websocket)
    
    try:
        # Enviar dados iniciais
        await websocket.send_json({
            "type": "init",
            "data": {
                "tool_calls": [asdict(tc) for tc in monitor.tool_calls[-10:]],
                "interactions": [asdict(i) for i in monitor.interactions[-5:]],
                "agent_status": "online" if agente else "offline"
            }
        })
        
        while True:
            data = await websocket.receive_json()
            
            if data["type"] == "chat":
                await handle_chat_message(websocket, data["message"])
                
            elif data["type"] == "get_stats":
                await send_stats(websocket)
                
    except WebSocketDisconnect:
        monitor.active_websockets.remove(websocket)

async def handle_chat_message(websocket: WebSocket, message: str):
    """Processa mensagem do chat"""
    if not agente:
        await websocket.send_json({
            "type": "error",
            "data": {"message": "❌ Agente não está disponível"}
        })
        return
        
    start_time = time.time()
    tool_calls_before = len(monitor.tool_calls)
    
    try:
        monitor.log_message("INFO", f"🤔 Usuário perguntou: {message}")
        
        # Executar análise interativa
        response = agente.interactive_analysis(message)
        
        duration = time.time() - start_time
        tool_calls_made = monitor.tool_calls[tool_calls_before:]
        
        # Registrar interação
        interaction = AgentInteraction(
            timestamp=datetime.now(),
            user_input=message,
            agent_response=response,
            tool_calls=tool_calls_made,
            duration=duration
        )
        
        monitor.log_interaction(interaction)
        
        await websocket.send_json({
            "type": "chat_response",
            "data": {
                "response": response,
                "duration": duration,
                "tool_calls_count": len(tool_calls_made)
            }
        })
        
    except Exception as e:
        monitor.log_message("ERROR", f"❌ Erro ao processar mensagem: {e}")
        await websocket.send_json({
            "type": "error",
            "data": {"message": f"Erro: {e}"}
        })

async def send_stats(websocket: WebSocket):
    """Envia estatísticas do agente"""
    stats = {
        "total_interactions": len(monitor.interactions),
        "total_tool_calls": len(monitor.tool_calls),
        "avg_response_time": sum(i.duration for i in monitor.interactions) / len(monitor.interactions) if monitor.interactions else 0,
        "most_used_tools": {},
        "recent_activity": [asdict(i) for i in monitor.interactions[-5:]]
    }
    
    # Calcular ferramentas mais usadas
    for tc in monitor.tool_calls:
        tool_key = f"{tc.tool_name}.{tc.method}"
        stats["most_used_tools"][tool_key] = stats["most_used_tools"].get(tool_key, 0) + 1
    
    await websocket.send_json({
        "type": "stats",
        "data": stats
    })

@app.get("/api/health")
async def health_check():
    """Health check"""
    return {
        "status": "healthy",
        "agent_ready": agente is not None,
        "timestamp": datetime.now()
    }

@app.get("/api/stats")
async def get_stats():
    """Estatísticas da API"""
    return {
        "total_interactions": len(monitor.interactions),
        "total_tool_calls": len(monitor.tool_calls),
        "agent_status": "online" if agente else "offline"
    }

# HTML do Playground
PLAYGROUND_HTML = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🎮 Playground do Agente Inteligente</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://unpkg.com/alpinejs@3.x.x/dist/cdn.min.js" defer></script>
    <style>
        [x-cloak] { display: none !important; }
        .fade-in { animation: fadeIn 0.3s ease-in; }
        @keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
    </style>
</head>
<body class="bg-gray-100 min-h-screen">
    <div x-data="playground()" x-init="init()" class="container mx-auto p-4">
        <!-- Header -->
        <div class="bg-white rounded-lg shadow-md p-6 mb-6">
            <div class="flex items-center justify-between">
                <div class="flex items-center space-x-4">
                    <h1 class="text-3xl font-bold text-gray-800">🎮 Playground do Agente</h1>
                    <div class="flex items-center space-x-2">
                        <div class="w-3 h-3 rounded-full" :class="agentStatus === 'online' ? 'bg-green-500' : 'bg-red-500'"></div>
                        <span class="text-sm font-medium" x-text="agentStatus === 'online' ? 'Online' : 'Offline'"></span>
                    </div>
                </div>
                <div class="flex space-x-4">
                    <div class="text-center">
                        <div class="text-2xl font-bold text-blue-600" x-text="stats.total_interactions"></div>
                        <div class="text-xs text-gray-500">Interações</div>
                    </div>
                    <div class="text-center">
                        <div class="text-2xl font-bold text-green-600" x-text="stats.total_tool_calls"></div>
                        <div class="text-xs text-gray-500">Tool Calls</div>
                    </div>
                    <div class="text-center">
                        <div class="text-2xl font-bold text-purple-600" x-text="stats.avg_response_time?.toFixed(1) + 's'"></div>
                        <div class="text-xs text-gray-500">Tempo Médio</div>
                    </div>
                </div>
            </div>
        </div>

        <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <!-- Chat Interface -->
            <div class="lg:col-span-2">
                <div class="bg-white rounded-lg shadow-md h-96 flex flex-col">
                    <div class="p-4 border-b">
                        <h2 class="text-xl font-semibold text-gray-800">💬 Chat com o Agente</h2>
                    </div>
                    
                    <!-- Messages -->
                    <div class="flex-1 overflow-y-auto p-4 space-y-4" id="messages">
                        <template x-for="message in messages" :key="message.id">
                            <div class="fade-in" :class="message.type === 'user' ? 'text-right' : 'text-left'">
                                <div class="inline-block max-w-3/4 p-3 rounded-lg" 
                                     :class="message.type === 'user' ? 'bg-blue-500 text-white' : 'bg-gray-200 text-gray-800'">
                                    <div x-html="message.content"></div>
                                    <div class="text-xs opacity-75 mt-1" x-text="message.timestamp"></div>
                                </div>
                            </div>
                        </template>
                    </div>
                    
                    <!-- Input -->
                    <div class="p-4 border-t">
                        <div class="flex space-x-2">
                            <input type="text" 
                                   x-model="currentMessage" 
                                   @keyup.enter="sendMessage()"
                                   :disabled="isLoading"
                                   placeholder="Digite sua pergunta sobre o negócio..."
                                   class="flex-1 p-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500">
                            <button @click="sendMessage()" 
                                    :disabled="isLoading || !currentMessage.trim()"
                                    class="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:opacity-50">
                                <span x-show="!isLoading">Enviar</span>
                                <span x-show="isLoading" class="flex items-center">
                                    <svg class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
                                        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                                        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                                    </svg>
                                    Processando...
                                </span>
                            </button>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Sidebar -->
            <div class="space-y-6">
                <!-- Tool Calls -->
                <div class="bg-white rounded-lg shadow-md">
                    <div class="p-4 border-b">
                        <h3 class="text-lg font-semibold text-gray-800">🛠️ Tool Calls Recentes</h3>
                    </div>
                    <div class="p-4 space-y-2 max-h-64 overflow-y-auto">
                        <template x-for="toolCall in recentToolCalls" :key="toolCall.timestamp">
                            <div class="text-sm p-2 bg-gray-50 rounded border-l-4" 
                                 :class="toolCall.success ? 'border-green-500' : 'border-red-500'">
                                <div class="font-medium" x-text="toolCall.tool_name + '.' + toolCall.method"></div>
                                <div class="text-gray-600 text-xs" x-text="toolCall.duration.toFixed(2) + 'ms'"></div>
                            </div>
                        </template>
                    </div>
                </div>

                <!-- Logs -->
                <div class="bg-white rounded-lg shadow-md">
                    <div class="p-4 border-b">
                        <h3 class="text-lg font-semibold text-gray-800">📋 Logs</h3>
                    </div>
                    <div class="p-4 space-y-1 max-h-64 overflow-y-auto text-xs font-mono">
                        <template x-for="log in recentLogs" :key="log.timestamp">
                            <div class="p-1" :class="{
                                'text-green-600': log.level === 'SUCCESS',
                                'text-red-600': log.level === 'ERROR',
                                'text-blue-600': log.level === 'INFO',
                                'text-gray-600': log.level === 'DEBUG'
                            }">
                                <span x-text="new Date(log.timestamp).toLocaleTimeString()"></span>
                                <span x-text="log.message"></span>
                            </div>
                        </template>
                    </div>
                </div>

                <!-- Quick Actions -->
                <div class="bg-white rounded-lg shadow-md">
                    <div class="p-4 border-b">
                        <h3 class="text-lg font-semibold text-gray-800">⚡ Análises Rápidas</h3>
                    </div>
                    <div class="p-4 space-y-2">
                        <button @click="quickAnalysis('Qual é a performance geral dos motoristas?')" 
                                class="w-full text-left p-2 text-sm bg-blue-50 hover:bg-blue-100 rounded">
                            📊 Performance Geral
                        </button>
                        <button @click="quickAnalysis('Como está a saúde financeira da empresa?')" 
                                class="w-full text-left p-2 text-sm bg-green-50 hover:bg-green-100 rounded">
                            💰 Saúde Financeira
                        </button>
                        <button @click="quickAnalysis('Quais cidades têm potencial de expansão?')" 
                                class="w-full text-left p-2 text-sm bg-purple-50 hover:bg-purple-100 rounded">
                            🌍 Oportunidades
                        </button>
                        <button @click="quickAnalysis('Gere um relatório executivo completo')" 
                                class="w-full text-left p-2 text-sm bg-orange-50 hover:bg-orange-100 rounded">
                            📋 Relatório Executivo
                        </button>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        function playground() {
            return {
                ws: null,
                agentStatus: 'offline',
                messages: [],
                currentMessage: '',
                isLoading: false,
                recentToolCalls: [],
                recentLogs: [],
                stats: {
                    total_interactions: 0,
                    total_tool_calls: 0,
                    avg_response_time: 0
                },

                init() {
                    this.connectWebSocket();
                },

                connectWebSocket() {
                    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
                    const wsUrl = `${protocol}//${window.location.host}/ws`;
                    
                    this.ws = new WebSocket(wsUrl);
                    
                    this.ws.onopen = () => {
                        console.log('WebSocket conectado');
                        this.agentStatus = 'online';
                    };
                    
                    this.ws.onmessage = (event) => {
                        const data = JSON.parse(event.data);
                        this.handleWebSocketMessage(data);
                    };
                    
                    this.ws.onclose = () => {
                        console.log('WebSocket desconectado');
                        this.agentStatus = 'offline';
                        // Tentar reconectar após 3 segundos
                        setTimeout(() => this.connectWebSocket(), 3000);
                    };
                },

                handleWebSocketMessage(data) {
                    switch(data.type) {
                        case 'init':
                            this.recentToolCalls = data.data.tool_calls || [];
                            this.agentStatus = data.data.agent_status;
                            break;
                            
                        case 'chat_response':
                            this.addMessage('agent', data.data.response);
                            this.isLoading = false;
                            break;
                            
                        case 'tool_call':
                            this.recentToolCalls.unshift(data.data);
                            this.recentToolCalls = this.recentToolCalls.slice(0, 10);
                            break;
                            
                        case 'log':
                            this.recentLogs.unshift(data.data);
                            this.recentLogs = this.recentLogs.slice(0, 20);
                            break;
                            
                        case 'stats':
                            this.stats = data.data;
                            break;
                            
                        case 'error':
                            this.addMessage('agent', `❌ ${data.data.message}`);
                            this.isLoading = false;
                            break;
                    }
                },

                sendMessage() {
                    if (!this.currentMessage.trim() || this.isLoading) return;
                    
                    const message = this.currentMessage.trim();
                    this.addMessage('user', message);
                    this.currentMessage = '';
                    this.isLoading = true;
                    
                    this.ws.send(JSON.stringify({
                        type: 'chat',
                        message: message
                    }));
                },

                quickAnalysis(question) {
                    this.currentMessage = question;
                    this.sendMessage();
                },

                addMessage(type, content) {
                    this.messages.push({
                        id: Date.now(),
                        type: type,
                        content: this.formatMessage(content),
                        timestamp: new Date().toLocaleTimeString()
                    });
                    
                    // Scroll para a última mensagem
                    this.$nextTick(() => {
                        const messagesDiv = document.getElementById('messages');
                        messagesDiv.scrollTop = messagesDiv.scrollHeight;
                    });
                },

                formatMessage(content) {
                    // Converter markdown básico para HTML
                    return content
                        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
                        .replace(/\*(.*?)\*/g, '<em>$1</em>')
                        .replace(/\n/g, '<br>');
                }
            }
        }
    </script>
</body>
</html>
"""

if __name__ == "__main__":
    print("🎮 INICIANDO PLAYGROUND DO AGENTE INTELIGENTE")
    print("=" * 50)
    print("🌐 Interface: http://localhost:8002")
    print("📊 API Docs: http://localhost:8002/docs")
    print("💬 WebSocket: ws://localhost:8002/ws")
    print("=" * 50)
    
    uvicorn.run(
        "playground:app",
        host="0.0.0.0",
        port=8002,
        reload=True,
        log_level="info"
    )
