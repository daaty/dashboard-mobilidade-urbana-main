# 🎛️ MÓDULO DE CONFIGURAÇÃO E GESTÃO DE DADOS - Dashboard Mobilidade

## 📋 VISÃO GERAL

Para tornar o dashboard funcional com dados reais, precisamos criar **interfaces de configuração intuitivas** que permitam ao usuário:

1. **Configurar campanhas** de aquisição de motoristas/corridas
2. **Cadastrar novas cidades** de expansão com suas metas
3. **Gerenciar transações de créditos** automaticamente
4. **Definir metas mensais** por cidade
5. **Importar dados** de sistemas externos

---

## 🎯 ESTRATÉGIA DE IMPLEMENTAÇÃO

### **ABORDAGEM 1: Aba "Configuração Avançada"**
Uma aba dedicada com sub-seções para cada tipo de configuração

### **ABORDAGEM 2: Modais de Configuração**  
Botões "Configurar" em cada aba que abrem modais específicos

### **ABORDAGEM 3: Wizard de Setup Inicial**
Assistente que guia o usuário na configuração inicial completa

**RECOMENDAÇÃO: Combinar as 3 abordagens**

---

## 🚀 IMPLEMENTAÇÃO DETALHADA

### **FASE 1: ABA "GESTÃO & CONFIGURAÇÃO"**

#### 1.1 Nova Estrutura da Sidebar

```javascript
// frontend/src/components/Sidebar.jsx
const menuItems = [
  { id: 'overview', label: 'Visão Geral', icon: Home },
  
  // GRUPO: ANÁLISES (Core Business)
  { id: 'operacional', label: 'Análise Operacional', icon: TrendingUp },
  { id: 'financeiro-creditos', label: 'Análise Financeira', icon: DollarSign },
  { id: 'metas-performance', label: 'Metas & Performance', icon: Target },
  
  // DIVISOR
  { id: 'divider1', type: 'divider' },
  
  // GRUPO: GESTÃO (Configurações)
  { id: 'gestao-campanhas', label: 'Gestão de Campanhas', icon: Megaphone },
  { id: 'gestao-cidades', label: 'Gestão de Cidades', icon: MapPin },
  { id: 'gestao-creditos', label: 'Sistema de Créditos', icon: CreditCard },
  { id: 'gestao-metas', label: 'Gestão de Metas', icon: Target },
  
  // DIVISOR  
  { id: 'divider2', type: 'divider' },
  
  // GRUPO: FERRAMENTAS
  { id: 'drivers', label: 'Motoristas', icon: Users },
  { id: 'importacao', label: 'Importação', icon: Upload },
  { id: 'configuracao', label: 'Configurações', icon: Settings }
]
```

---

### **FASE 2: GESTÃO DE CAMPANHAS**

#### 2.1 Interface Principal - Gestão de Campanhas

```javascript
// frontend/src/components/GestaoCampanhas.jsx
export function GestaoCampanhas() {
  const [campanhas, setCampanhas] = useState([])
  const [showModal, setShowModal] = useState(false)
  const [editingCampanha, setEditingCampanha] = useState(null)

  return (
    <div className="space-y-6">
      {/* Header com Actions */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold">Gestão de Campanhas</h1>
          <p className="text-gray-600">Configure campanhas de aquisição de motoristas e corridas</p>
        </div>
        <Button onClick={() => setShowModal(true)} className="bg-blue-600">
          <Plus className="w-4 h-4 mr-2" />
          Nova Campanha
        </Button>
      </div>

      {/* Filtros e Busca */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Input placeholder="Buscar campanhas..." />
        <Select>
          <SelectTrigger>
            <SelectValue placeholder="Fase" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="fase1">Fase 1</SelectItem>
            <SelectItem value="fase2">Fase 2</SelectItem>
            <SelectItem value="fase3">Fase 3</SelectItem>
          </SelectContent>
        </Select>
        <Select>
          <SelectTrigger>
            <SelectValue placeholder="Cidade" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="monte-verde">Monte Verde</SelectItem>
            <SelectItem value="colider">Colíder</SelectItem>
          </SelectContent>
        </Select>
        <Select>
          <SelectTrigger>
            <SelectValue placeholder="Status" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="ativa">Ativa</SelectItem>
            <SelectItem value="finalizada">Finalizada</SelectItem>
            <SelectItem value="pausada">Pausada</SelectItem>
          </SelectContent>
        </Select>
      </div>

      {/* Lista de Campanhas */}
      <div className="grid grid-cols-1 gap-4">
        {campanhas.map(campanha => (
          <CampanhaCard 
            key={campanha.id} 
            campanha={campanha}
            onEdit={setCampanha}
            onDelete={deleteCampanha}
          />
        ))}
      </div>

      {/* Modal de Criação/Edição */}
      {showModal && (
        <ModalCampanha 
          campanha={editingCampanha}
          onSave={saveCampanha}
          onClose={() => setShowModal(false)}
        />
      )}
    </div>
  )
}
```

