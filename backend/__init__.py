import os
from flask import Flask, send_from_directory, send_file
from flask_cors import CORS
# Import configuration mapping to select proper config by environment
from backend.config.config import config as config_map
from backend.models import db
import logging
def create_app():
    """Factory function para criar a aplicação Flask com base em FLASK_ENV"""
    app = Flask(__name__)
    # Selecionar configuração pelo FLASK_ENV (default para 'default')
    env = os.environ.get('FLASK_ENV', 'default')
    cfg = config_map.get(env, config_map['default'])
    app.config.from_object(cfg)
    
    # Configurar CORS
    CORS(app, resources={
        r"/api/*": {
            "origins": ["http://localhost:3000", "http://127.0.0.1:3000"],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })
    
    # Inicializar extensões
    db.init_app(app)
    
    # Configurar logging
    if not app.debug and not app.testing:
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        )
    
    # Registrar blueprints
    from backend.api.dashboard import bp as dashboard_bp
    app.register_blueprint(dashboard_bp, url_prefix='/api/dashboard')
    
    from backend.api.data_import import bp as import_bp
    app.register_blueprint(import_bp, url_prefix='/api/import')
    
    from backend.api.sync import bp as sync_bp
    app.register_blueprint(sync_bp, url_prefix='/api/sync')
    
    from backend.api.metrics import bp as metrics_bp
    app.register_blueprint(metrics_bp, url_prefix='/api/metrics')
    
    from backend.api.llm import bp as llm_bp
    app.register_blueprint(llm_bp, url_prefix='/api/llm')
    
    # Servir arquivos estáticos do frontend (para produção)
    @app.route('/')
    def serve_frontend():
        """Servir o index.html do frontend"""
        static_dir = os.path.join(app.root_path, '..', 'static')
        return send_file(os.path.join(static_dir, 'index.html'))
    
    @app.route('/<path:path>')
    def serve_static_files(path):
        """Servir arquivos estáticos do frontend"""
        static_dir = os.path.join(app.root_path, '..', 'static')
        try:
            return send_from_directory(static_dir, path)
        except:
            # Se arquivo não encontrado, retornar index.html (SPA behavior)
            return send_file(os.path.join(static_dir, 'index.html'))
    
    # Criar tabelas do banco de dados
    with app.app_context():
        db.create_all()
    
    return app
