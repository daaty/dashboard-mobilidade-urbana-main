CREATE TABLE IF NOT EXISTS campanhas (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    fase VARCHAR(20) NOT NULL,
    cidade VARCHAR(50) NOT NULL,
    data_inicio DATE NOT NULL,
    data_fim DATE NOT NULL,
    tipo_campanha VARCHAR(50) NOT NULL,
    meta_quantidade INTEGER NOT NULL,
    orcamento_previsto DECIMAL(10,2) NOT NULL,
    custo_real DECIMAL(10,2) DEFAULT 0,
    status VARCHAR(20) DEFAULT 'ativa',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
