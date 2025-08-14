# 🚀 PLANO DE REFATORAÇÃO: MetasCidades.jsx → Dashboard Inteligente

**Data de criação:** 14 de Agosto de 2025  
**Objetivo:** Eliminar dados hardcoded e implementar sistema dinâmico alinhado aos documentos estratégicos  
**Prazo estimado:** 3-4 semanas  

---

## 📋 **FASE 1: BACKEND - ESTRUTURA DE DADOS (Semana 1)**

### **🗄️ 1.1 Modelos de Dados**

- [ ] **Criar model `CidadesDemografia`**
  ```python
  # backend/app/models/cidades_demografia.py
  class CidadesDemografia(Base):
      __tablename__ = "cidades_demografia"
      
      id = Column(Integer, primary_key=True)
      cidade = Column(String, unique=True, nullable=False)
      populacao_censo_2022 = Column(Integer)
      populacao_estimada_2024 = Column(Integer)
      densidade_demografica = Column(Float)
      publico_alvo_15_44_anos = Column(Integer)
      publico_homens = Column(Integer)
      publico_mulheres = Column(Integer)
      regiao = Column(String)
      created_at = Column(DateTime, default=datetime.utcnow)
  ```

- [ ] **Expandir model `Campanha` com campos estratégicos**
  ```python
  # Novos campos para campanhas
  parte_campanha = Column(String)  # "Part 1" ou "Part 2"
  tipo_gasto = Column(String)  # "trafego_pago", "operacoes", "outros"
  pagamento_programado = Column(Date)
  status_financeiro = Column(String)  # "empenhado", "pago", "liquidado"
  meta_percentual_populacao = Column(Float)  # 0.5%, 1%, 2%, 10%
  cidade_id = Column(Integer, ForeignKey('cidades_demografia.id'))
  ```

- [ ] **Criar model `FasesPlanejamento`**
  ```python
  class FasesPlanejamento(Base):
      __tablename__ = "fases_planejamento"
      
      id = Column(Integer, primary_key=True)
      nome = Column(String, nullable=False)  # "Fase 1", "Fase 2", "Fase 3"
      data_inicio = Column(Date)
      data_fim = Column(Date)
      status = Column(String)  # "planejada", "em_execucao", "concluida"
      orcamento_empenhado = Column(Float)
      orcamento_pago = Column(Float)
      orcamento_liquidado = Column(Float)
      orcamento_previsto = Column(Float)
  ```

- [ ] **Criar model `MetasProgressivas`**
  ```python
  class MetasProgressivas(Base):
      __tablename__ = "metas_progressivas"
      
      id = Column(Integer, primary_key=True)
      cidade_id = Column(Integer, ForeignKey('cidades_demografia.id'))
      mes = Column(Integer)  # 1, 2, 3, 6
      percentual_publico = Column(Float)  # 0.5, 1.0, 2.0, 10.0
      meta_corridas = Column(Integer)
      meta_motoristas = Column(Integer)
      tipo_meta = Column(String)  # "muito_baixa", "baixa", "media", "alta"
  ```

### **🔧 1.2 Migrations e População de Dados**

- [ ] **Criar migrations para as novas tabelas**
  ```bash
  # Usar Alembic ou script SQL direto
  alembic revision --autogenerate -m "add_cidades_demografia_fases_metas"
  alembic upgrade head
  ```

- [ ] **Script de população com dados dos documentos**
  ```python
  # scripts/populate_cidades_demografia.py
  def populate_cidades_data():
      cidades_data = [
          {
              "cidade": "Colíder",
              "populacao_censo_2022": 31370,
              "populacao_estimada_2024": 32010,
              "densidade_demografica": 10.08,
              "publico_alvo_15_44_anos": 14045,
              "publico_homens": 6975,
              "publico_mulheres": 7070
          },
          # ... outras 6 cidades dos documentos
      ]
  ```

- [ ] **Popular metas progressivas automáticas**
  ```python
  # Para cada cidade, calcular metas por mês
  def calculate_progressive_metas(cidade_id, publico_alvo):
      metas = [
          {"mes": 1, "percentual": 0.5, "meta_corridas": int(publico_alvo * 0.005)},
          {"mes": 2, "percentual": 1.0, "meta_corridas": int(publico_alvo * 0.01)},
          {"mes": 3, "percentual": 2.0, "meta_corridas": int(publico_alvo * 0.02)},
          {"mes": 6, "percentual": 10.0, "meta_corridas": int(publico_alvo * 0.1)}
      ]
  ```

