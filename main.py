#!/usr/bin/env python3
"""
Dashboard de Mobilidade Urbana - Aplicação Principal
Sistema completo de dashboard com múltiplas fontes de dados
"""

import os
import sys
from datetime import datetime
from backend import create_app
from backend import create_app
from app.api import anomaly
from backend.models import db
from backend.services.sync_service import DataSyncService

# Configurar caminho para importações
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def setup_database():
    """Configura o banco de dados inicial"""
    print("Configurando banco de dados...")
    
    try:
        with app.app_context():
            # Criar todas as tabelas
            db.create_all()
            
            # Executar schema SQL se existir (apenas em modo de desenvolvimento)
            schema_path = os.path.join(os.path.dirname(__file__), 'database', 'schema.sql')
            if os.path.exists(schema_path):
                with open(schema_path, 'r', encoding='utf-8') as f:
                    sql_commands = f.read()
                
                # Executar comandos SQL (dividir por ';' e executar individualmente)
                commands = [cmd.strip() for cmd in sql_commands.split(';') if cmd.strip()]
                for command in commands:
                    try:
                        from sqlalchemy import text
                        db.session.execute(text(command))
                    except Exception as e:
                        # Ignorar erros de tabelas já existentes ou comandos PostgreSQL no SQLite
                        if not any(ignore in str(e).lower() for ignore in [
                            'already exists', 'no such function', 'syntax error', 
                            'near "create"', 'no such extension'
                        ]):
                            print(f"Aviso SQL: {e}")
                
                try:
                    db.session.commit()
                    print("Schema SQL aplicado")
                except Exception:
                    db.session.rollback()
        
        print("Banco de dados configurado")
        return True
        
    except Exception as e:
        print(f"Erro ao configurar banco de dados: {e}")
        return False

def sync_initial_data():
    """Sincroniza dados iniciais se necessário"""
    print("Verificando dados...")
    
    try:
        with app.app_context():
            sync_service = DataSyncService()
            
            # Verificar se já existem dados
            from backend.models import Corrida
            corridas_count = db.session.query(Corrida).count()
            
            if corridas_count == 0:
                print("Executando sincronização inicial...")
                result = sync_service.sync_all_data(force=True)
                
                if result['success']:
                    print("Dados sincronizados")
                else:
                    print(f"Dados mock criados")
            else:
                print(f"{corridas_count} corridas encontradas")
        
        return True
        
    except Exception as e:
        print(f"Usando dados mock: {e}")
        return True  # Não falhar por causa da sincronização

def run_development_server():
    """Executa o servidor de desenvolvimento"""
    print("\n" + "="*50)
    print("SERVIDOR INICIADO COM SUCESSO!")
    print("="*50)
    print("Backend API: http://localhost:5000")
    print("Frontend UI: http://localhost:5000")
    print("Dashboard: http://localhost:5000")
    print("Chat LLM: http://localhost:5000 (botão chat)")
    print("="*50)
    print("Pressione Ctrl+C para parar")
    print("Modo: DESENVOLVIMENTO")
    print("="*50)
    
    # Configurar logs menos verbosos em desenvolvimento
    import logging
    logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)
    
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True,
        use_reloader=True
    )

def run_production_server():
    """Executa o servidor de produção"""
    try:
        import gunicorn
        print("Iniciando servidor de produção com Gunicorn...")
        print("Aplicação disponível em: http://localhost:5000")
        os.system("gunicorn -w 4 -b 0.0.0.0:5000 'main:app'")
    except ImportError:
        print("Gunicorn não instalado. Executando em modo desenvolvimento...")
        run_development_server()

