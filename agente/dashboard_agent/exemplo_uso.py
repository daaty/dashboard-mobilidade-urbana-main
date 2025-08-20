"""
🎮 EXEMPLO DE USO DO AGENTE INTELIGENTE
Script de demonstração das capacidades do agente
"""

import os
import sys
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Adicionar o diretório atual ao path
sys.path.append(os.path.dirname(__file__))

from mobility_agent import MobilityDashboardAgent


def main():
    """Demonstração das capacidades do agente"""
    
    print("🚀 INICIANDO AGENTE INTELIGENTE DE MOBILIDADE URBANA")
    print("=" * 60)
    
    # Configurar agente
    try:
        agent = MobilityDashboardAgent(
            dashboard_url=os.getenv("DASHBOARD_URL", "https://fastapi.urbanmt.com.br"),
            openai_api_key=os.getenv("OPENAI_API_KEY")
        )
        print("✅ Agente configurado com sucesso!")
    except Exception as e:
        print(f"❌ Erro ao configurar agente: {e}")
        return
    
    # Menu interativo
    while True:
        print("\n🎯 ESCOLHA UMA ANÁLISE:")
        print("1. 📊 Análise Completa de Performance")
        print("2. 💰 Avaliação de Saúde Financeira")
        print("3. 👥 Análise de Performance dos Motoristas")
        print("4. 🌍 Análise de Expansão Geográfica")
        print("5. 📈 Tendências e Projeções de Mercado")
        print("6. 📋 Relatório Executivo Completo")
        print("7. 🤔 Pergunta Específica (Modo Interativo)")
        print("8. 🚪 Sair")
        
        escolha = input("\nDigite sua escolha (1-8): ").strip()
        
        try:
            if escolha == "1":
                print("\n📊 EXECUTANDO ANÁLISE COMPLETA...")
                resultado = agent.analyze_overall_performance()
                print("\n" + "="*80)
                print(resultado)
                
            elif escolha == "2":
                print("\n💰 AVALIANDO SAÚDE FINANCEIRA...")
                resultado = agent.financial_health_assessment()
                print("\n" + "="*80)
                print(resultado)
                
            elif escolha == "3":
                print("\n👥 ANALISANDO PERFORMANCE DOS MOTORISTAS...")
                resultado = agent.driver_performance_analysis()
                print("\n" + "="*80)
                print(resultado)
                
            elif escolha == "4":
                print("\n🌍 ANALISANDO OPORTUNIDADES DE EXPANSÃO...")
                cidades = input("Cidades específicas (opcional, separadas por vírgula): ").strip()
                cidades_lista = [c.strip() for c in cidades.split(",")] if cidades else None
                resultado = agent.city_expansion_analysis(cidades_lista)
                print("\n" + "="*80)
                print(resultado)
                
            elif escolha == "5":
                print("\n📈 ANALISANDO TENDÊNCIAS DE MERCADO...")
                resultado = agent.market_trends_forecast()
                print("\n" + "="*80)
                print(resultado)
                
            elif escolha == "6":
                print("\n📋 GERANDO RELATÓRIO EXECUTIVO...")
                resultado = agent.generate_executive_report()
                print("\n" + "="*80)
                print(resultado)
                
            elif escolha == "7":
                print("\n🤔 MODO INTERATIVO")
                pergunta = input("Faça sua pergunta sobre o negócio: ").strip()
                if pergunta:
                    print(f"\n🔍 Analisando: {pergunta}")
                    resultado = agent.interactive_analysis(pergunta)
                    print("\n" + "="*80)
                    print(resultado)
                else:
                    print("❌ Pergunta não pode estar vazia!")
                    
            elif escolha == "8":
                print("\n👋 Obrigado por usar o Agente de Mobilidade Urbana!")
                break
                
            else:
                print("❌ Escolha inválida! Digite um número de 1 a 8.")
                continue
                
        except KeyboardInterrupt:
            print("\n\n⏹️ Operação cancelada pelo usuário.")
            continue
        except Exception as e:
            print(f"\n❌ Erro durante a análise: {e}")
            continue
        
        # Aguardar confirmação antes de continuar
        input("\n📌 Pressione ENTER para voltar ao menu...")


def exemplo_rapido():
    """Exemplo rápido para testes"""
    print("🚀 EXEMPLO RÁPIDO - ANÁLISE DE PERFORMANCE")
    
    agent = MobilityDashboardAgent()
    
    # Fazer uma análise rápida
    resultado = agent.interactive_analysis(
        "Qual é o status atual das métricas principais do negócio?"
    )
    
    print("📊 RESULTADO:")
    print(resultado)


if __name__ == "__main__":
    # Verificar se é modo exemplo rápido
    if len(sys.argv) > 1 and sys.argv[1] == "--exemplo":
        exemplo_rapido()
    else:
        main()