### **🌐 1.3 APIs Backend**

- [ ] **Endpoint dados demográficos por cidade**
  ```python
  @router.get("/api/cidades/{cidade}/demografia")
  async def get_cidade_demografia(cidade: str, db: Session = Depends(get_db)):
      # Retornar população, público-alvo, densidade, etc.
  ```

- [ ] **Endpoint metas progressivas**
  ```python
  @router.get("/api/cidades/{cidade}/metas-progressivas")
  async def get_metas_progressivas(cidade: str, mes: Optional[int] = None):
      # Retornar metas por mês baseadas no público-alvo
  ```

- [ ] **Endpoint fases e planejamento**
  ```python
  @router.get("/api/fases-planejamento")
  async def get_fases_planejamento():
      # Retornar todas as fases com orçamentos e status
  ```

- [ ] **Endpoint KPIs estratégicos**
  ```python
  @router.get("/api/kpis/penetracao-mercado/{cidade}")
  async def get_kpis_penetracao(cidade: str):
      # Calcular penetração atual vs potencial, CAC, ROI, etc.
  ```

---

## 🎨 **FASE 2: FRONTEND - REFATORAÇÃO COMPONENTES (Semana 2)**

### **🔄 2.1 Substituir PLANO_EXECUCAO hardcoded**

- [ ] **Remover objeto PLANO_EXECUCAO do código**
  ```jsx
  // ❌ REMOVER ISTO:
  const PLANO_EXECUCAO = { ... }
  
  // ✅ SUBSTITUIR POR:
  const [fasesData, setFasesData] = useState([])
  const [metasData, setMetasData] = useState({})
  ```

- [ ] **Criar hook customizado para dados dinâmicos**
  ```jsx
  // hooks/useFasesData.js
  const useFasesData = () => {
      const [fases, setFases] = useState([])
      const [loading, setLoading] = useState(true)
      
      useEffect(() => {
          fetchFasesFromAPI()
      }, [])
      
      return { fases, loading, refetch: fetchFasesFromAPI }
  }
  ```

### **🏗️ 2.2 Refatorar Componente StatusFase**

- [ ] **Tornar StatusFase dinâmico**
  ```jsx
  const StatusFase = ({ fase, dadosFase, metasReais, orcamentoReal }) => {
      // ✅ Usar dados de API em vez de objeto fixo
      const statusAtual = calculateStatusFromRealData(dadosFase, metasReais)
      const progressoOrcamento = calculateBudgetProgress(orcamentoReal)
      
      return (
          <div className="bg-white rounded-xl shadow-lg p-6">
              {/* Renderizar com dados dinâmicos */}
          </div>
      )
  }
  ```

- [ ] **Adicionar cálculos automáticos de status**
  ```jsx
  const calculateStatusFromRealData = (fase, metasReais) => {
      // Calcular status baseado em dados reais vs metas planejadas
      if (metasReais.corridas >= fase.meta_corridas) return 'concluida'
      if (metasReais.corridas > 0) return 'em_execucao'
      return 'aguardando'
  }
  ```

### **📊 2.3 Tabela de Execução Inteligente**

- [ ] **Refatorar TabelaExecucaoComCruzamento**
  ```jsx
  const TabelaExecucaoComCruzamento = ({ cidades, onEditar }) => {
      const [demografiaData, setDemografiaData] = useState({})
      const [metasProgressivas, setMetasProgressivas] = useState({})
      const [kpisData, setKpisData] = useState({})
      
      // ✅ Buscar dados dinâmicos para cada cidade
      useEffect(() => {
          cidades.forEach(cidade => {
              fetchCidadeDemografia(cidade)
              fetchMetasProgressivas(cidade)
              fetchKPIs(cidade)
          })
      }, [cidades])
  }
  ```

- [ ] **Adicionar cálculos automáticos de KPIs**
  ```jsx
  const calculateKPIs = (cidade, demografiaData, metasReais) => {
      const penetracao = (metasReais.corridas / demografiaData.publico_alvo) * 100
      const receitaMensal = metasReais.corridas * 2.5
      const cac = demografiaData.orcamento_gasto / metasReais.motoristas
      
      return { penetracao, receitaMensal, cac }
  }
  ```

### **📈 2.4 Cards KPIs Estratégicos**

