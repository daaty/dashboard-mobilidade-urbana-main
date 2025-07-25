# 📊 PLANO DE AÇÃO - Dashboard de Mobilidade Urbana

## 🎯 **OBJETIVO**
Desenvolver uma dashboard completa para empresa de mobilidade urbana com múltiplas fontes de dados (PostgreSQL, Google Sheets e planilhas importadas), funcao de exportar para planilhas em XLS CSV, interface moderna e métricas avançadas para gestão empresarial.

---

## 📋 **ANÁLISE DO PROJETO ATUAL**

### **✅ O que já temos:**
- ✅ **Backend Flask** com integração Google Sheets funcional
- ✅ **Componentes React** desenvolvidos (Sidebar, Header, Métricas, etc.)
- ✅ **Estrutura de dados** bem definida para planilhas Google Sheets
- ✅ **Sistema de rotas** configurado no Flask
- ✅ **Documentação** completa da estrutura das planilhas
- ✅ **Serviço Google Sheets** implementado

### **❌ O que está faltando:**
- ❌ **Configuração do ambiente React** (package.json, dependências)
- ❌ **Integração com PostgreSQL**
- ❌ **Sistema de importação de planilhas locais**
- ❌ **Gráficos e visualizações interativas**
- ❌ **Build e deploy do projeto**
- ❌ **Interface moderna e responsiva**

---

## 🚀 **PLANO DE AÇÃO DETALHADO**

### **FASE 1: Configuração do Ambiente e Estrutura Base** 
**⏱️ Duração: 1-2 dias**

#### 1.1 Configurar Ambiente React
```bash
# Criar package.json e instalar dependências principais
npm init -y
npm install react@18 react-dom@18 react-router-dom@6
npm install @vitejs/plugin-react vite
npm install framer-motion lucide-react
npm install recharts chart.js react-chartjs-2
npm install axios date-fns clsx
npm install @headlessui/react @heroicons/react
```

#### 1.2 Configurar Ambiente Python Backend
```bash
# Dependências Python
pip install flask flask-cors pandas psycopg2-binary sqlalchemy
pip install google-auth google-auth-oauthlib google-auth-httplib2
pip install google-api-python-client openpyxl xlrd python-dotenv
pip install flask-sqlalchemy flask-migrate alembic
```

#### 1.3 Estrutura de Diretórios
```
projeto/
├── backend/
│   ├── app.py (main.py renomeado)
│   ├── config/
│   ├── models/
│   ├── services/
│   ├── routes/
│   └── migrations/
├── frontend/
│   ├── src/
│   ├── public/
│   ├── package.json
│   └── vite.config.js
├── database/
│   └── schema.sql
└── docs/
```

#### 1.4 Configuração PostgreSQL
```sql
-- Criar database
CREATE DATABASE mobilidade_urbana;

-- Configurar usuário
CREATE USER dashboard_user WITH PASSWORD 'senha_segura';
GRANT ALL PRIVILEGES ON DATABASE mobilidade_urbana TO dashboard_user;
```

---

### **FASE 2: Implementação do Sistema de Dados Multi-fonte**
**⏱️ Duração: 3-4 dias**

