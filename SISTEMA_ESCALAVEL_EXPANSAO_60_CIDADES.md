# 🚀 SISTEMA ESCALÁVEL DE EXPANSÃO - 60+ Cidades

## 📋 VISÃO ESTRATÉGICA

**SITUAÇÃO ATUAL:** 3 cidades piloto (Monte Verde, Colíder, Alta Floresta)
**OBJETIVO:** Escalar para 60+ cidades de forma eficiente e padronizada
**DESAFIO:** Sistema deve ser auto-suficiente para expansão rápida

---

## 🎯 ESTRATÉGIA DE ESCALABILIDADE

### **FASE 1: BASE SÓLIDA (Cidades Piloto)**
- ✅ Implementar dashboard com 3 cidades atuais
- ✅ Validar modelo de negócio e métricas
- ✅ Refinar processos operacionais

### **FASE 2: SISTEMA DE EXPANSÃO AUTOMATIZADO**
- 🚀 Interface de adição de cidades em massa
- 🚀 Templates de campanhas reutilizáveis  
- 🚀 Cálculo automático de metas baseado em dados demográficos
- 🚀 Processos de onboarding padronizados

### **FASE 3: EXPANSÃO ACELERADA**
- 📈 Adição de 5-10 cidades por mês
- 📈 Replicação automática de campanhas bem-sucedidas
- 📈 Dashboard regional para gestão em escala

---

## 🛠️ IMPLEMENTAÇÃO DO SISTEMA ESCALÁVEL

### **1. MÓDULO DE EXPANSÃO RÁPIDA**

#### 1.1 Interface "Expansion Hub"

```javascript
// frontend/src/components/ExpansionHub.jsx
export function ExpansionHub() {
  const [viewMode, setViewMode] = useState('mapa') // 'mapa', 'lista', 'regioes'
  const [cidades, setCidades] = useState([])
  const [filtros, setFiltros] = useState({
    status: 'todas', // 'ativas', 'planejadas', 'pausadas'
    regiao: 'todas',
    fase_expansao: 'todas'
  })

  return (
    <div className="space-y-6">
      {/* Header Estratégico */}
      <div className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-lg p-6 text-white">
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold">Central de Expansão</h1>
            <p className="text-blue-100">Gerencie a expansão para 60+ cidades</p>
          </div>
          <div className="grid grid-cols-3 gap-4 text-center">
            <div>
              <div className="text-2xl font-bold">{cidades.filter(c => c.status === 'ativa').length}</div>
              <div className="text-sm text-blue-100">Ativas</div>
            </div>
            <div>
              <div className="text-2xl font-bold">{cidades.filter(c => c.status === 'planejada').length}</div>
              <div className="text-sm text-blue-100">Planejadas</div>
            </div>
            <div>
              <div className="text-2xl font-bold">60+</div>
              <div className="text-sm text-blue-100">Meta Total</div>
            </div>
          </div>
        </div>
      </div>

      {/* Toolbar de Ações */}
      <div className="flex justify-between items-center">
        <div className="flex space-x-3">
          <Button onClick={() => setViewMode('mapa')} variant={viewMode === 'mapa' ? 'default' : 'outline'}>
            <MapIcon className="w-4 h-4 mr-2" />
            Mapa
          </Button>
          <Button onClick={() => setViewMode('lista')} variant={viewMode === 'lista' ? 'default' : 'outline'}>
            <ListIcon className="w-4 h-4 mr-2" />
            Lista
          </Button>
          <Button onClick={() => setViewMode('regioes')} variant={viewMode === 'regioes' ? 'default' : 'outline'}>
            <GridIcon className="w-4 h-4 mr-2" />
            Por Região
          </Button>
        </div>

        <div className="flex space-x-3">
          <Button onClick={() => openAddCidadesModal()} className="bg-green-600">
            <Plus className="w-4 h-4 mr-2" />
            Adicionar Cidades
          </Button>
          <Button onClick={() => openExpansionWizard()} className="bg-purple-600">
            <Zap className="w-4 h-4 mr-2" />
            Expansão Rápida
          </Button>
          <Button onClick={() => openTemplateManager()}>
            <Copy className="w-4 h-4 mr-2" />
            Templates
          </Button>
        </div>
      </div>

      {/* Filtros */}
      <Card>
        <CardContent className="pt-6">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <Select value={filtros.status} onValueChange={(value) => setFiltros({...filtros, status: value})}>
              <SelectTrigger>
                <SelectValue placeholder="Status" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="todas">Todas</SelectItem>
                <SelectItem value="ativas">Ativas</SelectItem>
                <SelectItem value="planejadas">Planejadas</SelectItem>
                <SelectItem value="pausadas">Pausadas</SelectItem>
              </SelectContent>
            </Select>

            <Select value={filtros.regiao} onValueChange={(value) => setFiltros({...filtros, regiao: value})}>
              <SelectTrigger>
                <SelectValue placeholder="Região" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="todas">Todas Regiões</SelectItem>
                <SelectItem value="norte">Norte</SelectItem>
                <SelectItem value="sul">Sul</SelectItem>
                <SelectItem value="centro">Centro</SelectItem>
                <SelectItem value="metropolitana">Metropolitana</SelectItem>
              </SelectContent>
            </Select>

            <Select value={filtros.fase_expansao} onValueChange={(value) => setFiltros({...filtros, fase_expansao: value})}>
              <SelectTrigger>
                <SelectValue placeholder="Fase de Expansão" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="todas">Todas as Fases</SelectItem>
                <SelectItem value="fase-1-3">Fases 1-3 (Piloto)</SelectItem>
                <SelectItem value="fase-4-10">Fases 4-10 (Inicial)</SelectItem>
                <SelectItem value="fase-11-30">Fases 11-30 (Acelerada)</SelectItem>
                <SelectItem value="fase-31-60">Fases 31-60 (Consolidação)</SelectItem>
              </SelectContent>
            </Select>

            <Input placeholder="Buscar cidade..." />
          </div>
        </CardContent>
      </Card>

      {/* Conteúdo Principal */}
      {viewMode === 'mapa' && <MapaExpansao cidades={cidades} />}
      {viewMode === 'lista' && <ListaCidades cidades={cidades} />}
      {viewMode === 'regioes' && <GestaoRegioes cidades={cidades} />}
    </div>
  )
}
```