#### 2.2 Modal de Configuração de Campanha

```javascript
// frontend/src/components/ModalCampanha.jsx
export function ModalCampanha({ campanha, onSave, onClose }) {
  const [formData, setFormData] = useState({
    nome: '',
    fase: 'Fase 1',
    cidade: '',
    tipo_campanha: 'aquisicao_motoristas',
    data_inicio: '',
    data_fim: '',
    meta_quantidade: 0,
    orcamento_previsto: 0,
    descricao: '',
    canais_marketing: [],
    kpis_principais: []
  })

  const tiposCampanha = [
    { value: 'aquisicao_motoristas', label: 'Aquisição de Motoristas' },
    { value: 'aquisicao_corridas', label: 'Aquisição de Corridas' },
    { value: 'retencao', label: 'Retenção' },
    { value: 'reativacao', label: 'Reativação' }
  ]

  return (
    <Dialog open={true} onOpenChange={onClose}>
      <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>
            {campanha ? 'Editar Campanha' : 'Nova Campanha'}
          </DialogTitle>
        </DialogHeader>

        <form className="space-y-6">
          {/* Informações Básicas */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <Label>Nome da Campanha</Label>
              <Input 
                value={formData.nome}
                onChange={(e) => setFormData({...formData, nome: e.target.value})}
                placeholder="Ex: Fase 1 - Aquisição Monte Verde"
              />
            </div>
            <div>
              <Label>Fase</Label>
              <Select value={formData.fase} onValueChange={(value) => setFormData({...formData, fase: value})}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="Fase 1">Fase 1</SelectItem>
                  <SelectItem value="Fase 2">Fase 2</SelectItem>
                  <SelectItem value="Fase 3">Fase 3</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>

          {/* Localização e Tipo */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <Label>Cidade</Label>
              <Select value={formData.cidade} onValueChange={(value) => setFormData({...formData, cidade: value})}>
                <SelectTrigger>
                  <SelectValue placeholder="Selecione a cidade" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="Monte Verde">Monte Verde</SelectItem>
                  <SelectItem value="Colíder">Colíder</SelectItem>
                  <SelectItem value="Alta Floresta">Alta Floresta</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div>
              <Label>Tipo de Campanha</Label>
              <Select value={formData.tipo_campanha} onValueChange={(value) => setFormData({...formData, tipo_campanha: value})}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {tiposCampanha.map(tipo => (
                    <SelectItem key={tipo.value} value={tipo.value}>
                      {tipo.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>

          {/* Período */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <Label>Data de Início</Label>
              <Input 
                type="date"
                value={formData.data_inicio}
                onChange={(e) => setFormData({...formData, data_inicio: e.target.value})}
              />
            </div>
            <div>
              <Label>Data de Fim</Label>
              <Input 
                type="date"
                value={formData.data_fim}
                onChange={(e) => setFormData({...formData, data_fim: e.target.value})}
              />
            </div>
          </div>

          {/* Metas e Orçamento */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <Label>Meta Quantidade</Label>
              <Input 
                type="number"
                value={formData.meta_quantidade}
                onChange={(e) => setFormData({...formData, meta_quantidade: parseInt(e.target.value)})}
                placeholder={formData.tipo_campanha === 'aquisicao_motoristas' ? 'Nº de motoristas' : 'Nº de corridas'}
              />
            </div>
            <div>
              <Label>Orçamento Previsto (R$)</Label>
              <Input 
                type="number"
                step="0.01"
                value={formData.orcamento_previsto}
                onChange={(e) => setFormData({...formData, orcamento_previsto: parseFloat(e.target.value)})}
                placeholder="0.00"
              />
            </div>
          </div>

          {/* Canais de Marketing */}
          <div>
            <Label>Canais de Marketing</Label>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-2 mt-2">
              {['Facebook Ads', 'Google Ads', 'Instagram', 'WhatsApp', 'Rádio', 'Outdoor', 'Boca a Boca', 'Indicação'].map(canal => (
                <div key={canal} className="flex items-center space-x-2">
                  <Checkbox 
                    id={canal}
                    checked={formData.canais_marketing.includes(canal)}
                    onCheckedChange={(checked) => {
                      if (checked) {
                        setFormData({...formData, canais_marketing: [...formData.canais_marketing, canal]})
                      } else {
                        setFormData({...formData, canais_marketing: formData.canais_marketing.filter(c => c !== canal)})
                      }
                    }}
                  />
                  <Label htmlFor={canal} className="text-sm">{canal}</Label>
                </div>
              ))}
            </div>
          </div>

          {/* Descrição */}
          <div>
            <Label>Descrição</Label>
            <Textarea 
              value={formData.descricao}
              onChange={(e) => setFormData({...formData, descricao: e.target.value})}
              placeholder="Descreva os objetivos e estratégias da campanha..."
              rows={3}
            />
          </div>
        </form>

        <DialogFooter>
          <Button variant="outline" onClick={onClose}>
            Cancelar
          </Button>
          <Button onClick={() => onSave(formData)}>
            {campanha ? 'Atualizar' : 'Criar'} Campanha
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
```