#### 2.1 Modelagem PostgreSQL
```python
# Tabelas principais:
class Corrida(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.DateTime, nullable=False)
    usuario_nome = db.Column(db.String(100))
    usuario_telefone = db.Column(db.String(20))
    motorista_nome = db.Column(db.String(100))
    municipio = db.Column(db.String(50))
    status = db.Column(db.Enum('concluida', 'cancelada', 'perdida'))
    valor = db.Column(db.Decimal(10,2))
    distancia = db.Column(db.Float)
    tempo_corrida = db.Column(db.Integer)  # em minutos
    avaliacao = db.Column(db.Integer)  # 1-5 estrelas
    motivo_cancelamento = db.Column(db.String(100))
    origem_dado = db.Column(db.String(20))  # 'postgres', 'sheets', 'import'

class Meta(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    municipio = db.Column(db.String(50))
    mes = db.Column(db.Date)
    meta_corridas = db.Column(db.Integer)
    meta_receita = db.Column(db.Decimal(10,2))
    meta_motoristas = db.Column(db.Integer)

class Motorista(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100))
    telefone = db.Column(db.String(20))
    municipio = db.Column(db.String(50))
    status = db.Column(db.Enum('ativo', 'inativo', 'bloqueado'))
    data_cadastro = db.Column(db.DateTime)
    total_corridas = db.Column(db.Integer, default=0)
    avaliacao_media = db.Column(db.Float)

class MetricaDiaria(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.Date)
    municipio = db.Column(db.String(50))
    corridas_concluidas = db.Column(db.Integer)
    corridas_canceladas = db.Column(db.Integer)
    corridas_perdidas = db.Column(db.Integer)
    receita_total = db.Column(db.Decimal(10,2))
    motoristas_ativos = db.Column(db.Integer)
```

#### 2.2 Sistema de Importação de Planilhas
```python
# Serviço de importação
class ImportService:
    def __init__(self):
        self.supported_formats = ['.xlsx', '.xls', '.csv']
    
    def validate_file(self, file_path):
        # Validar formato e estrutura
        pass
    
    def import_corridas(self, file_path, mapping_config):
        # Importar corridas com mapeamento de colunas
        pass
    
    def preview_import(self, file_path):
        # Preview dos dados antes da importação
        pass

# Endpoints para upload
@app.route('/api/import/upload', methods=['POST'])
def upload_file():
    # Endpoint para upload de arquivos
    pass

@app.route('/api/import/preview', methods=['POST'])
def preview_import():
    # Preview dos dados
    pass

@app.route('/api/import/confirm', methods=['POST'])
def confirm_import():
    # Confirmar importação
    pass
```

#### 2.3 Sincronização Multi-fonte
```python
class DataSyncService:
    def __init__(self):
        self.priority_order = ['postgres', 'import', 'sheets']
    
    def sync_all_sources(self):
        # Sincronizar todas as fontes
        # Prioridade: PostgreSQL > Planilhas Importadas > Google Sheets
        pass
    
    def get_consolidated_data(self, data_type, filters):
        # Consolidar dados de múltiplas fontes
        pass
```

---

### **FASE 3: Dashboard Completo com Visualizações Avançadas**
**⏱️ Duração: 4-5 dias**

#### 3.1 Métricas e KPIs Principais
```jsx
// Cards de KPIs principais
const kpis = [
  {
    title: "Total de Corridas",
    value: "1,234",
    period: "Hoje",
    change: "+12%",
    trend: "up",
    icon: "Car"
  },
  {
    title: "Taxa de Conclusão",
    value: "87.5%",
    period: "Este mês",
    change: "+3.2%",
    trend: "up",
    icon: "CheckCircle"
  },
  {
    title: "Receita Total",
    value: "R$ 45.678",
    period: "Este mês",
    change: "+15.4%",
    trend: "up",
    icon: "DollarSign"
  },
  {
    title: "Ticket Médio",
    value: "R$ 18.50",
    period: "Últimos 30 dias",
    change: "-2.1%",
    trend: "down",
    icon: "TrendingUp"
  },
  {
    title: "Motoristas Ativos",
    value: "67",
    period: "Hoje",
    change: "+5",
    trend: "up",
    icon: "Users"
  },
  {
    title: "Tempo Médio",
    value: "23 min",
    period: "Última semana",
    change: "-1.5 min",
    trend: "up",
    icon: "Clock"
  },
  {
    title: "Avaliação Média",
    value: "4.7",
    period: "Últimos 30 dias",
    change: "+0.2",
    trend: "up",
    icon: "Star"
  },
  {
    title: "Cancelamentos",
    value: "8.3%",
    period: "Este mês",
    change: "-1.7%",
    trend: "up",
    icon: "XCircle"
  }
]
```

