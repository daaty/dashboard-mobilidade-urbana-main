import React, { useState, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Upload, 
  FileText, 
  Check, 
  X, 
  AlertTriangle, 
  Info,
  Download,
  FileSpreadsheet,
  Database,
  Clock,
  CheckCircle,
  XCircle,
  RefreshCw
} from 'lucide-react';

const ImportacaoAvancada = () => {
  const [activeTab, setActiveTab] = useState('upload');
  const [dragActive, setDragActive] = useState(false);
  const [arquivoSelecionado, setArquivoSelecionado] = useState(null);
  const [previewData, setPreviewData] = useState(null);
  const [mappingColumns, setMappingColumns] = useState({});
  const [tipoImportacao, setTipoImportacao] = useState('corridas');
  const [statusImportacao, setStatusImportacao] = useState(null);
  const [historicoImportacoes, setHistoricoImportacoes] = useState([]);
  const [loading, setLoading] = useState(false);

  // Carregar histórico de importações
  React.useEffect(() => {
    carregarHistorico();
  }, []);

  const carregarHistorico = async () => {
    try {
      const response = await fetch('/api/import/history');
      const data = await response.json();
      setHistoricoImportacoes(data.imports || []);
    } catch (error) {
      console.error('Erro ao carregar histórico:', error);
    }
  };

  // Drag and drop handlers
  const handleDrag = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  }, []);

  const handleDrop = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFiles(e.dataTransfer.files);
    }
  }, []);

  const handleFiles = (files) => {
    const file = files[0];
    if (file && (file.type.includes('excel') || file.type.includes('csv') || file.name.endsWith('.xlsx') || file.name.endsWith('.csv'))) {
      setArquivoSelecionado(file);
      gerarPreview(file);
    } else {
      alert('Por favor, selecione um arquivo Excel (.xlsx) ou CSV (.csv)');
    }
  };

  const gerarPreview = async (file) => {
    setLoading(true);
    const formData = new FormData();
    formData.append('file', file);
    formData.append('import_type', tipoImportacao);

    try {
      const response = await fetch('/api/import/preview', {
        method: 'POST',
        body: formData
      });

      const data = await response.json();
      
      if (data.success) {
        setPreviewData(data);
        setMappingColumns(data.detected_mapping || {});
      } else {
        alert(`Erro ao gerar preview: ${data.error}`);
      }
    } catch (error) {
      console.error('Erro ao gerar preview:', error);
      alert('Erro ao processar arquivo');
    } finally {
      setLoading(false);
    }
  };

  const executarImportacao = async () => {
    if (!arquivoSelecionado || !previewData) return;

    setLoading(true);
    setStatusImportacao({ status: 'processing', message: 'Processando importação...' });

    const formData = new FormData();
    formData.append('file', arquivoSelecionado);
    formData.append('import_type', tipoImportacao);
    formData.append('column_mapping', JSON.stringify(mappingColumns));

    try {
      const response = await fetch('/api/import/execute', {
        method: 'POST',
        body: formData
      });

      const data = await response.json();
      
      if (data.success) {
        setStatusImportacao({
          status: 'success',
          message: `Importação concluída! ${data.imported} registros importados`,
          details: data
        });
        carregarHistorico();
      } else {
        setStatusImportacao({
          status: 'error',
          message: `Erro na importação: ${data.error}`,
          details: data
        });
      }
    } catch (error) {
      setStatusImportacao({
        status: 'error',
        message: 'Erro ao executar importação',
        details: { error: error.message }
      });
    } finally {
      setLoading(false);
    }
  };

  const resetarImportacao = () => {
    setArquivoSelecionado(null);
    setPreviewData(null);
    setMappingColumns({});
    setStatusImportacao(null);
  };

  const baixarTemplate = (tipo) => {
    const templates = {
      corridas: '/api/import/template/corridas',
      motoristas: '/api/import/template/motoristas',
      metas: '/api/import/template/metas'
    };

    const link = document.createElement('a');
    link.href = templates[tipo];
    link.download = `template_${tipo}.xlsx`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const formatarDataHora = (timestamp) => {
    return new Date(timestamp).toLocaleString('pt-BR');
  };

  const tabs = [
    { id: 'upload', label: 'Upload de Arquivo', icon: Upload },
    { id: 'historico', label: 'Histórico', icon: Clock },
    { id: 'templates', label: 'Templates', icon: Download }
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Database className="h-6 w-6 text-blue-600" />
          <h2 className="text-2xl font-bold text-gray-900">Importação de Dados</h2>
        </div>
      </div>

      {/* Tabs */}
      <div className="border-b">
        <div className="flex space-x-8">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`py-2 px-1 border-b-2 font-medium text-sm transition-colors ${
                  activeTab === tab.id
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700'
                }`}
              >
                <div className="flex items-center gap-2">
                  <Icon className="h-4 w-4" />
                  {tab.label}
                </div>
              </button>
            );
          })}
        </div>
      </div>

      {/* Content */}
      <AnimatePresence mode="wait">
        {activeTab === 'upload' && (
          <motion.div
            key="upload"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="space-y-6"
          >
            {/* Seleção do Tipo de Importação */}
            <div className="bg-white rounded-lg border p-4">
              <h3 className="text-lg font-medium mb-4">Tipo de Importação</h3>
              <div className="grid grid-cols-3 gap-4">
                {[
                  { id: 'corridas', label: 'Corridas', icon: FileText, desc: 'Importar dados de corridas' },
                  { id: 'motoristas', label: 'Motoristas', icon: FileText, desc: 'Importar dados de motoristas' },
                  { id: 'metas', label: 'Metas', icon: FileText, desc: 'Importar metas por cidade' }
                ].map((tipo) => {
                  const Icon = tipo.icon;
                  return (
                    <button
                      key={tipo.id}
                      onClick={() => setTipoImportacao(tipo.id)}
                      className={`p-4 border-2 rounded-lg text-left transition-colors ${
                        tipoImportacao === tipo.id
                          ? 'border-blue-500 bg-blue-50'
                          : 'border-gray-200 hover:border-gray-300'
                      }`}
                    >
                      <Icon className="h-6 w-6 mb-2 text-gray-600" />
                      <div className="font-medium text-gray-900">{tipo.label}</div>
                      <div className="text-sm text-gray-500">{tipo.desc}</div>
                    </button>
                  );
                })}
              </div>
            </div>

            {/* Upload Area */}
            <div
              className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
                dragActive
                  ? 'border-blue-500 bg-blue-50'
                  : 'border-gray-300 hover:border-gray-400'
              }`}
              onDragEnter={handleDrag}
              onDragLeave={handleDrag}
              onDragOver={handleDrag}
              onDrop={handleDrop}
            >
              {arquivoSelecionado ? (
                <div className="space-y-4">
                  <CheckCircle className="h-12 w-12 text-green-500 mx-auto" />
                  <div>
                    <p className="text-lg font-medium text-gray-900">
                      {arquivoSelecionado.name}
                    </p>
                    <p className="text-sm text-gray-500">
                      {(arquivoSelecionado.size / 1024 / 1024).toFixed(2)} MB
                    </p>
                  </div>
                  <button
                    onClick={resetarImportacao}
                    className="text-blue-600 hover:text-blue-800 text-sm font-medium"
                  >
                    Selecionar outro arquivo
                  </button>
                </div>
              ) : (
                <div>
                  <Upload className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                  <p className="text-lg text-gray-600 mb-2">
                    Arraste e solte seu arquivo aqui
                  </p>
                  <p className="text-sm text-gray-500 mb-4">
                    ou clique para selecionar
                  </p>
                  <input
                    type="file"
                    accept=".xlsx,.xls,.csv"
                    onChange={(e) => handleFiles(e.target.files)}
                    className="hidden"
                    id="file-upload"
                  />
                  <label
                    htmlFor="file-upload"
                    className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 cursor-pointer"
                  >
                    Selecionar Arquivo
                  </label>
                  <p className="text-xs text-gray-500 mt-2">
                    Formatos suportados: .xlsx, .xls, .csv (máx. 16MB)
                  </p>
                </div>
              )}
            </div>

            {/* Preview dos Dados */}
            {previewData && (
              <div className="bg-white rounded-lg border p-6 space-y-4">
                <h3 className="text-lg font-medium flex items-center gap-2">
                  <FileSpreadsheet className="h-5 w-5" />
                  Preview dos Dados ({previewData.total_rows} linhas)
                </h3>

                {/* Mapeamento de Colunas */}
                <div className="space-y-3">
                  <h4 className="font-medium text-gray-700">Mapeamento de Colunas</h4>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {Object.entries(previewData.required_fields || {}).map(([field, options]) => (
                      <div key={field} className="space-y-1">
                        <label className="block text-sm font-medium text-gray-700">
                          {field} <span className="text-red-500">*</span>
                        </label>
                        <select
                          value={mappingColumns[field] || ''}
                          onChange={(e) => setMappingColumns(prev => ({ ...prev, [field]: e.target.value }))}
                          className="w-full px-3 py-2 border rounded-lg"
                          required
                        >
                          <option value="">Selecionar coluna...</option>
                          {previewData.columns.map(col => (
                            <option key={col} value={col}>{col}</option>
                          ))}
                        </select>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Amostra dos dados */}
                <div className="overflow-x-auto">
                  <table className="min-w-full border border-gray-200">
                    <thead className="bg-gray-50">
                      <tr>
                        {previewData.columns.map(col => (
                          <th key={col} className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">
                            {col}
                          </th>
                        ))}
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-200">
                      {previewData.sample_data.slice(0, 3).map((row, idx) => (
                        <tr key={idx}>
                          {previewData.columns.map(col => (
                            <td key={col} className="px-4 py-2 text-sm text-gray-900">
                              {String(row[col] || '')}
                            </td>
                          ))}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>

                {/* Botão de Importação */}
                <div className="flex justify-end pt-4">
                  <button
                    onClick={executarImportacao}
                    disabled={loading || Object.keys(mappingColumns).length === 0}
                    className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
                  >
                    {loading ? (
                      <>
                        <RefreshCw className="h-4 w-4 animate-spin" />
                        Processando...
                      </>
                    ) : (
                      <>
                        <Database className="h-4 w-4" />
                        Executar Importação
                      </>
                    )}
                  </button>
                </div>
              </div>
            )}

            {/* Status da Importação */}
            {statusImportacao && (
              <motion.div
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                className={`p-4 rounded-lg border ${
                  statusImportacao.status === 'success'
                    ? 'bg-green-50 border-green-200'
                    : statusImportacao.status === 'error'
                    ? 'bg-red-50 border-red-200'
                    : 'bg-blue-50 border-blue-200'
                }`}
              >
                <div className="flex items-center gap-3">
                  {statusImportacao.status === 'success' && <CheckCircle className="h-5 w-5 text-green-600" />}
                  {statusImportacao.status === 'error' && <XCircle className="h-5 w-5 text-red-600" />}
                  {statusImportacao.status === 'processing' && <RefreshCw className="h-5 w-5 text-blue-600 animate-spin" />}
                  
                  <div>
                    <p className="font-medium">{statusImportacao.message}</p>
                    {statusImportacao.details && statusImportacao.details.error_details && (
                      <div className="mt-2 text-sm text-gray-600">
                        <p className="font-medium">Detalhes dos erros:</p>
                        <ul className="list-disc list-inside">
                          {statusImportacao.details.error_details.map((error, idx) => (
                            <li key={idx}>{error}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                </div>
              </motion.div>
            )}
          </motion.div>
        )}

        {activeTab === 'historico' && (
          <motion.div
            key="historico"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="space-y-4"
          >
            <div className="bg-white rounded-lg border">
              <div className="p-6">
                <h3 className="text-lg font-medium mb-4">Histórico de Importações</h3>
                
                {historicoImportacoes.length === 0 ? (
                  <div className="text-center py-8 text-gray-500">
                    <Clock className="h-12 w-12 mx-auto mb-3 text-gray-300" />
                    <p>Nenhuma importação realizada ainda</p>
                  </div>
                ) : (
                  <div className="space-y-3">
                    {historicoImportacoes.map((importacao) => (
                      <div key={importacao.id} className="border rounded-lg p-4">
                        <div className="flex items-center justify-between">
                          <div className="flex items-center gap-3">
                            <div className={`w-3 h-3 rounded-full ${
                              importacao.status === 'completed' ? 'bg-green-500' :
                              importacao.status === 'completed_with_errors' ? 'bg-yellow-500' :
                              importacao.status === 'failed' ? 'bg-red-500' : 'bg-gray-500'
                            }`} />
                            <div>
                              <p className="font-medium">{importacao.filename}</p>
                              <p className="text-sm text-gray-500">
                                {importacao.import_type} • {formatarDataHora(importacao.started_at)}
                              </p>
                            </div>
                          </div>
                          <div className="text-right">
                            <p className="text-sm font-medium">
                              {importacao.success_rows || 0} importados
                            </p>
                            {importacao.error_rows > 0 && (
                              <p className="text-sm text-red-600">
                                {importacao.error_rows} erros
                              </p>
                            )}
                          </div>
                        </div>
                        
                        {importacao.error_message && (
                          <div className="mt-3 p-2 bg-red-50 rounded text-sm text-red-700">
                            {importacao.error_message}
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          </motion.div>
        )}

        {activeTab === 'templates' && (
          <motion.div
            key="templates"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="space-y-6"
          >
            <div className="bg-white rounded-lg border p-6">
              <h3 className="text-lg font-medium mb-4">Templates de Importação</h3>
              <p className="text-gray-600 mb-6">
                Baixe os templates para garantir que seus dados estejam no formato correto:
              </p>
              
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {[
                  {
                    id: 'corridas',
                    title: 'Template de Corridas',
                    description: 'Campos: data, usuario_nome, motorista_nome, municipio, status, valor, etc.',
                    icon: FileText
                  },
                  {
                    id: 'motoristas',
                    title: 'Template de Motoristas',
                    description: 'Campos: nome, municipio, telefone, status, data_cadastro',
                    icon: FileText
                  },
                  {
                    id: 'metas',
                    title: 'Template de Metas',
                    description: 'Campos: municipio, mes, meta_corridas, meta_receita, meta_motoristas',
                    icon: FileText
                  }
                ].map((template) => {
                  const Icon = template.icon;
                  return (
                    <div key={template.id} className="border rounded-lg p-4">
                      <Icon className="h-8 w-8 text-blue-600 mb-3" />
                      <h4 className="font-medium text-gray-900 mb-2">{template.title}</h4>
                      <p className="text-sm text-gray-600 mb-4">{template.description}</p>
                      <button
                        onClick={() => baixarTemplate(template.id)}
                        className="w-full px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center justify-center gap-2"
                      >
                        <Download className="h-4 w-4" />
                        Baixar Template
                      </button>
                    </div>
                  );
                })}
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default ImportacaoAvancada;
