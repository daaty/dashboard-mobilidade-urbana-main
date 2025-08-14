from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
import os
from dotenv import load_dotenv

# Garante que o .env seja carregado
load_dotenv()

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://n8n_user:n8n_pw@148.230.73.27:5432/n8n_db"
)

# Adiciona pool_pre_ping para evitar conexões fechadas
engine = create_async_engine(
    DATABASE_URL,
    echo=True,
    future=True,
    pool_pre_ping=True,
    connect_args={
        "server_settings": {
            "client_encoding": "utf8"
        }
    }
)
SessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
Base = declarative_base()

# Adiciona função get_db síncrona para uso em endpoints que usam SQLAlchemy síncrono
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker as sync_sessionmaker

SYNC_DATABASE_URL = os.getenv(
    "SYNC_DATABASE_URL",
    "postgresql://n8n_user:n8n_pw@148.230.73.27:5432/n8n_db"
)
sync_engine = create_engine(
    SYNC_DATABASE_URL, 
    pool_pre_ping=True,
    connect_args={
        "client_encoding": "utf8",
        "options": "-c timezone=UTC"
    }
)
SyncSessionLocal = sync_sessionmaker(autocommit=False, autoflush=False, bind=sync_engine)

def get_db():
    db = SyncSessionLocal()
    try:
        yield db
    finally:
        db.close()
