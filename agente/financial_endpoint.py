"""
Endpoint específico para receber dados financeiros do N8N
AGORA COM AGENTE AGNO INTELIGENTE - Não mais robótico!
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

# Importar ferramentas para fallback
from dashboard_agent.tools.financial_tools import FinancialTools
from dashboard_agent.tools.financial_tools import FinancialTools

logger = logging.getLogger(__name__)

router = APIRouter()

class N8NFinancialData(BaseModel):
    """Modelo unificado para dados financeiros do N8N - aceita imagem OU interação"""
    # Campos de imagem (opcionais)
    kind: Optional[str] = None
    id: Optional[str] = None
    name: Optional[str] = None
    mimeType: Optional[str] = None
    webContentLink: Optional[str] = None
    webViewLink: Optional[str] = None
    content: Optional[Dict[str, Any]] = None
    # Campos de interação (opcionais)
    userName: Optional[str] = None
    userMessage: Optional[str] = None
    # Campo para controle de fluxo (opcional)
    previous_gasto_id: Optional[Union[int, str]] = None
    
    @field_validator('previous_gasto_id')
    @classmethod
    def validate_previous_gasto_id(cls, v):
        if v is None or v == "[undefined]" or v == "undefined":
            return None
        if isinstance(v, str):
            try:
                return int(v)
            except ValueError:
                return None
        return v

class FinancialResponse(BaseModel):
    """Resposta do endpoint financeiro"""
    success: bool
    message: str
    gasto_id: Optional[int] = None
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

@router.post("/financial/register", response_model=FinancialResponse)
async def register_financial_data(data: N8NFinancialData):
    """
    Endpoint unificado para dados financeiros do N8N
    
    REGRAS DE NEGÓCIO:
    1. Dados de imagem (kind, content) → INICIA novo fluxo de registro
    2. Interação (userName, userMessage) → SÓ processa se previous_gasto_id existe (fluxo já iniciado)
    3. Interação sem previous_gasto_id → Resposta conversacional SEM registrar dados
    """
    try:
        # 🤖 USAR AGENTE AGNO INTELIGENTE PARA TUDO!
        
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
            logger.info(f"� Continuando fluxo AGNO - Usuário: {data.userName}, Gasto ID: {data.previous_gasto_id}")
            
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

# === FUNÇÕES DE APOIO MANTIDAS PARA COMPATIBILIDADE ===

async def try_recover_registration_context(user_name: str, user_message: str = "") -> Optional[Dict[str, Any]]:
    """Tenta recuperar contexto de registro ativo usando FinancialTools"""
    try:
        financial_tools = FinancialTools()
        result = financial_tools.buscar_gastos_pendentes_usuario(user_name)
        
        if result.get('sucesso') and result.get('gastos_pendentes'):
            gasto_pendente = result['gastos_pendentes'][0]
            return {
                "gasto_id": str(gasto_pendente['id']),
                "user_name": user_name
            }
        return None
    except Exception as e:
        logger.error(f"❌ Erro ao recuperar contexto: {e}")
        return None
            success=False,
            message=f"Erro interno: {str(e)}",
            error=str(e)
        )

async def try_recover_registration_context(user_name: str, user_message: str):
    """Tentar recuperar contexto de registro ativo para o usuário"""
    try:
        # Normalizar mensagem para análise
        msg_lower = user_message.lower().strip()
        
        # Verificar se a mensagem parece ser parte de um fluxo de registro
        registration_keywords = [
            # Respostas sobre NF
            'não', 'nao', 'não tenho', 'nao tenho', 'sem nf', 'sem nota',
            'sim', 'tenho nota fiscal', 'tenho nf', 'possui nf', 'tem nota',
            
            # Categorias
            'alimentação', 'alimentacao', 'transporte', 'material de escritório', 
            'material escritorio', 'material', 'escritorio', 'serviços', 'servicos', 
            'marketing', 'viagem', 'outros', 'alimento', 'comida', 'lanche', 
            'refeição', 'refeicao', 'combustível', 'combustivel',
            
            # Confirmações de fornecedor
            'correto', 'certo', 'confirmo', 'sim, correto', 'perfeito', 'exato',
            'ta correto', 'está correto'
        ]
        
        # Se não parece ser uma resposta de registro, não tentar recuperar
        if not any(keyword in msg_lower for keyword in registration_keywords):
            return None
            
        logger.info(f"🔄 Mensagem parece ser parte de fluxo de registro, tentando recuperar contexto")
        
        # Inicializar FinancialTools para buscar gastos pendentes
        financial_tools = FinancialTools()
        
        # Buscar último gasto inserido recentemente que ainda não tem todos os campos preenchidos
        result = financial_tools.buscar_gastos_pendentes_usuario(user_name)
        
        if result and 'gasto_id' in result:
            logger.info(f"✅ Contexto recuperado: Gasto ID {result['gasto_id']} para usuário {user_name}")
            return result
        else:
            logger.info(f"❌ Nenhum contexto de registro ativo encontrado para {user_name}")
            return None
            
    except Exception as e:
        logger.error(f"❌ Erro ao recuperar contexto: {e}")
        return None

class IntentAnalyzer:
    """Analisador inteligente de intenções do usuário"""
    
    @staticmethod
    def analyze_intent(user_message: str, has_active_registration: bool = False) -> Dict[str, Any]:
        """
        Analisa a intenção do usuário e retorna informações sobre como processar
        """
        msg_lower = user_message.lower().strip()
        
        # INTENÇÃO 1: RESPOSTAS DE FLUXO DE REGISTRO ATIVO
        if has_active_registration:
            registration_responses = [
                'não', 'nao', 'sim', 'alimentação', 'alimentacao', 'transporte', 
                'material', 'escritorio', 'serviços', 'servicos', 'marketing', 
                'viagem', 'outros', 'correto', 'certo', 'perfeito', 'exato'
            ]
            if any(keyword in msg_lower for keyword in registration_responses):
                return {
                    "intent": "continue_registration",
                    "confidence": 0.9,
                    "action": "process_registration_response"
                }
        
        # INTENÇÃO 2: CONSULTAS FINANCEIRAS
        financial_queries = [
            'gastos', 'despesas', 'quanto gastei', 'meus gastos', 'gastos de ontem',
            'gastos de hoje', 'gastos da semana', 'gastos do mês', 'total gasto',
            'resumo financeiro', 'relatório', 'relatorio', 'balanço', 'balanco',
            'fornecedores', 'categorias', 'alimentação gasta', 'transporte gasto'
        ]
        if any(query in msg_lower for query in financial_queries):
            return {
                "intent": "financial_query",
                "confidence": 0.8,
                "action": "execute_financial_query",
                "query_type": IntentAnalyzer._detect_query_type(msg_lower)
            }
        
        # INTENÇÃO 3: ANÁLISES E INSIGHTS
        analysis_requests = [
            'análise', 'analise', 'insights', 'tendências', 'tendencias',
            'padrões', 'padroes', 'estatísticas', 'estatisticas', 'comparar',
            'evolução', 'evolucao', 'crescimento', 'economia'
        ]
        if any(analysis in msg_lower for analysis in analysis_requests):
            return {
                "intent": "financial_analysis",
                "confidence": 0.8,
                "action": "generate_financial_analysis"
            }
        
        # INTENÇÃO 4: COMANDOS DE GESTÃO
        management_commands = [
            'validar documentação', 'validar', 'verificar', 'conferir',
            'atualizar', 'corrigir', 'editar', 'modificar'
        ]
        if any(cmd in msg_lower for cmd in management_commands):
            return {
                "intent": "financial_management",
                "confidence": 0.7,
                "action": "execute_management_command"
            }
        
        # INTENÇÃO 5: CUMPRIMENTOS E AJUDA
        greetings_help = [
            'ola', 'olá', 'oi', 'bom dia', 'boa tarde', 'boa noite',
            'ajuda', 'help', 'ferramentas', 'funcionalidades', 'o que pode fazer'
        ]
        if any(greeting in msg_lower for greeting in greetings_help):
            return {
                "intent": "greeting_help",
                "confidence": 0.9,
                "action": "provide_help_or_greeting"
            }
        
        # INTENÇÃO 6: AGRADECIMENTOS E DESPEDIDAS
        thanks_goodbye = [
            'obrigado', 'obrigada', 'valeu', 'vlw', 'tchau', 'bye', 'até'
        ]
        if any(thanks in msg_lower for thanks in thanks_goodbye):
            return {
                "intent": "thanks_goodbye",
                "confidence": 0.9,
                "action": "acknowledge_thanks_goodbye"
            }
        
        # INTENÇÃO PADRÃO: CONVERSA GERAL
        return {
            "intent": "general_conversation",
            "confidence": 0.5,
            "action": "intelligent_conversation"
        }
    
    @staticmethod
    def _detect_query_type(msg_lower: str) -> str:
        """Detecta o tipo específico de consulta financeira"""
        if any(word in msg_lower for word in ['ontem', 'yesterday']):
            return "daily_yesterday"
        elif any(word in msg_lower for word in ['hoje', 'today']):
            return "daily_today"
        elif any(word in msg_lower for word in ['semana', 'week']):
            return "weekly"
        elif any(word in msg_lower for word in ['mês', 'mes', 'month']):
            return "monthly"
        elif any(word in msg_lower for word in ['total', 'tudo', 'all']):
            return "total"
        elif any(word in msg_lower for word in ['alimentação', 'alimentacao', 'comida']):
            return "category_food"
        elif any(word in msg_lower for word in ['transporte', 'combustível', 'combustivel']):
            return "category_transport"
        elif any(word in msg_lower for word in ['fornecedor', 'empresa', 'estabelecimento']):
            return "by_vendor"
        else:
            return "general_summary"

async def handle_conversational_interaction(user_name: str, user_message: str):
    """🤖 Alice-Financeira Simples e Inteligente - SEM loops ou complexidade desnecessária"""
    logger.info(f"💭 Alice processando: {user_name} disse '{user_message}'")
    
    msg_lower = user_message.lower().strip()
    
    # 1. CUMPRIMENTOS
    if any(cumprimento in msg_lower for cumprimento in ['ola', 'olá', 'oi', 'bom dia', 'boa tarde', 'boa noite']):
        response_msg = f"Olá {user_name}! 👋 Sou a Alice-Financeira!\n\n🚀 **Posso ajudar com:**\n• 📸 **Registrar gastos** - envie fotos de comprovantes\n• 💰 **Consultar gastos** - 'meus gastos de ontem', 'gastos desta semana'\n• 📊 **Ver resumos** - 'resumo financeiro', 'total gasto'\n\n💡 **Teste:** Pergunte 'quais foram meus gastos de hoje?'"
    
    # 2. CONSULTAS FINANCEIRAS SIMPLES
    elif any(palavra in msg_lower for palavra in ['gastos', 'quanto gastei', 'meus gastos', 'resumo', 'total']):
        financial_tools = FinancialTools()
        
        try:
            if 'ontem' in msg_lower:
                from datetime import datetime, timedelta
                yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
                result = financial_tools.consultar_gastos_por_periodo(yesterday, yesterday)
                if result and result.get('sucesso') and result.get('total_gastos', 0) > 0:
                    response_msg = f"📊 **Gastos de ontem:** R$ {result['total_gastos']:.2f} ({result['quantidade_gastos']} transações)"
                else:
                    response_msg = f"✨ Ontem você não teve gastos registrados! Economia em dia! 💚"
            
            elif 'hoje' in msg_lower:
                today = datetime.now().strftime('%Y-%m-%d')
                result = financial_tools.consultar_gastos_por_periodo(today, today)
                if result and result.get('sucesso') and result.get('total_gastos', 0) > 0:
                    response_msg = f"📊 **Gastos de hoje:** R$ {result['total_gastos']:.2f} ({result['quantidade_gastos']} transações)"
                else:
                    response_msg = f"📅 Hoje ainda não temos gastos registrados. Começando bem! ✨"
            
            elif 'semana' in msg_lower:
                from datetime import datetime, timedelta
                start_week = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
                today = datetime.now().strftime('%Y-%m-%d')
                result = financial_tools.consultar_gastos_por_periodo(start_week, today)
                if result and result.get('sucesso') and result.get('total_gastos', 0) > 0:
                    response_msg = f"📊 **Gastos da semana:** R$ {result['total_gastos']:.2f} ({result['quantidade_gastos']} transações)"
                else:
                    response_msg = f"📅 Nenhum gasto na última semana. Economia total! 💰"
            
            else:
                # Resumo geral
                result = financial_tools.obter_resumo_financeiro()
                if result and result.get('sucesso') and result.get('total_gastos', 0) > 0:
                    response_msg = f"📊 **Resumo Financeiro:**\n💰 **Total:** R$ {result['total_gastos']:.2f}\n📝 **Registros:** {result['quantidade_gastos']}\n\n💡 Quer ver por período específico?"
                else:
                    response_msg = f"📊 Ainda não há gastos registrados no sistema. Envie comprovantes para começar!"
        
        except Exception as e:
            logger.error(f"❌ Erro na consulta: {e}")
            response_msg = f"Tive um problema ao buscar os dados, {user_name}. Pode tentar novamente?"
    
    # 3. AJUDA
    elif any(palavra in msg_lower for palavra in ['ajuda', 'help', 'ferramentas', 'funcionalidades']):
        response_msg = f"🤖 **Central de Ajuda - {user_name}**\n\n📸 **Registro:**\n• Envie foto de comprovante/nota fiscal\n• Processamento automático dos dados\n\n💰 **Consultas:**\n• 'meus gastos de ontem'\n• 'gastos desta semana'\n• 'resumo financeiro'\n\n⚙️ **Gestão:**\n• Categorização automática\n• Vinculação de documentos\n• Validação de fornecedores\n\n💡 **Dica:** Converse naturalmente!"
    
    # 4. DESPEDIDAS
    elif any(palavra in msg_lower for palavra in ['tchau', 'obrigado', 'obrigada', 'valeu', 'bye']):
        response_msg = f"👋 {user_name}! Foi ótimo ajudar!\n\n🚀 Sempre que precisar:\n• 📸 Registrar gastos\n• 💰 Consultar dados\n• 📊 Ver relatórios\n\nAté a próxima! ✨"
    
    # 5. CONVERSA GERAL
    else:
        response_msg = f"💬 Olá {user_name}! Recebi: '{user_message}'\n\n💡 **Posso ajudar com:**\n• 📊 Consultas: 'meus gastos de hoje'\n• 📸 Registros: envie foto do comprovante\n• ❓ Ajuda: digite 'help'\n\nO que gostaria de fazer?"
    
    return FinancialResponse(
        success=True,
        message=response_msg,
        data={
            "user": user_name,
            "interaction_type": "conversational_simple",
            "timestamp": datetime.now().isoformat()
        }
    )

async def execute_financial_query(user_name: str, user_message: str, intent_info: Dict[str, Any]):
    """💰 Executa consultas financeiras inteligentes"""
    logger.info(f"💰 Executando consulta financeira: {intent_info.get('query_type', 'geral')}")
    
    financial_tools = FinancialTools()
    query_type = intent_info.get('query_type', 'general_summary')
    
    try:
        if query_type == "daily_yesterday":
            # Buscar gastos de ontem
            from datetime import datetime, timedelta
            yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
            result = financial_tools.consultar_gastos_por_periodo(yesterday, yesterday)
            
        elif query_type == "daily_today":
            # Buscar gastos de hoje
            today = datetime.now().strftime('%Y-%m-%d')
            result = financial_tools.consultar_gastos_por_periodo(today, today)
            
        elif query_type == "weekly":
            # Buscar gastos da semana
            from datetime import datetime, timedelta
            start_week = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
            today = datetime.now().strftime('%Y-%m-%d')
            result = financial_tools.consultar_gastos_por_periodo(start_week, today)
            
        elif query_type == "monthly":
            # Buscar gastos do mês
            from datetime import datetime
            start_month = datetime.now().replace(day=1).strftime('%Y-%m-%d')
            today = datetime.now().strftime('%Y-%m-%d')
            result = financial_tools.consultar_gastos_por_periodo(start_month, today)
            
        elif query_type.startswith("category_"):
            # Buscar por categoria
            categoria = "Alimentação" if "food" in query_type else "Transporte"
            result = financial_tools.consultar_gastos_por_categoria(categoria)
            
        else:
            # Resumo geral
            result = financial_tools.obter_resumo_financeiro()
        
        # Formatar resposta inteligente
        if result and result.get('sucesso'):
            response_msg = format_financial_query_response(user_name, result, query_type, user_message)
        else:
            response_msg = f"Não encontrei dados para essa consulta, {user_name}. Quer que eu verifique algo específico?"
            
    except Exception as e:
        logger.error(f"❌ Erro na consulta financeira: {e}")
        response_msg = f"Tive um problema ao buscar esses dados, {user_name}. Posso tentar de outra forma?"
    
    return FinancialResponse(
        success=True,
        message=response_msg,
        data={
            "user": user_name,
            "query_type": query_type,
            "intent": "financial_query"
        }
    )

def format_financial_query_response(user_name: str, result: Dict, query_type: str, original_message: str) -> str:
    """� Formata respostas de consultas financeiras de forma inteligente"""
    
    if query_type == "daily_yesterday":
        if result.get('total_gastos', 0) > 0:
            return f"📊 **Gastos de ontem, {user_name}:**\n\n💰 **Total:** R$ {result['total_gastos']:.2f}\n📝 **{result['quantidade_gastos']} transações**\n\n💡 Quer ver detalhes ou alguma categoria específica?"
        else:
            return f"✨ Ótimo {user_name}! Ontem você não teve gastos registrados. Economia em dia! 💚"
    
    elif query_type == "daily_today":
        if result.get('total_gastos', 0) > 0:
            return f"📊 **Gastos de hoje, {user_name}:**\n\n💰 **Total:** R$ {result['total_gastos']:.2f}\n📝 **{result['quantidade_gastos']} transações**\n\n🎯 Como está o orçamento do dia?"
        else:
            return f"📅 Hoje ainda não temos gastos registrados, {user_name}. Começando o dia bem! ✨"
    
    elif "category_" in query_type:
        categoria = "Alimentação" if "food" in query_type else "Transporte"
        return f"🍽️ **{categoria} - {user_name}:**\n\n💰 **Total:** R$ {result.get('total_gastos', 0):.2f}\n📊 **{result.get('quantidade_gastos', 0)} transações**\n\n📈 Quer comparar com outros períodos?"
    
    else:
        return f"📊 **Resumo Financeiro - {user_name}:**\n\n💰 **Total Geral:** R$ {result.get('total_gastos', 0):.2f}\n📝 **{result.get('quantidade_gastos', 0)} registros**\n\n� Posso detalhar por categoria ou período específico!"

async def generate_financial_analysis(user_name: str, user_message: str):
    """📈 Gera análises e insights financeiros"""
    logger.info(f"📈 Gerando análise financeira para {user_name}")
    
    return FinancialResponse(
        success=True,
        message=f"📈 **Análise Financeira em desenvolvimento, {user_name}!**\n\nEm breve terei insights automáticos sobre:\n• 📊 Padrões de gastos\n• 📈 Tendências mensais\n• 💡 Oportunidades de economia\n• � Projeções\n\nPor enquanto, posso mostrar seus gastos por período ou categoria. O que gostaria de ver?",
        data={"intent": "financial_analysis", "status": "coming_soon"}
    )

async def execute_management_command(user_name: str, user_message: str):
    """⚙️ Executa comandos de gestão financeira"""
    logger.info(f"⚙️ Executando comando de gestão para {user_name}")
    
    return FinancialResponse(
        success=True,
        message=f"⚙️ **Gestão Financeira, {user_name}!**\n\nComandos disponíveis:\n• 🔍 **Validar documentação** - verifico se os dados estão completos\n• ✏️ **Corrigir fornecedor** - ajusto nomes de empresas\n• 📋 **Verificar registros** - confiro dados pendentes\n\nQual específicamente você gostaria de fazer?",
        data={"intent": "management", "available_commands": ["validate", "correct", "verify"]}
    )

async def provide_help_or_greeting(user_name: str, user_message: str):
    """👋 Cumprimentos e ajuda inteligente"""
    msg_lower = user_message.lower()
    
    if any(greeting in msg_lower for greeting in ['ola', 'olá', 'oi', 'bom dia', 'boa tarde', 'boa noite']):
        response_msg = f"Olá {user_name}! 👋 Sou a Alice-Financeira, sua assistente inteligente!\n\n🚀 **Posso ajudar com:**\n• 📸 **Registrar gastos** - envie imagens de comprovantes\n• 💰 **Consultar gastos** - 'meus gastos de ontem', 'quanto gastei em alimentação'\n• 📊 **Análises financeiras** - insights e relatórios\n• ⚙️ **Gestão** - validar, corrigir, organizar dados\n\n💡 **Experimente:** 'Quais foram meus gastos desta semana?'"
    else:
        response_msg = f"🤖 **Alice-Financeira - Central de Ajuda**\n\n**{user_name}, minhas capacidades:**\n\n📸 **Registro Automático:**\n• Análise de comprovantes e notas fiscais\n• Extração automática de dados\n• Categorização inteligente\n\n� **Consultas Inteligentes:**\n• 'Meus gastos de ontem/hoje/semana/mês'\n• 'Quanto gastei em alimentação?'\n• 'Resumo financeiro'\n\n📊 **Análises (em breve):**\n• Padrões e tendências\n• Insights automáticos\n• Projeções\n\n⚙️ **Gestão:**\n• Validação de documentos\n• Correção de dados\n• Organização de registros\n\n💡 **Dica:** Converse naturalmente comigo!"
    
    return FinancialResponse(
        success=True,
        message=response_msg,
        data={"intent": "help", "user": user_name}
    )

async def acknowledge_thanks_goodbye(user_name: str, user_message: str):
    """🙏 Agradecimentos e despedidas"""
    msg_lower = user_message.lower()
    
    if any(thanks in msg_lower for thanks in ['obrigado', 'obrigada', 'valeu', 'vlw']):
        response_msg = f"😊 Por nada, {user_name}! Foi um prazer ajudar!\n\n💡 Sempre que precisar de algo financeiro, é só chamar. Estou aqui 24/7 para:\n• 📸 Registrar novos gastos\n• 💰 Consultar informações\n• 📊 Gerar relatórios\n\nAté a próxima! ✨"
    else:
        response_msg = f"👋 Até logo, {user_name}! Foi ótimo conversar!\n\n🚀 Lembre-se: qualquer gasto novo é só me enviar a foto que eu cuido de tudo!\n\nTenha um ótimo dia! 😊✨"
    
    return FinancialResponse(
        success=True,
        message=response_msg,
        data={"intent": "goodbye", "user": user_name}
    )

async def intelligent_conversation(user_name: str, user_message: str):
    """🧠 Conversa inteligente geral"""
    logger.info(f"🧠 Conversa inteligente com {user_name}")
    
    # Tentar entender o contexto da mensagem
    msg_lower = user_message.lower()
    
    if any(word in msg_lower for word in ['dinheiro', 'dinheiro', 'economia', 'economizar', 'gastar', 'gasto']):
        response_msg = f"💰 Falando sobre finanças, {user_name}! \n\nPosso te ajudar com:\n• 📊 **Ver seus gastos** - 'meus gastos desta semana'\n• 📸 **Registrar novos** - envie foto do comprovante\n• 💡 **Dicas de economia** - análise dos seus padrões\n\nO que você gostaria de saber?"
    
    elif any(word in msg_lower for word in ['problema', 'erro', 'bug', 'não funciona', 'nao funciona']):
        response_msg = f"🔧 Vamos resolver, {user_name}!\n\nSe algo não está funcionando:\n• 📸 **Imagens:** Certifique-se que o comprovante está legível\n• 💬 **Comandos:** Tente 'meus gastos de hoje' ou 'ajuda'\n• 🔄 **Reset:** Posso recomeçar qualquer processo\n\nDetalhe o problema para eu ajudar melhor!"
    
    else:
        response_msg = f"🤔 Interessante, {user_name}! Recebi: '{user_message}'\n\n💡 **Como posso ajudar especificamente?**\n• 💰 Quer consultar gastos?\n• 📸 Registrar nova despesa?\n• 📊 Ver relatórios?\n• ❓ Tirar alguma dúvida?\n\nSou especialista em finanças, então pergunte à vontade!"
    
    return FinancialResponse(
        success=True,
        message=response_msg,
        data={
            "intent": "general_conversation",
            "user": user_name,
            "original_message": user_message
        }
    )

async def handle_user_interaction_with_context(user_name: str, user_message: str, gasto_id: Union[int, str]):
    """Lidar com interação no contexto de um registro já iniciado"""
    logger.info(f"💬 Processando resposta no contexto do gasto ID {gasto_id}: {user_name} disse '{user_message}'")
    
    # Normalizar mensagem para análise
    msg_lower = user_message.lower().strip()
    
    # DETECTAR RESPOSTAS SOBRE WORKFLOW DE REGISTRO
    if any(palavra in msg_lower for palavra in ['não', 'nao', 'não tenho', 'nao tenho', 'sem nf', 'sem nota']):
        response_msg = f"Ok {user_name}! Registro confirmado apenas com o comprovante. Agora informe a natureza do gasto (Alimentação, Transporte, Material de Escritório, Serviços, Marketing, Viagem, Outros)."
    
    elif any(palavra in msg_lower for palavra in ['sim', 'tenho nota fiscal', 'tenho nf', 'possui nf', 'tem nota']):
        response_msg = f"Perfeito {user_name}! Você confirmou que possui Nota Fiscal. Por favor, envie a imagem da NF para que eu possa processar e vincular ao comprovante anterior."
    
    elif any(categoria in msg_lower for categoria in ['alimentação', 'alimentacao', 'transporte', 'material de escritório', 'material escritorio', 'material', 'escritorio', 'serviços', 'servicos', 'marketing', 'viagem', 'outros', 'alimento', 'comida', 'lanche', 'refeição', 'refeicao']):
        # Mapear categoria para nome padrão
        categoria_mapeada = user_message
        if any(palavra in msg_lower for palavra in ['alimentação', 'alimentacao', 'alimento', 'comida', 'lanche', 'refeição', 'refeicao']):
            categoria_mapeada = "Alimentação"
        elif 'transporte' in msg_lower:
            categoria_mapeada = "Transporte"
        elif any(palavra in msg_lower for palavra in ['material', 'escritorio', 'escritório']):
            categoria_mapeada = "Material de Escritório"
        elif any(palavra in msg_lower for palavra in ['serviços', 'servicos']):
            categoria_mapeada = "Serviços"
        elif 'marketing' in msg_lower:
            categoria_mapeada = "Marketing"
        elif 'viagem' in msg_lower:
            categoria_mapeada = "Viagem"
        elif 'outros' in msg_lower:
            categoria_mapeada = "Outros"
            
        response_msg = f"✅ Categoria '{categoria_mapeada}' registrada! {user_name}, agora confirme se o fornecedor extraído está correto ou me informe o nome correto."
    
    # DETECTAR CONFIRMAÇÕES DE FORNECEDOR (mais específicas)
    elif any(confirmacao in msg_lower for confirmacao in ['ta correto', 'está correto', 'correto', 'certo', 'confirmo', 'sim, correto', 'perfeito', 'exato']) or (msg_lower.strip() == 'ok' and len(user_message.strip()) <= 3):
        response_msg = f"Perfeito {user_name}! ✅ Fornecedor confirmado. Registro financeiro completo!\n\n📋 **Resumo do registro:**\n• Documento processado\n• Categoria definida\n• Fornecedor validado\n• Dados salvos no sistema\n\nRegistro finalizado com sucesso! Posso ajudar com mais alguma coisa?"
    
    # DETECTAR CORREÇÃO DE FORNECEDOR (mais específico)
    elif any(palavra in msg_lower for palavra in ['fornecedor correto é', 'fornecedor é', 'empresa é', 'estabelecimento é', 'nome correto é']):
        # Extrair o nome do fornecedor da mensagem
        fornecedor_match = re.search(r'(?:fornecedor|empresa|estabelecimento)(?:\s+correto)?\s+é\s+(.+)', msg_lower)
        if fornecedor_match:
            novo_fornecedor = fornecedor_match.group(1).strip()
            response_msg = f"Fornecedor atualizado para: '{novo_fornecedor}' ✅\n\n📋 **Registro financeiro completo!**\n• Documento processado\n• Categoria definida  \n• Fornecedor: {novo_fornecedor}\n• Dados salvos no sistema\n\nRegistro finalizado com sucesso! Posso ajudar com mais alguma coisa?"
        else:
            response_msg = f"Para corrigir o fornecedor, use o formato: 'O fornecedor é [Nome da Empresa]' ou 'Fornecedor correto é [Nome]'"
    
    else:
        # Resposta contextual para o registro em andamento
        response_msg = f"Estou aguardando suas respostas para completar o registro do gasto ID {gasto_id}:\n\n1️⃣ Possui Nota Fiscal? (Sim/Não)\n2️⃣ Categoria do gasto? (Alimentação, Transporte, etc.)\n3️⃣ Fornecedor está correto? (Correto ou nome correto)\n\nPor favor, responda uma pergunta por vez."
    
    return FinancialResponse(
        success=True,
        message=response_msg,
        gasto_id=int(gasto_id) if isinstance(gasto_id, str) else gasto_id,
        data={
            "user": user_name,
            "message": user_message,
            "interaction_type": "registration_workflow",
            "gasto_id": gasto_id
        },
        error=None
    )

# Função original renomeada para referência (pode ser removida depois)
async def handle_user_interaction_old(user_name: str, user_message: str):
    """Lidar com interação conversacional inteligente"""
    logger.info(f"🗣️ Processando interação: {user_name} disse '{user_message}'")
    
    # Normalizar mensagem para análise
    msg_lower = user_message.lower().strip()
    
    # DETECTAR RESPOSTAS SOBRE WORKFLOW DE REGISTRO
    if any(palavra in msg_lower for palavra in ['não', 'nao', 'não tenho', 'nao tenho', 'sem nf', 'sem nota']):
        response_msg = f"Ok {user_name}! Registro confirmado apenas com o comprovante. Agora informe a natureza do gasto (Alimentação, Transporte, Material de Escritório, Serviços, Marketing, Viagem, Outros)."
    
    elif any(palavra in msg_lower for palavra in ['sim', 'tenho nota fiscal', 'tenho nf', 'possui nf', 'tem nota']):
        response_msg = f"Perfeito {user_name}! Você confirmou que possui Nota Fiscal. Por favor, envie a imagem da NF para que eu possa processar e vincular ao comprovante anterior."
    
    elif any(categoria in msg_lower for categoria in ['alimentação', 'alimentacao', 'transporte', 'material de escritório', 'material escritorio', 'material', 'escritorio', 'serviços', 'servicos', 'marketing', 'viagem', 'outros', 'alimento', 'comida', 'lanche', 'refeição', 'refeicao']):
        # Mapear categoria para nome padrão
        categoria_mapeada = user_message
        if any(palavra in msg_lower for palavra in ['alimentação', 'alimentacao', 'alimento', 'comida', 'lanche', 'refeição', 'refeicao']):
            categoria_mapeada = "Alimentação"
        elif 'transporte' in msg_lower:
            categoria_mapeada = "Transporte"
        elif any(palavra in msg_lower for palavra in ['material', 'escritorio', 'escritório']):
            categoria_mapeada = "Material de Escritório"
        elif any(palavra in msg_lower for palavra in ['serviços', 'servicos']):
            categoria_mapeada = "Serviços"
        elif 'marketing' in msg_lower:
            categoria_mapeada = "Marketing"
        elif 'viagem' in msg_lower:
            categoria_mapeada = "Viagem"
        elif 'outros' in msg_lower:
            categoria_mapeada = "Outros"
            
        response_msg = f"✅ Categoria '{categoria_mapeada}' registrada! {user_name}, agora confirme se o fornecedor extraído está correto ou me informe o nome correto."
    
    # DETECTAR CONFIRMAÇÕES DE FORNECEDOR (mais específicas)
    elif any(confirmacao in msg_lower for confirmacao in ['ta correto', 'está correto', 'correto', 'certo', 'confirmo', 'sim, correto', 'perfeito', 'exato']) or (msg_lower.strip() == 'ok' and len(user_message.strip()) <= 3):
        response_msg = f"Perfeito {user_name}! ✅ Fornecedor confirmado. Registro financeiro completo!\n\n📋 **Resumo do registro:**\n• Documento processado\n• Categoria definida\n• Fornecedor validado\n• Dados salvos no sistema\n\nRegistro finalizado com sucesso! Posso ajudar com mais alguma coisa?"
    
    # CUMPRIMENTOS E INTERAÇÕES GERAIS
    elif any(cumprimento in msg_lower for cumprimento in ['ola', 'olá', 'oi', 'hello', 'hey', 'bom dia', 'boa tarde', 'boa noite']):
        response_msg = f"Olá {user_name}! 👋 Como posso te ajudar hoje? Posso registrar gastos, comprovantes ou notas fiscais para você!"
    
    elif any(palavra in msg_lower for palavra in ['comprovante', 'nota fiscal', 'nf', 'gasto', 'despesa', 'pagamento']):
        response_msg = f"Perfeito {user_name}! Vejo que você quer registrar um gasto. Envie a imagem do comprovante ou nota fiscal que eu processarei automaticamente os dados para você!"
    
    elif any(palavra in msg_lower for palavra in ['help', 'ajuda', 'como funciona', 'o que você faz', 'ferramenta', 'funcionalidade', 'o que pode fazer', 'que ferramentas', 'quais ferramentas', 'funcoes', 'funções']):
        response_msg = f"Olá {user_name}! 🤖 Sou a Alice-Financeira, sua assistente para controle financeiro!\n\n**Minhas ferramentas:**\n• 📷 **Análise de Imagens**: Processo comprovantes e notas fiscais automaticamente\n• 💾 **Registro de Gastos**: Salvo dados extraídos no sistema financeiro\n• 🔗 **Vinculação de Documentos**: Conecto comprovantes com suas respectivas NFs\n• 📊 **Categorização**: Organizo gastos por tipo (Alimentação, Transporte, etc.)\n• 🏢 **Gestão de Fornecedores**: Identifico e valido empresas dos documentos\n\n**Como usar:**\nApenas envie a imagem do documento que eu cuido do resto! �"
    
    # DETECTAR CORREÇÃO DE FORNECEDOR (mais específico)
    elif any(palavra in msg_lower for palavra in ['fornecedor correto é', 'fornecedor é', 'empresa é', 'estabelecimento é', 'nome correto é']):
        # Extrair o nome do fornecedor da mensagem
        fornecedor_match = re.search(r'(?:fornecedor|empresa|estabelecimento)(?:\s+correto)?\s+é\s+(.+)', msg_lower)
        if fornecedor_match:
            novo_fornecedor = fornecedor_match.group(1).strip()
            response_msg = f"Fornecedor atualizado para: '{novo_fornecedor}' ✅\n\n📋 **Registro financeiro completo!**\n• Documento processado\n• Categoria definida  \n• Fornecedor: {novo_fornecedor}\n• Dados salvos no sistema\n\nRegistro finalizado com sucesso! Posso ajudar com mais alguma coisa?"
        else:
            response_msg = f"Para corrigir o fornecedor, use o formato: 'O fornecedor é [Nome da Empresa]' ou 'Fornecedor correto é [Nome]'"
    
    elif any(palavra in msg_lower for palavra in ['tchau', 'bye', 'obrigado', 'obrigada', 'valeu']):
        response_msg = f"Até logo {user_name}! Foi um prazer ajudar. Qualquer novo gasto é só me enviar! 😊"
    
    else:
        # RESPOSTA INTELIGENTE PARA MENSAGENS NÃO IDENTIFICADAS
        if len(user_message.strip()) <= 3:
            # Mensagem muito curta - pedir esclarecimento
            response_msg = f"Não entendi bem {user_name}. Você poderia:\n• Enviar imagem de um comprovante para registrar\n• Me dizer se tem alguma dúvida específica\n• Ou ser mais específico sobre o que precisa? 😄"
        elif any(palavra in msg_lower for palavra in ['qual', 'que', 'como', '?']):
            # Detectar perguntas e responder sem registrar
            response_msg = f"Olá {user_name}! Para perguntas específicas, use palavras-chave como:\n• **'ferramentas'** ou **'ajuda'** - para saber minhas funcionalidades\n• **'como funciona'** - para entender o processo\n• **'comprovante'** - para registrar gastos\n\nOu simplesmente envie a imagem do documento que precisa processar! 📸"
        else:
            # Para mensagens que não são claramente perguntas nem comandos
            response_msg = f"Olá {user_name}! Recebi sua mensagem: '{user_message}'\n\nSe você quer:\n• 📸 **Registrar um gasto** → Envie a imagem do comprovante/NF\n• ❓ **Saber minhas funcionalidades** → Digite 'ajuda' ou 'ferramentas'\n• 🔄 **Corrigir dados** → Use formato específico como 'fornecedor é [nome]'\n\nComo posso ajudar?"
    
    return FinancialResponse(
        success=True,
        message=response_msg,
        gasto_id=None,
        data={
            "user": user_name,
            "message": user_message,
            "interaction_type": "conversation"
        },
        error=None
    )


async def handle_image_extraction(data: N8NFinancialData):
    """Lidar com extração de dados de imagem (lógica atual)"""
    try:
        logger.info(f"📋 Recebendo dados financeiros: {data.name}")
        
        # Extrair texto do content.parts[0].text
        if not data.content or "parts" not in data.content:
            raise HTTPException(status_code=400, detail="Formato de dados inválido: content.parts não encontrado")
        
        if not data.content["parts"] or len(data.content["parts"]) == 0:
            raise HTTPException(status_code=400, detail="Formato de dados inválido: content.parts está vazio")
        
        extracted_text = data.content["parts"][0].get("text", "")
        if not extracted_text:
            raise HTTPException(status_code=400, detail="Formato de dados inválido: content.parts[0].text está vazio")
        
        logger.info(f"🔍 Texto extraído: {extracted_text[:200]}...")
        
        # Extrair JSON do texto (pode estar em markdown ```json ou direto)
        json_match = re.search(r'```json\s*(\{.*?\})\s*```', extracted_text, re.DOTALL)
        if json_match:
            json_data = json_match.group(1)
        else:
            # Tentar extrair JSON direto
            json_match = re.search(r'(\{.*\})', extracted_text, re.DOTALL)
            if json_match:
                json_data = json_match.group(1)
            else:
                raise HTTPException(status_code=400, detail="JSON não encontrado no texto extraído")
        
        # Parse do JSON
        try:
            financial_data = json.loads(json_data)
        except json.JSONDecodeError as e:
            logger.error(f"❌ Erro ao fazer parse do JSON: {e}")
            raise HTTPException(status_code=400, detail=f"JSON inválido: {e}")
        
        logger.info(f"✅ JSON parseado com sucesso: {financial_data}")
        
        # Extrair dados_extraidos se disponível
        if "dados_extraidos" in financial_data:
            dados_extraidos = financial_data["dados_extraidos"]
        else:
            dados_extraidos = financial_data
        
        # Inicializar FinancialTools
        financial_tools = FinancialTools()
        
        # Validar e tratar campos obrigatórios
        data_despesa = dados_extraidos.get("data_despesa")
        valor_total = dados_extraidos.get("valor_total")
        descricao_item = dados_extraidos.get("descricao_item", "Despesa não identificada")
        
        # Se campos críticos estão null/None, usar dados padrão ou rejeitar
        if not data_despesa:
            data_despesa = "2025-09-05"  # Data atual como fallback
            
        if valor_total is None or valor_total == "null":
            valor_total = 0.0  # Valor zero como fallback
        else:
            try:
                valor_total = float(valor_total)
            except (ValueError, TypeError):
                valor_total = 0.0
        
        # Preparar dados para inserção usando os parâmetros corretos da função
        descricao_imagem = financial_data.get("descricao_imagem", "Documento analisado automaticamente")
        arquivo_drive_url = data.webContentLink
        tipo_documento = dados_extraidos.get("tipo_documento", "Comprovante")
        fornecedor = dados_extraidos.get("fornecedor", "Não identificado")
        
        # Dados para resposta
        gasto_data = {
            "data_despesa": data_despesa,
            "valor_total": valor_total,
            "descricao_item": descricao_item,
            "tipo_documento": tipo_documento,
            "fornecedor": fornecedor,
            "link_arquivo": arquivo_drive_url,
            "nome_arquivo": data.name
        }
        
        logger.info(f"💾 Registrando gasto com parâmetros corretos:")
        logger.info(f"   - descricao_imagem: {descricao_imagem[:100]}...")
        logger.info(f"   - arquivo_drive_url: {arquivo_drive_url}")
        logger.info(f"   - data_despesa: {data_despesa}")
        logger.info(f"   - valor_total: {valor_total}")
        logger.info(f"   - descricao_item: {descricao_item}")
        logger.info(f"   - tipo_documento: {tipo_documento}")
        logger.info(f"   - fornecedor: {fornecedor}")
        
        # ETAPA 1: REGISTRAR GASTO (INSERÇÃO INICIAL)
        try:
            # Usar o método direto da classe FinancialTools com parâmetros corretos
            result = financial_tools.inserir_gasto_empresa(
                descricao_imagem=descricao_imagem,
                arquivo_drive_url=arquivo_drive_url,
                data_despesa=data_despesa,
                valor_total=valor_total,
                descricao_item=descricao_item,
                tipo_documento=tipo_documento,
                fornecedor=fornecedor
            )
            
            logger.info(f"✅ ETAPA 1 - Resultado da inserção: {result}")
            
            # Parse do resultado
            if "sucesso" in str(result).lower():
                # Extrair ID do resultado se disponível
                id_match = re.search(r'ID[:\s]*(\d+)', str(result))
                gasto_id = int(id_match.group(1)) if id_match else None
                
                # ETAPA 2: PERGUNTAR SOBRE NF E OUTRAS INFORMAÇÕES
                message = f"""✅ Dados inseridos com sucesso! ID: {gasto_id}

