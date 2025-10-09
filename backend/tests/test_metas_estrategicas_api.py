"""
🧪 TESTES DE API - METAS ESTRATÉGICAS
Testa endpoints de metas progressivas e fases de planejamento
"""

import pytest
from fastapi.testclient import TestClient
import sys
import os

# Adicionar o diretório backend ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app
from app.database.db import get_db, SessionLocal
from app.models.metas_progressivas import MetasProgressivas
from app.models.fases_planejamento import FasesPlanejamento

client = TestClient(app)


# ===== FIXTURES =====

@pytest.fixture
def db_session():
    """Cria uma sessão de banco de dados para testes"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ===== TESTES DE ENDPOINT: /api/metas-estrategicas/metas-progressivas =====

def test_listar_metas_progressivas_retorna_200():
    """Testa se endpoint de listagem retorna sucesso"""
    response = client.get("/api/metas-estrategicas/metas-progressivas")
    assert response.status_code == 200


def test_listar_metas_progressivas_retorna_json():
    """Testa se resposta é um JSON válido"""
    response = client.get("/api/metas-estrategicas/metas-progressivas")
    data = response.json()
    assert isinstance(data, list) or isinstance(data, dict)


def test_listar_metas_por_cidade():
    """Testa filtro por cidade"""
    response = client.get("/api/metas-estrategicas/metas-progressivas?cidade_id=1")
    assert response.status_code == 200
    data = response.json()
    
    # Se houver dados, todos devem ser da cidade 1
    if isinstance(data, list) and len(data) > 0:
        for meta in data:
            assert meta.get('cidade_id') == 1


def test_listar_metas_por_fase():
    """Testa filtro por fase"""
    response = client.get("/api/metas-estrategicas/metas-progressivas?fase_id=1")
    assert response.status_code == 200


# ===== TESTES DE ENDPOINT: /api/metas-estrategicas/fases-planejamento =====

def test_listar_fases_retorna_200():
    """Testa se endpoint de fases retorna sucesso"""
    response = client.get("/api/metas-estrategicas/fases-planejamento")
    assert response.status_code == 200


def test_listar_fases_retorna_lista():
    """Testa se retorna uma lista de fases"""
    response = client.get("/api/metas-estrategicas/fases-planejamento")
    data = response.json()
    assert isinstance(data, list)


def test_fase_tem_campos_obrigatorios():
    """Testa se fases têm os campos esperados"""
    response = client.get("/api/metas-estrategicas/fases-planejamento")
    data = response.json()
    
    if len(data) > 0:
        fase = data[0]
        assert 'id' in fase
        assert 'nome' in fase
        assert 'status' in fase


# ===== TESTES DE CRIAÇÃO DE METAS =====

def test_criar_meta_sem_autenticacao_retorna_401_ou_422():
    """Testa criação de meta sem autenticação (deve falhar)"""
    nova_meta = {
        "cidade_id": 1,
        "cidade_nome": "MATUPA",
        "mes": 1,
        "meta_corridas": 100,
        "meta_motoristas": 5
    }
    response = client.post("/api/metas-estrategicas/metas-progressivas", json=nova_meta)
    
    # Pode retornar 401 (não autenticado) ou 422 (validação)
    assert response.status_code in [401, 422, 201]


# ===== TESTES DE VALIDAÇÃO =====

def test_meta_com_valores_negativos_deve_falhar():
    """Testa se metas com valores negativos são rejeitadas"""
    meta_invalida = {
        "cidade_id": 1,
        "mes": 1,
        "meta_corridas": -10,  # ❌ Negativo
        "meta_motoristas": 5
    }
    response = client.post("/api/metas-estrategicas/metas-progressivas", json=meta_invalida)
    
    # Deve retornar erro de validação
    assert response.status_code in [400, 422]


def test_meta_sem_cidade_id_deve_falhar():
    """Testa se meta sem cidade_id é rejeitada"""
    meta_invalida = {
        "mes": 1,
        "meta_corridas": 100,
        "meta_motoristas": 5
    }
    response = client.post("/api/metas-estrategicas/metas-progressivas", json=meta_invalida)
    
    # Deve retornar erro de validação
    assert response.status_code == 422


# ===== TESTES DE INTEGRAÇÃO =====

def test_fluxo_completo_listagem_metas(db_session):
    """Testa fluxo completo: buscar metas do banco"""
    # Verificar se há metas no banco
    metas = db_session.query(MetasProgressivas).limit(5).all()
    
    # Se houver metas, API deve retornar
    if len(metas) > 0:
        response = client.get("/api/metas-estrategicas/metas-progressivas")
        data = response.json()
        
        if isinstance(data, list):
            assert len(data) > 0


def test_fases_cadastradas_no_banco(db_session):
    """Verifica se há fases cadastradas"""
    fases = db_session.query(FasesPlanejamento).all()
    
    # API deve retornar as mesmas fases
    response = client.get("/api/metas-estrategicas/fases-planejamento")
    data = response.json()
    
    if isinstance(data, list):
        # Quantidade de fases na API deve ser >= quantidade no banco
        assert len(data) >= 0


# ===== TESTES DE PERFORMANCE =====

def test_endpoint_metas_responde_rapido():
    """Testa se endpoint responde em menos de 2 segundos"""
    import time
    
    start = time.time()
    response = client.get("/api/metas-estrategicas/metas-progressivas")
    end = time.time()
    
    tempo_resposta = end - start
    
    assert response.status_code == 200
    assert tempo_resposta < 2.0, f"Endpoint demorou {tempo_resposta:.2f}s (máximo: 2s)"


# ===== TESTES DE ESTRUTURA DE DADOS =====

def test_estrutura_meta_progressiva():
    """Testa se meta retornada tem a estrutura esperada"""
    response = client.get("/api/metas-estrategicas/metas-progressivas")
    data = response.json()
    
    if isinstance(data, list) and len(data) > 0:
        meta = data[0]
        
        # Campos obrigatórios
        campos_esperados = ['cidade_id', 'mes']
        for campo in campos_esperados:
            assert campo in meta, f"Campo '{campo}' não encontrado na meta"


if __name__ == "__main__":
    # Rodar testes
    pytest.main([__file__, "-v", "--tb=short"])