- [ ] **Criar componente MetasKPIs dinâmico**
  ```jsx
  const MetasKPIs = ({ cidade }) => {
      const { demografia, loading } = useCidadeDemografia(cidade)
      const { metas, metasReais } = useMetasProgressivas(cidade)
      const kpis = calculateKPIs(cidade, demografia, metasReais)
      
      return (
          <div className="grid grid-cols-4 gap-4">
              <KPICard title="Penetração de Mercado" value={kpis.penetracao} />
              <KPICard title="CAC por Motorista" value={kpis.cac} />
              <KPICard title="ROI Campanha" value={kpis.roi} />
              <KPICard title="Progressão Mensal" value={kpis.progressao} />
          </div>
      )
  }
  ```

---

## 📊 **FASE 3: DASHBOARDS E VISUALIZAÇÕES (Semana 3)**

### **📈 3.1 Gráficos de Progressão Temporal**

- [ ] **Componente ProgressaoMetas dinâmico**
  ```jsx
  const ProgressaoMetas = ({ cidade }) => {
      const { metasPorMes } = useMetasProgressivas(cidade)
      const { realizadoPorMes } = useCorridasHistorico(cidade)
      
      const chartData = {
          meses: ["Mês 1", "Mês 2", "Mês 3", "Mês 6"],
          metas: metasPorMes.map(m => m.meta_corridas),
          realizado: realizadoPorMes,
          projecao: calculateProjection(realizadoPorMes, metasPorMes)
      }
      
      return <LineChart data={chartData} />
  }
  ```

- [ ] **Gráfico de Penetração por Cidade**
  ```jsx
  const PenetracaoPorCidade = () => {
      const { todasCidades } = useCidadesData()
      
      const chartData = todasCidades.map(cidade => ({
          cidade: cidade.nome,
          penetracao_atual: cidade.penetracao_atual,
          penetracao_meta: cidade.penetracao_meta
      }))
      
      return <BarChart data={chartData} />
  }
  ```

### **💰 3.2 Dashboard Financeiro por Fase**

- [ ] **Componente ControleFases dinâmico**
  ```jsx
  const ControleFases = () => {
      const { fasesData } = useFasesData()
      
      return (
          <div className="grid grid-cols-3 gap-4">
              {fasesData.map(fase => (
                  <FaseFinanceiraCard 
                      key={fase.id}
                      fase={fase}
                      orcamento={fase.orcamento}
                      execucao={fase.execucao_real}
                  />
              ))}
          </div>
      )
  }
  ```

- [ ] **Breakdown de Gastos detalhado**
  ```jsx
  const DetalhamentoGastos = ({ faseId }) => {
      const { gastosDetalhados } = useGastosPorFase(faseId)
      
      const categorias = [
          { tipo: 'trafego_pago', valor: gastosDetalhados.trafego_pago },
          { tipo: 'operacoes', valor: gastosDetalhados.operacoes },
          { tipo: 'outros', valor: gastosDetalhados.outros }
      ]
      
      return <PieChart data={categorias} />
  }
  ```

### **🗓️ 3.3 Cronograma Automatizado**

- [ ] **Timeline de Campanhas dinâmica**
  ```jsx
  const TimelineCampanhas = () => {
      const { campanhasAtivas } = useCampanhasData()
      
      const timelineData = campanhasAtivas.map(campanha => ({
          id: campanha.id,
          titulo: campanha.nome,
          inicio: campanha.data_inicio,
          fim: campanha.data_fim,
          status: campanha.status,
          progresso: calculateProgress(campanha)
      }))
      
      return <GanttChart data={timelineData} />
  }
  ```

- [ ] **Calendário de Pagamentos**
  ```jsx
  const CalendarioPagamentos = () => {
      const { pagamentosPrevistos } = usePagamentosData()
      
      return (
          <Calendar
              events={pagamentosPrevistos}
              onEventClick={handlePagamentoClick}
              eventRender={renderPagamentoEvent}
          />
      )
  }
  ```

---

## ⚙️ **FASE 4: FUNCIONALIDADES AVANÇADAS (Semana 4)**

### **🔄 4.1 CRUD Dinâmico de Metas**

- [ ] **Formulário de criação de metas inteligente**
  ```jsx
  const FormularioCadastroMetas = ({ isOpen, onClose, onSave }) => {
      const { cidadesDisponiveis } = useCidadesData()
      
      const [formData, setFormData] = useState({
          cidade_id: '',
          tipo_campanha: '',
          meta_automatica: true, // Calcular baseado no público-alvo
          percentual_publico: 1.0, // 1% do público-alvo
          data_inicio: '',
          duracao_dias: 45
      })
      
      // ✅ Calcular metas automaticamente baseado na demografia
      const handleCidadeChange = (cidadeId) => {
          const demografia = getCidadeDemografia(cidadeId)
          const metaCalculada = demografia.publico_alvo * (formData.percentual_publico / 100)
          setFormData({...formData, meta_corridas: metaCalculada})
      }
  }
  ```

