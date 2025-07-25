# Estrutura das Planilhas Google Sheets

Este documento detalha a estrutura exata que suas planilhas Google Sheets devem seguir para integração com o dashboard.

## 📊 Visão Geral

O sistema requer **2 planilhas principais**:
1. **Planilha de Corridas** - Contém dados de corridas concluídas, canceladas e perdidas
2. **Planilha de Metas** - Contém metas mensais por cidade

## 📋 Planilha 1: Corridas

### Aba "Corridas Concluidas"

**Nome exato da aba**: `Corridas Concluidas`

| Coluna | Nome Exato | Tipo | Exemplo | Descrição |
|--------|------------|------|---------|-----------|
| A | Data | Data | 2025-01-20 | Data da corrida (formato YYYY-MM-DD) |
| B | Nº ID | Texto | 001 | Número identificador único da corrida |
| C | Nome Usuário | Texto | João Silva | Nome completo do usuário |
| D | Tel Usuário | Texto | 11999999999 | Telefone do usuário |
| E | Municipio | Texto | São Paulo | Cidade onde ocorreu a corrida |
| F | Nome Motorista | Texto | Carlos Santos | Nome completo do motorista |

**Exemplo de dados**:
```
Data        | Nº ID | Nome Usuário    | Tel Usuário  | Municipio      | Nome Motorista
2025-01-20  | 001   | João Silva      | 11999999999  | São Paulo      | Carlos Santos
2025-01-20  | 002   | Maria Oliveira  | 11888888888  | Rio de Janeiro | Ana Costa
2025-01-21  | 003   | Pedro Lima      | 11777777777  | São Paulo      | José Ferreira
```

### Aba "Corridas Canceladas"

**Nome exato da aba**: `Corridas Canceladas`

| Coluna | Nome Exato | Tipo | Exemplo | Descrição |
|--------|------------|------|---------|-----------|
| A | Data - CC | Data | 2025-01-20 | Data da corrida cancelada |
| B | Nº ID - CC | Texto | 006 | ID único da corrida cancelada |
| C | Nome Usuario - CC | Texto | Lucia Fernandes | Nome do usuário |
| D | Tel. Usuário - CC | Texto | 11444444444 | Telefone do usuário |
| E | Municipio - CC | Texto | São Paulo | Cidade da corrida |
| F | Nome Motorista - CC | Texto | Paulo Santos | Nome do motorista |
| G | Razão - CC | Texto | Cliente | Quem cancelou (Cliente/Motorista/Sistema) |
| H | Motivo - CC | Texto | Desistência | Motivo específico do cancelamento |

**Exemplo de dados**:
```
Data - CC   | Nº ID - CC | Nome Usuario - CC | Tel. Usuário - CC | Municipio - CC | Nome Motorista - CC | Razão - CC | Motivo - CC
2025-01-20  | 006        | Lucia Fernandes   | 11444444444       | São Paulo      | Paulo Santos        | Cliente    | Desistência
2025-01-21  | 007        | Roberto Costa     | 11333333333       | Rio de Janeiro | Sandra Lima         | Motorista  | Problema no veículo
```

### Aba "Corridas Perdidas"

**Nome exato da aba**: `Corridas Perdidas`

| Coluna | Nome Exato | Tipo | Exemplo | Descrição |
|--------|------------|------|---------|-----------|
| A | Data - CP | Data | 2025-01-20 | Data da corrida perdida |
| B | Nº ID _CP | Texto | 008 | ID único da corrida perdida |
| C | Nome Usuario - CP | Texto | Fernando Silva | Nome do usuário |
| D | Tel. Usuário - CP | Texto | 11222222222 | Telefone do usuário |
| E | Municipio - CP | Texto | São Paulo | Cidade da corrida |
| F | Razão - CP | Texto | Sistema | Categoria da razão da perda |
| G | Motivo - CP | Texto | Falha na conexão | Motivo específico da perda |

**Exemplo de dados**:
```
Data - CP   | Nº ID _CP | Nome Usuario - CP | Tel. Usuário - CP | Municipio - CP | Razão - CP      | Motivo - CP
2025-01-20  | 008       | Fernando Silva    | 11222222222       | São Paulo      | Sistema         | Falha na conexão
2025-01-21  | 009       | Mariana Oliveira  | 11111111111       | Belo Horizonte | Disponibilidade | Sem motoristas na região
```

## 🎯 Planilha 2: Metas

### Aba "Metas"

**Nome exato da aba**: `Metas`

| Coluna | Nome Exato | Tipo | Exemplo | Descrição |
|--------|------------|------|---------|-----------|
| A | Cidade | Texto | São Paulo | Nome da cidade |
| B | Media Corridas Mês | Número | 150 | Média histórica de corridas por mês |
| C | Meta Mês 1 | Número | 200 | Meta para o 1º mês |
| D | Meta Mês 2 | Número | 220 | Meta para o 2º mês |
| E | Meta Mês 3 | Número | 240 | Meta para o 3º mês |
| F | Meta Mês 4 | Número | 260 | Meta para o 4º mês |
| G | Meta Mês 5 | Número | 280 | Meta para o 5º mês |
| H | Meta Mês 6 | Número | 300 | Meta para o 6º mês |

