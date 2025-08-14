-- Exemplo de inserção de campanhas alinhadas com os documentos de planejamento
-- Para cada campanha, buscamos o cidade_id correspondente

-- FASE 1 (Monte Verde, Nova Bandeirantes)
INSERT INTO campanhas (
    nome, fase, parte_campanha, tipo_campanha, tipo_gasto, meta_quantidade, meta_percentual_populacao, orcamento_previsto, status, cidade_id, data_inicio, data_fim, created_at
) VALUES
('Campanha Motoristas Monte Verde', 'Fase 1', 'Part 1', 'aquisição_motoristas', 'operacoes', 4, NULL, 2030, 'ativa', (SELECT id FROM cidades_demografia WHERE cidade = 'Monte Verde'), '2025-08-01', '2025-09-15', NOW()),
('Campanha Corridas Monte Verde', 'Fase 1', 'Part 2', 'aquisição_corridas', 'trafego_pago', 20, 0.5, 2030, 'ativa', (SELECT id FROM cidades_demografia WHERE cidade = 'Monte Verde'), '2025-08-01', '2025-09-15', NOW()),
('Campanha Motoristas Nova Bandeirantes', 'Fase 1', 'Part 1', 'aquisição_motoristas', 'operacoes', 6, NULL, 2030, 'ativa', (SELECT id FROM cidades_demografia WHERE cidade = 'Nova Bandeirantes'), '2025-08-01', '2025-09-15', NOW()),
('Campanha Corridas Nova Bandeirantes', 'Fase 1', 'Part 2', 'aquisição_corridas', 'trafego_pago', 30, 0.5, 2030, 'ativa', (SELECT id FROM cidades_demografia WHERE cidade = 'Nova Bandeirantes'), '2025-08-01', '2025-09-15', NOW());

-- FASE 2 (Alta Floresta, Paranaíta)
INSERT INTO campanhas (
    nome, fase, parte_campanha, tipo_campanha, tipo_gasto, meta_quantidade, meta_percentual_populacao, orcamento_previsto, status, cidade_id, data_inicio, data_fim, created_at
) VALUES
('Campanha Motoristas Alta Floresta', 'Fase 2', 'Part 1', 'aquisição_motoristas', 'operacoes', 8, NULL, 3350, 'ativa', (SELECT id FROM cidades_demografia WHERE cidade = 'Alta Floresta'), '2025-09-01', '2025-10-15', NOW()),
('Campanha Corridas Alta Floresta', 'Fase 2', 'Part 2', 'aquisição_corridas', 'trafego_pago', 20, 0.5, 3350, 'ativa', (SELECT id FROM cidades_demografia WHERE cidade = 'Alta Floresta'), '2025-09-01', '2025-10-15', NOW()),
('Campanha Motoristas Paranaíta', 'Fase 2', 'Part 1', 'aquisição_motoristas', 'operacoes', 4, NULL, 3350, 'ativa', (SELECT id FROM cidades_demografia WHERE cidade = 'Paranaíta'), '2025-09-01', '2025-10-15', NOW()),
('Campanha Corridas Paranaíta', 'Fase 2', 'Part 2', 'aquisição_corridas', 'trafego_pago', 30, 0.5, 3350, 'ativa', (SELECT id FROM cidades_demografia WHERE cidade = 'Paranaíta'), '2025-09-01', '2025-10-15', NOW());

-- FASE 3 (Colíder, Nova Canaã do Norte, Carlinda)
INSERT INTO campanhas (
    nome, fase, parte_campanha, tipo_campanha, tipo_gasto, meta_quantidade, meta_percentual_populacao, orcamento_previsto, status, cidade_id, data_inicio, data_fim, created_at
) VALUES
('Campanha Motoristas Colíder', 'Fase 3', 'Part 1', 'aquisição_motoristas', 'operacoes', 6, NULL, 3010, 'ativa', (SELECT id FROM cidades_demografia WHERE cidade = 'Colíder'), '2025-11-01', '2025-12-15', NOW()),
('Campanha Corridas Colíder', 'Fase 3', 'Part 2', 'aquisição_corridas', 'trafego_pago', 50, 0.5, 3010, 'ativa', (SELECT id FROM cidades_demografia WHERE cidade = 'Colíder'), '2025-11-01', '2025-12-15', NOW()),
('Campanha Motoristas Nova Canaã do Norte', 'Fase 3', 'Part 1', 'aquisição_motoristas', 'operacoes', 5, NULL, 3010, 'ativa', (SELECT id FROM cidades_demografia WHERE cidade = 'Nova Canaã do Norte'), '2025-11-01', '2025-12-15', NOW()),
('Campanha Corridas Nova Canaã do Norte', 'Fase 3', 'Part 2', 'aquisição_corridas', 'trafego_pago', 30, 0.5, 3010, 'ativa', (SELECT id FROM cidades_demografia WHERE cidade = 'Nova Canaã do Norte'), '2025-11-01', '2025-12-15', NOW()),
('Campanha Motoristas Carlinda', 'Fase 3', 'Part 1', 'aquisição_motoristas', 'operacoes', 4, NULL, 3010, 'ativa', (SELECT id FROM cidades_demografia WHERE cidade = 'Carlinda'), '2025-11-01', '2025-12-15', NOW()),
('Campanha Corridas Carlinda', 'Fase 3', 'Part 2', 'aquisição_corridas', 'trafego_pago', 30, 0.5, 3010, 'ativa', (SELECT id FROM cidades_demografia WHERE cidade = 'Carlinda'), '2025-11-01', '2025-12-15', NOW());

-- Observação: Ajuste os valores de orcamento_previsto, meta_percentual_populacao e outros campos conforme detalhamento real dos documentos.
