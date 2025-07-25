import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Configuração base da aplicação"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'asdf#FGSgvasgf$5$WGT_development_key'
    
    # Configurações do Banco PostgreSQL
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'postgresql://dashboard_user:senha_segura@localhost:5432/mobilidade_urbana'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
        'pool_timeout': 30,
        'max_overflow': 20
    }
    
    # Configurações Redis
    REDIS_URL = os.environ.get('REDIS_URL') or 'redis://localhost:6379/0'
    
    # Configurações Google Sheets
    GOOGLE_SHEETS_CREDENTIALS_FILE = os.environ.get('GOOGLE_SHEETS_CREDENTIALS_FILE') or 'config/credentials.json'
    GOOGLE_SHEETS_TOKEN_FILE = os.environ.get('GOOGLE_SHEETS_TOKEN_FILE') or 'config/token.json'
    
    # Configurações CORS
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', 'http://localhost:3000').split(',')
    
    # Configurações de Upload
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER') or 'uploads'
    MAX_CONTENT_LENGTH = int(os.environ.get('MAX_CONTENT_LENGTH', 16777216))  # 16MB
    
    # Configurações de Cache
    CACHE_TYPE = os.environ.get('CACHE_TYPE') or 'redis'
    CACHE_REDIS_URL = os.environ.get('CACHE_REDIS_URL') or 'redis://localhost:6379/1'
    
    # Configurações de Log
    LOG_LEVEL = os.environ.get('LOG_LEVEL') or 'DEBUG'
    LOG_FILE = os.environ.get('LOG_FILE') or 'logs/app.log'

class DevelopmentConfig(Config):
    """Configuração para desenvolvimento"""
    DEBUG = True
    SQLALCHEMY_ECHO = True
    # Usar SQLite em desenvolvimento para evitar dependência de PostgreSQL
    SQLALCHEMY_DATABASE_URI = 'sqlite:///mobilidade_urbana_dev.db'

class ProductionConfig(Config):
    """Configuração para produção"""
    DEBUG = False
    SQLALCHEMY_ECHO = False
    LOG_LEVEL = 'INFO'

class TestingConfig(Config):
    """Configuração para testes"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