---

### **FASE 3: GESTÃO DE CIDADES**

#### 3.1 Interface de Gestão de Cidades

```javascript
// frontend/src/components/GestaoCidades.jsx
export function GestaoCidades() {
  const [cidades, setCidades] = useState([])
  const [showModal, setShowModal] = useState(false)

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold">Gestão de Cidades</h1>
          <p className="text-gray-600">Configure cidades de expansão e suas metas</p>
        </div>
        <Button onClick={() => setShowModal(true)} className="bg-green-600">
          <MapPin className="w-4 h-4 mr-2" />
          Adicionar Cidade
        </Button>
      </div>

      {/* Grid de Cidades */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {cidades.map(cidade => (
          <CidadeCard 
            key={cidade.id} 
            cidade={cidade}
            onEdit={editCidade}
            onViewDetails={viewCidadeDetails}
          />
        ))}
      </div>

      {/* Modal de Configuração */}
      {showModal && (
        <ModalCidade 
          onSave={saveCidade}
          onClose={() => setShowModal(false)}
        />
      )}
    </div>
  )
}

// Componente Card da Cidade
function CidadeCard({ cidade, onEdit, onViewDetails }) {
  const progressoAtual = (cidade.corridas_realizadas / cidade.meta_corridas_mes_6) * 100

  return (
    <Card className="hover:shadow-lg transition-all">
      <CardHeader>
        <div className="flex justify-between items-start">
          <div>
            <CardTitle className="text-lg">{cidade.nome}</CardTitle>
            <Badge variant={cidade.ativa ? "success" : "secondary"}>
              {cidade.ativa ? "Ativa" : "Inativa"}
            </Badge>
          </div>
          <DropdownMenu>
            <DropdownMenuTrigger>
              <MoreHorizontal className="w-4 h-4" />
            </DropdownMenuTrigger>
            <DropdownMenuContent>
              <DropdownMenuItem onClick={() => onEdit(cidade)}>
                Editar
              </DropdownMenuItem>
              <DropdownMenuItem onClick={() => onViewDetails(cidade)}>
                Ver Detalhes
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Dados Demográficos */}
        <div className="grid grid-cols-2 gap-4 text-sm">
          <div>
            <p className="text-gray-500">População</p>
            <p className="font-semibold">{cidade.populacao_estimada.toLocaleString()}</p>
          </div>
          <div>
            <p className="text-gray-500">Público-Alvo</p>
            <p className="font-semibold">{cidade.publico_alvo.toLocaleString()}</p>
          </div>
        </div>

        {/* Progresso da Meta */}
        <div>
          <div className="flex justify-between text-sm mb-2">
            <span>Progresso da Meta (6º mês)</span>
            <span>{progressoAtual.toFixed(1)}%</span>
          </div>
          <Progress value={progressoAtual} className="h-2" />
        </div>

        {/* Metas Mensais Resumidas */}
        <div className="grid grid-cols-3 gap-2 text-xs">
          <div className="text-center">
            <p className="text-gray-500">Mês 1</p>
            <p className="font-semibold">{cidade.meta_corridas_mes_1}</p>
          </div>
          <div className="text-center">
            <p className="text-gray-500">Mês 3</p>
            <p className="font-semibold">{cidade.meta_corridas_mes_3}</p>
          </div>
          <div className="text-center">
            <p className="text-gray-500">Mês 6</p>
            <p className="font-semibold">{cidade.meta_corridas_mes_6}</p>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
```

