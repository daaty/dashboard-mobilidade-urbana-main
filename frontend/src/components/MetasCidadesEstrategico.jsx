import React, { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from './ui/card'
import { Badge } from './ui/badge'
import { Button } from './ui/button'
import { 
  TrendingUp, 
  TrendingDown, 
  Target, 
  DollarSign, 
  Users, 
  MapPin,
  Zap,
  BarChart3,
  Activity
} from 'lucide-react'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export function MetasCidadesEstrategico() {
  const [cidadesData, setCidadesData] = useState([])
  const [kpisData, setKpisData] = useState([])
  const [progressaoData, setProgressaoData] = useState([])
  const [loading, setLoading] = useState(true)
  const [activeFilter, setActiveFilter] = useState('todas')

  useEffect(() => {
    fetchAllData()
  }, [])

  const fetchAllData = async () => {
    try {
      setLoading(true)
      
      // Buscar dados das APIs em paralelo
      const [cidadesRes, kpisRes, progressaoRes] = await Promise.all([
        fetch(`${API_URL}/api/cidades`).catch(err => {
          console.warn('Erro ao buscar cidades:', err)
          return { ok: false, json: () => Promise.resolve([]) }
        }),
        fetch(`${API_URL}/api/kpis/penetracao-mercado`).catch(err => {
          console.warn('Erro ao buscar KPIs:', err)
          return { ok: false, json: () => Promise.resolve([]) }
        }),
        fetch(`${API_URL}/api/metas/progressao-temporal`).catch(err => {
          console.warn('Erro ao buscar progressão:', err)
          return { ok: false, json: () => Promise.resolve([]) }
        })
      ])

      const cidades = cidadesRes.ok ? await cidadesRes.json() : []
      const kpis = kpisRes.ok ? await kpisRes.json() : []
      const progressao = progressaoRes.ok ? await progressaoRes.json() : []

      setCidadesData(Array.isArray(cidades) ? cidades : [])
      setKpisData(Array.isArray(kpis) ? kpis : [])
      setProgressaoData(Array.isArray(progressao) ? progressao : [])
      
      console.log('✅ Dados carregados:', { cidades, kpis, progressao })
    } catch (error) {
      console.error('Erro ao buscar dados estratégicos:', error)
      // Definir arrays vazios em caso de erro
      setCidadesData([])
      setKpisData([])
      setProgressaoData([])
    } finally {
      setLoading(false)
    }
  }

  // Filtrar dados baseado no filtro ativo
  const getFilteredData = () => {
    // Garantir que kpisData é um array
    const safeKpisData = Array.isArray(kpisData) ? kpisData : []
    
    if (activeFilter === 'todas') return safeKpisData
    if (activeFilter === 'fase1') return safeKpisData.filter(item => ['Monte Verde', 'Nova Bandeirantes'].includes(item.cidade))
    if (activeFilter === 'fase2') return safeKpisData.filter(item => ['Alta Floresta', 'Paranaíta'].includes(item.cidade))
    if (activeFilter === 'fase3') return safeKpisData.filter(item => ['Colíder', 'Nova Canaã do Norte', 'Carlinda'].includes(item.cidade))
    return safeKpisData
  }

  const getStatusColor = (penetracao) => {
    if (penetracao >= 2) return 'bg-green-500'
    if (penetracao >= 1) return 'bg-yellow-500'
    if (penetracao >= 0.5) return 'bg-blue-500'
    return 'bg-gray-500'
  }

  const getROIColor = (roi) => {
    if (roi >= 2) return 'text-green-600'
    if (roi >= 1.5) return 'text-yellow-600'
    return 'text-red-600'
  }

  const calculateTotals = () => {
    const filteredData = getFilteredData()
    
    // Verificar se filteredData é um array válido
    if (!Array.isArray(filteredData) || filteredData.length === 0) {
      return {
        totalCidades: 0,
        totalPopulacao: 0,
        totalPublicoAlvo: 0,
        totalOrcamento: 0,
        totalReceita: 0,
        mediaPenetracao: 0
      }
    }
    
    return {
      totalCidades: filteredData.length,
      totalPopulacao: filteredData.reduce((sum, item) => sum + (item.populacao || 0), 0),
      totalPublicoAlvo: filteredData.reduce((sum, item) => sum + (item.publico_alvo || 0), 0),
      totalOrcamento: filteredData.reduce((sum, item) => sum + (item.orcamento_total || 0), 0),
      totalReceita: filteredData.reduce((sum, item) => sum + (item.receita_estimada || 0), 0),
      mediaPenetracao: filteredData.reduce((sum, item) => sum + (item.penetracao_percentual || 0), 0) / filteredData.length
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        <span className="ml-2">Carregando dados estratégicos...</span>
      </div>
    )
  }

  const totals = calculateTotals()
  const filteredData = getFilteredData()

  return (
    <div className="space-y-6">
      {/* Header com KPIs Principais */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Cidades Ativas</p>
                <p className="text-2xl font-bold">{totals.totalCidades}</p>
              </div>
              <MapPin className="h-8 w-8 text-blue-600" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Público-Alvo Total</p>
                <p className="text-2xl font-bold">{totals.totalPublicoAlvo?.toLocaleString()}</p>
              </div>
              <Users className="h-8 w-8 text-green-600" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Penetração Média</p>
                <p className="text-2xl font-bold">{totals.mediaPenetracao?.toFixed(2)}%</p>
              </div>
              <Target className="h-8 w-8 text-purple-600" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Orçamento Total</p>
                <p className="text-2xl font-bold">R$ {totals.totalOrcamento?.toLocaleString()}</p>
              </div>
              <DollarSign className="h-8 w-8 text-orange-600" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Filtros */}
      <div className="flex space-x-2">
        <Button 
          variant={activeFilter === 'todas' ? 'default' : 'outline'}
          onClick={() => setActiveFilter('todas')}
        >
          Todas as Cidades
        </Button>
        <Button 
          variant={activeFilter === 'fase1' ? 'default' : 'outline'}
          onClick={() => setActiveFilter('fase1')}
        >
          Fase 1
        </Button>
        <Button 
          variant={activeFilter === 'fase2' ? 'default' : 'outline'}
          onClick={() => setActiveFilter('fase2')}
        >
          Fase 2
        </Button>
        <Button 
          variant={activeFilter === 'fase3' ? 'default' : 'outline'}
          onClick={() => setActiveFilter('fase3')}
        >
          Fase 3
        </Button>
      </div>

      {/* Tabela Estratégica */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <BarChart3 className="mr-2 h-5 w-5" />
            Análise Estratégica por Cidade
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b">
                  <th className="text-left p-2">Cidade</th>
                  <th className="text-right p-2">População</th>
                  <th className="text-right p-2">Público-Alvo</th>
                  <th className="text-right p-2">Meta Corridas</th>
                  <th className="text-right p-2">Penetração</th>
                  <th className="text-right p-2">Orçamento</th>
                  <th className="text-right p-2">Receita Est.</th>
                  <th className="text-right p-2">ROI</th>
                  <th className="text-center p-2">Status</th>
                </tr>
              </thead>
              <tbody>
                {filteredData.map((cidade) => (
                  <tr key={cidade.cidade} className="border-b hover:bg-gray-50">
                    <td className="p-2 font-medium">{cidade.cidade}</td>
                    <td className="p-2 text-right">{cidade.populacao?.toLocaleString()}</td>
                    <td className="p-2 text-right">{cidade.publico_alvo?.toLocaleString()}</td>
                    <td className="p-2 text-right">{cidade.meta_total_corridas}</td>
                    <td className="p-2 text-right">
                      <span className={`font-semibold ${cidade.penetracao_percentual >= 0.5 ? 'text-green-600' : 'text-red-600'}`}>
                        {cidade.penetracao_percentual}%
                      </span>
                    </td>
                    <td className="p-2 text-right">R$ {cidade.orcamento_total?.toLocaleString()}</td>
                    <td className="p-2 text-right">R$ {cidade.receita_estimada?.toLocaleString()}</td>
                    <td className={`p-2 text-right font-semibold ${getROIColor(cidade.roi_estimado)}`}>
                      {cidade.roi_estimado}%
                    </td>
                    <td className="p-2 text-center">
                      <div className={`w-3 h-3 rounded-full mx-auto ${getStatusColor(cidade.penetracao_percentual)}`}></div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>

      {/* Cards de Progressão de Metas */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {progressaoData.slice(0, 6).map((cidade) => (
          <Card key={cidade.cidade}>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm">{cidade.cidade}</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
              <div className="text-xs text-muted-foreground">
                Público-alvo: {cidade.publico_alvo?.toLocaleString()}
              </div>
              
              <div className="space-y-1">
                <div className="flex justify-between text-xs">
                  <span>Mês 1 (0.5%)</span>
                  <span className="font-semibold">{cidade.metas?.mes_1} corridas</span>
                </div>
                <div className="flex justify-between text-xs">
                  <span>Mês 2 (1%)</span>
                  <span className="font-semibold">{cidade.metas?.mes_2} corridas</span>
                </div>
                <div className="flex justify-between text-xs">
                  <span>Mês 3 (2%)</span>
                  <span className="font-semibold">{cidade.metas?.mes_3} corridas</span>
                </div>
                <div className="flex justify-between text-xs border-t pt-1">
                  <span className="font-medium">Meta 6 meses (10%)</span>
                  <span className="font-bold text-blue-600">{cidade.metas?.mes_6} corridas</span>
                </div>
              </div>

              <div className="text-xs bg-gray-50 p-2 rounded">
                <div className="flex justify-between">
                  <span>Receita anual est.:</span>
                  <span className="font-semibold text-green-600">
                    R$ {cidade.receita_estimada?.mes_6?.toLocaleString()}
                  </span>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  )
}
