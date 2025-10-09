-- 🗄️ QUERIES DE ANÁLISE - BANCO DE DADOS METAS POR CIDADE
-- Execute estas queries para verificar o estado atual dos dados

-- ========== ANÁLISE DA TABELA: metas_progressivas ==========

-- 1️⃣ Visão geral dos dados
SELECT 
  COUNT(*) as total_registros,
  COUNT(DISTINCT cidade_id) as cidades_com_metas,
  COUNT(DISTINCT fase_id) as fases_distintas,
  MIN(mes) as mes_minimo,
  MAX(mes) as mes_maximo
FROM metas_progressivas;

-- 2️⃣ Verificar registros com dados reais vs. vazios
SELECT 
  COUNT(*) as total_metas,
  SUM(CASE WHEN resultado_corridas > 0 THEN 1 ELSE 0 END) as com_resultados_corridas,
  SUM(CASE WHEN resultado_corridas = 0 OR resultado_corridas IS NULL THEN 1 ELSE 0 END) as sem_resultados_corridas,
  SUM(CASE WHEN resultado_motoristas > 0 THEN 1 ELSE 0 END) as com_resultados_motoristas,
  SUM(CASE WHEN resultado_receita > 0 THEN 1 ELSE 0 END) as com_resultados_receita
FROM metas_progressivas;

-- 3️⃣ Metas por cidade (detalhado)
SELECT 
  cidade_id,
  cidade_nome,
  COUNT(*) as total_metas,
  SUM(CASE WHEN resultado_corridas > 0 THEN 1 ELSE 0 END) as metas_com_dados,
  AVG(meta_corridas) as media_meta_corridas,
  AVG(resultado_corridas) as media_resultado_corridas,
  SUM(CASE WHEN atingida = true THEN 1 ELSE 0 END) as metas_atingidas
FROM metas_progressivas
GROUP BY cidade_id, cidade_nome
ORDER BY cidade_id;

-- 4️⃣ Verificar se há metas sem cidade associada
SELECT COUNT(*) as metas_sem_cidade
FROM metas_progressivas
WHERE cidade_id IS NULL OR cidade_id = 0;

-- 5️⃣ Amostra de dados (5 registros)
SELECT 
  id,
  cidade_nome,
  mes,
  meta_corridas,
  resultado_corridas,
  meta_motoristas,
  resultado_motoristas,
  meta_receita,
  resultado_receita,
  status,
  atingida
FROM metas_progressivas
LIMIT 5;

-- ========== ANÁLISE DA TABELA: fases_planejamento ==========

-- 6️⃣ Listar todas as fases
SELECT 
  id,
  nome,
  status,
  data_inicio,
  data_fim,
  progresso_percentual,
  meta_cidades,
  meta_motoristas,
  meta_corridas,
  orcamento_previsto,
  orcamento_empenhado
FROM fases_planejamento
ORDER BY id;

-- 7️⃣ Verificar se há fases sem datas
SELECT COUNT(*) as fases_sem_datas
FROM fases_planejamento
WHERE data_inicio IS NULL OR data_fim IS NULL;

-- 8️⃣ Fases ativas vs. concluídas
SELECT 
  status,
  COUNT(*) as quantidade,
  AVG(progresso_percentual) as progresso_medio
FROM fases_planejamento
GROUP BY status;

-- ========== ANÁLISE DA TABELA: cidades_demografia ==========

-- 9️⃣ Verificar dados demográficos das cidades
SELECT 
  id,
  cidade,
  populacao_estimada_2024,
  populacao_15_44_anos,
  CASE 
    WHEN populacao_estimada_2024 > 0 
    THEN ROUND((populacao_15_44_anos::numeric / populacao_estimada_2024::numeric) * 100, 2)
    ELSE 0
  END as percentual_publico_alvo
FROM cidades_demografia
ORDER BY populacao_estimada_2024 DESC;

-- 🔟 Cidades sem dados demográficos
SELECT COUNT(*) as cidades_sem_populacao
FROM cidades_demografia
WHERE populacao_estimada_2024 IS NULL OR populacao_estimada_2024 = 0;

-- ========== QUERIES DE INTEGRIDADE ==========

