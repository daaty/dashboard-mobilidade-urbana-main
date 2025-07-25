#!/usr/bin/env python3
"""
Serviço LLM Inteligente - Versão Aprimorada
LLM que realmente analisa dados e fornece insights verdadeiros
"""

import os
import json
import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import google.generativeai as genai

logger = logging.getLogger(__name__)

class IntelligentLLMService:
    """Serviço LLM que realmente analisa dados e fornece insights inteligentes"""
    
    def __init__(self):
        """Inicializa o serviço Gemini"""
        self.api_key = os.getenv('GEMINI_API_KEY')
        if self.api_key:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-1.5-flash')
            self.enabled = True
            print("✅ Gemini LLM configurado com sucesso")
        else:
            print("⚠️ GEMINI_API_KEY não configurada, usando análise inteligente mock")
            self.enabled = False
    
    def _get_dashboard_context(self, dashboard_data: Dict[str, Any]) -> str:
        """Cria contexto rico dos dados do dashboard para o LLM"""
        context = f"""
🎯 CONTEXTO: Você é um consultor especialista em mobilidade urbana e análise de dados.
Seja conversacional, inteligente e forneça insights REAIS baseados nos dados.

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

📈 ANÁLISE AUTOMÁTICA:
- Taxa de Sucesso: {(metrics.get('corridas_concluidas', 0) / max(metrics.get('total_corridas', 1), 1) * 100):.1f}%
- Receita por Corrida: R$ {(metrics.get('receita_total', 0) / max(metrics.get('corridas_concluidas', 1), 1)):.2f}
- Produtividade: {(metrics.get('total_corridas', 0) / max(metrics.get('motoristas_ativos', 1), 1)):.1f} corridas/motorista
"""
        
        context += """

🎯 SEJA UM CONSULTOR INTELIGENTE:
- Analise REALMENTE os números fornecidos
- Identifique padrões, oportunidades e problemas
- Dê recomendações específicas e práticas
- Seja conversacional mas profissional
- Use insights de negócio de mobilidade urbana
"""
        return context
    
    def chat(self, question: str, dashboard_data: dict = None, cache_service=None) -> dict:
        """Chat inteligente que analisa dados reais"""
        if not dashboard_data:
            from backend.api.dashboard import get_dashboard_data
            try:
                dashboard_data = get_dashboard_data()
            except:
                dashboard_data = self._get_mock_dashboard_data()
        
        if not self.enabled:
            return self._intelligent_mock_response(question, dashboard_data)
        
        try:
            context_text = self._get_dashboard_context(dashboard_data)
            
            # Prompt para análise inteligente
            prompt = f"""{context_text}

🗣️ CONVERSA:
Usuário: {question}

Assistente: [Analise os dados fornecidos e responda de forma inteligente e útil]"""
            
            response = self.model.generate_content(prompt)
            
            return {
                'success': True,
                'response': response.text,
                'timestamp': datetime.now().isoformat(),
                'type': 'chat'
            }
            
        except Exception as e:
            print(f"Erro no chat LLM: {e}")
            return self._intelligent_mock_response(question, dashboard_data)
    
    def _intelligent_mock_response(self, question: str, dashboard_data: dict) -> Dict[str, Any]:
        """Sistema mock inteligente que realmente analisa dados"""
        
        question_lower = question.lower().strip()
        
        # Sistema inteligente de análise contextual
        if self._is_greeting(question_lower):
            return self._generate_greeting_response()
        elif self._is_confirmation(question_lower):
            return self._generate_confirmation_response() 
        elif self._is_farewell(question_lower):
            return self._generate_farewell_response()
        else:
            # Análise real dos dados para qualquer pergunta
            return self._generate_data_analysis_response(question, dashboard_data)
    
    def _is_greeting(self, text: str) -> bool:
        """Detecta saudações"""
        greetings = ['oi', 'olá', 'ola', 'hello', 'hi', 'hey', 'e aí', 'e ai', 'bom dia', 'boa tarde', 'boa noite']
        return any(greet in text for greet in greetings)
    
    def _is_confirmation(self, text: str) -> bool:
        """Detecta confirmações"""
        confirmations = ['ok', 'blz', 'beleza', 'certo', 'entendi', 'perfeito', 'legal', 'show', 'tranquilo', 'valeu', 'obrigado', 'obrigada', 'tá bom', 'ta bom']
        return any(conf in text for conf in confirmations)
    
    def _is_farewell(self, text: str) -> bool:
        """Detecta despedidas"""
        farewells = ['tchau', 'até logo', 'ate logo', 'até mais', 'ate mais', 'bye', 'fui', 'xau']
        return any(fare in text for fare in farewells)
    
    def _generate_greeting_response(self) -> Dict[str, Any]:
        """Resposta de saudação contextualizada"""
        return {
            'success': True,
            'response': "👋 Olá! Sou seu analista de dados especializado em mobilidade urbana. Posso te ajudar a entender as métricas do dashboard, identificar oportunidades de crescimento e otimizar operações. O que você gostaria de analisar?",
            'timestamp': datetime.now().isoformat(),
            'type': 'chat',
            'mock': True
        }
    
    def _generate_confirmation_response(self) -> Dict[str, Any]:
        """Resposta de confirmação proativa"""
        return {
            'success': True,
            'response': "✅ Perfeito! Estou aqui para analisar qualquer aspecto do seu negócio de mobilidade urbana. Posso examinar padrões de corridas, performance de motoristas, otimização de preços, análise de rotas... Em que posso focar?",
            'timestamp': datetime.now().isoformat(),
            'type': 'chat',
            'mock': True
        }
    
    def _generate_farewell_response(self) -> Dict[str, Any]:
        """Resposta de despedida"""
        return {
            'success': True,
            'response': "👋 Até logo! Continue focando no crescimento sustentável da operação. Estarei aqui sempre que precisar de análises de dados!",
            'timestamp': datetime.now().isoformat(),
            'type': 'chat',
            'mock': True
        }
    
    def _generate_data_analysis_response(self, question: str, dashboard_data: dict) -> Dict[str, Any]:
        """Análise real e inteligente dos dados"""
        
        # Extrair métricas principais
        metrics = dashboard_data.get('metricas_principais', {})
        total_corridas = metrics.get('total_corridas', 0)
        corridas_concluidas = metrics.get('corridas_concluidas', 0)
        corridas_canceladas = metrics.get('corridas_canceladas', 0)
        receita_total = metrics.get('receita_total', 0)
        motoristas_ativos = metrics.get('motoristas_ativos', 0)
        avaliacao_media = metrics.get('avaliacao_media', 0)
        
        # Análise contextual baseada na pergunta
        question_lower = question.lower()
        
        if any(word in question_lower for word in ['corrida', 'viagem', 'trajeto', 'demanda']):
            response = self._analyze_rides_data(total_corridas, corridas_concluidas, corridas_canceladas)
        elif any(word in question_lower for word in ['receita', 'dinheiro', 'faturamento', 'ganho', 'lucro', 'preço']):
            response = self._analyze_revenue_data(receita_total, total_corridas, corridas_concluidas)
        elif any(word in question_lower for word in ['motorista', 'driver', 'condutor']):
            response = self._analyze_drivers_data(motoristas_ativos, total_corridas, avaliacao_media)
        elif any(word in question_lower for word in ['avaliação', 'qualidade', 'satisfação', 'rating']):
            response = self._analyze_quality_data(avaliacao_media, corridas_concluidas)
        elif any(word in question_lower for word in ['cancelamento', 'problema', 'falha']):
            response = self._analyze_cancellation_data(corridas_canceladas, total_corridas)
        elif any(word in question_lower for word in ['crescimento', 'crescer', 'expandir', 'melhorar']):
            response = self._analyze_growth_opportunities(metrics)
        elif any(word in question_lower for word in ['kpi', 'métrica', 'performance', 'indicador']):
            response = self._analyze_kpis(metrics)
        else:
            # Análise geral dos dados
            response = self._generate_general_analysis(metrics, question)
        
        return {
            'success': True,
            'response': response,
            'timestamp': datetime.now().isoformat(),
            'type': 'chat',
            'mock': True
        }
    
    def _analyze_rides_data(self, total, concluidas, canceladas):
        """Análise inteligente dos dados de corridas"""
        if total == 0:
            return "🚗 **Análise de Corridas**: Ainda não há corridas registradas no sistema. Para começar a operar, recomendo:\n\n• **Fase 1**: Recrutar 5-10 motoristas piloto\n• **Fase 2**: Campanha de lançamento para usuários\n• **Meta inicial**: 50-100 corridas/semana\n• **Foco**: Taxa de conversão >80% (baixo cancelamento)"
        
        taxa_sucesso = (concluidas / total) * 100 if total > 0 else 0
        taxa_cancelamento = (canceladas / total) * 100 if total > 0 else 0
        
        if taxa_sucesso >= 80:
            status = "🟢 Excelente"
        elif taxa_sucesso >= 60:
            status = "🟡 Bom, mas pode melhorar" 
        else:
            status = "🔴 Crítico - Requer ação imediata"
            
        return f"🚗 **Análise de Corridas** {status}\n\n• **Total**: {total} corridas\n• **Taxa de Sucesso**: {taxa_sucesso:.1f}%\n• **Cancelamentos**: {taxa_cancelamento:.1f}%\n\n**Insights**: {'Alta performance!' if taxa_sucesso >= 80 else 'Investigar causas de cancelamentos e otimizar matching motorista-passageiro.'}"
    
    def _analyze_revenue_data(self, receita, total_corridas, concluidas):
        """Análise financeira inteligente"""
        if receita == 0:
            return "💰 **Análise Financeira**: Sem receita registrada ainda. Estrutura recomendada:\n\n• **Preço base**: R$ 3,50 bandeirada + R$ 1,80/km\n• **Comissão**: 20-25% por corrida\n• **Meta mês 1**: R$ 10.000 de GMV\n• **Estratégia**: Promoções de lançamento para ganhar tração"
        
        ticket_medio = receita / concluidas if concluidas > 0 else 0
        
        if ticket_medio >= 25:
            performance = "🟢 Ticket médio excelente"
        elif ticket_medio >= 15:
            performance = "🟡 Ticket médio bom"
        else:
            performance = "🔴 Ticket médio baixo"
            
        return f"💰 **Análise Financeira** {performance}\n\n• **Receita Total**: R$ {receita:,.2f}\n• **Ticket Médio**: R$ {ticket_medio:.2f}\n• **Corridas Pagas**: {concluidas}\n\n**Estratégia**: {'Manter estratégia atual' if ticket_medio >= 20 else 'Implementar preços dinâmicos e promoções para horários de baixa demanda'}"
    
    def _analyze_drivers_data(self, motoristas, corridas, avaliacao):
        """Análise da base de motoristas"""
        if motoristas == 0:
            return "👥 **Análise de Motoristas**: Base vazia - Crítico!\n\n• **Ação Urgente**: Programa de recrutamento\n• **Incentivos**: R$ 200 bônus primeiras 20 corridas\n• **Meta inicial**: 15-20 motoristas ativos\n• **Estratégia**: Parcerias com cooperativas existentes"
        
        corridas_por_motorista = corridas / motoristas if motoristas > 0 else 0
        
        if corridas_por_motorista >= 10:
            eficiencia = "🟢 Alta produtividade"
        elif corridas_por_motorista >= 5:
            eficiencia = "🟡 Produtividade média"
        else:
            eficiencia = "🔴 Baixa utilização"
            
        return f"👥 **Análise de Motoristas** {eficiencia}\n\n• **Ativos**: {motoristas} motoristas\n• **Corridas/Motorista**: {corridas_por_motorista:.1f}\n• **Avaliação**: {avaliacao:.1f}/5.0\n\n**Ação**: {'Focar em retenção' if corridas_por_motorista >= 8 else 'Programas de engajamento e incentivos por meta'}"
    
    def _analyze_quality_data(self, avaliacao, corridas_concluidas):
        """Análise de qualidade do serviço"""
        if corridas_concluidas == 0:
            return "⭐ **Análise de Qualidade**: Sem avaliações ainda. Implementar:\n\n• **Sistema obrigatório** de avaliação pós-corrida\n• **Meta**: Manter >4.5 estrelas\n• **Incentivos**: Motoristas 5★ ganham prioridade\n• **Qualidade primeiro**: Melhor que quantidade"
        
        if avaliacao >= 4.5:
            status = "🟢 Excelente qualidade"
        elif avaliacao >= 4.0:
            status = "🟡 Boa qualidade"
        else:
            status = "🔴 Qualidade crítica"
            
        return f"⭐ **Análise de Qualidade** {status}\n\n• **Avaliação Média**: {avaliacao:.2f}/5.0\n• **Base**: {corridas_concluidas} avaliações\n\n**Ação**: {'Manter padrão' if avaliacao >= 4.5 else 'Programa de treinamento de motoristas e feedback ativo'}"
    
    def _analyze_cancellation_data(self, canceladas, total):
        """Análise de cancelamentos"""
        if total == 0:
            return "⚠️ **Análise de Cancelamentos**: Sem dados ainda. Quando começar, manter <15% de cancelamentos é crucial para sucesso da operação."
        
        taxa = (canceladas / total) * 100 if total > 0 else 0
        
        if taxa <= 10:
            status = "🟢 Taxa excelente"
        elif taxa <= 20:
            status = "🟡 Taxa aceitável"
        else:
            status = "🔴 Taxa crítica"
            
        return f"⚠️ **Análise de Cancelamentos** {status}\n\n• **Taxa**: {taxa:.1f}%\n• **Total Cancelado**: {canceladas} corridas\n\n**Causas comuns**: Distância, trânsito, tempo de espera\n**Solução**: {'Manter padrão' if taxa <= 15 else 'Otimizar algoritmo de matching e reduzir tempo de resposta'}"
    
    def _analyze_growth_opportunities(self, metrics):
        """Análise de oportunidades de crescimento"""
        return "📈 **Oportunidades de Crescimento**:\n\n• **Expansão Geográfica**: Mapear bairros de alta demanda\n• **Horários Premium**: Preços dinâmicos em rush\n• **Parcerias**: Empresas, hotéis, aeroporto\n• **Fidelização**: Programa de pontos para usuários\n• **Tecnologia**: IA para previsão de demanda"
    
    def _analyze_kpis(self, metrics):
        """Análise de KPIs do negócio"""
        return "📊 **KPIs Essenciais Mobilidade Urbana**:\n\n• **Operacionais**: Taxa conversão >80%, Tempo resposta <5min\n• **Financeiros**: GMV crescimento 20%/mês, CAC <R$50\n• **Qualidade**: NPS >70, Avaliação >4.5★\n• **Motoristas**: Retenção >80%, Produtividade >8 corridas/dia\n• **Usuários**: Reativação >40%, Frequência >2x/semana"
    
    def _generate_general_analysis(self, metrics, question):
        """Análise geral quando não há categoria específica"""
        total_corridas = metrics.get('total_corridas', 0)
        
        if total_corridas == 0:
            return f"🤔 Sobre '{question}': No momento estamos na fase de lançamento com dados zerados. Posso te ajudar com estratégias de:\n\n• **Lançamento**: Como estruturar operação inicial\n• **Métricas**: Quais KPIs acompanhar\n• **Crescimento**: Estratégias de aquisição\n• **Operações**: Otimização de processos\n\nEm que área específica posso focar?"
        else:
            return f"💡 Analisando '{question}' com base nos dados atuais: {total_corridas} corridas registradas. Posso detalhar qualquer aspecto específico - financeiro, operacional, motoristas ou usuários. O que te interessa mais?"
    
    def _get_mock_dashboard_data(self):
        """Dados mock quando não consegue acessar API"""
        return {
            'metricas_principais': {
                'total_corridas': 0,
                'corridas_concluidas': 0, 
                'corridas_canceladas': 0,
                'receita_total': 0,
                'motoristas_ativos': 0,
                'avaliacao_media': 0
            }
        }

# Instância do serviço LLM inteligente
intelligent_llm = IntelligentLLMService()
