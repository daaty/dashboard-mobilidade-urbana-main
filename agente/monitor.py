"""
🔧 WRAPPER PERSONALIZADO PARA O AGENTE AGNO
Adiciona funcionalidades de monitoramento e debugging
"""

import time
import json
from datetime import datetime
from typing import Any, Dict, List, Optional
from dataclasses import dataclass

@dataclass
class ToolCallRecord:
    """Registro detalhado de uma chamada de ferramenta"""
    timestamp: datetime
    tool_name: str
    method: str
    args: Dict[str, Any]
    result: Any
    duration: float
    success: bool
    error: Optional[str] = None
    
    def to_dict(self):
        """Converte para dicionário serializável"""
        return {
            "timestamp": self.timestamp.isoformat(),
            "tool_name": self.tool_name,
            "method": self.method,
            "args": self.args,
            "result": str(self.result) if self.result else None,
            "duration": self.duration,
            "success": self.success,
            "error": self.error
        }

class MonitoredAgent:
    """Wrapper para agente AGNO com monitoramento avançado"""
    
    def __init__(self, agent, monitor_callback=None):
        self.agent = agent
        self.monitor_callback = monitor_callback
        self.tool_calls: List[ToolCallRecord] = []
        self.conversation_history: List[Dict[str, Any]] = []
        
        # Hook nas ferramentas do agente
        self._setup_tool_monitoring()
    
    def _setup_tool_monitoring(self):
        """Configura monitoramento das ferramentas"""
        if hasattr(self.agent, 'tools'):
            for tool in self.agent.tools:
                self._wrap_toolkit(tool)
    
    def _wrap_toolkit(self, toolkit):
        """Aplica wrapper em um toolkit"""
        if hasattr(toolkit, 'tools'):
            for tool_func in toolkit.tools:
                self._wrap_tool_function(toolkit, tool_func)
    
    def _wrap_tool_function(self, toolkit, tool_func):
        """Aplica wrapper em uma função de ferramenta"""
        original_func = tool_func
        toolkit_name = type(toolkit).__name__
        
        def wrapped_tool(*args, **kwargs):
            start_time = time.time()
            
            try:
                # Registrar início da chamada
                if self.monitor_callback:
                    self.monitor_callback({
                        "type": "tool_call_start",
                        "tool_name": toolkit_name,
                        "method": tool_func.__name__,
                        "args": {"args": args, "kwargs": kwargs}
                    })
                
                # Executar função original
                result = original_func(*args, **kwargs)
                duration = time.time() - start_time
                
                # Registrar sucesso
                record = ToolCallRecord(
                    timestamp=datetime.now(),
                    tool_name=toolkit_name,
                    method=tool_func.__name__,
                    args={"args": args, "kwargs": kwargs},
                    result=result,
                    duration=duration,
                    success=True
                )
                
                self.tool_calls.append(record)
                
                if self.monitor_callback:
                    self.monitor_callback({
                        "type": "tool_call_success",
                        "data": record.to_dict()
                    })
                
                return result
                
            except Exception as e:
                duration = time.time() - start_time
                
                # Registrar erro
                record = ToolCallRecord(
                    timestamp=datetime.now(),
                    tool_name=toolkit_name,
                    method=tool_func.__name__,
                    args={"args": args, "kwargs": kwargs},
                    result=None,
                    duration=duration,
                    success=False,
                    error=str(e)
                )
                
                self.tool_calls.append(record)
                
                if self.monitor_callback:
                    self.monitor_callback({
                        "type": "tool_call_error",
                        "data": record.to_dict()
                    })
                
                raise e
        
        # Substituir função original
        wrapped_tool.__name__ = tool_func.__name__
        wrapped_tool.__doc__ = tool_func.__doc__
        
        # Encontrar índice da ferramenta e substituir
        if hasattr(toolkit, 'tools') and tool_func in toolkit.tools:
            idx = toolkit.tools.index(tool_func)
            toolkit.tools[idx] = wrapped_tool
    
    def run(self, message: str, **kwargs) -> str:
        """Executa o agente com monitoramento"""
        start_time = time.time()
        
        try:
            if self.monitor_callback:
                self.monitor_callback({
                    "type": "conversation_start",
                    "message": message
                })
            
            # Executar agente
            response = self.agent.run(message, **kwargs)
            
            duration = time.time() - start_time
            
            # Registrar conversa
            conversation_record = {
                "timestamp": datetime.now().isoformat(),
                "user_message": message,
                "agent_response": response,
                "duration": duration,
                "tool_calls_count": len([tc for tc in self.tool_calls if tc.timestamp.timestamp() > start_time])
            }
            
            self.conversation_history.append(conversation_record)
            
            if self.monitor_callback:
                self.monitor_callback({
                    "type": "conversation_complete",
                    "data": conversation_record
                })
            
            return response
            
        except Exception as e:
            if self.monitor_callback:
                self.monitor_callback({
                    "type": "conversation_error",
                    "error": str(e)
                })
            raise e
    
    def get_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas do agente"""
        successful_calls = [tc for tc in self.tool_calls if tc.success]
        failed_calls = [tc for tc in self.tool_calls if not tc.success]
        
        # Calcular ferramentas mais usadas
        tool_usage = {}
        for tc in self.tool_calls:
            key = f"{tc.tool_name}.{tc.method}"
            tool_usage[key] = tool_usage.get(key, 0) + 1
        
        # Calcular tempos médios
        avg_tool_time = sum(tc.duration for tc in self.tool_calls) / len(self.tool_calls) if self.tool_calls else 0
        avg_conversation_time = sum(conv["duration"] for conv in self.conversation_history) / len(self.conversation_history) if self.conversation_history else 0
        
        return {
            "total_conversations": len(self.conversation_history),
            "total_tool_calls": len(self.tool_calls),
            "successful_tool_calls": len(successful_calls),
            "failed_tool_calls": len(failed_calls),
            "success_rate": len(successful_calls) / len(self.tool_calls) * 100 if self.tool_calls else 0,
            "avg_tool_call_time": avg_tool_time,
            "avg_conversation_time": avg_conversation_time,
            "most_used_tools": dict(sorted(tool_usage.items(), key=lambda x: x[1], reverse=True)[:5]),
            "recent_conversations": self.conversation_history[-5:],
            "recent_tool_calls": [tc.to_dict() for tc in self.tool_calls[-10:]]
        }
    
    def export_session_data(self) -> Dict[str, Any]:
        """Exporta todos os dados da sessão"""
        return {
            "session_start": self.conversation_history[0]["timestamp"] if self.conversation_history else None,
            "conversation_history": self.conversation_history,
            "tool_calls": [tc.to_dict() for tc in self.tool_calls],
            "stats": self.get_stats()
        }

class DebugLogger:
    """Logger especializado para debugging do agente"""
    
    def __init__(self, log_file=None):
        self.log_file = log_file
        self.logs = []
    
    def log(self, level: str, message: str, data: Optional[Dict] = None):
        """Registra uma mensagem de log"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "level": level,
            "message": message,
            "data": data
        }
        
        self.logs.append(log_entry)
        
        # Imprimir no console
        emoji_map = {
            "DEBUG": "🔍",
            "INFO": "ℹ️",
            "SUCCESS": "✅",
            "WARNING": "⚠️",
            "ERROR": "❌"
        }
        
        emoji = emoji_map.get(level, "📝")
        print(f"{emoji} [{level}] {message}")
        
        if data:
            print(f"   Data: {json.dumps(data, indent=2, default=str)}")
        
        # Salvar em arquivo se especificado
        if self.log_file:
            try:
                with open(self.log_file, "a", encoding="utf-8") as f:
                    f.write(f"{json.dumps(log_entry, default=str)}\n")
            except Exception as e:
                print(f"⚠️ Erro ao salvar log: {e}")
    
    def debug(self, message: str, data: Optional[Dict] = None):
        self.log("DEBUG", message, data)
    
    def info(self, message: str, data: Optional[Dict] = None):
        self.log("INFO", message, data)
    
    def success(self, message: str, data: Optional[Dict] = None):
        self.log("SUCCESS", message, data)
    
    def warning(self, message: str, data: Optional[Dict] = None):
        self.log("WARNING", message, data)
    
    def error(self, message: str, data: Optional[Dict] = None):
        self.log("ERROR", message, data)