#### 3.2 Gráficos Interativos (Recharts)
```jsx
// 1. Gráfico de Linha: Evolução de corridas
<LineChart data={corridasEvolution}>
  <XAxis dataKey="data" />
  <YAxis />
  <CartesianGrid strokeDasharray="3 3" />
  <Tooltip />
  <Legend />
  <Line type="monotone" dataKey="concluidas" stroke="#28a745" strokeWidth={3} />
  <Line type="monotone" dataKey="canceladas" stroke="#dc3545" strokeWidth={2} />
</LineChart>

// 2. Gráfico de Barras: Corridas por cidade
<BarChart data={corridasPorCidade}>
  <XAxis dataKey="cidade" />
  <YAxis />
  <Tooltip />
  <Bar dataKey="corridas" fill="#667eea" />
  <Bar dataKey="meta" fill="#764ba2" />
</BarChart>

// 3. Gráfico de Pizza: Status das corridas
<PieChart>
  <Pie
    data={statusData}
    cx="50%"
    cy="50%"
    labelLine={false}
    label={renderCustomizedLabel}
    outerRadius={80}
    fill="#8884d8"
    dataKey="value"
  >
    {statusData.map((entry, index) => (
      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
    ))}
  </Pie>
  <Tooltip />
</PieChart>

// 4. Heatmap: Corridas por horário/dia
<ResponsiveContainer width="100%" height={300}>
  <ScatterChart data={heatmapData}>
    <XAxis dataKey="hora" />
    <YAxis dataKey="dia" />
    <ZAxis dataKey="corridas" range={[60, 400]} />
    <Tooltip cursor={{ strokeDasharray: '3 3' }} />
    <Scatter dataKey="corridas" fill="#8884d8" />
  </ScatterChart>
</ResponsiveContainer>

// 5. Gauge Chart: Progresso de metas
<RadialBarChart cx="50%" cy="50%" innerRadius="60%" outerRadius="90%" data={metaData}>
  <RadialBar minAngle={15} label={{ position: 'insideStart', fill: '#fff' }} background clockWise dataKey="percentage" />
</RadialBarChart>

// 6. Gráfico de Área: Receita acumulada
<AreaChart data={receitaData}>
  <defs>
    <linearGradient id="colorReceita" x1="0" y1="0" x2="0" y2="1">
      <stop offset="5%" stopColor="#667eea" stopOpacity={0.8}/>
      <stop offset="95%" stopColor="#667eea" stopOpacity={0}/>
    </linearGradient>
  </defs>
  <XAxis dataKey="data" />
  <YAxis />
  <CartesianGrid strokeDasharray="3 3" />
  <Tooltip />
  <Area type="monotone" dataKey="receita" stroke="#667eea" fillOpacity={1} fill="url(#colorReceita)" />
</AreaChart>
```

#### 3.3 Filtros e Interatividade
```jsx
// Componente de filtros avançados
const FilterPanel = () => {
  const [filters, setFilters] = useState({
    dateRange: 'today', // today, week, month, custom
    cities: [],
    drivers: [],
    status: 'all'
  });

  const filterOptions = {
    dateRanges: [
      { value: 'today', label: 'Hoje' },
      { value: 'yesterday', label: 'Ontem' },
      { value: 'week', label: 'Esta semana' },
      { value: 'month', label: 'Este mês' },
      { value: 'quarter', label: 'Este trimestre' },
      { value: 'year', label: 'Este ano' },
      { value: 'custom', label: 'Personalizado' }
    ],
    comparisons: [
      { value: 'previous_period', label: 'Período anterior' },
      { value: 'same_period_last_year', label: 'Mesmo período ano passado' }
    ]
  };

  return (
    <div className="filter-panel">
      {/* Filtros de data */}
      {/* Filtros de cidade */}
      {/* Filtros de motorista */}
      {/* Botões de ação */}
    </div>
  );
};
```