#### 1.2 Wizard de Expansão Rápida

```javascript
// frontend/src/components/ExpansionWizard.jsx
export function ExpansionWizard({ onClose }) {
  const [step, setStep] = useState(1)
  const [expansionMode, setExpansionMode] = useState('individual') // 'individual', 'batch', 'region'
  const [selectedCities, setSelectedCities] = useState([])
  const [templateConfig, setTemplateConfig] = useState(null)

  return (
    <Dialog open={true} onOpenChange={onClose}>
      <DialogContent className="max-w-6xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Assistente de Expansão Rápida</DialogTitle>
          <DialogDescription>
            Configure a expansão para múltiplas cidades de forma eficiente
          </DialogDescription>
        </DialogHeader>

        {/* Progress Steps */}
        <div className="flex items-center justify-center space-x-4 mb-6">
          {[
            { num: 1, label: 'Modo de Expansão' },
            { num: 2, label: 'Seleção de Cidades' },
            { num: 3, label: 'Template de Configuração' },
            { num: 4, label: 'Campanhas' },
            { num: 5, label: 'Confirmação' }
          ].map((stepInfo, index) => (
            <div key={stepInfo.num} className="flex items-center">
              <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-semibold ${
                step >= stepInfo.num ? 'bg-blue-600 text-white' : 'bg-gray-200 text-gray-600'
              }`}>
                {stepInfo.num}
              </div>
              <span className="ml-2 text-sm">{stepInfo.label}</span>
              {index < 4 && <div className="w-8 border-t border-gray-300 mx-4"></div>}
            </div>
          ))}
        </div>

        {/* Step 1: Modo de Expansão */}
        {step === 1 && (
          <div className="space-y-6">
            <h3 className="text-lg font-semibold">Como você quer expandir?</h3>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <Card 
                className={`cursor-pointer transition-all ${expansionMode === 'individual' ? 'ring-2 ring-blue-600' : ''}`}
                onClick={() => setExpansionMode('individual')}
              >
                <CardContent className="pt-6 text-center">
                  <MapPin className="w-12 h-12 mx-auto text-blue-600 mb-4" />
                  <h4 className="font-semibold">Cidade Individual</h4>
                  <p className="text-sm text-gray-600 mt-2">
                    Adicionar uma cidade por vez com configuração detalhada
                  </p>
                </CardContent>
              </Card>

              <Card 
                className={`cursor-pointer transition-all ${expansionMode === 'batch' ? 'ring-2 ring-blue-600' : ''}`}
                onClick={() => setExpansionMode('batch')}
              >
                <CardContent className="pt-6 text-center">
                  <Grid className="w-12 h-12 mx-auto text-green-600 mb-4" />
                  <h4 className="font-semibold">Lote de Cidades</h4>
                  <p className="text-sm text-gray-600 mt-2">
                    Adicionar múltiplas cidades usando template padrão
                  </p>
                </CardContent>
              </Card>

              <Card 
                className={`cursor-pointer transition-all ${expansionMode === 'region' ? 'ring-2 ring-blue-600' : ''}`}
                onClick={() => setExpansionMode('region')}
              >
                <CardContent className="pt-6 text-center">
                  <Globe className="w-12 h-12 mx-auto text-purple-600 mb-4" />
                  <h4 className="font-semibold">Por Região</h4>
                  <p className="text-sm text-gray-600 mt-2">
                    Expandir para uma região inteira com configuração regional
                  </p>
                </CardContent>
              </Card>
            </div>
          </div>
        )}

        {/* Step 2: Seleção de Cidades */}
        {step === 2 && (
          <div className="space-y-6">
            <h3 className="text-lg font-semibold">Selecione as Cidades</h3>
            
            {expansionMode === 'batch' && (
              <div>
                <Label>Upload de Lista de Cidades (CSV/Excel)</Label>
                <div className="border-2 border-dashed border-gray-300 rounded-lg p-6">
                  <div className="text-center">
                    <Upload className="w-12 h-12 mx-auto text-gray-400 mb-4" />
                    <p>Arraste um arquivo CSV/Excel ou clique para selecionar</p>
                    <p className="text-sm text-gray-500 mt-2">
                      Formato: Nome, População, Público-Alvo, Região
                    </p>
                  </div>
                </div>
              </div>
            )}

            {expansionMode === 'individual' && (
              <div>
                <CidadeSearchSelector 
                  onCitySelect={(city) => setSelectedCities([city])}
                  maxSelections={1}
                />
              </div>
            )}

            {expansionMode === 'region' && (
              <div>
                <RegionSelector 
                  onRegionSelect={(cities) => setSelectedCities(cities)}
                />
              </div>
            )}

            {/* Preview das Cidades Selecionadas */}
            {selectedCities.length > 0 && (
              <div>
                <h4 className="font-semibold mb-3">Cidades Selecionadas ({selectedCities.length})</h4>
                <div className="max-h-40 overflow-y-auto">
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-2">
                    {selectedCities.map((city, index) => (
                      <div key={index} className="flex items-center justify-between p-2 bg-gray-50 rounded">
                        <span className="text-sm">{city.nome}</span>
                        <span className="text-xs text-gray-500">{city.populacao?.toLocaleString()}</span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}
          </div>
        )}

        {/* Step 3: Template de Configuração */}
        {step === 3 && (
          <div className="space-y-6">
            <h3 className="text-lg font-semibold">Escolha o Template de Configuração</h3>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <Card className="cursor-pointer hover:shadow-lg">
                <CardContent className="pt-6">
                  <h4 className="font-semibold">Template Padrão</h4>
                  <p className="text-sm text-gray-600 mt-2">
                    Baseado nas cidades piloto (Monte Verde, Colíder, Alta Floresta)
                  </p>
                  <div className="mt-4 space-y-2">
                    <div className="flex justify-between text-sm">
                      <span>Penetração Mês 1:</span>
                      <span>0.5%</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span>Penetração Mês 6:</span>
                      <span>11%</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span>Valor por Crédito:</span>
                      <span>R$ 2,50</span>
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card className="cursor-pointer hover:shadow-lg">
                <CardContent className="pt-6">
                  <h4 className="font-semibold">Template Personalizado</h4>
                  <p className="text-sm text-gray-600 mt-2">
                    Configure metas específicas para este grupo de cidades
                  </p>
                  <Button variant="outline" className="mt-4">
                    Personalizar
                  </Button>
                </CardContent>
              </Card>
            </div>

            {/* Template Config Preview */}
            <Card>
              <CardHeader>
                <CardTitle>Preview da Configuração</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <div>
                    <Label>Mês 1 (0.5%)</Label>
                    <p className="text-sm text-gray-600">~35 corridas (cidade 15k hab)</p>
                  </div>
                  <div>
                    <Label>Mês 2 (1%)</Label>
                    <p className="text-sm text-gray-600">~70 corridas</p>
                  </div>
                  <div>
                    <Label>Mês 3 (2%)</Label>
                    <p className="text-sm text-gray-600">~140 corridas</p>
                  </div>
                  <div>
                    <Label>Mês 6 (11%)</Label>
                    <p className="text-sm text-gray-600">~770 corridas</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        )}

        {/* Step 4: Campanhas */}
        {step === 4 && (
          <div className="space-y-6">
            <h3 className="text-lg font-semibold">Configurar Campanhas de Lançamento</h3>
            
            <div className="space-y-4">
              <div className="flex items-center space-x-2">
                <Checkbox id="create-campaigns" defaultChecked />
                <Label htmlFor="create-campaigns">
                  Criar campanhas de lançamento automaticamente
                </Label>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <Label>Template de Campanha</Label>
                  <Select defaultValue="padrao">
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="padrao">Padrão (Fases 1-3)</SelectItem>
                      <SelectItem value="acelerado">Acelerado</SelectItem>
                      <SelectItem value="conservador">Conservador</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div>
                  <Label>Orçamento por Cidade</Label>
                  <Input type="number" placeholder="Ex: 4000" />
                  <p className="text-xs text-gray-500">R$ para campanhas de aquisição</p>
                </div>
              </div>

              <div>
                <Label>Canais de Marketing (aplicar a todas)</Label>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-2 mt-2">
                  {['Facebook Ads', 'Google Ads', 'Instagram', 'WhatsApp', 'Rádio Local', 'Outdoor', 'Boca a Boca'].map(canal => (
                    <div key={canal} className="flex items-center space-x-2">
                      <Checkbox id={canal} defaultChecked={['Facebook Ads', 'Google Ads', 'WhatsApp'].includes(canal)} />
                      <Label htmlFor={canal} className="text-sm">{canal}</Label>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Step 5: Confirmação */}
        {step === 5 && (
          <div className="space-y-6">
            <h3 className="text-lg font-semibold">Confirmar Expansão</h3>
            
            <Card>
              <CardContent className="pt-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <h4 className="font-semibold mb-3">Resumo da Expansão</h4>
                    <div className="space-y-2 text-sm">
                      <div className="flex justify-between">
                        <span>Cidades a Adicionar:</span>
                        <span className="font-semibold">{selectedCities.length}</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Campanhas a Criar:</span>
                        <span>{selectedCities.length * 2}</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Orçamento Total:</span>
                        <span>R$ {(selectedCities.length * 4000).toLocaleString()}</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Template:</span>
                        <span>Padrão</span>
                      </div>
                    </div>
                  </div>
                  
                  <div>
                    <h4 className="font-semibold mb-3">O que será criado</h4>
                    <div className="space-y-2 text-sm">
                      <div className="flex items-center space-x-2">
                        <CheckCircle className="w-4 h-4 text-green-500" />
                        <span>Registros das cidades</span>
                      </div>
                      <div className="flex items-center space-x-2">
                        <CheckCircle className="w-4 h-4 text-green-500" />
                        <span>Metas mensais (12 meses)</span>
                      </div>
                      <div className="flex items-center space-x-2">
                        <CheckCircle className="w-4 h-4 text-green-500" />
                        <span>Campanhas de aquisição</span>
                      </div>
                      <div className="flex items-center space-x-2">
                        <CheckCircle className="w-4 h-4 text-green-500" />
                        <span>Configuração de créditos</span>
                      </div>
                      <div className="flex items-center space-x-2">
                        <CheckCircle className="w-4 h-4 text-green-500" />
                        <span>Dashboards regionais</span>
                      </div>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Alert>
              <AlertTriangle className="h-4 w-4" />
              <AlertTitle>Atenção</AlertTitle>
              <AlertDescription>
                Esta ação criará {selectedCities.length} novas cidades e suas configurações. 
                O processo pode levar alguns minutos para ser concluído.
              </AlertDescription>
            </Alert>
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
          {step < 5 ? (
            <Button 
              onClick={() => setStep(step + 1)}
              disabled={step === 2 && selectedCities.length === 0}
            >
              Próximo
            </Button>
          ) : (
            <Button onClick={() => processExpansion()} className="bg-green-600">
              <Zap className="w-4 h-4 mr-2" />
              Executar Expansão
            </Button>
          )}
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
```

### **2. SISTEMA DE TEMPLATES REUTILIZÁVEIS**

#### 2.1 Gerenciador de Templates

```javascript
// frontend/src/components/TemplateManager.jsx
export function TemplateManager() {
  const [templates, setTemplates] = useState([
    {
      id: 1,
      nome: "Piloto Standard",
      baseado_em: ["Monte Verde", "Colíder", "Alta Floresta"],
      configuracao: {
        penetracao_mes_1: 0.5,
        penetracao_mes_6: 11.0,
        valor_credito: 2.50,
        orcamento_aquisicao: 4000
      },
      uso: 3,
      performance_media: 87.3
    },
    {
      id: 2,
      nome: "Expansão Acelerada",
      baseado_em: ["Melhores performers"],
      configuracao: {
        penetracao_mes_1: 0.8,
        penetracao_mes_6: 15.0,
        valor_credito: 2.75,
        orcamento_aquisicao: 6000
      },
      uso: 0,
      performance_media: null
    }
  ])

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold">Gerenciador de Templates</h1>
          <p className="text-gray-600">Templates para expansão rápida e padronizada</p>
        </div>
        <Button onClick={() => createNewTemplate()}>
          <Plus className="w-4 h-4 mr-2" />
          Novo Template
        </Button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {templates.map(template => (
          <TemplateCard 
            key={template.id} 
            template={template}
            onEdit={editTemplate}
            onClone={cloneTemplate}
            onUse={useTemplate}
          />
        ))}
      </div>
    </div>
  )
}

function TemplateCard({ template, onEdit, onClone, onUse }) {
  return (
    <Card className="hover:shadow-lg transition-all">
      <CardHeader>
        <div className="flex justify-between items-start">
          <div>
            <CardTitle className="text-lg">{template.nome}</CardTitle>
            <p className="text-sm text-gray-600">
              Baseado em: {template.baseado_em.join(", ")}
            </p>
          </div>
          <DropdownMenu>
            <DropdownMenuTrigger>
              <MoreHorizontal className="w-4 h-4" />
            </DropdownMenuTrigger>
            <DropdownMenuContent>
              <DropdownMenuItem onClick={() => onUse(template)}>
                Usar Template
              </DropdownMenuItem>
              <DropdownMenuItem onClick={() => onEdit(template)}>
                Editar
              </DropdownMenuItem>
              <DropdownMenuItem onClick={() => onClone(template)}>
                Clonar
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Estatísticas de Uso */}
        <div className="grid grid-cols-2 gap-4 text-sm">
          <div>
            <p className="text-gray-500">Usado em</p>
            <p className="font-semibold">{template.uso} cidades</p>
          </div>
          <div>
            <p className="text-gray-500">Performance Média</p>
            <p className="font-semibold">
              {template.performance_media ? `${template.performance_media}%` : 'N/A'}
            </p>
          </div>
        </div>

        {/* Configuração Preview */}
        <div className="border-t pt-4 space-y-2 text-sm">
          <div className="flex justify-between">
            <span>Penetração Mês 1:</span>
            <span>{template.configuracao.penetracao_mes_1}%</span>
          </div>
          <div className="flex justify-between">
            <span>Penetração Mês 6:</span>
            <span>{template.configuracao.penetracao_mes_6}%</span>
          </div>
          <div className="flex justify-between">
            <span>Valor Crédito:</span>
            <span>R$ {template.configuracao.valor_credito}</span>
          </div>
          <div className="flex justify-between">
            <span>Orçamento:</span>
            <span>R$ {template.configuracao.orcamento_aquisicao.toLocaleString()}</span>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
```

### **3. API BACKEND ESCALÁVEL**

#### 3.1 Expansão em Lote

```python
# backend/app/api/expansion.py
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from typing import List
import asyncio
from ..services.expansion_service import ExpansionService

router = APIRouter(prefix="/expansion", tags=["Expansion"])

@router.post("/batch-cities")
async def add_cities_batch(
    cities_data: List[CidadeExpansaoCreate],
    template_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Adiciona múltiplas cidades usando template"""
    try:
        # Validar template
        template = db.query(Template).filter(Template.id == template_id).first()
        if not template:
            raise HTTPException(status_code=404, detail="Template não encontrado")
        
        # Iniciar processo em background
        task_id = str(uuid.uuid4())
        background_tasks.add_task(
            process_batch_expansion,
            task_id, cities_data, template, db
        )
        
        return {
            "task_id": task_id,
            "message": f"Iniciando expansão para {len(cities_data)} cidades",
            "cities_count": len(cities_data),
            "estimated_time": f"{len(cities_data) * 2} minutos"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def process_batch_expansion(
    task_id: str, 
    cities_data: List[CidadeExpansaoCreate], 
    template: Template,
    db: Session
):
    """Processa expansão em lote (background task)"""
    
    expansion_service = ExpansionService(db)
    
    for i, city_data in enumerate(cities_data):
        try:
            # 1. Criar cidade
            cidade = await expansion_service.create_city_from_template(
                city_data, template
            )
            
            # 2. Criar metas mensais (12 meses)
            await expansion_service.create_monthly_goals(cidade, template)
            
            # 3. Criar campanhas de lançamento
            await expansion_service.create_launch_campaigns(cidade, template)
            
            # 4. Configurar sistema de créditos
            await expansion_service.setup_credit_system(cidade, template)
            
            # 5. Atualizar progresso
            progress = ((i + 1) / len(cities_data)) * 100
            await expansion_service.update_task_progress(task_id, progress)
            
            # Small delay to prevent DB overload
            await asyncio.sleep(0.5)
            
        except Exception as e:
            await expansion_service.log_expansion_error(
                task_id, city_data.nome, str(e)
            )
            continue
    
    # Finalizar task
    await expansion_service.complete_expansion_task(task_id)

@router.get("/task/{task_id}/status")
async def get_expansion_status(task_id: str, db: Session = Depends(get_db)):
    """Verifica status da expansão em lote"""
    
    task = db.query(ExpansionTask).filter(ExpansionTask.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task não encontrada")
    
    return {
        "task_id": task_id,
        "status": task.status,
        "progress": task.progress,
        "cities_processed": task.cities_processed,
        "cities_total": task.cities_total,
        "errors": task.errors,
        "estimated_completion": task.estimated_completion,
        "created_at": task.created_at
    }

@router.post("/from-csv")
async def import_cities_from_csv(
    file: UploadFile,
    template_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Importa cidades de arquivo CSV"""
    
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Apenas arquivos CSV são aceitos")
    
    try:
        # Ler CSV
        content = await file.read()
        cities_data = parse_cities_csv(content)
        
        # Validar dados
        for city in cities_data:
            validate_city_data(city)
        
        # Processar em lote
        return await add_cities_batch(cities_data, template_id, background_tasks, db)
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Erro ao processar CSV: {str(e)}")

def parse_cities_csv(content: bytes) -> List[CidadeExpansaoCreate]:
    """Parse do arquivo CSV para lista de cidades"""
    
    df = pd.read_csv(io.StringIO(content.decode('utf-8')))
    
    required_columns = ['nome', 'populacao_estimada', 'publico_alvo', 'regiao']
    missing_columns = [col for col in required_columns if col not in df.columns]
    
    if missing_columns:
        raise ValueError(f"Colunas obrigatórias faltando: {missing_columns}")
    
    cities_data = []
    for _, row in df.iterrows():
        city_data = CidadeExpansaoCreate(
            nome=row['nome'],
            populacao_estimada=int(row['populacao_estimada']),
            publico_alvo=int(row['publico_alvo']),
            regiao=row.get('regiao', 'centro'),
            densidade_demografica=row.get('densidade_demografica', 0),
            data_lancamento=row.get('data_lancamento', None)
        )
        cities_data.append(city_data)
    
    return cities_data
```

### **4. DASHBOARD REGIONAL PARA ESCALA**

```javascript
// frontend/src/components/DashboardRegional.jsx
export function DashboardRegional() {
  const [selectedRegion, setSelectedRegion] = useState('todas')
  const [viewMode, setViewMode] = useState('overview') // 'overview', 'performance', 'expansion'

  const regioes = [
    { id: 'todas', nome: 'Todas as Regiões', cidades: 60 },
    { id: 'norte', nome: 'Região Norte', cidades: 15 },
    { id: 'sul', nome: 'Região Sul', cidades: 18 },
    { id: 'centro', nome: 'Região Centro', cidades: 12 },
    { id: 'metropolitana', nome: 'Região Metropolitana', cidades: 15 }
  ]

  return (
    <div className="space-y-6">
      {/* Header Regional */}
      <div className="bg-gradient-to-r from-purple-600 to-blue-600 rounded-lg p-6 text-white">
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold">Dashboard Regional</h1>
            <p className="text-purple-100">Visão consolidada de {regioes.find(r => r.id === selectedRegion)?.cidades || 60} cidades</p>
          </div>
          
          <div className="flex space-x-4">
            <Select value={selectedRegion} onValueChange={setSelectedRegion}>
              <SelectTrigger className="bg-white text-gray-900">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {regioes.map(regiao => (
                  <SelectItem key={regiao.id} value={regiao.id}>
                    {regiao.nome} ({regiao.cidades} cidades)
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        </div>
      </div>

      {/* KPIs Consolidados */}
      <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
        <KPICard
          title="Cidades Ativas"
          value="47"
          subtitle="de 60 planejadas"
          trend="up"
          change="+3 este mês"
        />
        <KPICard
          title="Corridas Totais"
          value="125.7K"
          subtitle="últimos 30 dias"
          trend="up"
          change="+23.1%"
        />
        <KPICard
          title="Receita Regional"
          value="R$ 314.2K"
          subtitle="créditos vendidos"
          trend="up"
          change="+18.5%"
        />
        <KPICard
          title="Motoristas Ativos"
          value="2.847"
          subtitle="em todas as cidades"
          trend="up"
          change="+156 novos"
        />
        <KPICard
          title="Taxa Média Conclusão"
          value="88.3%"
          subtitle="média regional"
          trend="stable"
          change="+0.8%"
        />
      </div>

      {/* Mapa de Performance Regional */}
      <Card>
        <CardHeader>
          <CardTitle>Performance por Cidade</CardTitle>
          <CardDescription>
            Visualize a performance de todas as cidades na região selecionada
          </CardDescription>
        </CardHeader>
        <CardContent>
          <MapaPerformanceRegional regiao={selectedRegion} />
        </CardContent>
      </Card>

      {/* Ranking de Cidades */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Top 10 - Performance</CardTitle>
          </CardHeader>
          <CardContent>
            <RankingCidades tipo="performance" regiao={selectedRegion} />
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Top 10 - Receita</CardTitle>
          </CardHeader>
          <CardContent>
            <RankingCidades tipo="receita" regiao={selectedRegion} />
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
```

---

## 🎯 ROADMAP DE EXPANSÃO

### **CRONOGRAMA SUGERIDO**

**Mês 1-2: Consolidação Base**
- ✅ Finalizar dashboard das 3 cidades piloto
- ✅ Implementar sistema de templates
- ✅ Criar wizard de expansão rápida

**Mês 3-4: Primeira Onda (7 cidades)**
- 🚀 Usar wizard para adicionar 4-7 cidades
- 🚀 Testar templates e ajustar configurações
- 🚀 Implementar dashboard regional

**Mês 5-8: Expansão Acelerada (20 cidades)**
- 📈 Adicionar 3-5 cidades por mês usando templates
- 📈 Otimizar processos baseado em dados
- 📈 Implementar automações adicionais

**Mês 9-12: Consolidação Grande Escala (60+ cidades)**
- 🏆 Expansão para 35+ cidades restantes
- 🏆 Dashboard nacional consolidado
- 🏆 Sistema totalmente automatizado

### **BENEFÍCIOS DA ABORDAGEM ESCALÁVEL**

✅ **Rápida Expansão**: Wizard permite adicionar 10+ cidades em minutos
✅ **Padronização**: Templates garantem consistência
✅ **Automação**: Reduz trabalho manual em 90%
✅ **Flexibilidade**: Fácil ajustar configurações
✅ **Visibilidade**: Dashboard regional para gestão em escala
✅ **Eficiência**: Background tasks evitam travamentos

---

## 🚀 IMPLEMENTAÇÃO PRIORITÁRIA

**PRÓXIMOS PASSOS IMEDIATOS:**

1. **Implementar base sólida** com as 3 cidades atuais
2. **Criar wizard de expansão** rápida
3. **Testar com 2-3 cidades** piloto do wizard
4. **Escalar para 60+ cidades** usando sistema automatizado

Esta abordagem torna a expansão para 60+ cidades não apenas possível, mas **eficiente e escalável**! 🚀
