"""
🤖 ALICE-FINANCEIRA ENDPOINT - Powered by AGNO
Agente inteligente para gestão financeira empresarial
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, field_validator
import logging
import json
import re
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Union

# Importar o novo agente AGNO
from financial_agent_agno import process_with_agno_agent

# Importar ferramentas para compatibilidade
from dashboard_agent.tools.financial_tools import FinancialTools

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Router do FastAPI
router = APIRouter(prefix="/financial", tags=["Financial-AGNO"])

# === MODELOS DE DADOS ===

class FinancialRequest(BaseModel):
    """Modelo de dados para requisições financeiras"""
    
    # Dados de imagem/documento (N8N)
    kind: Optional[str] = None
    name: Optional[str] = None
    content: Optional[str] = None
    webContentLink: Optional[str] = None
    
    # Dados de interação conversacional
    userName: Optional[str] = None
    userMessage: Optional[str] = None
    previous_gasto_id: Optional[str] = None
    
    @field_validator('content')
    def validate_content(cls, v):
        if v and len(v) > 100000:  # 100KB limit
            raise ValueError('Conteúdo muito longo')
        return v

class FinancialResponse(BaseModel):
    """Modelo de resposta padronizado"""
    success: bool
    message: str
    gasto_id: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

# === ENDPOINT PRINCIPAL ===

@router.post("/register", response_model=FinancialResponse)
async def register_financial_data(data: FinancialRequest):
    """🤖 Alice-Financeira AGNO - Agente Inteligente para Gestão Financeira"""
    
    try:
        # 🧠 USAR AGENTE AGNO INTELIGENTE PARA TUDO!
        
        # CENÁRIO 1: DADOS DE IMAGEM - INICIA FLUXO DE REGISTRO COM AGNO
        if data.kind and data.content:
            logger.info(f"📋 INICIANDO fluxo de registro AGNO - Arquivo: {data.name}")
            
            # Preparar contexto de registro para AGNO
            registration_context = f"""
📸 **NOVO DOCUMENTO FINANCEIRO RECEBIDO**

**Arquivo:** {data.name}
**Tipo:** {data.kind}
**Link Google Drive:** {data.webContentLink}

**Dados Extraídos da Imagem:**
```
{data.content}
```

**Instrução:** Este é um documento financeiro que precisa ser registrado no sistema. 
Analise os dados extraídos e execute o fluxo de registro completo usando suas ferramentas financeiras.
"""
            
            # USAR AGENTE AGNO
            result = await process_with_agno_agent(
                user_name=data.userName or "Usuário",
                user_message=registration_context
            )
            
            return FinancialResponse(**result)
            
        # CENÁRIO 2: INTERAÇÃO COM FLUXO JÁ INICIADO - AGNO COM CONTEXTO
        elif data.userName and data.userMessage and data.previous_gasto_id:
            logger.info(f"💬 Continuando fluxo AGNO - Usuário: {data.userName}, Gasto ID: {data.previous_gasto_id}")
            
            # USAR AGENTE AGNO com contexto
            result = await process_with_agno_agent(
                user_name=data.userName,
                user_message=data.userMessage,
                previous_gasto_id=data.previous_gasto_id
            )
            
            return FinancialResponse(**result)
            
        # CENÁRIO 3: INTERAÇÃO CONVERSACIONAL - AGNO INTELIGENTE
        elif data.userName and data.userMessage:
            logger.info(f"🧠 Conversa inteligente AGNO - Usuário: {data.userName}, Mensagem: {data.userMessage}")
            
            # USAR AGENTE AGNO para conversa inteligente
            result = await process_with_agno_agent(
                user_name=data.userName,
                user_message=data.userMessage
            )
            
            return FinancialResponse(**result)
            
        else:
            raise HTTPException(status_code=400, detail="Formato de dados inválido: dados insuficientes")
            
    except Exception as e:
        logger.error(f"❌ Erro no endpoint AGNO: {e}")
        return FinancialResponse(
            success=False,
            message=f"Desculpe, tive um problema técnico. Pode tentar novamente?",
            error=str(e)
        )

# === FUNÇÕES DE APOIO PARA COMPATIBILIDADE ===

async def try_recover_registration_context(user_name: str) -> Optional[str]:
    """Tenta recuperar contexto de registro ativo usando FinancialTools"""
    try:
        financial_tools = FinancialTools()
        result = financial_tools.buscar_gastos_pendentes_usuario(user_name)
        
        if result.get('sucesso') and result.get('gastos_pendentes'):
            gasto_pendente = result['gastos_pendentes'][0]
            return str(gasto_pendente['id'])
        return None
    except Exception as e:
        logger.error(f"❌ Erro ao recuperar contexto: {e}")
        return None

def is_continuation_message(message: str) -> bool:
    """Detecta se mensagem é continuação de fluxo de registro"""
    continuation_patterns = [
        r'^(sim|não|nao)$',
        r'^(alimentação|transporte|material|serviços|marketing|viagem|outros)$',
        r'^(correto|incorreto)$',
        r'^\w+\s*(ltda|s\.a\.|me|eireli).*$'
    ]
    
    msg_lower = message.lower().strip()
    return any(re.match(pattern, msg_lower) for pattern in continuation_patterns)

# === ENDPOINT DE SAÚDE ===

@router.get("/health")
async def health_check():
    """Verificação de saúde do serviço"""
    return {
        "status": "healthy",
        "service": "Alice-Financeira AGNO",
        "timestamp": datetime.now().isoformat(),
        "capabilities": [
            "Registro inteligente de documentos",
            "Consultas financeiras conversacionais", 
            "Análise de dados com raciocínio",
            "Memória persistente de sessões",
            "Gestão completa de gastos empresariais"
        ]
    }
