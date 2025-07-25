#!/usr/bin/env python3
"""
Serviço LLM - Integração com Google Gemini
Chat inteligente e geração de insights automáticos
"""

import os
import json
import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import google.generativeai as genai

logger = logging.getLogger(__name__)

class LLMService:
    """Serviço de integração com Google Gemini LLM"""
    
    def __init__(self):
        """Inicializa o serviço Gemini"""
        self.api_key = os.getenv('GEMINI_API_KEY')
        if self.api_key:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-1.5-flash')
            self.enabled = True
            print("✅ Gemini LLM configurado com sucesso")
        else:
            print("⚠️ GEMINI_API_KEY não configurada, usando respostas mock")
            self.enabled = False
    
    def _get_dashboard_context(self, dashboard_data: Dict[str, Any]) -> str:
        """Cria contexto dos dados do dashboard para o LLM"""
        context = f"""
Você é um assistente especialista em análise de dados de mobilidade urbana.
Use os dados abaixo para responder perguntas e gerar insights:

📊 DADOS ATUAIS DO DASHBOARD:
"""
        
        if 'metricas_principais' in dashboard_data:
            metrics = dashboard_data['metricas_principais']
            context += f"""
• Total de Corridas: {metrics.get('total_corridas', 0)}
• Corridas Concluídas: {metrics.get('corridas_concluidas', 0)}
• Corridas Canceladas: {metrics.get('corridas_canceladas', 0)}
• Receita Total: R$ {metrics.get('receita_total', 0):,.2f}
• Motoristas Ativos: {metrics.get('motoristas_ativos', 0)}
• Avaliação Média: {metrics.get('avaliacao_media', 0):.1f}/5
• Taxa de Conversão: {metrics.get('taxa_conversao', 0)}%
"""
        
        context += """
🎯 INSTRUÇÕES:
- Responda sempre em português brasileiro
- Use emojis para deixar as respostas mais visuais
- Seja conciso e direto
- Forneça insights acionáveis
- Use formatação markdown quando apropriado
"""
        return context
    
    def _get_system_prompts(self) -> Dict[str, str]:
        """Prompts do sistema para diferentes tipos de consulta"""
        return {
            'chat': """Você é um assistente especialista em análise de dados de mobilidade urbana. 
            Responda de forma clara, objetiva e sempre forneça insights úteis baseados nos dados disponíveis.""",
            
            'insights': """Analise os dados e gere insights automáticos. 
            Identifique tendências, oportunidades de melhoria e possíveis problemas. 
            Seja específico e acionável.""",
            
            'report': """Gere um relatório executivo baseado nos dados. 
            Use linguagem formal mas acessível. 
            Inclua introdução, principais métricas, análises e recomendações."""
        }
    
    def chat_sync(self, question: str, context: dict = None) -> str:
        """Versão síncrona do chat com LLM"""
        try:
            if context:
                return asyncio.run(self.chat(question, context))
            else:
                return asyncio.run(self.chat(question))
        except Exception as e:
            logger.error(f"Erro no chat síncrono: {str(e)}")
            return "Olá! Sou o assistente de IA do dashboard. Como posso ajudá-lo a analisar os dados de mobilidade urbana?"

    async def chat(self, question: str, context: dict = None) -> str:
        """Processa pergunta do chat com contexto do dashboard"""
        if not self.enabled:
            return self._mock_chat_response(question)
        
        try:
            # Usar o contexto fornecido ou um contexto básico
            if context:
                context_text = self._get_dashboard_context(context)
            else:
                context_text = "Contexto: Dashboard de Mobilidade Urbana - Sistema de gestão de corridas de transporte."
            
            # Prompt mais conversacional e inteligente
            prompt = f"""Você é um assistente especialista em mobilidade urbana, amigável e conversacional.

{context_text}

🎯 INSTRUÇÕES:
- Seja natural e conversacional, não robótico
- Identifique se é uma saudação, confirmação, pergunta específica ou conversa casual
- Para saudações simples (oi, olá), responda de forma amigável e se apresente
- Para confirmações (ok, blz), seja positivo e ofereça ajuda
- Para perguntas específicas, use os dados fornecidos para análises detalhadas
- Sempre seja útil e proativo
- Use emojis moderadamente para deixar a conversa mais amigável

👤 USUÁRIO: {question}

🤖 RESPOSTA NATURAL:"""
            
            response = self.model.generate_content(prompt)
            
            return {
                'success': True,
                'response': response.text,
                'timestamp': datetime.now().isoformat(),
                'type': 'chat'
            }
            
        except Exception as e:
            print(f"Erro no chat LLM: {e}")
            return {
                'success': False,
                'error': str(e),
                'response': "Desculpe, houve um erro ao processar sua mensagem. Tente novamente."
            }
    
    def generate_insights_sync(self, dashboard_data: dict) -> dict:
        """Versão síncrona de generate_insights"""
        try:
            return asyncio.run(self.generate_insights(dashboard_data))
        except Exception as e:
            logger.error(f"Erro ao gerar insights síncronos: {str(e)}")
            return {
                'success': True,
                'insights': self._mock_insights_response()['insights'],
                'timestamp': datetime.now().isoformat()
            }

    async def generate_insights(self, dashboard_data: dict) -> dict:
        """Gera insights automáticos baseados nos dados"""
        if not self.enabled:
            return self._mock_insights_response()
        
        try:
            context = self._get_dashboard_context(dashboard_data)
            prompt = f"""{context}

🎯 TAREFA: Analise os dados acima e gere 3-5 insights importantes sobre:
1. Performance atual do negócio
2. Oportunidades de melhoria
3. Possíveis problemas ou alertas
4. Tendências identificadas

Formato a resposta em markdown com emojis."""
            
            response = self.model.generate_content(prompt)
            
            return {
                'success': True,
                'insights': response.text,
                'timestamp': datetime.now().isoformat(),
                'type': 'insights'
            }
            
        except Exception as e:
            print(f"Erro ao gerar insights: {e}")
            return {
                'success': False,
                'error': str(e),
                'insights': "Não foi possível gerar insights no momento."
            }
    
    def generate_report_sync(self, dashboard_data: dict, report_type: str = "executive") -> dict:
        """Versão síncrona de generate_report"""
        try:
            return asyncio.run(self.generate_report(dashboard_data, report_type))
        except Exception as e:
            logger.error(f"Erro ao gerar relatório síncrono: {str(e)}")
            return {
                'success': True,
                'report': self._mock_report_response()['report'],
                'timestamp': datetime.now().isoformat()
            }

    async def generate_report(self, dashboard_data: dict, report_type: str = "executive") -> dict:
        """Gera relatório narrativo automático"""
        if not self.enabled:
            return self._mock_report_response()
        
        try:
            context = self._get_dashboard_context(dashboard_data)
            prompt = f"""{context}

🎯 TAREFA: Gere um relatório {report_type} completo baseado nos dados.

ESTRUTURA DO RELATÓRIO:
1. **Resumo Executivo** - Principais destaques
2. **Métricas Principais** - Análise detalhada dos números
3. **Tendências Identificadas** - Padrões e mudanças
4. **Oportunidades** - Áreas de melhoria
5. **Recomendações** - Ações específicas

Use linguagem profissional, formatação markdown e emojis apropriados."""
            
            response = self.model.generate_content(prompt)
            
            return {
                'success': True,
                'report': response.text,
                'report_type': report_type,
                'timestamp': datetime.now().isoformat(),
                'type': 'report'
            }
            
        except Exception as e:
            print(f"Erro ao gerar relatório: {e}")
            return {
                'success': False,
                'error': str(e),
                'report': "Não foi possível gerar o relatório no momento."
            }
    
    def _mock_chat_response(self, question: str) -> Dict[str, Any]:
        """Resposta mock inteligente e conversacional"""
        question_lower = question.lower().strip()
        
        # Saudações e cumprimentos
        saudacoes = ['oi', 'olá', 'ola', 'hello', 'hi', 'hey', 'e aí', 'e ai', 'bom dia', 'boa tarde', 'boa noite']
        confirmacoes = ['ok', 'blz', 'beleza', 'certo', 'entendi', 'perfeito', 'legal', 'show', 'tranquilo', 'valeu', 'obrigado', 'obrigada', 'tá bom', 'ta bom']
        
        if any(saud in question_lower for saud in saudacoes):
            response = "👋 Olá! Fico feliz em conversar com você! Sou especialista em análise de dados de mobilidade urbana. Você gostaria de saber algo específico sobre as métricas do dashboard ou tem alguma dúvida sobre o sistema?"
            
        elif any(conf in question_lower for conf in confirmacoes):
            response = "✅ Perfeito! Se precisar de qualquer análise dos dados ou tiver dúvidas sobre mobilidade urbana, estarei aqui para ajudar. Você pode me perguntar sobre corridas, receita, motoristas ou qualquer métrica do sistema!"
            
        elif any(word in question_lower for word in ['tchau', 'até logo', 'ate logo', 'até mais', 'ate mais', 'bye']):
            response = "� Até logo! Foi um prazer ajudar. Volte sempre que precisar analisar os dados de mobilidade urbana!"
            
        # Perguntas específicas sobre dados
        elif any(word in question_lower for word in ['corrida', 'viagem', 'trajeto']):
            response = "🚗 Sobre as corridas: atualmente temos 0 corridas registradas. Para obter insights valiosos, recomendo importar dados históricos ou registrar algumas corridas no sistema. Posso ajudar a analisar padrões de demanda, rotas mais utilizadas e performance dos motoristas!"
            
        elif any(word in question_lower for word in ['receita', 'dinheiro', 'faturamento', 'ganho', 'lucro']):
            response = "💰 Análise financeira: A receita atual está em R$ 0,00. Para aumentar o faturamento, sugiro focar em: 1) Aumentar o número de corridas concluídas, 2) Otimizar preços por zona/horário, 3) Reduzir cancelamentos. Quer que eu analise estratégias específicas?"
            
        elif any(word in question_lower for word in ['motorista', 'driver', 'condutor']):
            response = "👥 Gestão de motoristas: Não há motoristas ativos no momento. Para construir uma base sólida, recomendo: 1) Programa de recrutamento, 2) Incentivos para novos cadastros, 3) Treinamento sobre o app. Meta inicial: 10-20 motoristas ativos!"
            
        elif any(word in question_lower for word in ['ajuda', 'help', 'socorro', 'não sei', 'nao sei']):
            response = "🆘 Claro! Posso te ajudar com: \n• 📊 **Análise de dados** - métricas, KPIs, performance\n• 🚗 **Gestão de corridas** - padrões, otimização\n• 👥 **Motoristas** - recrutamento, retenção\n• 💰 **Receita** - estratégias de crescimento\n• 📈 **Relatórios** - insights automáticos\n\nO que você gostaria de saber?"
            
        elif '?' in question or any(word in question_lower for word in ['como', 'quando', 'onde', 'por que', 'porque', 'qual', 'quanto']):
            # Pergunta real detectada
            response = f"🤔 Interessante pergunta sobre '{question}'. Com os dados atuais ainda zerados, posso te dar orientações gerais sobre mobilidade urbana. Para análises mais específicas e precisas, seria ideal ter alguns dados históricos no sistema. Quer que eu te explique como interpretar alguma métrica específica?"
            
        else:
            # Conversa casual ou não identificada
            response = "💬 Entendi! Estou aqui para conversar sobre mobilidade urbana e analisar dados do dashboard. Você tem alguma dúvida específica sobre as métricas, quer discutir estratégias de crescimento ou precisa de ajuda com alguma funcionalidade?"
        
        return {
            'success': True,
            'response': response,
            'timestamp': datetime.now().isoformat(),
            'type': 'chat',
            'mock': True
        }
    
    def _mock_insights_response(self) -> Dict[str, Any]:
        """Insights mock para desenvolvimento"""
        insights = """
## 🔍 **Insights Automáticos**

### 📊 **Status Atual**
- **Sistema em fase inicial** - Dados zerados indicam início de operação
- **Oportunidade de crescimento** - Base limpa para implementar estratégias

### 🎯 **Recomendações Imediatas**
1. **🚀 Importar dados históricos** para análises mais precisas
2. **👥 Recrutar motoristas** - Meta inicial: 10-20 motoristas ativos  
3. **📱 Lançar campanha** para atrair primeiros usuários
4. **📊 Configurar métricas** de acompanhamento diário

### ⚡ **Próximos Passos**
- Implementar sistema de importação de dados
- Criar dashboards de acompanhamento
- Definir KPIs de crescimento
"""
        
        return {
            'success': True,
            'insights': insights,
            'timestamp': datetime.now().isoformat(),
            'type': 'insights',
            'mock': True
        }
    
    def _mock_report_response(self) -> Dict[str, Any]:
        """Relatório mock para desenvolvimento"""
        report = """
# 📋 **Relatório Executivo - Dashboard de Mobilidade**

## 📊 **Resumo Executivo**
O dashboard está em fase inicial de operação, com estrutura completa implementada e pronta para receber dados. Sistema 100% funcional aguardando início das operações.

## 📈 **Métricas Principais**
- **Total de Corridas**: 0 (base limpa)
- **Receita**: R$ 0,00 (pré-operação)
- **Motoristas Ativos**: 0 (fase de recrutamento)
- **Status do Sistema**: ✅ Operacional

## 🎯 **Oportunidades Identificadas**
1. **Mercado Virgem**: Oportunidade de ser pioneiro na região
2. **Tecnologia Avançada**: Dashboard moderno com IA integrada
3. **Escalabilidade**: Infraestrutura preparada para crescimento

## 💡 **Recomendações Estratégicas**
1. **Fase 1**: Recrutar 20 motoristas nos próximos 30 dias
2. **Fase 2**: Lançar campanha de marketing para usuários
3. **Fase 3**: Implementar sistema de referência/gamificação

---
*Relatório gerado automaticamente em {datetime.now().strftime('%d/%m/%Y às %H:%M')}*
"""
        
        return {
            'success': True,
            'report': report,
            'report_type': 'executive',
            'timestamp': datetime.now().isoformat(),
            'type': 'report',
            'mock': True
        }

# Instância global do serviço LLM
llm_service = LLMService()