---

### **FASE 4: Interface Moderna e Responsiva**
**⏱️ Duração: 2-3 dias**

#### 4.1 Design System
```css
/* styles/variables.css */
:root {
  /* Cores principais */
  --color-primary: #1a1a1a;
  --color-primary-light: #2d2d2d;
  --color-secondary: #f8f9fa;
  --color-secondary-dark: #e9ecef;
  --color-accent: #6c757d;
  
  /* Cores de status */
  --color-success: #28a745;
  --color-success-light: #d4edda;
  --color-warning: #ffc107;
  --color-warning-light: #fff3cd;
  --color-danger: #dc3545;
  --color-danger-light: #f8d7da;
  --color-info: #17a2b8;
  --color-info-light: #d1ecf1;
  
  /* Gradientes */
  --gradient-primary: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  --gradient-success: linear-gradient(135deg, #28a745 0%, #20c997 100%);
  --gradient-warning: linear-gradient(135deg, #ffc107 0%, #fd7e14 100%);
  --gradient-danger: linear-gradient(135deg, #dc3545 0%, #e83e8c 100%);
  
  /* Sombras */
  --shadow-sm: 0 1px 3px rgba(0, 0, 0, 0.12), 0 1px 2px rgba(0, 0, 0, 0.24);
  --shadow-md: 0 4px 6px rgba(0, 0, 0, 0.12), 0 2px 4px rgba(0, 0, 0, 0.08);
  --shadow-lg: 0 10px 15px rgba(0, 0, 0, 0.12), 0 4px 6px rgba(0, 0, 0, 0.08);
  --shadow-xl: 0 20px 25px rgba(0, 0, 0, 0.15), 0 10px 10px rgba(0, 0, 0, 0.04);
  
  /* Transições */
  --transition-fast: 0.15s ease-out;
  --transition-base: 0.3s ease-out;
  --transition-slow: 0.5s ease-out;
  
  /* Tipografia */
  --font-family-sans: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  --font-family-mono: 'JetBrains Mono', Consolas, 'Liberation Mono', Menlo, monospace;
  
  /* Tamanhos */
  --text-xs: 0.75rem;
  --text-sm: 0.875rem;
  --text-base: 1rem;
  --text-lg: 1.125rem;
  --text-xl: 1.25rem;
  --text-2xl: 1.5rem;
  --text-3xl: 1.875rem;
  --text-4xl: 2.25rem;
  
  /* Espaçamentos */
  --space-1: 0.25rem;
  --space-2: 0.5rem;
  --space-3: 0.75rem;
  --space-4: 1rem;
  --space-5: 1.25rem;
  --space-6: 1.5rem;
  --space-8: 2rem;
  --space-10: 2.5rem;
  --space-12: 3rem;
  --space-16: 4rem;
  --space-20: 5rem;
  
  /* Raios de borda */
  --radius-sm: 0.125rem;
  --radius-base: 0.25rem;
  --radius-md: 0.375rem;
  --radius-lg: 0.5rem;
  --radius-xl: 0.75rem;
  --radius-2xl: 1rem;
  --radius-full: 9999px;
}

/* Base styles */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: var(--font-family-sans);
  background-color: var(--color-secondary);
  color: var(--color-primary);
  line-height: 1.6;
}

/* Utility classes */
.gradient-text {
  background: var(--gradient-primary);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.glass-effect {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.hover-lift {
  transition: transform var(--transition-base);
}

.hover-lift:hover {
  transform: translateY(-2px);
}
```

