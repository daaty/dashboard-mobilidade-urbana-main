# 🚗 Dashboard de Mobilidade Urbana

Um dashboard moderno e interativo para análise de dados de mobilidade urbana, desenvolvido com React + Vite e Flask.

## ✨ Funcionalidades

### 📊 **Gráficos Avançados**
- Gráficos interativos com Recharts
- Visualizações em tempo real
- Múltiplos tipos: linha, área, barra, pizza, radial
- Responsivo e animado

### 📈 **Métricas Principais**
- Corridas concluídas
- Receita total com formatação brasileira
- Motoristas ativos
- Avaliação média
- Comparações temporais

### 🎛️ **Páginas e Funcionalidades**
- **Visão Geral**: Overview com métricas principais
- **Performance**: Análise detalhada de desempenho
- **Análises Avançadas**: Gráficos interativos
- **Sistema de Alertas**: Notificações em tempo real
- **Importação de Dados**: Upload de arquivos
- **Análise de Corridas**: Relatórios detalhados
- **Gestão de Motoristas**: Controle de condutores
- **Metas por Cidade**: Configuração de objetivos
- **Comparativo Temporal**: Análises históricas
- **Configurações**: Personalização do sistema

### 🔔 **Sistema de Notificações**
- Alertas em tempo real
- Contador de notificações não lidas
- Interface interativa

## 🛠️ Tecnologias Utilizadas

### Frontend
- **React 18+** - Biblioteca de interface
- **Vite** - Build tool rápido
- **Framer Motion** - Animações suaves
- **Recharts** - Gráficos profissionais
- **Lucide React** - Ícones modernos
- **Tailwind CSS** - Estilização utility-first

### Backend
- **Flask** - Framework Python
- **Google Sheets API** - Integração com planilhas
- **RESTful API** - Endpoints organizados

## 🚀 Instalação e Execução

### **🏠 Desenvolvimento Local**

#### Pré-requisitos
- Node.js 16+
- Python 3.8+
- npm ou yarn

#### Frontend
```bash
# Instalar dependências
npm install

# Executar em desenvolvimento
npm run dev

# Build para produção
npm run build
```

#### Backend
```bash
# Instalar dependências Python
pip install -r backend/requirements.txt

# Executar servidor FastAPI (Uvicorn)
cd backend
python -m uvicorn main:app --reload
<<<<<<< HEAD
```
=======
>>>>>>> b79eb8c1fab2d681c0f2e542b205b8cb7e099b4f

### **� Deploy com Docker (Easypanel)**

#### Deploy Rápido
```bash
# Tornar script executável e executar
chmod +x deploy_easypanel.sh
./deploy_easypanel.sh
```

#### Deploy Manual
```bash
# Build da imagem
docker build -t dashboard-mobilidade-urbana .

# Executar container
docker run -p 8080:8080 \
  -e FLASK_ENV=production \
  -e DATABASE_URL=postgresql://user:pass@host:5432/db \
  dashboard-mobilidade-urbana
```

📋 **Guia completo**: Ver [`DEPLOY_EASYPANEL.md`](DEPLOY_EASYPANEL.md)

## 📱 Acesso
- **Desenvolvimento**: http://localhost:3000 (frontend) + http://localhost:5000 (backend)
- **Produção**: URL fornecida pelo Easypanel

## 📁 Estrutura do Projeto

```
dashboard-mobilidade-urbana/
├── src/
│   ├── components/
│   │   ├── GraficosAvancados.jsx
│   │   ├── ResumoPerformance.jsx
│   │   ├── SistemaNotificacoes.jsx
│   │   └── ...
│   ├── App.jsx
│   └── main.jsx
├── public/
├── backend/
│   ├── main.py
│   ├── google_sheets_service.py
│   └── dashboard.py
└── package.json
```

## 🎨 Características do Design

- **Interface Moderna**: Design clean e profissional
- **Responsivo**: Funciona em desktop, tablet e mobile
- **Animações Suaves**: Transições com Framer Motion
- **Paleta de Cores**: Azul, verde, roxo, amarelo
- **Tipografia**: Hierarquia clara e legível
- **UX Intuitiva**: Navegação simples e eficiente

## 📊 Dados e API

- **Fetch Inteligente**: Tenta backend real, fallback para mock
- **Dados Mock**: Valores realistas para desenvolvimento
- **Formatação BR**: Moeda, números e datas em português
- **Atualização Dinâmica**: Dados atualizados automaticamente

## 🔧 Configuração

### Variáveis de Ambiente
```env
VITE_API_URL=http://localhost:5000
GOOGLE_SHEETS_CREDENTIALS=path/to/credentials.json
```

### Proxy de Desenvolvimento
O Vite está configurado para fazer proxy das requisições `/api/*` para `http://localhost:5000`.

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch (`git checkout -b feature/nova-funcionalidade`)
3. Commit suas mudanças (`git commit -m 'Adiciona nova funcionalidade'`)
4. Push para a branch (`git push origin feature/nova-funcionalidade`)
5. Abra um Pull Request

## 📝 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

## 🎯 Roadmap

- [ ] Integração com APIs reais de transporte
- [ ] Sistema de autenticação
- [ ] Relatórios em PDF
- [ ] Dashboard mobile nativo
- [ ] Integração com mapas
- [ ] Análise preditiva com IA
- [ ] Sistema de backup automático

## 📞 Contato

**Desenvolvido com ❤️ para análise de mobilidade urbana**

---

### 🌟 Status do Projeto
**✅ Em produção** - Dashboard funcional com gráficos interativos e interface completa
