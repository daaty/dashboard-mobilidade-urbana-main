-- Popula a tabela cidades_demografia com os dados das 7 cidades principais
-- Ajuste os valores de densidade, homens e mulheres conforme dados oficiais se necessário

INSERT INTO cidades_demografia (
    cidade, populacao_censo_2022, populacao_estimada_2024, densidade_demografica, publico_alvo_15_44_anos, publico_homens, publico_mulheres, created_at
) VALUES
('Colíder', 32010, 32010, NULL, 14045, NULL, NULL, NOW()),
('Alta Floresta', 61291, 61291, NULL, 27522, NULL, NULL, NOW()),
('Nova Canaã do Norte', 11771, 11771, NULL, 5091, NULL, NULL, NOW()),
('Carlinda', 10324, 10324, NULL, 4171, NULL, NULL, NOW()),
('Paranaíta', 11989, 11989, NULL, 5032, NULL, NULL, NOW()),
('Monte Verde', 8451, 8451, NULL, 3844, NULL, NULL, NOW()),
('Nova Bandeirantes', 14160, 14160, NULL, 6115, NULL, NULL, NOW());

-- Observação: Complete os campos de densidade_demografica, publico_homens e publico_mulheres se tiver os dados detalhados.