#### 3.2 Modal de Configuração de Cidade

```javascript
// frontend/src/components/ModalCidade.jsx
export function ModalCidade({ cidade, onSave, onClose }) {
  const [step, setStep] = useState(1)
  const [formData, setFormData] = useState({
    nome: '',
    populacao_estimada: 0,
    publico_alvo: 0,
    densidade_demografica: 0,
    data_lancamento: '',
    
    // Calculado automaticamente baseado no público-alvo
    meta_corridas_mes_1: 0, // 0.5% do público
    meta_corridas_mes_2: 0, // 1% do público
    meta_corridas_mes_3: 0, // 2% do público
    meta_corridas_mes_6: 0, // 11% do público
    
    meta_receita_media_mensal: 0, // R$ 2.50 * meta_corridas_mes_6
    
    // Configurações avançadas
    percentual_mes_1: 0.5,
    percentual_mes_2: 1.0,
    percentual_mes_3: 2.0,
    percentual_mes_6: 11.0,
    valor_por_corrida: 2.50
  })

  // Calcular metas automaticamente quando população mudar
  useEffect(() => {
    if (formData.publico_alvo > 0) {
      const novasMetaas = {
        meta_corridas_mes_1: Math.round((formData.publico_alvo * formData.percentual_mes_1) / 100),
        meta_corridas_mes_2: Math.round((formData.publico_alvo * formData.percentual_mes_2) / 100),
        meta_corridas_mes_3: Math.round((formData.publico_alvo * formData.percentual_mes_3) / 100),
        meta_corridas_mes_6: Math.round((formData.publico_alvo * formData.percentual_mes_6) / 100),
      }
      
      novasMetaas.meta_receita_media_mensal = novasMetaas.meta_corridas_mes_6 * formData.valor_por_corrida
      
      setFormData({...formData, ...novasMetaas})
    }
  }, [formData.publico_alvo, formData.percentual_mes_1, formData.percentual_mes_2, formData.percentual_mes_3, formData.percentual_mes_6, formData.valor_por_corrida])

  return (
    <Dialog open={true} onOpenChange={onClose}>
      <DialogContent className="max-w-3xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>
            {cidade ? 'Editar Cidade' : 'Nova Cidade de Expansão'}
          </DialogTitle>
          <DialogDescription>
            Configure uma nova cidade para expansão do serviço
          </DialogDescription>
        </DialogHeader>

        {/* Wizard Steps */}
        <div className="flex items-center space-x-4 mb-6">
          <div className={`flex items-center space-x-2 ${step >= 1 ? 'text-blue-600' : 'text-gray-400'}`}>
            <div className={`w-8 h-8 rounded-full flex items-center justify-center ${step >= 1 ? 'bg-blue-600 text-white' : 'bg-gray-200'}`}>1</div>
            <span className="text-sm">Dados Básicos</span>
          </div>
          <div className="flex-1 border-t border-gray-300"></div>
          <div className={`flex items-center space-x-2 ${step >= 2 ? 'text-blue-600' : 'text-gray-400'}`}>
            <div className={`w-8 h-8 rounded-full flex items-center justify-center ${step >= 2 ? 'bg-blue-600 text-white' : 'bg-gray-200'}`}>2</div>
            <span className="text-sm">Metas de Crescimento</span>
          </div>
          <div className="flex-1 border-t border-gray-300"></div>
          <div className={`flex items-center space-x-2 ${step >= 3 ? 'text-blue-600' : 'text-gray-400'}`}>
            <div className={`w-8 h-8 rounded-full flex items-center justify-center ${step >= 3 ? 'bg-blue-600 text-white' : 'bg-gray-200'}`}>3</div>
            <span className="text-sm">Confirmação</span>
          </div>
        </div>

        {/* Step 1: Dados Básicos */}
        {step === 1 && (
          <div className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <Label>Nome da Cidade</Label>
                <Input 
                  value={formData.nome}
                  onChange={(e) => setFormData({...formData, nome: e.target.value})}
                  placeholder="Ex: Nova Bandeirantes"
                />
              </div>
              <div>
                <Label>Data de Lançamento Prevista</Label>
                <Input 
                  type="date"
                  value={formData.data_lancamento}
                  onChange={(e) => setFormData({...formData, data_lancamento: e.target.value})}
                />
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <Label>População Estimada (2024)</Label>
                <Input 
                  type="number"
                  value={formData.populacao_estimada}
                  onChange={(e) => setFormData({...formData, populacao_estimada: parseInt(e.target.value)})}
                  placeholder="Ex: 32010"
                />
              </div>
              <div>
                <Label>Público-Alvo (15-44 anos)</Label>
                <Input 
                  type="number"
                  value={formData.publico_alvo}
                  onChange={(e) => setFormData({...formData, publico_alvo: parseInt(e.target.value)})}
                  placeholder="Ex: 14045"
                />
                <p className="text-xs text-gray-500 mt-1">
                  ~{((formData.publico_alvo / formData.populacao_estimada) * 100).toFixed(1)}% da população
                </p>
              </div>
              <div>
                <Label>Densidade Demográfica</Label>
                <Input 
                  type="number"
                  step="0.01"
                  value={formData.densidade_demografica}
                  onChange={(e) => setFormData({...formData, densidade_demografica: parseFloat(e.target.value)})}
                  placeholder="hab/km²"
                />
              </div>
            </div>
          </div>
        )}

        {/* Step 2: Metas de Crescimento */}
        {step === 2 && (
          <div className="space-y-6">
            <div>
              <h3 className="text-lg font-semibold mb-4">Configuração de Metas de Penetração</h3>
              <p className="text-sm text-gray-600 mb-4">
                Ajuste os percentuais de penetração do público-alvo para cada mês:
              </p>
            </div>

            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div>
                <Label>Mês 1 (%)</Label>
                <Input 
                  type="number"
                  step="0.1"
                  value={formData.percentual_mes_1}
                  onChange={(e) => setFormData({...formData, percentual_mes_1: parseFloat(e.target.value)})}
                />
                <p className="text-xs text-gray-500">≈ {formData.meta_corridas_mes_1} corridas</p>
              </div>
              <div>
                <Label>Mês 2 (%)</Label>
                <Input 
                  type="number"
                  step="0.1"
                  value={formData.percentual_mes_2}
                  onChange={(e) => setFormData({...formData, percentual_mes_2: parseFloat(e.target.value)})}
                />
                <p className="text-xs text-gray-500">≈ {formData.meta_corridas_mes_2} corridas</p>
              </div>
              <div>
                <Label>Mês 3 (%)</Label>
                <Input 
                  type="number"
                  step="0.1"
                  value={formData.percentual_mes_3}
                  onChange={(e) => setFormData({...formData, percentual_mes_3: parseFloat(e.target.value)})}
                />
                <p className="text-xs text-gray-500">≈ {formData.meta_corridas_mes_3} corridas</p>
              </div>
              <div>
                <Label>Mês 6 (%)</Label>
                <Input 
                  type="number"
                  step="0.1"
                  value={formData.percentual_mes_6}
                  onChange={(e) => setFormData({...formData, percentual_mes_6: parseFloat(e.target.value)})}
                />
                <p className="text-xs text-gray-500">≈ {formData.meta_corridas_mes_6} corridas</p>
              </div>
            </div>

            <div>
              <Label>Valor por Corrida (R$)</Label>
              <Input 
                type="number"
                step="0.01"
                value={formData.valor_por_corrida}
                onChange={(e) => setFormData({...formData, valor_por_corrida: parseFloat(e.target.value)})}
              />
              <p className="text-xs text-gray-500">
                Receita média mensal projetada: R$ {formData.meta_receita_media_mensal.toFixed(2)}
              </p>
            </div>

            {/* Preview das Metas */}
            <div className="bg-gray-50 p-4 rounded-lg">
              <h4 className="font-semibold mb-3">Preview das Metas Calculadas</h4>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                <div>
                  <p className="text-gray-500">Mês 1</p>
                  <p className="font-semibold">{formData.meta_corridas_mes_1} corridas</p>
                </div>
                <div>
                  <p className="text-gray-500">Mês 2</p>
                  <p className="font-semibold">{formData.meta_corridas_mes_2} corridas</p>
                </div>
                <div>
                  <p className="text-gray-500">Mês 3</p>
                  <p className="font-semibold">{formData.meta_corridas_mes_3} corridas</p>
                </div>
                <div>
                  <p className="text-gray-500">Mês 6</p>
                  <p className="font-semibold">{formData.meta_corridas_mes_6} corridas</p>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Step 3: Confirmação */}
        {step === 3 && (
          <div className="space-y-4">
            <h3 className="text-lg font-semibold">Confirmar Configuração</h3>
            
            <Card>
              <CardContent className="pt-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <h4 className="font-semibold mb-3">Dados da Cidade</h4>
                    <div className="space-y-2 text-sm">
                      <div className="flex justify-between">
                        <span>Nome:</span>
                        <span className="font-semibold">{formData.nome}</span>
                      </div>
                      <div className="flex justify-between">
                        <span>População:</span>
                        <span>{formData.populacao_estimada.toLocaleString()}</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Público-Alvo:</span>
                        <span>{formData.publico_alvo.toLocaleString()}</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Lançamento:</span>
                        <span>{new Date(formData.data_lancamento).toLocaleDateString()}</span>
                      </div>
                    </div>
                  </div>
                  
                  <div>
                    <h4 className="font-semibold mb-3">Metas de Crescimento</h4>
                    <div className="space-y-2 text-sm">
                      <div className="flex justify-between">
                        <span>Mês 1:</span>
                        <span>{formData.meta_corridas_mes_1} corridas</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Mês 2:</span>
                        <span>{formData.meta_corridas_mes_2} corridas</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Mês 3:</span>
                        <span>{formData.meta_corridas_mes_3} corridas</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Mês 6:</span>
                        <span>{formData.meta_corridas_mes_6} corridas</span>
                      </div>
                      <div className="flex justify-between font-semibold border-t pt-2">
                        <span>Receita Mensal:</span>
                        <span>R$ {formData.meta_receita_media_mensal.toFixed(2)}</span>
                      </div>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        )}

        <DialogFooter>
          <Button variant="outline" onClick={onClose}>
            Cancelar
          </Button>
          {step > 1 && (
            <Button variant="outline" onClick={() => setStep(step - 1)}>
              Voltar
            </Button>
          )}
          {step < 3 ? (
            <Button onClick={() => setStep(step + 1)}>
              Próximo
            </Button>
          ) : (
            <Button onClick={() => onSave(formData)}>
              Criar Cidade
            </Button>
          )}
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
```

