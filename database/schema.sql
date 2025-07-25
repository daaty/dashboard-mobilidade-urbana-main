-- Schema para Dashboard de Mobilidade Urbana
-- PostgreSQL 15+

-- Criar database (executar como superuser)
-- CREATE DATABASE mobilidade_urbana;
-- CREATE USER dashboard_user WITH PASSWORD 'senha_segura';
-- GRANT ALL PRIVILEGES ON DATABASE mobilidade_urbana TO dashboard_user;

-- Conectar ao database mobilidade_urbana

-- Criar extensões necessárias
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Enum types
CREATE TYPE status_corrida AS ENUM ('concluida', 'cancelada', 'perdida');
CREATE TYPE status_motorista AS ENUM ('ativo', 'inativo', 'bloqueado');
CREATE TYPE origem_dado AS ENUM ('postgres', 'sheets', 'import');

-- Tabela de motoristas
CREATE TABLE motoristas (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    telefone VARCHAR(20) UNIQUE,
    municipio VARCHAR(50) NOT NULL,
    status status_motorista NOT NULL DEFAULT 'ativo',
    data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    total_corridas INTEGER DEFAULT 0,
    avaliacao_media FLOAT,
    ultima_corrida TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de corridas
CREATE TABLE corridas (
    id SERIAL PRIMARY KEY,
    data TIMESTAMP NOT NULL,
    usuario_nome VARCHAR(100) NOT NULL,
    usuario_telefone VARCHAR(20),
    motorista_nome VARCHAR(100) NOT NULL,
    municipio VARCHAR(50) NOT NULL,
    status status_corrida NOT NULL,
    valor DECIMAL(10,2),
    distancia FLOAT,
    tempo_corrida INTEGER,  -- em minutos
    avaliacao INTEGER CHECK (avaliacao >= 1 AND avaliacao <= 5),
    motivo_cancelamento VARCHAR(100),
    origem_dado origem_dado NOT NULL DEFAULT 'postgres',
    motorista_id INTEGER REFERENCES motoristas(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de metas
CREATE TABLE metas (
    id SERIAL PRIMARY KEY,
    municipio VARCHAR(50) NOT NULL,
    mes DATE NOT NULL,
    meta_corridas INTEGER NOT NULL,
    meta_receita DECIMAL(10,2),
    meta_motoristas INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(municipio, mes)
);

-- Tabela de métricas diárias consolidadas
CREATE TABLE metricas_diarias (
    id SERIAL PRIMARY KEY,
    data DATE NOT NULL,
    municipio VARCHAR(50) NOT NULL,
    corridas_concluidas INTEGER DEFAULT 0,
    corridas_canceladas INTEGER DEFAULT 0,
    corridas_perdidas INTEGER DEFAULT 0,
    receita_total DECIMAL(10,2) DEFAULT 0,
    motoristas_ativos INTEGER DEFAULT 0,
    avaliacao_media FLOAT,
    tempo_medio_corrida FLOAT,
    distancia_media FLOAT,
    total_corridas INTEGER DEFAULT 0,
    taxa_conclusao FLOAT,
    ticket_medio DECIMAL(10,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(data, municipio)
);

-- Tabela de log de importações
CREATE TABLE import_logs (
    id SERIAL PRIMARY KEY,
    filename VARCHAR(255) NOT NULL,
    file_size INTEGER,
    total_rows INTEGER,
    success_rows INTEGER,
    error_rows INTEGER,
    import_type VARCHAR(50),
    status VARCHAR(20),
    error_message TEXT,
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP
);

-- Índices para performance
CREATE INDEX idx_corridas_data ON corridas(data);
CREATE INDEX idx_corridas_municipio ON corridas(municipio);
CREATE INDEX idx_corridas_status ON corridas(status);
CREATE INDEX idx_corridas_motorista_id ON corridas(motorista_id);
CREATE INDEX idx_corridas_data_municipio ON corridas(data, municipio);

CREATE INDEX idx_motoristas_municipio ON motoristas(municipio);
CREATE INDEX idx_motoristas_status ON motoristas(status);
CREATE INDEX idx_motoristas_telefone ON motoristas(telefone);

CREATE INDEX idx_metas_municipio ON metas(municipio);
CREATE INDEX idx_metas_mes ON metas(mes);

CREATE INDEX idx_metricas_data ON metricas_diarias(data);
CREATE INDEX idx_metricas_municipio ON metricas_diarias(municipio);
CREATE INDEX idx_metricas_data_municipio ON metricas_diarias(data, municipio);

-- Índices de texto para busca
CREATE INDEX idx_motoristas_nome_gin ON motoristas USING gin(nome gin_trgm_ops);
CREATE INDEX idx_corridas_usuario_gin ON corridas USING gin(usuario_nome gin_trgm_ops);

-- Function para atualizar updated_at automaticamente
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers para updated_at
CREATE TRIGGER update_motoristas_updated_at 
    BEFORE UPDATE ON motoristas 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_corridas_updated_at 
    BEFORE UPDATE ON corridas 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_metas_updated_at 
    BEFORE UPDATE ON metas 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_metricas_updated_at 
    BEFORE UPDATE ON metricas_diarias 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Function para calcular métricas diárias
CREATE OR REPLACE FUNCTION calcular_metricas_diarias()
RETURNS TRIGGER AS $$
BEGIN
    -- Recalcular métricas para a data e município da corrida inserida/atualizada
    INSERT INTO metricas_diarias (
        data, municipio, 
        corridas_concluidas, corridas_canceladas, corridas_perdidas,
        receita_total, avaliacao_media, tempo_medio_corrida, distancia_media,
        total_corridas, taxa_conclusao, ticket_medio,
        motoristas_ativos
    )
    SELECT 
        DATE(NEW.data) as data,
        NEW.municipio,
        COUNT(*) FILTER (WHERE status = 'concluida') as corridas_concluidas,
        COUNT(*) FILTER (WHERE status = 'cancelada') as corridas_canceladas,
        COUNT(*) FILTER (WHERE status = 'perdida') as corridas_perdidas,
        COALESCE(SUM(valor) FILTER (WHERE status = 'concluida'), 0) as receita_total,
        AVG(avaliacao) FILTER (WHERE avaliacao IS NOT NULL) as avaliacao_media,
        AVG(tempo_corrida) FILTER (WHERE tempo_corrida IS NOT NULL) as tempo_medio_corrida,
        AVG(distancia) FILTER (WHERE distancia IS NOT NULL) as distancia_media,
        COUNT(*) as total_corridas,
        ROUND((COUNT(*) FILTER (WHERE status = 'concluida') * 100.0 / COUNT(*)), 2) as taxa_conclusao,
        CASE 
            WHEN COUNT(*) FILTER (WHERE status = 'concluida') > 0 
            THEN SUM(valor) FILTER (WHERE status = 'concluida') / COUNT(*) FILTER (WHERE status = 'concluida')
            ELSE 0 
        END as ticket_medio,
        COUNT(DISTINCT motorista_nome) as motoristas_ativos
    FROM corridas 
    WHERE DATE(data) = DATE(NEW.data) AND municipio = NEW.municipio
    ON CONFLICT (data, municipio) 
    DO UPDATE SET
        corridas_concluidas = EXCLUDED.corridas_concluidas,
        corridas_canceladas = EXCLUDED.corridas_canceladas,
        corridas_perdidas = EXCLUDED.corridas_perdidas,
        receita_total = EXCLUDED.receita_total,
        avaliacao_media = EXCLUDED.avaliacao_media,
        tempo_medio_corrida = EXCLUDED.tempo_medio_corrida,
        distancia_media = EXCLUDED.distancia_media,
        total_corridas = EXCLUDED.total_corridas,
        taxa_conclusao = EXCLUDED.taxa_conclusao,
        ticket_medio = EXCLUDED.ticket_medio,
        motoristas_ativos = EXCLUDED.motoristas_ativos,
        updated_at = CURRENT_TIMESTAMP;
    
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Trigger para calcular métricas automaticamente
CREATE TRIGGER trigger_calcular_metricas_diarias
    AFTER INSERT OR UPDATE ON corridas
    FOR EACH ROW EXECUTE FUNCTION calcular_metricas_diarias();

-- Inserir dados de exemplo para teste
INSERT INTO motoristas (nome, telefone, municipio) VALUES
('João Silva', '11999999999', 'São Paulo'),
('Maria Santos', '11888888888', 'Rio de Janeiro'),
('Pedro Oliveira', '11777777777', 'São Paulo'),
('Ana Costa', '11666666666', 'Belo Horizonte'),
('Carlos Ferreira', '11555555555', 'São Paulo');

INSERT INTO metas (municipio, mes, meta_corridas, meta_receita, meta_motoristas) VALUES
('São Paulo', '2025-01-01', 1000, 25000.00, 10),
('Rio de Janeiro', '2025-01-01', 800, 20000.00, 8),
('Belo Horizonte', '2025-01-01', 600, 15000.00, 6);

-- Inserir algumas corridas de exemplo
INSERT INTO corridas (data, usuario_nome, usuario_telefone, motorista_nome, municipio, status, valor, distancia, tempo_corrida, avaliacao, motorista_id) VALUES
('2025-01-20 10:30:00', 'Cliente 1', '11123456789', 'João Silva', 'São Paulo', 'concluida', 18.50, 12.5, 25, 5, 1),
('2025-01-20 11:15:00', 'Cliente 2', '11234567890', 'Maria Santos', 'Rio de Janeiro', 'concluida', 22.00, 15.2, 30, 4, 2),
('2025-01-20 12:00:00', 'Cliente 3', '11345678901', 'Pedro Oliveira', 'São Paulo', 'cancelada', NULL, NULL, NULL, NULL, 3),
('2025-01-20 14:30:00', 'Cliente 4', '11456789012', 'Ana Costa', 'Belo Horizonte', 'concluida', 15.75, 8.3, 20, 5, 4),
('2025-01-20 16:45:00', 'Cliente 5', '11567890123', 'Carlos Ferreira', 'São Paulo', 'concluida', 28.90, 18.7, 35, 4, 5);

-- Verificar se os dados foram inseridos corretamente
SELECT 'Motoristas' as tabela, COUNT(*) as registros FROM motoristas
UNION ALL
SELECT 'Corridas', COUNT(*) FROM corridas
UNION ALL
SELECT 'Metas', COUNT(*) FROM metas
UNION ALL
SELECT 'Métricas Diárias', COUNT(*) FROM metricas_diarias;
