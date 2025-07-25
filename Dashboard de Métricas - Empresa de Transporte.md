# Dashboard de Métricas - Empresa de Transporte

Um dashboard interativo desenvolvido em React com backend Flask para acompanhar métricas de corridas, integrado ao Google Sheets para atualização em tempo real.

## 🚀 Características Principais

- **Interface Moderna**: Design responsivo com tema preto, branco e cinza
- **Visualizações Interativas**: Gráficos de pizza, barras e linhas com animações
- **Integração Google Sheets**: Conexão direta com suas planilhas para dados em tempo real
- **Sistema de Abas**: Organização clara das diferentes visualizações
- **Indicadores Visuais**: Sistema de cores para status de metas (verde/amarelo/vermelho)
- **Responsivo**: Funciona perfeitamente em desktop e mobile

## 📊 Funcionalidades

### 1. Visão Geral
- Cards com métricas principais (corridas concluídas, canceladas, perdidas)
- Percentuais e tendências
- Resumo rápido com taxas de sucesso

### 2. Metas por Cidade
- Barras de progresso para cada cidade
- Indicadores visuais de status das metas
- Comparativo realizado vs. meta mensal

### 3. Análise de Corridas
- Gráficos de pizza para motivos de cancelamento e perda
- Gráfico comparativo de barras
- Estatísticas detalhadas por categoria

### 4. Comparativo Temporal
- Análises por últimos 7 dias, 4 semanas ou 6 meses
- Gráficos de linha, área e barras
- Médias e totais por período

### 5. Configurações
- Interface para configurar IDs das planilhas Google Sheets
- Teste de conexão
- Documentação da estrutura das planilhas

## 🛠️ Tecnologias Utilizadas

### Backend
- **Flask**: Framework web Python
- **Google Sheets API**: Integração com planilhas
- **Flask-CORS**: Suporte a requisições cross-origin
- **Pandas**: Manipulação de dados

### Frontend
- **React**: Biblioteca JavaScript para UI
- **Vite**: Build tool e servidor de desenvolvimento
- **Tailwind CSS**: Framework CSS utilitário
- **Recharts**: Biblioteca de gráficos
- **Framer Motion**: Animações e transições
- **Lucide React**: Ícones modernos
- **shadcn/ui**: Componentes de interface

## 📁 Estrutura do Projeto

```
dashboard_transporte/
├── backend/
│   └── dashboard_api/
│       ├── src/
│       │   ├── routes/
│       │   │   └── dashboard.py
│       │   ├── services/
│       │   │   └── google_sheets_service.py
│       │   └── main.py
│       ├── venv/
│       └── requirements.txt
├── frontend/
│   └── dashboard-ui/
│       ├── src/
│       │   ├── components/
│       │   │   ├── ui/
│       │   │   ├── Header.jsx
│       │   │   ├── Sidebar.jsx
│       │   │   ├── MetricsOverview.jsx
│       │   │   ├── MetasCidades.jsx
│       │   │   ├── AnaliseCorreidas.jsx
│       │   │   ├── ComparativoTemporal.jsx
│       │   │   └── ConfiguracaoSheets.jsx
│       │   ├── App.jsx
│       │   └── main.jsx
│       ├── package.json
│       └── vite.config.js
└── README.md
```

## 🚀 Instalação e Configuração

### Pré-requisitos
- Python 3.11+
- Node.js 20+
- pnpm (ou npm)

### 1. Configuração do Backend

```bash
# Navegar para o diretório do backend
cd dashboard_transporte/backend/dashboard_api

# Ativar ambiente virtual
source venv/bin/activate

# Instalar dependências (já instaladas)
pip install -r requirements.txt

# Iniciar servidor Flask
python src/main.py
```

O backend estará disponível em `http://localhost:5003`

### 2. Configuração do Frontend

```bash
# Navegar para o diretório do frontend
cd dashboard_transporte/frontend/dashboard-ui

# Instalar dependências (já instaladas)
pnpm install

# Iniciar servidor de desenvolvimento
pnpm run dev --host
```

O frontend estará disponível em `http://localhost:5173`

## 📋 Configuração das Planilhas Google Sheets

### Estrutura Necessária

#### Planilha 1 - Corridas
Deve conter as seguintes abas:

**Aba "Corridas Concluidas":**
- Data
- Nº ID
- Nome Usuário
- Tel Usuário
- Municipio
- Nome Motorista

**Aba "Corridas Canceladas":**
- Data - CC
- Nº ID - CC
- Nome Usuario - CC
- Tel. Usuário - CC
- Municipio - CC
- Nome Motorista - CC
- Razão - CC
- Motivo - CC

**Aba "Corridas Perdidas":**
- Data - CP
- Nº ID _CP
- Nome Usuario - CP
- Tel. Usuário - CP
- Municipio - CP
- Razão - CP
- Motivo - CP

#### Planilha 2 - Metas
Deve conter a seguinte aba:

**Aba "Metas":**
- Cidade
- Media Corridas Mês
- Meta Mês 1
- Meta Mês 2
- Meta Mês 3
- Meta Mês 4
- Meta Mês 5
- Meta Mês 6

### Como Configurar

1. Acesse a aba "Configurações" no dashboard
2. Cole as URLs completas das suas planilhas Google Sheets
3. O sistema extrairá automaticamente os IDs das planilhas
4. Clique em "Testar Conexão" para verificar
5. Clique em "Salvar Configuração" para persistir as configurações

## 🎨 Personalização

### Cores da Empresa
O dashboard utiliza um esquema de cores em preto, branco e cinza:
- **Preto**: Elementos principais e navegação ativa
- **Branco**: Fundo e texto principal
- **Cinza**: Elementos secundários e bordas
- **Verde**: Indicadores de sucesso e metas atingidas
- **Amarelo**: Avisos e próximo da meta
- **Vermelho**: Alertas e abaixo da meta

### Indicadores de Status
- 🟢 **Verde**: Meta atingida (≥100%)
- 🟡 **Amarelo**: Próximo da meta (≥80%)
- 🔴 **Vermelho**: Abaixo da meta (<80%)

## 🔧 Manutenção

### Atualizando Dados
- Os dados são atualizados automaticamente a cada carregamento
- Use o botão "Atualizar" no cabeçalho para forçar atualização
- O sistema utiliza dados mock quando as credenciais do Google Sheets não estão configuradas

### Logs e Debug
- Logs do backend: `dashboard_transporte/backend/dashboard_api/flask.log`
- Console do navegador para debug do frontend
- Modo debug ativado por padrão no desenvolvimento

## 📱 Responsividade

O dashboard é totalmente responsivo e se adapta a diferentes tamanhos de tela:
- **Desktop**: Layout completo com sidebar expandida
- **Tablet**: Sidebar colapsável
- **Mobile**: Navegação otimizada para toque

## 🚀 Deploy em Produção

### Backend
Para produção, recomenda-se usar um servidor WSGI como Gunicorn:

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5003 src.main:app
```

### Frontend
Para build de produção:

```bash
pnpm run build
```

Os arquivos estarão na pasta `dist/` prontos para deploy.

## 🤝 Suporte

Para dúvidas ou problemas:
1. Verifique os logs do backend e console do navegador
2. Confirme se as planilhas seguem a estrutura correta
3. Teste a conectividade com as APIs do Google Sheets

## 📄 Licença

Este projeto foi desenvolvido especificamente para sua empresa de transporte.

---

**Desenvolvido com ❤️ para otimizar o acompanhamento de métricas da sua empresa de transporte.**

