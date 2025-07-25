import { useState } from 'react'
import { CheckCircle, XCircle, AlertCircle } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
// import { ResumoPerformance } from './ResumoPerformance'
// import { SistemaAlertas } from './SistemaAlertas'

const periodOptions = [
  { label: 'Hoje', value: 'hoje' },
  { label: 'Últimos 7 dias', value: '7dias' },
  { label: 'Últimos 30 dias', value: '30dias' },
]



export function MetricsOverview({ data, loading = false, onPeriodChange }) {
  // Garante que data nunca será null/undefined
  const safeData = data || {};
  const [period, setPeriod] = useState('7dias')

  // Simulação de dados caso não venha da API
  const metricas = safeData.metricas_principais || {
    corridas_concluidas: 0,
    corridas_canceladas: 0,
    corridas_perdidas: 0,
    variacao_concluidas: 0,
    variacao_canceladas: 0,
    variacao_perdidas: 0,
  }
  const atividadeRecente = safeData.atividade_recente || {
    concluidas: [],
    canceladas: [],
    perdidas: []
  }

  // Dispara callback para buscar dados ao trocar período
  const handlePeriodChange = (e) => {
    setPeriod(e.target.value)
    if (onPeriodChange) onPeriodChange(e.target.value)
  }


  return (
    <div className="w-full max-w-7xl mx-auto p-4 space-y-8">
      {/* Filtro de período - botões */}
      <div className="flex justify-end mb-4 gap-2">
        {periodOptions.map(opt => (
          <button
            key={opt.value}
            type="button"
            className={`px-4 py-1 rounded border text-sm transition-colors
              ${period === opt.value
                ? 'bg-white border-gray-400 font-semibold shadow text-gray-900'
                : 'bg-gray-100 border-gray-200 text-gray-500 hover:bg-gray-200'}`}
            onClick={() => {
              setPeriod(opt.value);
              if (onPeriodChange) onPeriodChange(opt.value);
            }}
          >
            {opt.label === 'Hoje' ? 'Hoje' : opt.label.includes('7') ? '7d' : '30d'}
          </button>
        ))}
      </div>

      {/* KPIs principais */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card>
          <CardHeader className="flex items-center gap-2">
            <CheckCircle className="text-green-600" />
            <CardTitle>Corridas Concluídas</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-4xl font-bold">{metricas.corridas_concluidas}</div>
            <div className={`text-xs mt-1 ${metricas.variacao_concluidas >= 0 ? 'text-green-600' : 'text-red-600'}`}>Variação: {metricas.variacao_concluidas}%</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex items-center gap-2">
            <XCircle className="text-red-600" />
            <CardTitle>Corridas Canceladas</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-4xl font-bold">{metricas.corridas_canceladas}</div>
            <div className={`text-xs mt-1 ${metricas.variacao_canceladas >= 0 ? 'text-green-600' : 'text-red-600'}`}>Variação: {metricas.variacao_canceladas}%</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex items-center gap-2">
            <AlertCircle className="text-yellow-600" />
            <CardTitle>Corridas Perdidas</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-4xl font-bold">{metricas.corridas_perdidas}</div>
            <div className={`text-xs mt-1 ${metricas.variacao_perdidas >= 0 ? 'text-green-600' : 'text-red-600'}`}>Variação: {metricas.variacao_perdidas}%</div>
          </CardContent>
        </Card>
      </div>

      {/* Bloco de Atividade Recente */}
      <div className="mt-8">
        <h2 className="text-xl font-bold mb-4">Atividade Recente</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* Concluídas */}
          <div>
            <div className="rounded-t-lg bg-green-500 text-white px-4 py-2 font-semibold">Últimas 3 Corridas Concluídas</div>
            <div className="bg-white rounded-b-lg shadow p-4 flex flex-col gap-4">
              {atividadeRecente.concluidas.map((corrida, idx) => (
                <div key={idx} className="flex gap-3 items-start border-b last:border-b-0 pb-3 last:pb-0">
                  <img src={corrida.avatar} alt={corrida.nome} className="w-10 h-10 rounded-full object-cover" />
                  <div className="flex-1">
                    <div className="flex justify-between items-center">
                      <span className="font-bold text-gray-900">{corrida.nome}</span>
                      <span className="text-green-500 font-semibold">{corrida.hora}</span>
                    </div>
                    <div className="text-xs text-gray-500">{corrida.grupo}</div>
                    <div className="text-xs text-gray-700 mt-1">{corrida.local}</div>
                    <div className="text-xs text-gray-700 font-semibold mt-1">{corrida.destino}</div>
                    <div className="text-xs text-gray-400">{corrida.cidade}</div>
                    <div className="text-xs text-gray-400">{corrida.tempo}</div>
                  </div>
                </div>
              ))}
            </div>
          </div>
          {/* Canceladas */}
          <div>
            <div className="rounded-t-lg bg-red-500 text-white px-4 py-2 font-semibold">Últimas 3 Corridas Canceladas</div>
            <div className="bg-white rounded-b-lg shadow p-4 flex flex-col gap-4">
              {atividadeRecente.canceladas.map((corrida, idx) => (
                <div key={idx} className="flex gap-3 items-start border-b last:border-b-0 pb-3 last:pb-0">
                  <img src={corrida.avatar} alt={corrida.nome} className="w-10 h-10 rounded-full object-cover" />
                  <div className="flex-1">
                    <div className="flex justify-between items-center">
                      <span className="font-bold text-gray-900">{corrida.nome}</span>
                      <span className="text-red-500 font-semibold">{corrida.hora}</span>
                    </div>
                    <div className="text-xs text-gray-500">{corrida.grupo}</div>
                    <div className="text-xs text-gray-700 mt-1">{corrida.local}</div>
                    <div className="text-xs text-gray-700 font-semibold mt-1">{corrida.motivo}</div>
                  </div>
                </div>
              ))}
            </div>
          </div>
          {/* Perdidas */}
          <div>
            <div className="rounded-t-lg bg-yellow-400 text-white px-4 py-2 font-semibold">Últimas 3 Corridas Perdidas</div>
            <div className="bg-white rounded-b-lg shadow p-4 flex flex-col gap-4">
              {atividadeRecente.perdidas.map((corrida, idx) => (
                <div key={idx} className="flex gap-3 items-start border-b last:border-b-0 pb-3 last:pb-0">
                  <img src={corrida.avatar} alt={corrida.nome} className="w-10 h-10 rounded-full object-cover" />
                  <div className="flex-1">
                    <div className="flex justify-between items-center">
                      <span className="font-bold text-gray-900">{corrida.nome}</span>
                      <span className="text-yellow-500 font-semibold">{corrida.hora}</span>
                    </div>
                    <div className="text-xs text-gray-500">{corrida.grupo}</div>
                    <div className="text-xs text-gray-700 mt-1">{corrida.local}</div>
                    <div className="text-xs text-gray-700 font-semibold mt-1">{corrida.motivo}</div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Performance removida, agora em tela própria */}
    </div>
  )
}