#### 4.2 Componentes Avançados
```jsx
// Card com animações e hover effects
const MetricCard = ({ title, value, change, trend, icon: Icon, gradient }) => {
  return (
    <motion.div
      className={`metric-card ${gradient ? 'gradient-bg' : ''}`}
      whileHover={{ y: -4, boxShadow: "var(--shadow-xl)" }}
      transition={{ duration: 0.2 }}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
    >
      <div className="metric-card-header">
        <div className="metric-icon">
          <Icon size={24} />
        </div>
        <div className={`metric-trend ${trend}`}>
          {trend === 'up' ? <TrendingUp size={16} /> : <TrendingDown size={16} />}
          <span>{change}</span>
        </div>
      </div>
      
      <div className="metric-content">
        <h3 className="metric-value">{value}</h3>
        <p className="metric-title">{title}</p>
      </div>
      
      <div className="metric-footer">
        <div className="metric-sparkline">
          {/* Mini gráfico sparkline */}
        </div>
      </div>
    </motion.div>
  );
};

// Sidebar com animações
const Sidebar = ({ isOpen, setIsOpen }) => {
  const menuItems = [
    { id: 'overview', label: 'Visão Geral', icon: BarChart3 },
    { id: 'corridas', label: 'Corridas', icon: Car },
    { id: 'motoristas', label: 'Motoristas', icon: Users },
    { id: 'receita', label: 'Receita', icon: DollarSign },
    { id: 'metas', label: 'Metas', icon: Target },
    { id: 'relatorios', label: 'Relatórios', icon: FileText },
    { id: 'importar', label: 'Importar Dados', icon: Upload },
    { id: 'configuracoes', label: 'Configurações', icon: Settings }
  ];

  return (
    <motion.aside
      className="sidebar"
      initial={{ width: isOpen ? 280 : 80 }}
      animate={{ width: isOpen ? 280 : 80 }}
      transition={{ duration: 0.3, ease: "easeInOut" }}
    >
      <div className="sidebar-header">
        <motion.div
          className="logo"
          initial={{ opacity: isOpen ? 1 : 0 }}
          animate={{ opacity: isOpen ? 1 : 0 }}
        >
          {isOpen && <span>Dashboard Mobilidade</span>}
        </motion.div>
        <button onClick={() => setIsOpen(!isOpen)}>
          <Menu size={24} />
        </button>
      </div>
      
      <nav className="sidebar-nav">
        {menuItems.map((item) => (
          <motion.a
            key={item.id}
            href={`#${item.id}`}
            className="nav-item"
            whileHover={{ backgroundColor: "var(--color-primary-light)" }}
            whileTap={{ scale: 0.98 }}
          >
            <item.icon size={20} />
            <motion.span
              initial={{ opacity: isOpen ? 1 : 0, x: isOpen ? 0 : -10 }}
              animate={{ opacity: isOpen ? 1 : 0, x: isOpen ? 0 : -10 }}
              transition={{ delay: isOpen ? 0.1 : 0 }}
            >
              {item.label}
            </motion.span>
          </motion.a>
        ))}
      </nav>
    </motion.aside>
  );
};

