-- Criação da tabela cidades_demografia
CREATE TABLE cidades_demografia (
    id SERIAL PRIMARY KEY,
    cidade VARCHAR(100) UNIQUE NOT NULL,
    populacao_censo_2022 INTEGER,
    populacao_estimada_2024 INTEGER,
    densidade_demografica FLOAT,
    publico_alvo_15_44_anos INTEGER,
    publico_homens INTEGER,
    publico_mulheres INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Adição dos novos campos na tabela campanhas
ALTER TABLE campanhas
    ADD COLUMN parte_campanha VARCHAR(20),
    ADD COLUMN tipo_gasto VARCHAR(30),
    ADD COLUMN pagamento_programado DATE,
    ADD COLUMN status_financeiro VARCHAR(20),
    ADD COLUMN meta_percentual_populacao FLOAT,
    ADD COLUMN cidade_id INTEGER,
    ADD CONSTRAINT fk_cidade_id FOREIGN KEY (cidade_id) REFERENCES cidades_demografia(id);