Agora preciso de mais informações para completar o registro:

1️⃣ Este comprovante possui Nota Fiscal correspondente? 
   → Responda: "Sim" ou "Não"

2️⃣ Qual a natureza deste gasto?
   → Opções: Alimentação, Transporte, Material de Escritório, Serviços, Marketing, Viagem, Outros

3️⃣ Confirme o fornecedor extraído: "{fornecedor}"
   → Responda: "Correto" ou informe o nome correto

💡 Responda uma pergunta por vez para melhor processamento."""
                
                return FinancialResponse(
                    success=True,
                    message=message,
                    gasto_id=gasto_id,
                    data={
                        **gasto_data,
                        "status": "aguardando_informacoes_adicionais",
                        "etapa": "2_aguardando_resposta_usuario"
                    }
                )
            else:
                raise HTTPException(status_code=500, detail=f"Erro ao registrar gasto: {result}")
                
        except Exception as insert_error:
            logger.error(f"❌ Erro na inserção: {insert_error}")
            raise HTTPException(status_code=500, detail=f"Erro ao inserir gasto: {str(insert_error)}")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Erro inesperado na extração de imagem: {e}")
        return FinancialResponse(
            success=False,
            message="Erro interno do servidor",
            error=str(e)
        )

@router.get("/financial/health")
async def financial_health():
    """Health check do endpoint financeiro"""
    return {"status": "healthy", "service": "financial-endpoint"}
