# Plano de Ação — Implementação das Melhorias do Dashboard de Mobilidade Urbana

## 1. Visão Geral ("/")
### 1.1. Bloco de KPIs
- [x] Refatorar o bloco superior para exibir 3 cartões: Corridas Concluídas, Canceladas e Perdidas.
- [x] Implementar filtro global de período (Hoje, Últimos 7 dias, Últimos 30 dias).
- [x] Exibir variação percentual em relação ao período anterior em cada cartão.

### 1.2. Bloco de Atividade Recente
- [x] Criar 3 colunas: Últimas 3 Corridas Concluídas, Canceladas e Perdidas.
- [x] Exibir dados detalhados por corrida conforme especificação.

## 2. Análise de Corridas ("/analise-corridas")
### 2.1. Painel de Filtros
- [ ] Adicionar filtro de período com seleção de datas e atalhos.
- [ ] Implementar filtro por cidade (múltipla seleção).
- [ ] Implementar filtro por motorista e passageiro (autocompletar).

### 2.2. Visualização de Dados
- [ ] Exibir dados filtrados em tabela detalhada (com virtual scroll).
- [ ] Exibir gráficos dinâmicos baseados nos filtros.
- [ ] Implementar função de comparação entre dois períodos distintos (Período A x Período B).
- [ ] Gerar gráfico comparativo entre cidades para a métrica selecionada.

## 3. Motoristas ("/motoristas")
- [ ] Exibir lista de motoristas com nome, cidade principal e tempo total de atividade (HH:MM:SS).
- [ ] Adicionar filtro por cidade.

## 4. Metas por Cidade ("/metas")
### 4.1. CRUD de Metas
- [ ] Implementar interface CRUD para metas (nome, métrica, cidade, valor alvo, período).
- [ ] Permitir criação, edição, visualização e exclusão de metas.

### 4.2. Visualização e Comparativo
- [ ] Exibir tabela/cartões comparando progresso das metas entre cidades.
- [ ] Adicionar barra de progresso visual para cada meta.

## 5. Performance ("/performance")
### 5.1. Resumo de Performance
- [ ] Exibir meta global, realizado global e balanço geral (excedente/déficit).

### 5.2. Análise Comparativa de Cidades
- [ ] Exibir tabela classificando cidades pelo atingimento das metas.
- [ ] Mostrar status visual/textual (Não Atingida, Atingida, Superada).
- [ ] Implementar análise de compensação entre excedentes e déficits das cidades.

---

## Observações Gerais
- Priorizar telas e funcionalidades mais críticas para o negócio.
- Garantir responsividade e boa experiência de usuário.
- Manter documentação e testes atualizados a cada entrega.
- Validar integrações frontend-backend a cada nova feature.

---