- [ ] **Editor de fases e partes flexível**
  ```jsx
  const EditorFases = () => {
      const [fases, setFases] = useState([])
      
      const adicionarFase = () => {
          const novaFase = {
              nome: `Fase ${fases.length + 1}`,
              data_inicio: '',
              data_fim: '',
              cidades: [],
              partes: [
                  { nome: 'Part 1', tipo: 'motoristas', duracao: 15 },
                  { nome: 'Part 2', tipo: 'corridas', duracao: 30 }
              ]
          }
          setFases([...fases, novaFase])
      }
      
      return <FaseEditor fases={fases} onChange={setFases} />
  }
  ```

### **🚨 4.2 Alertas e Notificações**

- [ ] **Sistema de alertas automáticos**
  ```jsx
  const useAlertas = () => {
      const [alertas, setAlertas] = useState([])
      
      useEffect(() => {
          // ✅ Verificar desvios orçamentários
          checkOrcamentoDesvios()
          // ✅ Verificar metas em atraso
          checkMetasAtrasadas()
          // ✅ Verificar datas de pagamento próximas
          checkPagamentosPendentes()
      }, [])
      
      return { alertas, markAsRead: markAlertAsRead }
  }
  ```

- [ ] **Notificações em tempo real**
  ```jsx
  const NotificationCenter = () => {
      const { alertas } = useAlertas()
      
      return (
          <div className="notification-center">
              {alertas.map(alerta => (
                  <AlertCard key={alerta.id} alerta={alerta} />
              ))}
          </div>
      )
  }
  ```

### **📊 4.3 Relatórios Executivos**

- [ ] **Gerador de relatórios automático**
  ```jsx
  const RelatorioExecutivo = () => {
      const { dadosConsolidados } = useRelatorioData()
      
      const gerarRelatorio = (tipo) => {
          // ✅ Relatório financeiro por fase
          // ✅ Relatório de penetração por cidade
          // ✅ Relatório de ROI e CAC
          // ✅ Projeções e tendências
      }
      
      return <ReportGenerator onGenerate={gerarRelatorio} />
  }
  ```

---

## 🎯 **CHECKLIST DE VALIDAÇÃO**

### **✅ Dados Dinâmicos**
- [ ] Nenhum dado hardcoded permanece no código
- [ ] Todas as metas são calculadas baseadas em população real
- [ ] Orçamentos vêm do banco de dados
- [ ] Status das fases é calculado automaticamente

### **✅ Performance**
- [ ] APIs otimizadas com cache
- [ ] Componentes usando React.memo onde necessário
- [ ] Loading states implementados
- [ ] Error boundaries para robustez

### **✅ UX/UI**
- [ ] Interface responsiva em todos os dispositivos
- [ ] Feedback visual para todas as ações
- [ ] Navegação intuitiva entre seções
- [ ] Tooltips explicativos para KPIs

### **✅ Funcionalidades**
- [ ] CRUD completo para metas e campanhas
- [ ] Relatórios exportáveis (PDF/Excel)
- [ ] Sistema de notificações funcional
- [ ] Sincronização em tempo real

---

## 🚀 **PRÓXIMOS PASSOS IMEDIATOS**

1. **[ ] Executar Fase 1.1** - Criar modelos de dados
2. **[ ] Executar Fase 1.2** - Popular dados demográficos
3. **[ ] Executar Fase 1.3** - Criar APIs básicas
4. **[ ] Testar integração** frontend-backend
5. **[ ] Validar com dados reais** de uma cidade piloto

---

## 📝 **NOTAS IMPORTANTES**

- **Backup:** Fazer backup completo antes de iniciar refatoração
- **Testes:** Criar testes unitários para novos endpoints
- **Documentação:** Atualizar documentação da API conforme alterações
- **Rollback:** Manter versão anterior funcional durante transição
- **Performance:** Monitorar performance após cada fase implementada

---

**🎯 Objetivo Final:** Dashboard 100% dinâmico, alinhado com planejamento estratégico, sem dados hardcoded, com cálculos automáticos de metas, KPIs e relatórios executivos prontos.

**📅 Prazo Total:** 4 semanas  
**👥 Recursos:** 1-2 desenvolvedores full-stack  
**🔄 Metodologia:** Implementação incremental com testes contínuos