def show_help():
    """Mostra ajuda de uso"""
    print("""
Dashboard de Mobilidade Urbana

COMANDOS:
    python main.py                     - Executar aplicação completa (padrão)
    python main.py --production        - Executar em modo produção
    python main.py --setup-db          - Configurar apenas o banco
    python main.py --sync              - Sincronizar dados
    python main.py --help              - Mostrar esta ajuda

APLICAÇÃO:
    Interface Completa: http://localhost:5000
    Dashboard de métricas com gráficos interativos
    Chat LLM inteligente integrado
    Sistema de importação de dados
    
ENDPOINTS DA API:
    GET  /api/dashboard/overview       - Overview geral
    GET  /api/dashboard/municipios     - Lista de municípios
    GET  /api/dashboard/metricas-diarias - Métricas por dia
    POST /api/llm/chat                 - Chat com LLM
    POST /api/import/upload            - Upload de planilhas
    GET  /api/health                   - Status da aplicação

DOCUMENTAÇÃO:
    README.md                       - Guia completo
    Dashboard de Métricas.md        - Especificações
    Guia de Instalação.md           - Setup detalhado
    """)

if __name__ == '__main__':
    # Configurar logging mais limpo
    import logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(levelname)s: %(message)s'
    )
    
    print("=" * 60)
    print("DASHBOARD DE MOBILIDADE URBANA")
    print("=" * 60)
    
    # Criar aplicação
    app = create_app()
    app.include_router(anomaly.router, prefix="/api/anomaly", tags=["anomaly"])
    
    # Adicionar health check endpoint
    @app.route('/api/health')
    def health_check():
        """Health check para monitoramento"""
        try:
            with app.app_context():
                from sqlalchemy import text
                db.session.execute(text('SELECT 1'))
            return {"status": "healthy", "timestamp": datetime.now().isoformat(), "version": "1.0.0", "database": "connected"}, 200
        except Exception as e:
            return {
                'status': 'unhealthy',
                'timestamp': datetime.now().isoformat(),
                'error': str(e)
            }, 503
    
    # Servir frontend integrado
    @app.route('/')
    def serve_index():
        """Serve a interface principal"""
        static_dir = os.path.join(os.path.dirname(__file__), 'static')
        if os.path.exists(os.path.join(static_dir, 'index.html')):
            # Removido: send_from_directory (Flask)
            return "Index.html (static)"
        else:
            # Fallback para index.html na raiz
            # Removido: send_file (Flask)
            return "Index.html (file)"
    
    @app.route('/<path:path>')
    def serve_static(path):
        """Serve arquivos estáticos"""
        static_dir = os.path.join(os.path.dirname(__file__), 'static')
        try:
            # Removido: send_from_directory (Flask)
            return f"Arquivo estático: {path}"
        except FileNotFoundError:
            # SPA routing - sempre retorna index.html
            try:
                # Removido: send_from_directory (Flask)
                return "Index.html (static)"
            except FileNotFoundError:
                # Removido: send_file (Flask)
                return "Index.html (file)"
    
    # Verificar argumentos de linha de comando
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command in ['help', '--help', '-h']:
            show_help()
            sys.exit(0)
        elif command in ['setup-db', '--setup-db']:
            if setup_database():
                print("Configuração concluída!")
            else:
                print("❌ Falha na configuração!")
                sys.exit(1)
            sys.exit(0)
        elif command in ['sync-data', '--sync']:
            if setup_database():
                sync_initial_data()
                print("Sincronização concluída!")
            else:
                print("❌ Falha na configuração!")
                sys.exit(1)
            sys.exit(0)
        elif command in ['production', '--production']:
            print("Modo: PRODUÇÃO")
            if setup_database() and sync_initial_data():
                run_production_server()
            else:
                print("❌ Falha na configuração de produção!")
                sys.exit(1)
        else:
            print(f"❌ Comando desconhecido: {command}")
            print("💡 Use 'python main.py --help' para ver comandos disponíveis")
            sys.exit(1)
    
    # Inicializar aplicação padrão (desenvolvimento)
    print("🚀 Iniciando aplicação em modo desenvolvimento...")
    if setup_database():
        sync_initial_data()
        print("✅ Sistema pronto! Aplicação rodando...")
    else:
        print("❌ Falha na configuração do banco!")
        sys.exit(1)
        print("Modo: DESENVOLVIMENTO")
        if setup_database() and sync_initial_data():
            run_development_server()
        else:
            sys.exit(1)
