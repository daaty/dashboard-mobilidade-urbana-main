"""
🚀 AGENTE INTELIGENTE PARA DASHBOARD DE MOBILIDADE URBANA
Agente com reasoning, memória e ferramentas especializadas
"""

import os
import sys
from datetime import datetime
from typing import Optional, List, Dict, Any

try:
    from agno.agent import Agent, AgentMemory
    from agno.models.openai import OpenAIChat
    from agno.tools import Toolkit
    import json
    import psycopg2
    
    # Importar nossas ferramentas customizadas
    from tools.dashboard_api_tools import DashboardAPITools
    from tools.business_analysis_tools import BusinessAnalysisTools
    
    AGNO_AVAILABLE = True
    print("✅ AGNO framework carregado com sucesso!")
    
except ImportError as e:
    print(f"Erro ao importar AGNO: {e}")
    print("Certifique-se de que o framework agno está instalado:")
    print("pip install agno")
    sys.exit(1)


class MobilityDashboardAgent:
    """
    🎯 Agente Inteligente para Análise de Mobilidade Urbana
    
    Capacidades:
    - Reasoning avançado sobre dados de negócio
    - Memória persistente de análises
    - Ferramentas especializadas em mobilidade urbana
    - Geração de insights e recomendações estratégicas
    """
    
    def __init__(
        self,
        dashboard_url: str = "http://localhost:8000",
        openai_api_key: Optional[str] = None,
        memory_db_url: Optional[str] = None
    ):
        self.dashboard_url = dashboard_url
        
        # Configurar modelo de linguagem
        model_config = {
            "id": "gpt-4o-mini",
            "api_key": openai_api_key or os.getenv("OPENAI_API_KEY")
        }
        
        # Configurar memória (se database URL fornecido)
        memory = None
        if memory_db_url or os.getenv("MEMORY_DB_URL"):
            try:
                db_url = memory_db_url or os.getenv("MEMORY_DB_URL")
                table_prefix = os.getenv("AGENT_MEMORY_TABLE_PREFIX", "agente_")
                
                # Criar memória personalizada usando PostgreSQL
                memory = self._create_custom_memory(db_url, table_prefix)
                print(f"✅ Memória persistente configurada com tabela: {table_prefix}memory")
            except Exception as e:
                print(f"Aviso: Não foi possível configurar memória persistente: {e}")
                print("💡 O agente funcionará sem memória persistente")
                memory = None
        
        # Definir instruções especializadas
        instructions = self._get_agent_instructions()
        
        # Criar agente
        self.agent = Agent(
            name="MobilityInsightAgent",
            model=OpenAIChat(**model_config),
            tools=[
                DashboardAPITools(base_url=dashboard_url),
                BusinessAnalysisTools()
            ],
            instructions=instructions,
            memory=memory,
            show_tool_calls=True,
            markdown=True
        )
        
        # Base de conhecimento sobre mobilidade urbana
        self.knowledge_base = self._build_knowledge_base()
    
    def _get_agent_instructions(self) -> str:
        """Instruções especializadas para o agente"""
        return """
        Você é um AGENTE ESPECIALISTA EM MOBILIDADE URBANA e análise de dados de transporte.
        
        🎯 SUA MISSÃO:
        - Analisar dados do dashboard de mobilidade urbana
        - Gerar insights estratégicos baseados em dados reais
        - Fornecer recomendações práticas para crescimento
        - Identificar tendências e oportunidades de mercado
        
        📊 EXPERTISE:
        - KPIs de mobilidade urbana (taxa de cancelamento, ROI, penetração de mercado)
        - Análise competitiva em mercados pequenos/médios
        - Estratégias de crescimento para cidades de 20k-100k habitantes
        - Otimização operacional (motoristas, corridas, custos)
        
        🧠 ABORDAGEM DE REASONING:
        1. SEMPRE use as ferramentas para buscar dados atualizados
        2. Combine múltiplas fontes de dados para análises completas
        3. Calcule KPIs relevantes e compare com benchmarks da indústria
        4. Identifique padrões, tendências e anomalias
        5. Gere recomendações específicas e acionáveis
        
        📋 FORMATO DE RESPOSTA:
        - Use tabelas para apresentar dados estruturados
        - Inclua emojis para destacar insights importantes
        - Priorize recomendações por impacto e facilidade de implementação
        - Forneça justificativas baseadas em dados
        
        🚨 ALERTAS CRÍTICOS:
        - Taxa de cancelamento > 15%
        - ROI de campanhas < 150%
        - Produtividade motoristas < 8 corridas/dia
        - Crescimento negativo por mais de 7 dias
        
        Lembre-se: Você tem acesso a dados REAIS do dashboard. Use isso para fornecer insights precisos e valiosos!
        """
    
    def _create_custom_memory(self, db_url: str, table_prefix: str):
        """Cria memória personalizada usando PostgreSQL"""
        try:
            # Para simplicidade, vamos usar uma implementação básica de memória
            # que salva e carrega contexto do PostgreSQL
            class CustomMemory:
                def __init__(self, db_url, table_prefix):
                    self.db_url = db_url
                    self.table_name = f"{table_prefix}memory"
                    self.conversations_table = f"{table_prefix}conversations"
                
                def save_conversation(self, session_id: str, user_message: str, agent_response: str):
                    try:
                        conn = psycopg2.connect(db_url)
                        cursor = conn.cursor()
                        cursor.execute(f"""
                            INSERT INTO {self.conversations_table} 
                            (session_id, user_message, agent_response, created_at)
                            VALUES (%s, %s, %s, NOW())
                        """, (session_id, user_message, agent_response))
                        conn.commit()
                        cursor.close()
                        conn.close()
                    except Exception as e:
                        print(f"Erro ao salvar conversa: {e}")
                
                def get_recent_conversations(self, session_id: str, limit: int = 5):
                    try:
                        conn = psycopg2.connect(db_url)
                        cursor = conn.cursor()
                        cursor.execute(f"""
                            SELECT user_message, agent_response, created_at 
                            FROM {self.conversations_table} 
                            WHERE session_id = %s 
                            ORDER BY created_at DESC 
                            LIMIT %s
                        """, (session_id, limit))
                        results = cursor.fetchall()
                        cursor.close()
                        conn.close()
                        return results
                    except Exception as e:
                        print(f"Erro ao carregar conversas: {e}")
                        return []
            
            return CustomMemory(db_url, table_prefix)
        except Exception as e:
            print(f"Erro ao criar memória customizada: {e}")
            return None
    
    def _build_knowledge_base(self) -> Dict[str, Any]:
        """Constrói base de conhecimento sobre o negócio"""
        return {
            "benchmarks_industria": {
                "taxa_cancelamento_ideal": "< 15%",
                "rating_motoristas_minimo": "4.0/5.0",
                "corridas_por_motorista_dia": "6-10",
                "roi_campanha_marketing": "> 150%",
                "penetracao_mercado_meta": "2-5%"
            },
            "cidades_target": {
                "populacao_ideal": "20.000 - 100.000 habitantes",
                "caracteristicas": "Interior, menor concorrência, demanda latente",
                "estrategia": "Relacionamento próximo, serviço personalizado"
            },
            "sazonalidade": {
                "picos": "Sexta/sábado noite, feriados, eventos",
                "baixas": "Madrugada, segunda-feira, chuva",
                "estrategias": "Incentivos dinâmicos, promoções targeted"
            }
        }
    
    def analyze_overall_performance(self) -> str:
        """Análise completa de performance da operação"""
        return self.agent.run("""
        Faça uma análise COMPLETA da performance atual da operação de mobilidade urbana.
        
        Execute estas análises na ordem:
        1. Busque métricas gerais de corridas (30 dias)
        2. Analise dados de motoristas e produtividade
        3. Examine indicadores financeiros
        4. Verifique metas estratégicas e progresso
        5. Calcule KPIs críticos de negócio
        
        Depois, forneça:
        ✅ RESUMO EXECUTIVO com os principais KPIs
        📊 ANÁLISE DE TENDÊNCIAS (crescimento, sazonalidade)
        ⚠️ ALERTAS CRÍTICOS (se houver)
        🎯 TOP 3 RECOMENDAÇÕES estratégicas
        📈 PROJEÇÕES para próximos 30 dias
        """)
    
    def city_expansion_analysis(self, cities: Optional[List[str]] = None) -> str:
        """Análise para expansão em novas cidades"""
        cities_filter = f" focando nestas cidades: {', '.join(cities)}" if cities else ""
        
        return self.agent.run(f"""
        Realize uma análise estratégica para EXPANSÃO GEOGRÁFICA{cities_filter}.
        
        Processo:
        1. Busque dados demográficos de todas as cidades
        2. Analise campanhas atuais por cidade
        3. Examine metas progressivas por localização
        4. Gere estratégia de crescimento baseada nos dados
        
        Entregue:
        🎯 RANKING de cidades por prioridade de expansão
        💰 INVESTIMENTO estimado por cidade
        📅 CRONOGRAMA de expansão (Q1-Q4 2025)
        🚀 ESTRATÉGIAS específicas por cidade
        📊 PROJEÇÕES de ROI para cada mercado
        """)
    
    def financial_health_assessment(self) -> str:
        """Avaliação da saúde financeira"""
        return self.agent.run("""
        Conduza uma auditoria FINANCEIRA completa da operação.
        
        Analise:
        1. Métricas financeiras gerais (30 dias)
        2. Gastos por categoria
        3. ROI de campanhas de marketing
        4. Dados de corridas para calcular receita
        5. Saúde financeira geral
        
        Entregue:
        💰 SCORE de saúde financeira (0-100)
        📊 BREAKDOWN de custos por categoria
        📈 ANÁLISE de ROI e eficiência
        ⚠️ RISCOS financeiros identificados
        💡 OPORTUNIDADES de otimização
        🎯 PLANO DE AÇÃO para melhoria
        """)
    
    def driver_performance_analysis(self) -> str:
        """Análise de performance dos motoristas"""
        return self.agent.run("""
        Faça uma análise DETALHADA da performance dos motoristas.
        
        Examine:
        1. Métricas gerais de motoristas (ativos, ratings, etc.)
        2. Produtividade por cidade
        3. Distribuição de corridas
        4. Calcule KPIs de produtividade
        
        Forneça:
        👥 OVERVIEW da base de motoristas
        ⭐ ANÁLISE de ratings e qualidade
        📊 PRODUTIVIDADE média por motorista
        🏆 BENCHMARK vs indústria
        🎯 ESTRATÉGIAS para melhorar engajamento
        💡 PROGRAMA de incentivos recomendado
        """)
    
    def market_trends_forecast(self) -> str:
        """Análise de tendências e projeções"""
        return self.agent.run("""
        Realize uma análise de TENDÊNCIAS DE MERCADO e projeções.
        
        Analise:
        1. Dados históricos de evolução (corridas, motoristas)
        2. Padrões sazonais identificados
        3. Tendências de crescimento por cidade
        4. Análise competitiva do mercado
        
        Entregue:
        📈 TENDÊNCIAS principais identificadas
        🔮 PROJEÇÕES para 30, 60, 90 dias
        🌍 ANÁLISE competitiva do mercado
        🎯 OPORTUNIDADES emergentes
        ⚡ AÇÕES táticas recomendadas
        """)
    
    def generate_executive_report(self) -> str:
        """Gera relatório executivo completo"""
        return self.agent.run("""
        Crie um RELATÓRIO EXECUTIVO COMPLETO para a liderança.
        
        Compile dados de:
        1. Performance geral da operação
        2. Saúde financeira
        3. Performance de motoristas
        4. Progresso das metas estratégicas
        5. Análise de mercado e concorrência
        
        Estruture como:
        📋 SUMÁRIO EXECUTIVO (principais métricas)
        📊 DASHBOARD DE KPIS críticos
        💰 STATUS FINANCEIRO
        🎯 PROGRESSO DAS METAS
        🚨 ALERTAS E RISCOS
        🚀 RECOMENDAÇÕES ESTRATÉGICAS
        📅 PRÓXIMOS PASSOS (ações prioritárias)
        """)
    
    def _classify_user_intent(self, user_question: str) -> str:
        """Classifica a intenção do usuário baseada na mensagem"""
        question_lower = user_question.lower().strip()
        
        # Saudações simples
        greetings = ['oi', 'olá', 'hello', 'hi', 'hey', 'ola', 'eai', 'e ai', 'tudo bem', 'como vai']
        if question_lower in greetings or len(question_lower.split()) <= 2 and any(g in question_lower for g in greetings):
            return 'greeting'
        
        # Perguntas sobre ajuda ou capacidades
        help_keywords = ['ajuda', 'help', 'pode fazer', 'capaz', 'funcionalidades', 'como usar']
        if any(keyword in question_lower for keyword in help_keywords):
            return 'help'
        
        # Agradecimentos
        thanks = ['obrigado', 'obrigada', 'valeu', 'thanks', 'thank you', 'brigado']
        if any(thank in question_lower for thank in thanks):
            return 'thanks'
        
        # Perguntas simples (com interrogação ou palavras interrogativas)
        question_words = ['que', 'como', 'quando', 'onde', 'por que', 'porque', 'qual', 'quais', 'quantos', 'quantas']
        if '?' in question_lower or any(word in question_lower for word in question_words):
            return 'question'
        
        # Solicitações de análise específica
        analysis_keywords = ['analise', 'análise', 'analisa', 'avalie', 'mostre', 'gere', 'relatório', 'dashboard']
        if any(keyword in question_lower for keyword in analysis_keywords):
            return 'analysis_request'
        
        # Default para análise geral
        return 'general'

    def _generate_contextual_response(self, user_question: str, intent: str) -> str:
        """Gera resposta baseada no contexto e intenção"""
        
        if intent == 'greeting':
            return """Olá! 👋 

Sou o agente AGNO, seu assistente inteligente para análise de mobilidade urbana.

Como posso ajudá-lo hoje? Posso:
• 📊 Analisar performance das cidades
• 💰 Gerar insights financeiros  
• 🚗 Avaliar dados de motoristas
• 📈 Criar relatórios executivos
• ❓ Responder perguntas específicas sobre o dashboard

O que gostaria de saber?"""

        elif intent == 'help':
            return """🤖 **Capacidades do Agente AGNO:**

**📊 Análises Disponíveis:**
• Performance geral do sistema
• Saúde financeira e receitas
• Produtividade de motoristas
• Oportunidades de expansão
• Tendências de mercado
• Relatórios executivos

**💬 Como Interagir:**
• Faça perguntas diretas: "Como está a performance desta semana?"
• Solicite análises: "Analise os dados financeiros"
• Peça comparações: "Compare o desempenho entre cidades"
• Busque insights: "Quais são as principais oportunidades?"

**🎯 Exemplos de Perguntas:**
• "Qual cidade tem melhor ROI?"
• "Como melhorar a retenção de clientes?"
• "Quais motoristas são mais produtivos?"
• "Analyze as tendências dos últimos 30 dias"

Que tipo de análise posso fazer para você?"""

        elif intent == 'thanks':
            return """De nada! 😊

Fico feliz em ajudar com suas análises de mobilidade urbana.

Se precisar de mais insights ou tiver outras perguntas, estarei aqui! 🚀"""

        elif intent == 'question':
            # Para perguntas diretas, usar análise focada
            return self.agent.run(f"""
            Responda esta pergunta específica de forma direta e concisa:
            
            PERGUNTA: {user_question}
            
            Instruções:
            1. Forneça uma resposta direta e focada
            2. Use dados específicos quando disponível
            3. Seja conciso mas informativo
            4. Inclua 1-2 insights práticos relevantes
            5. Mantenha tom conversacional e profissional
            """)
        
        elif intent == 'analysis_request':
            # Para solicitações de análise, usar análise completa
            return self.agent.run(f"""
            Execute esta solicitação de análise de forma completa:
            
            SOLICITAÇÃO: {user_question}
            
            Processo:
            1. Identifique quais dados são necessários
            2. Busque as informações relevantes usando as ferramentas
            3. Analise os dados com reasoning avançado
            4. Forneça insights acionáveis e recomendações
            5. Inclua dados específicos e métricas relevantes
            """)
        
        else:
            # Resposta geral balanceada
            return self.agent.run(f"""
            Responda ao usuário de forma equilibrada e útil:
            
            MENSAGEM: {user_question}
            
            Diretrizes:
            1. Mantenha tom profissional mas amigável
            2. Forneça informações relevantes sem exagerar
            3. Inclua dados específicos quando apropriado
            4. Sugira próximos passos ou análises relacionadas
            """)

    def interactive_analysis(self, user_question: str) -> str:
        """Análise interativa inteligente baseada no contexto da pergunta"""
        
        # Classificar intenção do usuário
        intent = self._classify_user_intent(user_question)
        
        # Gerar resposta contextual
        return self._generate_contextual_response(user_question, intent)


def main():
    """Função principal para demonstração"""
    # Carregar variáveis de ambiente
    from dotenv import load_dotenv
    load_dotenv()
    
    print("🚀 Iniciando Agente de Mobilidade Urbana...")
    print(f"📡 Dashboard URL: {os.getenv('DASHBOARD_URL', 'http://localhost:8000')}")
    
    # Configurar agente com as variáveis de ambiente
    agent = MobilityDashboardAgent(
        dashboard_url=os.getenv("DASHBOARD_URL", "http://localhost:8000"),
        openai_api_key=os.getenv("OPENAI_API_KEY"),
        memory_db_url=os.getenv("MEMORY_DB_URL")
    )
    
    # Exemplo de uso
    print("\n📊 Executando análise de performance...")
    result = agent.analyze_overall_performance()
    print(result)


if __name__ == "__main__":
    main()