// Modal para detalhes
const CorridaDetailModal = ({ corrida, isOpen, onClose }) => {
  return (
    <AnimatePresence>
      {isOpen && (
        <motion.div
          className="modal-overlay"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          onClick={onClose}
        >
          <motion.div
            className="modal-content"
            initial={{ scale: 0.8, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            exit={{ scale: 0.8, opacity: 0 }}
            onClick={(e) => e.stopPropagation()}
          >
            {/* Conteúdo do modal */}
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
};
```

---

### **FASE 5: Funcionalidades Avançadas**
**⏱️ Duração: 3-4 dias**

#### 5.1 Sistema de Alertas
```python
# backend/services/alert_service.py
class AlertService:
    def __init__(self):
        self.alert_rules = [
            {
                'name': 'meta_nao_atingida',
                'condition': 'metas.percentual_atingido < 80',
                'severity': 'warning',
                'message': 'Meta de {municipio} abaixo de 80%'
            },
            {
                'name': 'queda_conclusao',
                'condition': 'taxa_conclusao < taxa_conclusao_anterior * 0.9',
                'severity': 'danger',
                'message': 'Queda significativa na taxa de conclusão'
            },
            {
                'name': 'motorista_inativo',
                'condition': 'motorista.ultima_corrida > 7 dias',
                'severity': 'info',
                'message': 'Motorista {nome} inativo há {dias} dias'
            }
        ]
    
    def check_alerts(self):
        alerts = []
        # Verificar cada regra
        return alerts
    
    def send_notification(self, alert):
        # Enviar por email, Slack, etc.
        pass

# Frontend - Componente de notificações
const NotificationCenter = () => {
  const [alerts, setAlerts] = useState([]);
  const [unreadCount, setUnreadCount] = useState(0);

  return (
    <div className="notification-center">
      <button className="notification-trigger">
        <Bell size={20} />
        {unreadCount > 0 && (
          <span className="notification-badge">{unreadCount}</span>
        )}
      </button>
      
      <div className="notification-dropdown">
        {alerts.map(alert => (
          <div key={alert.id} className={`alert alert-${alert.severity}`}>
            <div className="alert-content">
              <h4>{alert.title}</h4>
              <p>{alert.message}</p>
              <small>{formatRelativeTime(alert.created_at)}</small>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
```

#### 5.2 Relatórios Automatizados
```python
# backend/services/report_service.py
class ReportService:
    def __init__(self):
        self.templates = {
            'daily': 'relatorio_diario.html',
            'weekly': 'relatorio_semanal.html',
            'monthly': 'relatorio_mensal.html'
        }
    
    def generate_daily_report(self, date=None):
        date = date or datetime.now().date()
        
        data = {
            'data': date,
            'total_corridas': self.get_total_corridas(date),
            'receita': self.get_receita(date),
            'top_motoristas': self.get_top_motoristas(date),
            'problemas': self.get_problemas(date)
        }
        
        return self.render_template('daily', data)
    
    def send_report_email(self, report_html, recipients):
        # Enviar relatório por email
        pass
    
    def export_to_pdf(self, report_html):
        # Converter para PDF
        pass
    
    def schedule_reports(self):
        # Agendar relatórios automáticos
        pass

# Endpoints para relatórios
@app.route('/api/reports/generate', methods=['POST'])
def generate_report():
    report_type = request.json.get('type')
    period = request.json.get('period')
    format = request.json.get('format', 'html')
    
    report_service = ReportService()
    
    if report_type == 'daily':
        report = report_service.generate_daily_report()
    elif report_type == 'weekly':
        report = report_service.generate_weekly_report()
    # ... outros tipos
    
    if format == 'pdf':
        return report_service.export_to_pdf(report)
    else:
        return jsonify({'report_html': report})
```

#### 5.3 Dashboard em Tempo Real
```python
# backend/realtime/websocket.py
from flask_socketio import SocketIO, emit, join_room, leave_room

socketio = SocketIO(app, cors_allowed_origins="*")

@socketio.on('connect')
def handle_connect():
    print('Cliente conectado')
    join_room('dashboard')

@socketio.on('disconnect')
def handle_disconnect():
    print('Cliente desconectado')
    leave_room('dashboard')

@socketio.on('subscribe_metrics')
def handle_subscribe_metrics(data):
    # Cliente solicitando métricas em tempo real
    metrics = get_real_time_metrics()
    emit('metrics_update', metrics)

def broadcast_metric_update(metric_data):
    socketio.emit('metrics_update', metric_data, room='dashboard')

# Frontend - Hook para WebSocket
const useRealTimeMetrics = () => {
  const [metrics, setMetrics] = useState({});
  const [connected, setConnected] = useState(false);

  useEffect(() => {
    const socket = io('http://localhost:5003');
    
    socket.on('connect', () => {
      setConnected(true);
      socket.emit('subscribe_metrics');
    });
    
    socket.on('metrics_update', (data) => {
      setMetrics(data);
    });
    
    socket.on('disconnect', () => {
      setConnected(false);
    });
    
    return () => socket.disconnect();
  }, []);

  return { metrics, connected };
};
```

---

### **FASE 6: Otimização e Deploy**
**⏱️ Duração: 2 dias**

#### 6.1 Performance e Otimização
```jsx
// Lazy loading de componentes
const MetricsOverview = lazy(() => import('./components/MetricsOverview'));
const AnaliseCorreidas = lazy(() => import('./components/AnaliseCorreidas'));
const ComparativoTemporal = lazy(() => import('./components/ComparativoTemporal'));

// Virtualização para listas grandes
import { FixedSizeList as List } from 'react-window';

const VirtualizedTable = ({ data }) => {
  const Row = ({ index, style }) => (
    <div style={style} className="table-row">
      {/* Conteúdo da linha */}
    </div>
  );

  return (
    <List
      height={600}
      itemCount={data.length}
      itemSize={50}
      itemData={data}
    >
      {Row}
    </List>
  );
};

// Memoização de componentes pesados
const ExpensiveChart = memo(({ data }) => {
  return (
    <ResponsiveContainer width="100%" height={400}>
      {/* Gráfico complexo */}
    </ResponsiveContainer>
  );
});

// Cache inteligente
const useDataCache = (key, fetcher, dependencies = []) => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const cacheRef = useRef(new Map());

  useEffect(() => {
    const cacheKey = `${key}-${JSON.stringify(dependencies)}`;
    
    if (cacheRef.current.has(cacheKey)) {
      setData(cacheRef.current.get(cacheKey));
      setLoading(false);
      return;
    }

    setLoading(true);
    fetcher()
      .then(result => {
        cacheRef.current.set(cacheKey, result);
        setData(result);
        setLoading(false);
      });
  }, dependencies);

  return { data, loading };
};
```

#### 6.2 Configuração Docker
```dockerfile
# Dockerfile.backend
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5003

CMD ["python", "app.py"]

# Dockerfile.frontend
FROM node:18-alpine

WORKDIR /app

COPY package*.json ./
RUN npm ci --only=production

COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=0 /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

# docker-compose.yml
version: '3.8'

services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: mobilidade_urbana
      POSTGRES_USER: dashboard_user
      POSTGRES_PASSWORD: senha_segura
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./database/init.sql:/docker-entrypoint-initdb.d/init.sql
    ports:
      - "5432:5432"

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    environment:
      DATABASE_URL: postgresql://dashboard_user:senha_segura@postgres:5432/mobilidade_urbana
      FLASK_ENV: production
    depends_on:
      - postgres
    ports:
      - "5003:5003"
    volumes:
      - ./config:/app/config

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - "80:80"
    depends_on:
      - backend

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

volumes:
  postgres_data:
```

---

## 📈 **MÉTRICAS E KPIs IMPLEMENTADOS**

### **🚗 Operacionais**
- **Total de corridas** por período (hora, dia, semana, mês)
- **Taxa de conclusão** (corridas concluídas / total de corridas)
- **Taxa de cancelamento** por motivo (cliente, motorista, sistema)
- **Tempo médio de resposta** (desde solicitação até aceitação)
- **Distância média** das corridas
- **Avaliação média** dos usuários (1-5 estrelas)
- **Tempo médio de corrida** (em minutos)
- **Corridas por hora de pico** (heatmap)

### **💰 Financeiros**
- **Receita total** por período
- **Ticket médio** (receita / número de corridas)
- **Receita por motorista** (ranking e distribuição)
- **Comissão da plataforma** (% sobre receita)
- **Crescimento mês a mês** (MoM growth)
- **Projeção de receita** (baseada em tendências)
- **Análise de lucratividade** por cidade

### **⚡ Eficiência**
- **Corridas por motorista/dia** (produtividade)
- **Tempo ocioso dos motoristas** (tempo online vs corridas)
- **Concentração geográfica** (mapa de calor)
- **Horários de pico** (análise temporal)
- **Taxa de utilização da frota** (motoristas ativos/total)
- **Eficiência por rota** (tempo vs distância)

### **🎯 Qualidade**
- **NPS (Net Promoter Score)** calculado das avaliações
- **Taxa de rejeição** (corridas rejeitadas pelos motoristas)
- **Reclamações por categoria** (app, motorista, preço, etc.)
- **Tempo de resolução** de problemas
- **Taxa de retenção** de usuários e motoristas
- **Satisfação por cidade** (comparativo)

---

## 📅 **CRONOGRAMA DETALHADO**

### **Semana 1 (5 dias úteis)**
- **Dias 1-2:** Fase 1 - Configuração do ambiente
- **Dias 3-5:** Fase 2 - Sistema de dados multi-fonte

### **Semana 2 (5 dias úteis)**
- **Dias 1-3:** Fase 3 - Dashboard e visualizações
- **Dias 4-5:** Fase 4 - Interface moderna

### **Semana 3 (5 dias úteis)**
- **Dias 1-3:** Fase 5 - Funcionalidades avançadas
- **Dias 4-5:** Fase 6 - Otimização e deploy

### **Total: 15 dias úteis (3 semanas)**

---

## 🛠️ **TECNOLOGIAS E FERRAMENTAS**

### **Backend**
- **Flask** 2.3+ (Framework web)
- **SQLAlchemy** (ORM)
- **PostgreSQL** 15+ (Database principal)
- **Redis** (Cache e sessões)
- **Celery** (Tasks assíncronas)
- **Flask-SocketIO** (WebSocket para tempo real)
- **Pandas** (Manipulação de dados)
- **Google Sheets API** (Integração planilhas)

### **Frontend**
- **React** 18+ (UI Framework)
- **Vite** (Build tool)
- **React Router** 6+ (Roteamento)
- **Framer Motion** (Animações)
- **Recharts** (Gráficos)
- **Headless UI** (Componentes acessíveis)
- **Tailwind CSS** (Styling)
- **Lucide React** (Ícones)

### **DevOps & Deploy**
- **Docker** & **Docker Compose**
- **Nginx** (Reverse proxy)
- **PostgreSQL** (Production database)
- **Redis** (Cache)
- **GitHub Actions** (CI/CD)

---

## 🎯 **RESULTADOS ESPERADOS**

### **Para Gestores**
- ✅ **Visão 360°** da operação em tempo real
- ✅ **Identificação rápida** de problemas e oportunidades
- ✅ **Relatórios automatizados** para tomada de decisão
- ✅ **Monitoramento de metas** por cidade/período
- ✅ **Análises preditivas** para planejamento

### **Para Equipe Operacional**
- ✅ **Dashboard intuitivo** com métricas relevantes
- ✅ **Alertas automáticos** para situações críticas
- ✅ **Ferramentas de análise** para otimização
- ✅ **Exportação fácil** de dados para outros sistemas
- ✅ **Acesso mobile** para acompanhamento remoto

### **Para Analistas**
- ✅ **Dados consolidados** de múltiplas fontes
- ✅ **Ferramentas de filtro** e segmentação avançadas
- ✅ **Exportação** para Excel/PDF
- ✅ **API robusta** para integrações futuras
- ✅ **Histórico completo** para análises temporais

---

## 🚀 **PRÓXIMOS PASSOS**

1. **Aprovar o plano** e definir prioridades
2. **Configurar ambiente de desenvolvimento**
3. **Iniciar Fase 1** - Configuração base
4. **Definir design final** da interface
5. **Começar desenvolvimento iterativo**

**Pronto para começar? Qual fase você gostaria de iniciar primeiro?**