**Exemplo de dados**:
```
Cidade         | Media Corridas Mês | Meta Mês 1 | Meta Mês 2 | Meta Mês 3 | Meta Mês 4 | Meta Mês 5 | Meta Mês 6
São Paulo      | 150                | 200        | 220        | 240        | 260        | 280        | 300
Rio de Janeiro | 100                | 120        | 130        | 140        | 150        | 160        | 170
Belo Horizonte | 80                 | 90         | 95         | 100        | 105        | 110        | 115
```

## 🔧 Configuração no Google Sheets

### 1. Criar as Planilhas

1. **Planilha de Corridas**:
   - Acesse [Google Sheets](https://sheets.google.com)
   - Crie nova planilha
   - Renomeie para "Corridas - [Sua Empresa]"
   - Crie as 3 abas com os nomes exatos

2. **Planilha de Metas**:
   - Crie segunda planilha
   - Renomeie para "Metas - [Sua Empresa]"
   - Crie a aba "Metas"

### 2. Configurar Cabeçalhos

**⚠️ IMPORTANTE**: Os nomes das colunas devem ser **exatamente** como especificado, incluindo:
- Maiúsculas e minúsculas
- Espaços
- Hífens e underscores
- Acentos

### 3. Formatar Dados

#### Datas
- Formato recomendado: `YYYY-MM-DD` (ex: 2025-01-20)
- Aceita também: `DD/MM/YYYY` (ex: 20/01/2025)

#### Números
- Use apenas números (sem formatação de moeda)
- Decimais com ponto (ex: 150.5)

#### Texto
- Evite caracteres especiais desnecessários
- Mantenha consistência na grafia dos nomes

### 4. Permissões

1. **Compartilhar planilhas**:
   - Clique em "Compartilhar" no canto superior direito
   - Adicione o email da conta que será usada para integração
   - Defina permissão como "Visualizador" ou "Editor"

2. **Tornar público** (alternativa):
   - Clique em "Compartilhar" > "Alterar para qualquer pessoa com o link"
   - Defina como "Visualizador"

## 📊 Validação dos Dados

### Verificações Automáticas

O sistema realiza as seguintes validações:

1. **Estrutura das abas**: Verifica se existem as abas necessárias
2. **Cabeçalhos**: Confirma se os nomes das colunas estão corretos
3. **Tipos de dados**: Valida se os dados estão no formato esperado
4. **Dados obrigatórios**: Verifica se campos essenciais não estão vazios

### Indicadores de Problemas

Se houver problemas na estrutura, você verá:
- ❌ Erro na conexão
- ⚠️ Dados incompletos
- 🔄 Usando dados mock (quando não consegue acessar as planilhas)

## 🔍 Exemplos de URLs

### Como obter o ID da planilha

**URL completa**:
```
https://docs.google.com/spreadsheets/d/1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms/edit#gid=0
```

**ID da planilha**:
```
1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms
```

O dashboard aceita tanto a URL completa quanto apenas o ID.

## 🚨 Problemas Comuns

### 1. Nomes de Abas Incorretos
**Problema**: Aba não encontrada
**Solução**: Verificar se o nome está exatamente como especificado

### 2. Cabeçalhos Incorretos
**Problema**: Colunas não reconhecidas
**Solução**: Copiar e colar os nomes exatos das colunas

### 3. Formatos de Data
**Problema**: Datas não são reconhecidas
**Solução**: Usar formato YYYY-MM-DD ou DD/MM/YYYY

### 4. Permissões
**Problema**: Acesso negado
**Solução**: Verificar se a planilha está compartilhada corretamente

### 5. Dados Vazios
**Problema**: Métricas zeradas
**Solução**: Verificar se há dados nas linhas (não apenas cabeçalhos)

## 📈 Dicas de Organização

### 1. Manter Histórico
- Não delete dados antigos
- Use filtros para visualizar períodos específicos
- Mantenha backup regular das planilhas

### 2. Padronização
- Use sempre os mesmos nomes para cidades
- Mantenha padrão nos motivos de cancelamento/perda
- Documente códigos e abreviações

### 3. Atualização
- Atualize dados regularmente
- Configure notificações para lembretes
- Valide dados antes de inserir

## 🔄 Integração com o Dashboard

### Configuração no Sistema

1. Acesse a aba "Configurações" no dashboard
2. Cole as URLs das planilhas nos campos correspondentes
3. Clique em "Testar Conexão"
4. Se bem-sucedido, clique em "Salvar Configuração"

### Frequência de Atualização

- **Automática**: A cada carregamento de página
- **Manual**: Botão "Atualizar" no cabeçalho
- **Cache**: Dados ficam em cache por alguns minutos para performance

---

**📋 Checklist de Configuração**:
- [ ] Planilha de Corridas criada com 3 abas
- [ ] Planilha de Metas criada com 1 aba
- [ ] Cabeçalhos configurados corretamente
- [ ] Dados de exemplo inseridos
- [ ] Permissões configuradas
- [ ] URLs/IDs copiados
- [ ] Teste de conexão realizado
- [ ] Configuração salva no dashboard

**✅ Pronto! Suas planilhas estão configuradas para integração com o dashboard.**