---

### **FASE 4: SISTEMA DE CRÉDITOS AUTOMATIZADO**

#### 4.1 Configuração do Sistema de Créditos

```javascript
// frontend/src/components/GestaoCreditos.jsx
export function GestaoCreditos() {
  const [configCreditos, setConfigCreditos] = useState({
    valor_por_credito: 2.50,
    pacotes_disponíveis: [
      { creditos: 10, valor: 25.00, bonus: 0 },
      { creditos: 25, valor: 60.00, bonus: 2 },
      { creditos: 50, valor: 120.00, bonus: 5 },
      { creditos: 100, valor: 230.00, bonus: 15 }
    ],
    auto_debito_ativo: true,
    limite_minimo_saldo: 5,
    notificacoes_saldo_baixo: true
  })

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold">Sistema de Créditos</h1>
        <p className="text-gray-600">Configure o sistema de créditos para motoristas</p>
      </div>

      {/* Configurações Gerais */}
      <Card>
        <CardHeader>
          <CardTitle>Configurações Gerais</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <Label>Valor por Crédito (R$)</Label>
              <Input 
                type="number"
                step="0.01"
                value={configCreditos.valor_por_credito}
                onChange={(e) => setConfigCreditos({...configCreditos, valor_por_credito: parseFloat(e.target.value)})}
              />
            </div>
            <div>
              <Label>Limite Mínimo de Saldo</Label>
              <Input 
                type="number"
                value={configCreditos.limite_minimo_saldo}
                onChange={(e) => setConfigCreditos({...configCreditos, limite_minimo_saldo: parseInt(e.target.value)})}
              />
            </div>
            <div className="flex items-center space-x-2 pt-6">
              <Checkbox 
                id="auto-debito"
                checked={configCreditos.auto_debito_ativo}
                onCheckedChange={(checked) => setConfigCreditos({...configCreditos, auto_debito_ativo: checked})}
              />
              <Label htmlFor="auto-debito">Auto-débito ativo</Label>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Pacotes de Créditos */}
      <Card>
        <CardHeader>
          <CardTitle>Pacotes de Créditos</CardTitle>
          <CardDescription>
            Configure os pacotes de créditos disponíveis para compra
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {configCreditos.pacotes_disponíveis.map((pacote, index) => (
              <Card key={index} className="border-2">
                <CardContent className="pt-6">
                  <div className="text-center space-y-2">
                    <div className="text-2xl font-bold">{pacote.creditos}</div>
                    <div className="text-sm text-gray-500">créditos</div>
                    {pacote.bonus > 0 && (
                      <div className="text-xs bg-green-100 text-green-600 px-2 py-1 rounded">
                        +{pacote.bonus} bônus
                      </div>
                    )}
                    <div className="text-lg font-semibold">
                      R$ {pacote.valor.toFixed(2)}
                    </div>
                    <div className="text-xs text-gray-500">
                      R$ {(pacote.valor / (pacote.creditos + pacote.bonus)).toFixed(2)}/crédito
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Relatório de Transações */}
      <Card>
        <CardHeader>
          <CardTitle>Transações Recentes</CardTitle>
        </CardHeader>
        <CardContent>
          <TabelaTransacoesCreditos />
        </CardContent>
      </Card>
    </div>
  )
}
```

