"""
🎯 INICIALIZAÇÃO RÁPIDA DO AGENTE
Script para configurar e testar o agente rapidamente
"""

import os
import sys
from pathlib import Path

def verificar_dependencias():
    """Verifica se todas as dependências estão instaladas"""
    dependencias = [
        ('agno', 'agno'),
        ('openai', 'openai'),
        ('dotenv', 'python-dotenv'),
        ('requests', 'requests'),
        ('pandas', 'pandas'),
        ('numpy', 'numpy')
    ]
    
    print("🔍 Verificando dependências...")
    faltando = []
    
    for modulo, pacote in dependencias:
        try:
            __import__(modulo)
            print(f"✅ {pacote}")
        except ImportError:
            print(f"❌ {pacote}")
            faltando.append(pacote)
    
    if faltando:
        print(f"\n⚠️ Dependências faltando: {', '.join(faltando)}")
        print("Execute: pip install " + " ".join(faltando))
        return False
    
    print("✅ Todas as dependências estão instaladas!")
    return True


def verificar_configuracao():
    """Verifica se a configuração está correta"""
    print("\n🔧 Verificando configuração...")
    
    # Verificar arquivo .env
    env_file = Path(".env")
    if not env_file.exists():
        print("⚠️ Arquivo .env não encontrado!")
        print("📋 Criando arquivo .env de exemplo...")
        
        # Copiar .env.example para .env
        example_file = Path(".env.example")
        if example_file.exists():
            with open(example_file, 'r') as f:
                content = f.read()
            with open(env_file, 'w') as f:
                f.write(content)
            print("✅ Arquivo .env criado! Configure sua OPENAI_API_KEY")
        else:
            print("❌ Arquivo .env.example não encontrado!")
        return False
    
    # Verificar variáveis essenciais
    from dotenv import load_dotenv
    load_dotenv()
    
    openai_key = os.getenv("OPENAI_API_KEY")
    dashboard_url = os.getenv("DASHBOARD_URL")
    memory_db_url = os.getenv("MEMORY_DB_URL")
    
    if not openai_key or openai_key == "sua_chave_openai_aqui":
        print("❌ OPENAI_API_KEY não configurada!")
        print("📝 Configure sua chave no arquivo .env")
        return False
    
    print(f"✅ OPENAI_API_KEY configurada")
    print(f"✅ DASHBOARD_URL: {dashboard_url}")
    
    if memory_db_url:
        print(f"✅ MEMORY_DB_URL: {memory_db_url[:50]}...")
        
        # Verificar se tabelas de memória existem
        resposta = input("🗄️ Deseja verificar/criar tabelas de memória? (s/n): ").strip().lower()
        if resposta in ['s', 'sim', 'y', 'yes']:
            try:
                from init_memory import verificar_tabelas, criar_tabelas_agente
                
                if not verificar_tabelas():
                    print("📊 Criando tabelas de memória...")
                    criar_tabelas_agente()
                else:
                    print("✅ Tabelas de memória já existem")
            except Exception as e:
                print(f"⚠️ Erro ao configurar memória: {e}")
    else:
        print("⚠️ MEMORY_DB_URL não configurada (modo sem memória)")
    
    return True


def testar_conectividade():
    """Testa conectividade com APIs"""
    print("\n🌐 Testando conectividade...")
    
    # Testar dashboard
    import requests
    dashboard_url = os.getenv("DASHBOARD_URL", "https://fastapi.urbanmt.com.br")
    
    try:
        response = requests.get(f"{dashboard_url}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Dashboard acessível")
        else:
            print(f"⚠️ Dashboard retornou status {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Dashboard não acessível: {e}")
        print("💡 Certifique-se que o backend está rodando")
    
    # Testar OpenAI (rápido)
    try:
        from openai import OpenAI
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        # Teste simples
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Teste"}],
            max_tokens=1
        )
        print("✅ OpenAI API funcionando")
    except Exception as e:
        print(f"❌ Erro na OpenAI API: {e}")


def executar_teste_agente():
    """Executa um teste rápido do agente"""
    print("\n🤖 Testando agente...")
    
    try:
        from mobility_agent import MobilityDashboardAgent
        
        agent = MobilityDashboardAgent(
            dashboard_url=os.getenv("DASHBOARD_URL", "https://fastapi.urbanmt.com.br"),
            openai_api_key=os.getenv("OPENAI_API_KEY")
        )
        
        print("✅ Agente criado com sucesso!")
        
        # Teste rápido
        print("🔍 Executando teste de reasoning...")
        resultado = agent.interactive_analysis("Qual é o status atual do sistema?")
        
        if resultado:
            print("✅ Agente funcionando corretamente!")
            print("📊 Exemplo de resposta:")
            print(resultado[:200] + "..." if len(resultado) > 200 else resultado)
        else:
            print("⚠️ Agente não retornou resposta")
            
    except Exception as e:
        print(f"❌ Erro ao testar agente: {e}")


def main():
    """Função principal de inicialização"""
    print("🚀 INICIALIZAÇÃO DO AGENTE DE MOBILIDADE URBANA")
    print("=" * 60)
    
    # Passo 1: Verificar dependências
    if not verificar_dependencias():
        return
    
    # Passo 2: Verificar configuração
    if not verificar_configuracao():
        return
    
    # Passo 3: Testar conectividade
    testar_conectividade()
    
    # Passo 4: Testar agente
    resposta = input("\n🤖 Deseja testar o agente? (s/n): ").strip().lower()
    if resposta in ['s', 'sim', 'y', 'yes']:
        executar_teste_agente()
    
    print("\n🎯 INICIALIZAÇÃO CONCLUÍDA!")
    print("💡 Execute 'python exemplo_uso.py' para usar o agente")
    print("📚 Consulte README.md para mais informações")


if __name__ == "__main__":
    main()
