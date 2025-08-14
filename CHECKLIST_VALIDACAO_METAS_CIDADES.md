# ✅ CHECKLIST DE VALIDAÇÃO: MetasCidades.jsx

**Data:** 14-15 de Agosto de 2025  
**Objetivo:** Validar funcionamento completo do dashboard dinâmico  
**Status:** 🎯 EM TESTE

---

## 📋 **VALIDAÇÃO DOS DADOS**

### **🔍 1. APIs FUNCIONANDO**
- [ ] **Backend rodando**: `http://localhost:8000/health` responde OK
- [ ] **Frontend rodando**: Interface carrega sem erros
- [ ] **API Campanhas**: `/api/dashboard-executivo/campanhas` retorna 31 campanhas
- [ ] **API Cidades**: `/api/cidades` retorna dados demográficos
- [ ] **API Corridas**: `/api/metrics/overview` funciona por cidade
- [ ] **API Motoristas**: `/api/drivers/by-city` funciona por cidade

### **🔍 2. DADOS DINÂMICOS CARREGANDO**
- [ ] **Plano dinâmico**: `buildPlanoDinamico()` gera fases automaticamente
- [ ] **Cidades reais**: 7 da API + 3 garantidas = 10 total
- [ ] **Campanhas por fase**: Fase 1, Fase 2, Fase 3 com campanhas corretas
- [ ] **KPIs calculados**: Orçamento, cidades, fases ativas dinâmicos

### **🔍 3. CRUZAMENTO DE DADOS**
- [ ] **MATUPA**: Mostra 22 corridas + 19 motoristas ativos
- [ ] **PEIXOTO**: Mostra 57 corridas + dados de motoristas
- [ ] **GUARANTA DO NORTE**: Mostra 9 corridas + dados de motoristas
- [ ] **Outras cidades**: Mostram dados das campanhas
- [ ] **Penetração calculada**: % baseado em público-alvo real

---

## 📋 **VALIDAÇÃO DA INTERFACE**

### **🔍 4. TABELA DE EXECUÇÃO**
- [ ] **Colunas corretas**: Cidade/Fase, Demografia, Motoristas, Corridas, Orçamento, Status
- [ ] **Dados reais**: Números não zerados para as 3 cidades principais
- [ ] **Barras de progresso**: Funcionando com % real de execução
- [ ] **Status dinâmico**: "X% concluído" baseado em dados reais
- [ ] **Botões ação**: Editar e Apagar funcionando

### **🔍 5. CARDS DE STATUS DAS FASES**
- [ ] **Fase 1**: Status "Em Execução", cidades corretas, metas calculadas
- [ ] **Fase 2**: Status correto baseado na data atual
- [ ] **Fase 3**: Status "Planejada", dados das campanhas
- [ ] **Orçamentos**: Valores dinâmicos das campanhas, não hardcoded

### **🔍 6. KPIs RESUMO**
- [ ] **Orçamento Total**: Soma real das 31 campanhas
- [ ] **Já Pago**: 60% do empenhado (cálculo dinâmico)
- [ ] **Cidades no Plano**: Conta cidades únicas das campanhas
- [ ] **Fases Ativas**: Baseado em datas e status real

---

## 📋 **VALIDAÇÃO DO CRUD**

### **🔍 7. FORMULÁRIO "NOVA META"**
- [ ] **Abre modal**: Botão "Nova Meta" funciona
- [ ] **4 steps**: Cidade → Metas → Fases → Resumo
- [ ] **Dados das cidades**: Dropdowns com cidades reais da API
- [ ] **Validação**: Campos obrigatórios funcionando
- [ ] **Preview**: Cálculos dinâmicos (CAC, receita estimada)

### **🔍 8. EDIÇÃO DE CAMPANHAS**
- [ ] **Botão editar**: Abre modal com dados pré-preenchidos
- [ ] **Dados carregados**: Informações da campanha selecionada
- [ ] **Salvamento**: PUT para `/api/campanhas/{id}` funciona
- [ ] **Atualização**: Interface recarrega dados após edição

### **🔍 9. EXCLUSÃO DE CAMPANHAS**
- [ ] **Botão apagar**: Abre modal de confirmação
- [ ] **Confirmação**: DELETE para `/api/campanhas/{id}` funciona
- [ ] **Atualização**: Campanha removida da lista
- [ ] **Recálculo**: KPIs atualizados após exclusão

---

## 📋 **TESTES DE CENÁRIOS**

### **🔍 10. CENÁRIOS DE ERRO**
- [ ] **API offline**: Frontend mostra fallback adequado
- [ ] **Dados incompletos**: Não quebra a interface
- [ ] **Cidade sem dados**: Mostra "0" em vez de erro
- [ ] **Conexão lenta**: Loading states funcionando

### **🔍 11. CENÁRIOS DE SUCESSO**
- [ ] **Cidade com dados**: MATUPA mostra todos os valores corretos
- [ ] **Nova campanha**: Formulário salva e aparece na tabela
- [ ] **Edição**: Mudanças refletem imediatamente
- [ ] **Filtros**: Interface responsiva a mudanças de dados

---

## 🎯 **PRÓXIMAS AÇÕES BASEADAS NOS RESULTADOS**

### **✅ SE TUDO FUNCIONAR:**
- Marcar Fase 2 como concluída
- Partir para Fase 3: Melhorias e features avançadas
- Documentar o sistema finalizado

### **⚠️ SE HOUVER PROBLEMAS:**
- Identificar e corrigir bugs específicos
- Ajustar mapeamento de dados
- Refinar cálculos dinâmicos

---

## 📝 **REGISTRO DE TESTES**

**Data/Hora:** ___________  
**Testado por:** ___________  

**Resultado geral:** [ ] ✅ Passou | [ ] ⚠️ Problemas menores | [ ] ❌ Problemas críticos

**Observações:**
```
_______________________________________________________________
_______________________________________________________________
_______________________________________________________________
```

**Próximos passos identificados:**
```
_______________________________________________________________
_______________________________________________________________
_______________________________________________________________
```