---

### **FASE 5: ENDPOINTS BACKEND PARA GESTÃO**

#### 5.1 API para Campanhas

```python
# backend/app/api/gestao_campanhas.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from ..database import get_db
from ..models.campanha import Campanha
from ..schemas.campanha import CampanhaCreate, CampanhaResponse

router = APIRouter(prefix="/gestao-campanhas", tags=["Gestão de Campanhas"])

@router.post("/", response_model=CampanhaResponse)
async def criar_campanha(
    campanha_data: CampanhaCreate,
    db: Session = Depends(get_db)
):
    """Cria uma nova campanha"""
    try:
        # Validar se cidade existe
        cidade_exists = db.query(CidadeExpansao).filter(
            CidadeExpansao.nome == campanha_data.cidade
        ).first()
        
        if not cidade_exists:
            raise HTTPException(status_code=400, detail="Cidade não encontrada")
        
        # Criar campanha
        db_campanha = Campanha(**campanha_data.dict())
        db.add(db_campanha)
        db.commit()
        db.refresh(db_campanha)
        
        return db_campanha
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/", response_model=List[CampanhaResponse])
async def listar_campanhas(
    fase: Optional[str] = None,
    cidade: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Lista campanhas com filtros opcionais"""
    query = db.query(Campanha)
    
    if fase:
        query = query.filter(Campanha.fase == fase)
    if cidade:
        query = query.filter(Campanha.cidade == cidade)
    if status:
        query = query.filter(Campanha.status == status)
    
    return query.all()

@router.put("/{campanha_id}", response_model=CampanhaResponse)
async def atualizar_campanha(
    campanha_id: int,
    campanha_data: CampanhaCreate,
    db: Session = Depends(get_db)
):
    """Atualiza uma campanha existente"""
    db_campanha = db.query(Campanha).filter(Campanha.id == campanha_id).first()
    
    if not db_campanha:
        raise HTTPException(status_code=404, detail="Campanha não encontrada")
    
    for field, value in campanha_data.dict().items():
        setattr(db_campanha, field, value)
    
    db.commit()
    db.refresh(db_campanha)
    return db_campanha

@router.get("/{campanha_id}/performance")
async def get_performance_campanha(
    campanha_id: int,
    db: Session = Depends(get_db)
):
    """Retorna performance detalhada da campanha"""
    campanha = db.query(Campanha).filter(Campanha.id == campanha_id).first()
    
    if not campanha:
        raise HTTPException(status_code=404, detail="Campanha não encontrada")
    
    # Calcular métricas de performance
    if campanha.tipo_campanha == "aquisicao_motoristas":
        # Contar motoristas adquiridos no período
        realizado = db.query(Motorista).filter(
            Motorista.data_cadastro >= campanha.data_inicio,
            Motorista.data_cadastro <= campanha.data_fim,
            Motorista.municipio == campanha.cidade
        ).count()
    else:
        # Contar corridas no período
        realizado = db.query(Corrida).filter(
            Corrida.data >= campanha.data_inicio,
            Corrida.data <= campanha.data_fim,
            Corrida.municipio == campanha.cidade,
            Corrida.status == 'concluida'
        ).count()
    
    atingimento = (realizado / campanha.meta_quantidade) * 100 if campanha.meta_quantidade > 0 else 0
    cac = campanha.custo_real / realizado if realizado > 0 else 0
    
    return {
        "campanha": campanha,
        "realizado": realizado,
        "atingimento_percentual": atingimento,
        "cac": cac,
        "status_meta": "atingida" if atingimento >= 100 else "em_andamento" if atingimento >= 80 else "abaixo_esperado"
    }
```

