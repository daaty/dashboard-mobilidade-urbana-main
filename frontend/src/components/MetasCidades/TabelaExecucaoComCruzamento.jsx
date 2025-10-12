import React from 'react'
import { Target, Edit, X } from 'lucide-react'

/**
 * Tabela de execução com cruzamento completo de dados e ações de edição
 * Exibe dados cruzados de Campanhas + Demografia + Plano Financeiro
 * 
 * Props:
 * - dadosCruzados: array - Dados processados do cruzamento
 * - onEditar: function - Callback para editar item
 */
const TabelaExecucaoComCruzamento = ({ dadosCruzados, onEditar }) => {
  return (
    <div className="bg-white rounded-xl shadow-lg overflow-hidden">
      <div className="bg-gradient-to-r from-gray-800 to-gray-900 text-white p-6">
        <h3 className="text-xl font-bold flex items-center gap-2">
          <Target className="w-5 h-5" />
          🎯 CRUZAMENTO DE DADOS: Execução vs Planejamento
        </h3>
        <p className="text-gray-300 text-sm mt-1">
          API Campanhas + Tabela Demografia + Plano Financeiro = VISÃO REAL DE EXECUÇÃO
        </p>
      </div>
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-4 text-left text-xs font-medium text-gray-600 uppercase">Cidade/Fase</th>
              <th className="px-6 py-4 text-left text-xs font-medium text-gray-600 uppercase">Demografia</th>
              <th className="px-6 py-4 text-left text-xs font-medium text-gray-600 uppercase">Motoristas (Meta vs Real)</th>
              <th className="px-6 py-4 text-left text-xs font-medium text-gray-600 uppercase">Corridas (Meta vs Real)</th>
              <th className="px-6 py-4 text-left text-xs font-medium text-gray-600 uppercase">Orçamento</th>
              <th className="px-6 py-4 text-left text-xs font-medium text-gray-600 uppercase">Status Execução</th>
              <th className="px-6 py-4 text-left text-xs font-medium text-gray-600 uppercase">Ações</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200">
            {dadosCruzados.map((item, index) => (
              <tr key={index} className="hover:bg-gray-50">
                <td className="px-6 py-4">
                  <div>
                    <div className="font-semibold text-gray-900">{item.cidade}</div>
                    <div className="text-sm text-gray-500">{item.fase} • {item.periodo}</div>
                    <div className="text-xs text-blue-600">{item.campanhas_ativas} campanhas ativas</div>
                  </div>
                </td>
                <td className="px-6 py-4">
                  <div className="text-sm">
                    <div className="font-medium">{item.populacao.toLocaleString()} hab</div>
                    <div className="text-gray-500">Público: {item.publico_alvo.toLocaleString()}</div>
                    <div className="text-blue-600">Penetração: {item.penetracao_atual.toFixed(2)}%</div>
                  </div>
                </td>
                <td className="px-6 py-4">
                  <div className="text-sm">
                    <div className="flex items-center gap-2">
                      <span className="font-bold text-green-600">{item.realizado_motoristas}</span>
                      <span className="text-gray-400">/</span>
                      <span className="font-medium">{item.meta_motoristas}</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2 mt-1">
                      <div 
                        className="bg-blue-600 h-2 rounded-full" 
                        style={{ width: `${Math.min(item.percentual_motoristas, 100)}%` }}
                      ></div>
                    </div>
                    <div className="text-xs text-gray-500 mt-1">
                      {item.percentual_motoristas.toFixed(0)}% concluído
                    </div>
                  </div>
                </td>
                <td className="px-6 py-4">
                  <div className="text-sm">
                    <div className="flex items-center gap-2">
                      <span className="font-bold text-green-600">{item.realizado_corridas}</span>
                      <span className="text-gray-400">/</span>
                      <span className="font-medium">{item.meta_corridas}</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2 mt-1">
                      <div 
                        className="bg-emerald-600 h-2 rounded-full" 
                        style={{ width: `${Math.min(item.percentual_corridas, 100)}%` }}
                      ></div>
                    </div>
                    <div className="text-xs text-gray-500 mt-1">
                      {item.percentual_corridas.toFixed(0)}% concluído
                    </div>
                  </div>
                </td>
                <td className="px-6 py-4">
                  <div className="text-sm">
                    <div className="font-medium text-blue-600">
                      R$ {item.orcamento_empenhado.toLocaleString()}
                    </div>
                    <div className="text-xs text-gray-500">
                      Pago: R$ {item.orcamento_pago.toLocaleString()}
                    </div>
                    <div className="text-xs text-green-600">
                      Receita: R$ {item.receita_estimada.toLocaleString()}
                    </div>
                  </div>
                </td>
                <td className="px-6 py-4">
                  <div className="text-sm">
                    <span className={`inline-flex px-2 py-1 text-xs font-medium rounded-full ${
                      item.status_execucao.includes('87%') ? 'bg-blue-100 text-blue-800' :
                      item.status_execucao.includes('execução') ? 'bg-green-100 text-green-800' :
                      item.status_execucao.includes('Planejamento') ? 'bg-yellow-100 text-yellow-800' :
                      'bg-gray-100 text-gray-800'
                    }`}>
                      {item.status_execucao}
                    </span>
                  </div>
                </td>
                <td className="px-6 py-4">
                  <div className="flex gap-2">
                    <button
                      className="p-2 rounded-lg bg-yellow-100 hover:bg-yellow-200 text-yellow-700"
                      title="Editar"
                      onClick={() => onEditar && onEditar(item)}
                    >
                      <Edit className="w-4 h-4" />
                    </button>
                    <button
                      className="p-2 rounded-lg bg-red-100 hover:bg-red-200 text-red-700"
                      title="Apagar"
                      onClick={() => window.onApagarMeta && window.onApagarMeta(item)}
                    >
                      <X className="w-4 h-4" />
                    </button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}

export default TabelaExecucaoComCruzamento
