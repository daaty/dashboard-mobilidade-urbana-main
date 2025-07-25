import React from 'react';
import { AlertTriangle, CheckCircle, XCircle, Info } from 'lucide-react';

// Exemplo de alertas mockados (pode ser substituído por props/data)
const mockAlertas = [
  {
    tipo: 'crítico',
    titulo: 'Receita abaixo do esperado',
    mensagem: 'A receita do período está 15% abaixo da meta.',
    icone: <XCircle className="text-red-600 w-6 h-6" />,
  },
  {
    tipo: 'aviso',
    titulo: 'Avaliação média em queda',
    mensagem: 'A avaliação dos passageiros caiu para 4.1.',
    icone: <AlertTriangle className="text-yellow-500 w-6 h-6" />,
  },
  {
    tipo: 'sucesso',
    titulo: 'Meta de corridas atingida',
    mensagem: 'A meta de corridas concluídas foi superada!',
    icone: <CheckCircle className="text-green-600 w-6 h-6" />,
  },
  {
    tipo: 'info',
    titulo: 'Novo relatório disponível',
    mensagem: 'O relatório executivo mensal já pode ser baixado.',
    icone: <Info className="text-blue-500 w-6 h-6" />,
  },
];

export function SistemaAlertas({ data }) {
  // Aqui você pode usar data.alertas ou mockAlertas
  const alertas = (data && data.alertas) || mockAlertas;

  return (
    <div className="bg-white dark:bg-gray-900 rounded-xl shadow p-6 h-full flex flex-col gap-4 border border-gray-100 dark:border-gray-800">
      <h2 className="text-lg font-bold mb-2 text-gray-900 dark:text-white flex items-center gap-2">
        <AlertTriangle className="w-5 h-5 text-yellow-500" /> Alertas do Sistema
      </h2>
      <div className="flex flex-col gap-3">
        {alertas.length === 0 && (
          <div className="text-gray-400 text-sm flex items-center gap-2">
            <CheckCircle className="w-4 h-4 text-green-500" /> Nenhum alerta ativo no momento.
          </div>
        )}
        {alertas.map((alerta, idx) => (
          <div
            key={idx}
            className={`flex items-start gap-3 rounded-lg p-3 border-l-4 shadow-sm
              ${
                alerta.tipo === 'crítico'
                  ? 'border-red-600 bg-red-50 dark:bg-red-900/20'
                  : alerta.tipo === 'aviso'
                  ? 'border-yellow-500 bg-yellow-50 dark:bg-yellow-900/20'
                  : alerta.tipo === 'sucesso'
                  ? 'border-green-600 bg-green-50 dark:bg-green-900/20'
                  : 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
              }
            `}
          >
            <div className="mt-1">{alerta.icone}</div>
            <div>
              <div className="font-semibold text-gray-900 dark:text-white mb-0.5">{alerta.titulo}</div>
              <div className="text-sm text-gray-700 dark:text-gray-300">{alerta.mensagem}</div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