-- 1️⃣1️⃣ Verificar referências quebradas (metas com cidade_id inválido)
SELECT m.id, m.cidade_id, m.cidade_nome
FROM metas_progressivas m
LEFT JOIN cidades_demografia c ON m.cidade_id = c.id
WHERE c.id IS NULL;

-- 1️⃣2️⃣ Verificar referências quebradas (metas com fase_id inválido)
SELECT m.id, m.fase_id
FROM metas_progressivas m
LEFT JOIN fases_planejamento f ON m.fase_id = f.id
WHERE m.fase_id IS NOT NULL AND f.id IS NULL;

-- ========== QUERIES DE RELATÓRIO ==========

-- 1️⃣3️⃣ Relatório consolidado por cidade
SELECT 
  c.cidade,
  c.populacao_estimada_2024,
  c.populacao_15_44_anos,
  COUNT(m.id) as total_metas_cadastradas,
  SUM(m.meta_corridas) as soma_metas_corridas,
  SUM(m.resultado_corridas) as soma_resultados_corridas,
  CASE 
    WHEN SUM(m.meta_corridas) > 0 
    THEN ROUND((SUM(m.resultado_corridas)::numeric / SUM(m.meta_corridas)::numeric) * 100, 2)
    ELSE 0
  END as percentual_atingimento_geral
FROM cidades_demografia c
LEFT JOIN metas_progressivas m ON c.id = m.cidade_id
GROUP BY c.id, c.cidade, c.populacao_estimada_2024, c.populacao_15_44_anos
ORDER BY c.cidade;

-- 1️⃣4️⃣ Identificar cidades SEM metas cadastradas
SELECT 
  c.id,
  c.cidade,
  c.populacao_estimada_2024
FROM cidades_demografia c
LEFT JOIN metas_progressivas m ON c.id = m.cidade_id
WHERE m.id IS NULL
ORDER BY c.cidade;

-- ========== QUERIES PARA POPULAR DADOS ==========

-- 1️⃣5️⃣ Exemplo de INSERT de meta base (ajustar valores conforme necessário)
-- NOTA: NÃO EXECUTAR SEM REVISÃO!

/*
INSERT INTO metas_progressivas (
  cidade_id,
  cidade_nome,
  fase_id,
  mes,
  percentual_publico,
  tipo_meta,
  meta_corridas,
  meta_motoristas,
  meta_receita,
  status
)
SELECT 
  c.id as cidade_id,
  c.cidade as cidade_nome,
  1 as fase_id, -- Ajustar para fase correta
  1 as mes,
  0.5 as percentual_publico,
  'media' as tipo_meta,
  ROUND((c.populacao_15_44_anos * 0.005)::numeric, 0) as meta_corridas,
  GREATEST(1, ROUND((c.populacao_15_44_anos * 0.005 / 25)::numeric, 0)) as meta_motoristas,
  ROUND((c.populacao_15_44_anos * 0.005 * 15.00)::numeric, 2) as meta_receita,
  'ativa' as status
FROM cidades_demografia c
WHERE NOT EXISTS (
  SELECT 1 FROM metas_progressivas m 
  WHERE m.cidade_id = c.id AND m.mes = 1
);
*/

-- ========== RESULTADOS ESPERADOS ==========

/*
📊 CHECKLIST DE VALIDAÇÃO:

Query 1: Total de registros em metas_progressivas
[ ] Total de registros: _______
[ ] Cidades com metas: _______
[ ] Fases distintas: _______

Query 2: Dados reais vs. vazios
[ ] Com resultados de corridas: _______
[ ] Sem resultados de corridas: _______
[ ] % com dados reais: _______%

Query 6: Fases cadastradas
[ ] Fase 1: _______ (status: _______)
[ ] Fase 2: _______ (status: _______)
[ ] Fase 3: _______ (status: _______)

Query 14: Cidades sem metas
[ ] Total de cidades sem metas: _______

🎯 AÇÕES NECESSÁRIAS:
[ ] Popular metas_progressivas se tabela estiver vazia
[ ] Integrar com rides_data para preencher resultado_corridas
[ ] Verificar integridade referencial
[ ] Criar script de migração se necessário
*/
