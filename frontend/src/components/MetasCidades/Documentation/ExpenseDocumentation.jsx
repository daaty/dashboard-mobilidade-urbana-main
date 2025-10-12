import React, { useState, useRef } from 'react';
import { Upload, File, Check, X, Eye, Download, Trash2, Edit2, AlertCircle, FileText, Image as ImageIcon } from 'lucide-react';

/**
 * Componente para gerenciar documentação de gastos
 * Features:
 * - Upload de comprovantes (PDF, imagens)
 * - Vinculação com campanhas
 * - Categorização
 * - Workflow de aprovação (Pendente → Aprovado → Liquidado)
 * 
 * @param {string} fase - Fase da campanha
 * @param {string} cidade - Cidade (opcional)
 * @param {Object} campanha - Campanha vinculada (opcional)
 * @param {Function} onDocumentAdded - Callback quando documento é adicionado
 */
const ExpenseDocumentation = ({ fase, cidade, campanha, onDocumentAdded }) => {
  const [documents, setDocuments] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [selectedDoc, setSelectedDoc] = useState(null);
  const [editMode, setEditMode] = useState(null);
  const fileInputRef = useRef(null);
  
  // Categorias de gastos
  const categorias = [
    { value: 'facebook_ads', label: '📱 Anúncios Facebook', color: 'blue' },
    { value: 'google_ads', label: '🔍 Anúncios Google', color: 'red' },
    { value: 'instagram_ads', label: '📷 Anúncios Instagram', color: 'purple' },
    { value: 'hotel', label: '🏨 Hospedagem', color: 'indigo' },
    { value: 'restaurante', label: '🍽️ Alimentação', color: 'yellow' },
    { value: 'combustivel', label: '⛽ Combustível', color: 'green' },
    { value: 'transporte', label: '🚗 Transporte', color: 'cyan' },
    { value: 'material_grafico', label: '🖨️ Material Gráfico', color: 'pink' },
    { value: 'evento', label: '🎉 Evento/Divulgação', color: 'orange' },
    { value: 'outros', label: '📦 Outros', color: 'gray' },
  ];
  
  // Status de documentação
  const statusOptions = [
    { value: 'pendente', label: 'Pendente', color: 'yellow', icon: AlertCircle },
    { value: 'aprovado', label: 'Aprovado', color: 'green', icon: Check },
    { value: 'rejeitado', label: 'Rejeitado', color: 'red', icon: X },
  ];
  
  // Tipos de documento
  const tiposDocumento = [
    { value: 'comprovante', label: 'Comprovante de Pagamento' },
    { value: 'nota_fiscal', label: 'Nota Fiscal' },
    { value: 'recibo', label: 'Recibo' },
    { value: 'orcamento', label: 'Orçamento' },
    { value: 'contrato', label: 'Contrato' },
  ];
  
  // Handler de upload de arquivos
  const handleFileUpload = async (files) => {
    if (!files || files.length === 0) return;
    
    setUploading(true);
    
    try {
      const newDocuments = Array.from(files).map((file, index) => {
        // Validar tamanho (máx 10MB)
        if (file.size > 10 * 1024 * 1024) {
          throw new Error(`Arquivo ${file.name} excede 10MB`);
        }
        
        // Validar tipo
        const allowedTypes = ['application/pdf', 'image/jpeg', 'image/jpg', 'image/png'];
        if (!allowedTypes.includes(file.type)) {
          throw new Error(`Tipo de arquivo não permitido: ${file.type}`);
        }
        
        return {
          id: `doc_${Date.now()}_${index}`,
          arquivo: file,
          nome: file.name,
          tamanho: file.size,
          tipo_arquivo: file.type,
          data_upload: new Date().toISOString(),
          
          // Metadados editáveis
          tipo_documento: 'comprovante',
          categoria: 'outros',
          descricao: '',
          valor: 0,
          fornecedor: '',
          data_despesa: new Date().toISOString().split('T')[0],
          possui_nota_fiscal: false,
          numero_nf: '',
          
          // Status e vinculação
          status: 'pendente',
          fase: fase || '',
          cidade: cidade || '',
          campanha_vinculada: campanha?.id || null,
          campanha_nome: campanha?.nome || '',
          
          // URL temporária para preview
          url_preview: URL.createObjectURL(file),
        };
      });
      
      setDocuments(prev => [...prev, ...newDocuments]);
      
      // Callback para componente pai
      if (onDocumentAdded) {
        onDocumentAdded(newDocuments);
      }
      
      // Limpar input
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
      
      console.log(`✅ ${newDocuments.length} documento(s) adicionado(s)`);
      
    } catch (error) {
      console.error('❌ Erro no upload:', error);
      alert(error.message);
    } finally {
      setUploading(false);
    }
  };
  
  // Atualizar documento
  const updateDocument = (docId, updates) => {
    setDocuments(prev => prev.map(doc =>
      doc.id === docId ? { ...doc, ...updates } : doc
    ));
  };
  
  // Remover documento
  const removeDocument = (docId) => {
    if (!confirm('Tem certeza que deseja remover este documento?')) return;
    
    const doc = documents.find(d => d.id === docId);
    if (doc?.url_preview) {
      URL.revokeObjectURL(doc.url_preview);
    }
    
    setDocuments(prev => prev.filter(d => d.id !== docId));
  };
  
  // Aprovar documento
  const approveDocument = (docId) => {
    updateDocument(docId, { 
      status: 'aprovado',
      data_aprovacao: new Date().toISOString()
    });
  };
  
  // Rejeitar documento
  const rejectDocument = (docId, motivo = '') => {
    updateDocument(docId, { 
      status: 'rejeitado',
      motivo_rejeicao: motivo,
      data_rejeicao: new Date().toISOString()
    });
  };
  
  // Formatar tamanho de arquivo
  const formatFileSize = (bytes) => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(2)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(2)} MB`;
  };
  
  // Formatar moeda
  const formatCurrency = (value) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL'
    }).format(value || 0);
  };
  
  // Estatísticas
  const stats = {
    total: documents.length,
    pendentes: documents.filter(d => d.status === 'pendente').length,
    aprovados: documents.filter(d => d.status === 'aprovado').length,
    rejeitados: documents.filter(d => d.status === 'rejeitado').length,
    valor_total: documents.reduce((sum, d) => sum + (parseFloat(d.valor) || 0), 0),
    com_nf: documents.filter(d => d.possui_nota_fiscal).length,
  };
  
  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-xl font-bold text-gray-900">Documentação de Gastos</h3>
          <p className="text-sm text-gray-600 mt-1">
            {fase && `Fase: ${fase}`}
            {cidade && ` • Cidade: ${cidade}`}
            {campanha && ` • Campanha: ${campanha.nome}`}
          </p>
        </div>
        
        <button
          onClick={() => fileInputRef.current?.click()}
          disabled={uploading}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 flex items-center gap-2"
        >
          <Upload className="h-4 w-4" />
          {uploading ? 'Enviando...' : 'Adicionar Documentos'}
        </button>
        
        <input
          ref={fileInputRef}
          type="file"
          multiple
          accept=".pdf,.jpg,.jpeg,.png"
          onChange={(e) => handleFileUpload(e.target.files)}
          className="hidden"
        />
      </div>
      
      {/* Upload Area (drag & drop) */}
      <div 
        className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center hover:border-blue-500 transition-colors cursor-pointer"
        onClick={() => fileInputRef.current?.click()}
        onDragOver={(e) => {
          e.preventDefault();
          e.currentTarget.classList.add('border-blue-500', 'bg-blue-50');
        }}
        onDragLeave={(e) => {
          e.currentTarget.classList.remove('border-blue-500', 'bg-blue-50');
        }}
        onDrop={(e) => {
          e.preventDefault();
          e.currentTarget.classList.remove('border-blue-500', 'bg-blue-50');
          handleFileUpload(e.dataTransfer.files);
        }}
      >
        <Upload className="mx-auto h-12 w-12 text-gray-400 mb-4" />
        <p className="text-gray-600 mb-2 font-medium">
          Arraste arquivos aqui ou clique para selecionar
        </p>
        <p className="text-sm text-gray-500">
          Formatos aceitos: PDF, JPG, PNG • Tamanho máximo: 10MB por arquivo
        </p>
      </div>
      
      {/* Estatísticas */}
      {documents.length > 0 && (
        <div className="grid grid-cols-2 md:grid-cols-6 gap-4">
          <div className="bg-blue-50 p-4 rounded-lg">
            <p className="text-2xl font-bold text-blue-600">{stats.total}</p>
            <p className="text-sm text-gray-600">Total</p>
          </div>
          
          <div className="bg-yellow-50 p-4 rounded-lg">
            <p className="text-2xl font-bold text-yellow-600">{stats.pendentes}</p>
            <p className="text-sm text-gray-600">Pendentes</p>
          </div>
          
          <div className="bg-green-50 p-4 rounded-lg">
            <p className="text-2xl font-bold text-green-600">{stats.aprovados}</p>
            <p className="text-sm text-gray-600">Aprovados</p>
          </div>
          
          <div className="bg-red-50 p-4 rounded-lg">
            <p className="text-2xl font-bold text-red-600">{stats.rejeitados}</p>
            <p className="text-sm text-gray-600">Rejeitados</p>
          </div>
          
          <div className="bg-purple-50 p-4 rounded-lg">
            <p className="text-2xl font-bold text-purple-600">{stats.com_nf}</p>
            <p className="text-sm text-gray-600">Com NF</p>
          </div>
          
          <div className="bg-indigo-50 p-4 rounded-lg">
            <p className="text-lg font-bold text-indigo-600">{formatCurrency(stats.valor_total)}</p>
            <p className="text-sm text-gray-600">Valor Total</p>
          </div>
        </div>
      )}
      
      {/* Lista de Documentos */}
      <div className="space-y-3">
        <h4 className="font-semibold text-gray-700 flex items-center gap-2">
          <FileText className="h-5 w-5" />
          Documentos Anexados ({documents.length})
        </h4>
        
        {documents.length === 0 ? (
          <div className="text-center py-12 bg-gray-50 rounded-lg">
            <File className="mx-auto h-16 w-16 text-gray-300 mb-4" />
            <p className="text-gray-500 text-sm italic">
              Nenhum documento anexado ainda
            </p>
            <p className="text-gray-400 text-xs mt-2">
              Adicione comprovantes, notas fiscais ou recibos acima
            </p>
          </div>
        ) : (
          documents.map((doc) => {
            const categoria = categorias.find(c => c.value === doc.categoria);
            const status = statusOptions.find(s => s.value === doc.status);
            const StatusIcon = status?.icon || AlertCircle;
            
            const isEditing = editMode === doc.id;
            
            return (
              <div 
                key={doc.id}
                className={`p-4 border-2 rounded-lg hover:shadow-md transition-all ${
                  doc.status === 'aprovado' ? 'border-green-200 bg-green-50' :
                  doc.status === 'rejeitado' ? 'border-red-200 bg-red-50' :
                  'border-gray-200 bg-white'
                }`}
              >
                <div className="flex items-start gap-4">
                  {/* Ícone do arquivo */}
                  <div className="flex-shrink-0">
                    {doc.tipo_arquivo.includes('pdf') ? (
                      <FileText className="h-10 w-10 text-red-600" />
                    ) : (
                      <ImageIcon className="h-10 w-10 text-blue-600" />
                    )}
                  </div>
                  
                  {/* Conteúdo */}
                  <div className="flex-1 min-w-0">
                    {/* Linha 1: Nome e ações */}
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex-1">
                        <p className="font-medium text-gray-900 truncate">{doc.nome}</p>
                        <p className="text-xs text-gray-500">
                          {formatFileSize(doc.tamanho)} • 
                          {new Date(doc.data_upload).toLocaleDateString('pt-BR')}
                        </p>
                      </div>
                      
                      <div className="flex items-center gap-2 ml-4">
                        {/* Status */}
                        <span className={`px-3 py-1 rounded-full text-xs font-medium flex items-center gap-1 bg-${status?.color}-100 text-${status?.color}-800`}>
                          <StatusIcon className="h-3 w-3" />
                          {status?.label}
                        </span>
                        
                        {/* Ações */}
                        <button
                          onClick={() => setEditMode(isEditing ? null : doc.id)}
                          className="p-1.5 hover:bg-gray-200 rounded"
                          title="Editar"
                        >
                          <Edit2 className="h-4 w-4 text-gray-600" />
                        </button>
                        
                        <a
                          href={doc.url_preview}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="p-1.5 hover:bg-gray-200 rounded"
                          title="Visualizar"
                        >
                          <Eye className="h-4 w-4 text-gray-600" />
                        </a>
                        
                        <button
                          onClick={() => removeDocument(doc.id)}
                          className="p-1.5 hover:bg-red-100 rounded"
                          title="Remover"
                        >
                          <Trash2 className="h-4 w-4 text-red-600" />
                        </button>
                      </div>
                    </div>
                    
                    {/* Linha 2: Categoria e tipo */}
                    {!isEditing ? (
                      <div className="flex flex-wrap gap-2 mb-2">
                        <span className="px-2 py-1 bg-gray-100 rounded text-xs">
                          {categoria?.label || '📦 Outros'}
                        </span>
                        <span className="px-2 py-1 bg-gray-100 rounded text-xs">
                          {tiposDocumento.find(t => t.value === doc.tipo_documento)?.label || 'Comprovante'}
                        </span>
                        {doc.valor > 0 && (
                          <span className="px-2 py-1 bg-blue-100 text-blue-800 rounded text-xs font-medium">
                            {formatCurrency(doc.valor)}
                          </span>
                        )}
                        {doc.possui_nota_fiscal && (
                          <span className="px-2 py-1 bg-green-100 text-green-800 rounded text-xs">
                            ✓ NF: {doc.numero_nf || 'S/N'}
                          </span>
                        )}
                      </div>
                    ) : (
                      <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-3">
                        <select
                          value={doc.categoria}
                          onChange={(e) => updateDocument(doc.id, { categoria: e.target.value })}
                          className="px-2 py-1 border rounded text-sm"
                        >
                          {categorias.map(cat => (
                            <option key={cat.value} value={cat.value}>{cat.label}</option>
                          ))}
                        </select>
                        
                        <select
                          value={doc.tipo_documento}
                          onChange={(e) => updateDocument(doc.id, { tipo_documento: e.target.value })}
                          className="px-2 py-1 border rounded text-sm"
                        >
                          {tiposDocumento.map(tipo => (
                            <option key={tipo.value} value={tipo.value}>{tipo.label}</option>
                          ))}
                        </select>
                        
                        <input
                          type="number"
                          step="0.01"
                          value={doc.valor}
                          onChange={(e) => updateDocument(doc.id, { valor: parseFloat(e.target.value) || 0 })}
                          placeholder="Valor (R$)"
                          className="px-2 py-1 border rounded text-sm"
                        />
                        
                        <input
                          type="date"
                          value={doc.data_despesa}
                          onChange={(e) => updateDocument(doc.id, { data_despesa: e.target.value })}
                          className="px-2 py-1 border rounded text-sm"
                        />
                        
                        <input
                          type="text"
                          value={doc.fornecedor}
                          onChange={(e) => updateDocument(doc.id, { fornecedor: e.target.value })}
                          placeholder="Fornecedor"
                          className="px-2 py-1 border rounded text-sm col-span-2"
                        />
                        
                        <label className="flex items-center gap-2 col-span-2">
                          <input
                            type="checkbox"
                            checked={doc.possui_nota_fiscal}
                            onChange={(e) => updateDocument(doc.id, { possui_nota_fiscal: e.target.checked })}
                            className="rounded"
                          />
                          <span className="text-sm">Possui Nota Fiscal</span>
                          {doc.possui_nota_fiscal && (
                            <input
                              type="text"
                              value={doc.numero_nf}
                              onChange={(e) => updateDocument(doc.id, { numero_nf: e.target.value })}
                              placeholder="Número NF"
                              className="px-2 py-1 border rounded text-sm flex-1"
                            />
                          )}
                        </label>
                      </div>
                    )}
                    
                    {/* Linha 3: Descrição */}
                    {isEditing && (
                      <textarea
                        value={doc.descricao}
                        onChange={(e) => updateDocument(doc.id, { descricao: e.target.value })}
                        placeholder="Descrição do gasto..."
                        className="w-full px-3 py-2 border rounded text-sm resize-none"
                        rows={2}
                      />
                    )}
                    
                    {!isEditing && doc.descricao && (
                      <p className="text-sm text-gray-600 mb-2">{doc.descricao}</p>
                    )}
                    
                    {/* Linha 4: Ações de aprovação */}
                    {doc.status === 'pendente' && (
                      <div className="flex gap-2 mt-3 pt-3 border-t">
                        <button
                          onClick={() => approveDocument(doc.id)}
                          className="px-3 py-1.5 bg-green-600 text-white rounded text-sm hover:bg-green-700 flex items-center gap-1"
                        >
                          <Check className="h-4 w-4" />
                          Aprovar
                        </button>
                        
                        <button
                          onClick={() => {
                            const motivo = prompt('Motivo da rejeição (opcional):');
                            rejectDocument(doc.id, motivo || '');
                          }}
                          className="px-3 py-1.5 bg-red-600 text-white rounded text-sm hover:bg-red-700 flex items-center gap-1"
                        >
                          <X className="h-4 w-4" />
                          Rejeitar
                        </button>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
};

export default ExpenseDocumentation;
