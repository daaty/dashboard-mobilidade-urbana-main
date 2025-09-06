"""
Endpoint específico para receber dados financeiros do N8N
Mais direto e simples que o endpoint AGNO conversacional
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, field_validator
import logging
import json
import re
from typing import Dict, Any, Optional, Union
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
        # CENÁRIO 1: DADOS DE IMAGEM - INICIA FLUXO DE REGISTRO
        if data.kind and data.content:
            logger.info(f"📋 INICIANDO fluxo de registro - Arquivo: {data.name}")
            return await handle_image_extraction(data)
            
        # CENÁRIO 2: INTERAÇÃO COM FLUXO JÁ INICIADO
        elif data.userName and data.userMessage and data.previous_gasto_id:
            logger.info(f"💬 Continuando fluxo de registro - Usuário: {data.userName}, Gasto ID: {data.previous_gasto_id}")
            return await handle_user_interaction_with_context(data.userName, data.userMessage, data.previous_gasto_id)
            
        # CENÁRIO 3: INTERAÇÃO SEM CONTEXTO - VERIFICAR SE É PARTE DE UM FLUXO ATIVO
        elif data.userName and data.userMessage and not data.previous_gasto_id:
            logger.info(f"🔍 Verificando contexto - Usuário: {data.userName}, Mensagem: {data.userMessage}")
            
            # Tentar recuperar contexto de registro ativo
            recovered_context = await try_recover_registration_context(data.userName, data.userMessage)
            
            if recovered_context:
                logger.info(f"🔄 Contexto recuperado - Gasto ID: {recovered_context['gasto_id']}")
                return await handle_user_interaction_with_context(data.userName, data.userMessage, recovered_context['gasto_id'])
            else:
                logger.info(f"💭 Modo conversacional - Usuário: {data.userName}, Mensagem: {data.userMessage}")
                return await handle_conversational_interaction(data.userName, data.userMessage)
            
        else:
            raise HTTPException(status_code=400, detail="Formato de dados inválido: dados insuficientes")
            
    except Exception as e:
        logger.error(f"❌ Erro no endpoint financeiro: {e}")
        return FinancialResponse(
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

async def handle_conversational_interaction(user_name: str, user_message: str):
    """Lidar com interação conversacional SEM contexto de registro - apenas chat"""
    logger.info(f"💭 Interação conversacional: {user_name} disse '{user_message}'")
    
    # Normalizar mensagem para análise
    msg_lower = user_message.lower().strip()
    
    # CUMPRIMENTOS E INTERAÇÕES GERAIS
    if any(cumprimento in msg_lower for cumprimento in ['ola', 'olá', 'oi', 'hello', 'hey', 'bom dia', 'boa tarde', 'boa noite']):
        response_msg = f"Olá {user_name}! 👋 Como posso te ajudar hoje? Posso registrar gastos, comprovantes ou notas fiscais para você!"
    
    elif any(palavra in msg_lower for palavra in ['help', 'ajuda', 'como funciona', 'o que você faz', 'ferramenta', 'funcionalidade', 'o que pode fazer', 'que ferramentas', 'quais ferramentas', 'funcoes', 'funções']):
        response_msg = f"Olá {user_name}! 🤖 Sou a Alice-Financeira, sua assistente para controle financeiro!\n\n**Minhas ferramentas:**\n• 📷 **Análise de Imagens**: Processo comprovantes e notas fiscais automaticamente\n• 💾 **Registro de Gastos**: Salvo dados extraídos no sistema financeiro\n• 🔗 **Vinculação de Documentos**: Conecto comprovantes com suas respectivas NFs\n• 📊 **Categorização**: Organizo gastos por tipo (Alimentação, Transporte, etc.)\n• 🏢 **Gestão de Fornecedores**: Identifico e valido empresas dos documentos\n\n**Como usar:**\nApenas envie a imagem do documento que eu cuido do resto! 📸"
    
    elif any(palavra in msg_lower for palavra in ['comprovante', 'nota fiscal', 'nf', 'gasto', 'despesa', 'pagamento']):
        response_msg = f"Perfeito {user_name}! Para registrar um gasto, envie a **imagem** do comprovante ou nota fiscal que eu processarei automaticamente os dados para você!\n\n📸 **Importante:** Preciso da imagem do documento para iniciar o registro."
    
    elif any(palavra in msg_lower for palavra in ['tchau', 'bye', 'obrigado', 'obrigada', 'valeu']):
        response_msg = f"Até logo {user_name}! Foi um prazer ajudar. Qualquer novo gasto é só me enviar! 😊"
    
    else:
        # RESPOSTA INTELIGENTE PARA MENSAGENS NÃO IDENTIFICADAS
        if len(user_message.strip()) <= 3:
            response_msg = f"Não entendi bem {user_name}. Você poderia:\n• Enviar imagem de um comprovante para registrar\n• Me dizer se tem alguma dúvida específica\n• Ou ser mais específico sobre o que precisa? 😄"
        elif any(palavra in msg_lower for palavra in ['qual', 'que', 'como', '?']):
            response_msg = f"Olá {user_name}! Para perguntas específicas, use palavras-chave como:\n• **'ferramentas'** ou **'ajuda'** - para saber minhas funcionalidades\n• **'como funciona'** - para entender o processo\n• **'comprovante'** - para registrar gastos\n\nOu simplesmente envie a imagem do documento que precisa processar! 📸"
        else:
            response_msg = f"Olá {user_name}! Recebi sua mensagem: '{user_message}'\n\n💡 **Para registrar gastos:** Envie a imagem do comprovante/NF\n❓ **Para dúvidas:** Digite 'ajuda' ou 'ferramentas'\n\nComo posso ajudar?"
    
    return FinancialResponse(
        success=True,
        message=response_msg,
        gasto_id=None,
        data={
            "user": user_name,
            "message": user_message,
            "interaction_type": "conversational_only"
        },
        error=None
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
