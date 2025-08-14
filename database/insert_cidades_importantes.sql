-- Inserir as 3 cidades importantes na tabela cidades_demografia
INSERT INTO cidades_demografia (
    cidade, 
    populacao_censo_2022, 
    populacao_estimada_2024, 
    densidade_demografica, 
    publico_alvo_15_44_anos, 
    publico_homens, 
    publico_mulheres, 
    created_at
) VALUES
('MATUPA', 15000, 15000, NULL, 6600, NULL, NULL, NOW()),
('PEIXOTO', 12000, 12000, NULL, 5280, NULL, NULL, NOW()),
('GUARANTA DO NORTE', 8000, 8000, NULL, 3520, NULL, NULL, NOW());
