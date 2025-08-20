import React, { useState, useEffect } from 'react'
import { 
  Calculator, 
  Clock, 
  DollarSign, 
  Target, 
  TrendingUp, 
  Settings,
  RefreshCw,
  Info,
  CheckCircle,
  AlertTriangle,
  ChevronDown,
  ChevronUp
} from 'lucide-react'

const CalculadorProgressoFases = ({ faseId, progressoAtual, onProgressoAtualizado }) => {
  const [mostrarCalculadora, setMostrarCalculadora] = useState(false)
  const [metodoSelecionado, setMetodoSelecionado] = useState('hibrido')
  const [calculando, setCalculando] = useState(false)
  const [configuracao, setConfiguracao] = useState(null)
  const [detalhesCalculo, setDetalhesCalculo] = useState(null)

  // Buscar configurações disponíveis
  useEffect(() => {
    const buscarConfiguracao = async () => {
      try {
        const response = await fetch('/api/metas-estrategicas/configuracao-progresso')
        const data = await response.json()
        setConfiguracao(data)
      } catch (error) {
        console.error('Erro ao buscar configuração:', error)
      }
    }

    buscarConfiguracao()
  }, [])

  const calcularProgresso = async () => {
    try {
      setCalculando(true)
      
      const response = await fetch(
        `/api/metas-estrategicas/fases-estrategicas/${faseId}/calcular-progresso?metodo=${metodoSelecionado}`,
        { method: 'POST' }
      )
      
      const resultado = await response.json()
      
      if (resultado.success) {
        setDetalhesCalculo(resultado)
        onProgressoAtualizado && onProgressoAtualizado(resultado.progresso_novo)
      } else {
        alert('Erro ao calcular progresso: ' + resultado.error)
      }
    } catch (error) {
      console.error('Erro ao calcular progresso:', error)
      alert('Erro ao calcular progresso')
    } finally {
      setCalculando(false)
    }
  }

  const getIconeMetodo = (metodo) => {
    switch (metodo) {
      case 'temporal': return <Clock className="w-3 h-3" />
      case 'orcamentario': return <DollarSign className="w-3 h-3" />
      case 'metas': return <Target className="w-3 h-3" />
      case 'campanhas': return <TrendingUp className="w-3 h-3" />
      default: return <Calculator className="w-3 h-3" />
    }
  }

  const getCorProgresso = (progresso) => {
    if (progresso >= 80) return 'text-green-600'
    if (progresso >= 60) return 'text-blue-600'
    if (progresso >= 40) return 'text-yellow-600'
    return 'text-red-600'
  }

  if (!configuracao) return null

  return (
    <div className="mt-2 border border-gray-200 rounded-lg">
      <div 
        className="flex items-center justify-between p-3 bg-gray-50 cursor-pointer hover:bg-gray-100 transition-colors"
        onClick={() => setMostrarCalculadora(!mostrarCalculadora)}
      >
        <div className="flex items-center gap-2">
          <Calculator className="w-4 h-4 text-blue-600" />
          <span className="text-sm font-medium text-gray-700">Cálculo Automático</span>
        </div>
        
        <div className="flex items-center gap-2">
          <span className="text-xs text-gray-500">Atual:</span>
          <span className={`font-semibold text-sm ${getCorProgresso(progressoAtual)}`}>
            {progressoAtual?.toFixed(1) || 0}%
          </span>
          {mostrarCalculadora ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
        </div>
      </div>

      {mostrarCalculadora && (
        <div className="p-4 space-y-4 border-t border-gray-200">
          
          {/* Seleção do Método - Layout mais compacto */}
          <div>
            <label className="block text-xs font-medium text-gray-700 mb-2">
              Método de Cálculo
            </label>
            <div className="grid grid-cols-1 gap-2">
              {Object.entries(configuracao.metodos_disponiveis).map(([key, metodo]) => (
                <label
                  key={key}
                  className={`flex items-center gap-2 p-2 rounded-md border cursor-pointer transition-all text-xs ${
                    metodoSelecionado === key 
                      ? 'border-blue-500 bg-blue-50' 
                      : 'border-gray-200 hover:border-gray-300'
                  }`}
                >
                  <input
                    type="radio"
                    name="metodo"
                    value={key}
                    checked={metodoSelecionado === key}
                    onChange={(e) => setMetodoSelecionado(e.target.value)}
                    className="w-3 h-3"
                  />
                  <div className="flex items-center gap-1">
                    {getIconeMetodo(key)}
                    <span className="font-medium">{metodo.nome}</span>
                  </div>
                </label>
              ))}
            </div>
          </div>

          {/* Configuração Híbrida - Mais compacta */}
          {metodoSelecionado === 'hibrido' && (
            <div className="bg-blue-50 rounded-md p-3">
              <h4 className="text-xs font-medium text-blue-800 mb-2 flex items-center gap-1">
                <Info className="w-3 h-3" />
                Composição Híbrida
              </h4>
              <div className="grid grid-cols-2 gap-2 text-xs">
                {Object.entries(configuracao.configuracao_hibrida).map(([tipo, peso]) => (
                  <div key={tipo} className="flex justify-between">
                    <span className="text-blue-700 capitalize">{tipo}:</span>
                    <span className="font-medium text-blue-800">{peso}%</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Botão de Cálculo */}
          <button
            onClick={calcularProgresso}
            disabled={calculando}
            className="w-full flex items-center justify-center gap-2 px-3 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 transition-colors text-sm"
          >
            {calculando ? (
              <>
                <RefreshCw className="w-3 h-3 animate-spin" />
                Calculando...
              </>
            ) : (
              <>
                <Calculator className="w-3 h-3" />
                Calcular Automaticamente
              </>
            )}
          </button>

          {/* Resultados do Cálculo - Mais compacto */}
          {detalhesCalculo && (
            <div className="bg-green-50 rounded-md p-3 border border-green-200">
              <h4 className="text-xs font-medium text-green-800 mb-2 flex items-center gap-1">
                <CheckCircle className="w-3 h-3" />
                Resultado
              </h4>
              
              <div className="space-y-2 text-xs">
                <div className="flex justify-between">
                  <span className="text-green-700">Anterior:</span>
                  <span>{detalhesCalculo.progresso_anterior?.toFixed(1)}%</span>
                </div>
                
                <div className="flex justify-between">
                  <span className="text-green-700">Novo:</span>
                  <span className={`font-bold ${getCorProgresso(detalhesCalculo.progresso_novo)}`}>
                    {detalhesCalculo.progresso_novo?.toFixed(1)}%
                  </span>
                </div>
                
                <div className="flex justify-between">
                  <span className="text-green-700">Variação:</span>
                  <span className={`font-medium ${
                    detalhesCalculo.variacao >= 0 ? 'text-green-600' : 'text-red-600'
                  }`}>
                    {detalhesCalculo.variacao >= 0 ? '+' : ''}{detalhesCalculo.variacao?.toFixed(1)}%
                  </span>
                </div>
              </div>
            </div>
          )}

          {/* Informações - Versão compacta */}
          <div className="bg-yellow-50 rounded-md p-3 border border-yellow-200">
            <div className="text-xs text-yellow-700">
              <p><strong>Temporal:</strong> Baseado no tempo decorrido</p>
              <p><strong>Orçamentário:</strong> Valor pago vs previsto</p>
              <p><strong>Metas:</strong> Cumprimento das metas das cidades</p>
              <p><strong>Híbrido:</strong> Combina todos com pesos balanceados</p>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default CalculadorProgressoFases