#### 5.2 API para Cidades

```python
# backend/app/api/gestao_cidades.py
@router.post("/", response_model=CidadeExpansaoResponse)
async def criar_cidade(
    cidade_data: CidadeExpansaoCreate,
    db: Session = Depends(get_db)
):
    """Cria uma nova cidade de expansão"""
    try:
        # Criar cidade
        db_cidade = CidadeExpansao(**cidade_data.dict())
        db.add(db_cidade)
        db.flush()  # Para obter o ID
        
        # Criar metas mensais automaticamente para os próximos 12 meses
        hoje = datetime.now()
        for mes_offset in range(12):
            data_meta = hoje + relativedelta(months=mes_offset)
            
            # Determinar meta baseada no mês
            if mes_offset == 0:
                meta_corridas = cidade_data.meta_corridas_mes_1
            elif mes_offset == 1:
                meta_corridas = cidade_data.meta_corridas_mes_2
            elif mes_offset == 2:
                meta_corridas = cidade_data.meta_corridas_mes_3
            elif mes_offset == 5:
                meta_corridas = cidade_data.meta_corridas_mes_6
            else:
                # Interpolar valores para outros meses
                meta_corridas = interpolar_meta_mensal(mes_offset, cidade_data)
            
            meta_mensal = MetaMensal(
                cidade=cidade_data.nome,
                ano=data_meta.year,
                mes=data_meta.month,
                meta_corridas=meta_corridas,
                meta_receita=meta_corridas * 2.50,
                meta_penetracao_mercado=(meta_corridas / cidade_data.publico_alvo) * 100
            )
            db.add(meta_mensal)
        
        db.commit()
        db.refresh(db_cidade)
        return db_cidade
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

def interpolar_meta_mensal(mes_offset: int, cidade_data: CidadeExpansaoCreate) -> int:
    """Interpola metas para meses não especificados"""
    # Pontos conhecidos: mês 1, 2, 3, 6
    pontos = {
        0: cidade_data.meta_corridas_mes_1,
        1: cidade_data.meta_corridas_mes_2,
        2: cidade_data.meta_corridas_mes_3,
        5: cidade_data.meta_corridas_mes_6
    }
    
    # Interpolação linear simples
    if mes_offset < 2:
        return pontos[mes_offset]
    elif mes_offset < 5:
        # Interpolar entre mês 3 e mês 6
        t = (mes_offset - 2) / (5 - 2)
        return int(pontos[2] + t * (pontos[5] - pontos[2]))
    else:
        return pontos[5]
```

---

## 🎯 WORKFLOW COMPLETO DO USUÁRIO

### **1. Setup Inicial (Primeira vez)**
1. **Wizard de Configuração** - Aparece na primeira entrada
2. **Adicionar Cidades** - Usuário configura 2-3 cidades iniciais
3. **Criar Campanhas** - Define campanhas de lançamento
4. **Configurar Sistema de Créditos** - Define valores e pacotes

### **2. Operação Diária**
1. **Dashboard Principal** - Visualiza KPIs e métricas
2. **Análise Operacional** - Monitora taxas de conclusão/cancelamento
3. **Análise Financeira** - Acompanha receita e fluxo de créditos
4. **Metas & Performance** - Verifica atingimento de campanhas

### **3. Gestão Periódica**
1. **Ajustar Metas** - Atualiza metas conforme performance
2. **Criar Novas Campanhas** - Lança campanhas sazonais
3. **Expandir para Novas Cidades** - Adiciona novas praças
4. **Análise de ROI** - Revisa CAC e otimiza investimentos

---

## 🚀 PRÓXIMOS PASSOS

1. **Aprovação do Design** - Review das interfaces propostas
2. **Implementação Backend** - APIs de gestão e configuração
3. **Desenvolvimento Frontend** - Componentes e modais
4. **Integração e Testes** - Workflow completo
5. **Wizard de Setup** - Experiência inicial do usuário

**Este sistema torna o dashboard completamente self-service, permitindo que o usuário configure e opere tudo através da interface, sem necessidade de intervenção técnica.**
