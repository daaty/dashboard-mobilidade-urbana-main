import { useState, useRef } from 'react'
import { motion } from 'framer-motion'
import { Settings, Save, TestTube, AlertCircle, CheckCircle, ExternalLink, FileSpreadsheet, Upload, FileCheck, Trash2 } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Alert, AlertDescription } from '@/components/ui/alert'

export function ConfiguracaoSheets() {
  const [config, setConfig] = useState({
    spreadsheet_id_corridas: '',
    spreadsheet_id_metas: ''
  })
  const [loading, setLoading] = useState(false)
  const [testResult, setTestResult] = useState(null)
  const [saveResult, setSaveResult] = useState(null)
  
  // Estados para importação de arquivos
  const [uploadFile, setUploadFile] = useState(null)
  const [uploadPreview, setUploadPreview] = useState(null)
  const [importResult, setImportResult] = useState(null)
  const [importLoading, setImportLoading] = useState(false)
  const fileInputRef = useRef(null)

  const handleInputChange = (field, value) => {
    setConfig(prev => ({
      ...prev,
      [field]: value
    }))
  }

  const extractSpreadsheetId = (url) => {
    const match = url.match(/\/spreadsheets\/d\/([a-zA-Z0-9-_]+)/)
    return match ? match[1] : url
  }

  const handleUrlPaste = (field, value) => {
    const id = extractSpreadsheetId(value)
    handleInputChange(field, id)
  }

  const testConnection = async () => {
    try {
      setLoading(true)
      setTestResult(null)
      
      // Simular teste de conexão
      await new Promise(resolve => setTimeout(resolve, 2000))
      
      setTestResult({
        status: 'success',
        message: 'Conexão testada com sucesso! Dados mock carregados.',
        details: {
          corridas_count: 7,
          metas_count: 3
        }
      })
    } catch (error) {
      setTestResult({
        status: 'error',
        message: 'Erro ao testar conexão: ' + error.message
      })
    } finally {
      setLoading(false)
    }
  }

  const saveConfiguration = async () => {
    try {
      setLoading(true)
      setSaveResult(null)

      // Atualizar para usar nossa nova API
      const response = await fetch('http://localhost:8000/api/sync/google-sheets', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          config: config,
          force: true
        })
      })

      const result = await response.json()

      if (response.ok && result.success) {
        setSaveResult({
          status: 'success',
          message: 'Configuração salva e sincronização executada com sucesso!'
        })
      } else {
        setSaveResult({
          status: 'error',
          message: result.error || 'Erro ao salvar configuração'
        })
      }
    } catch (error) {
      setSaveResult({
        status: 'error',
        message: 'Erro ao salvar configuração: ' + error.message
      })
    } finally {
      setLoading(false)
    }
  }

  // Funções para importação de arquivos
  const handleFileSelect = (event) => {
    const file = event.target.files[0]
    if (file) {
      setUploadFile(file)
      setUploadPreview(null)
      setImportResult(null)
    }
  }

  const generatePreview = async () => {
    if (!uploadFile) return

    try {
      setImportLoading(true)
      const formData = new FormData()
      formData.append('file', uploadFile)
      formData.append('import_type', 'corridas')

      const response = await fetch('http://localhost:8000/api/import/upload', {
        method: 'POST',
        body: formData
      })

      const result = await response.json()

      if (result.success) {
        setUploadPreview(result.data.preview)
      } else {
        setImportResult({
          status: 'error',
          message: result.error
        })
      }
    } catch (error) {
      setImportResult({
        status: 'error',
        message: 'Erro ao gerar preview: ' + error.message
      })
    } finally {
      setImportLoading(false)
    }
  }

  const executeImport = async () => {
    if (!uploadPreview) return

    try {
      setImportLoading(true)
      
      // Usar mapeamento automático detectado
      const columnMapping = uploadPreview.detected_mapping

      const response = await fetch('http://localhost:8000/api/import/execute', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          filepath: uploadPreview.filepath,
          import_type: 'corridas',
          column_mapping: columnMapping
        })
      })

      const result = await response.json()

      if (result.success) {
        setImportResult({
          status: 'success',
          message: `Importação concluída! ${result.imported} corridas importadas${result.errors > 0 ? `, ${result.errors} erros` : ''}.`
        })
        setUploadFile(null)
        setUploadPreview(null)
        if (fileInputRef.current) {
          fileInputRef.current.value = ''
        }
      } else {
        setImportResult({
          status: 'error',
          message: result.error
        })
      }
    } catch (error) {
      setImportResult({
        status: 'error',
        message: 'Erro na importação: ' + error.message
      })
    } finally {
      setImportLoading(false)
    }
  }

  const clearUpload = () => {
    setUploadFile(null)
    setUploadPreview(null)
    setImportResult(null)
    if (fileInputRef.current) {
      fileInputRef.current.value = ''
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex items-center space-x-2"
      >
        <Settings className="w-6 h-6 text-gray-700 dark:text-gray-300" />
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white">Importação de Dados</h2>
      </motion.div>

      {/* Instructions */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
      >
        <Alert>
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>
            Você pode importar dados através de planilhas locais (Excel/CSV) ou configurar integração com Google Sheets.
            As duas opções podem ser usadas simultaneamente.
          </AlertDescription>
        </Alert>
      </motion.div>

      {/* Importação de Arquivos Locais */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
      >
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Upload className="w-5 h-5" />
              <span>Importar Planilha Local</span>
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {/* File Upload */}
            <div>
              <Label htmlFor="file-upload">Selecionar arquivo Excel ou CSV</Label>
              <div className="mt-2 flex items-center space-x-2">
                <Input
                  ref={fileInputRef}
                  id="file-upload"
                  type="file"
                  accept=".xlsx,.xls,.csv"
                  onChange={handleFileSelect}
                  disabled={importLoading}
                />
                {uploadFile && (
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={clearUpload}
                    disabled={importLoading}
                  >
                    <Trash2 className="w-4 h-4" />
                  </Button>
                )}
              </div>
              {uploadFile && (
                <p className="text-sm text-gray-600 mt-1">
                  Arquivo: {uploadFile.name} ({(uploadFile.size / 1024 / 1024).toFixed(2)} MB)
                </p>
              )}
            </div>

            {/* Botões de ação */}
            {uploadFile && !uploadPreview && (
              <Button
                onClick={generatePreview}
                disabled={importLoading}
                className="w-full"
              >
                {importLoading ? 'Gerando preview...' : 'Gerar Preview'}
              </Button>
            )}

            {/* Preview dos dados */}
            {uploadPreview && (
              <div className="space-y-4">
                <div className="bg-gray-50 dark:bg-gray-800 p-4 rounded-lg">
                  <h4 className="font-medium mb-2">Preview dos Dados</h4>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
                    <div>
                      <span className="font-medium">Total de linhas:</span> {uploadPreview.total_rows}
                    </div>
                    <div>
                      <span className="font-medium">Colunas detectadas:</span> {uploadPreview.columns.length}
                    </div>
                    <div>
                      <span className="font-medium">Campos mapeados:</span> {Object.keys(uploadPreview.detected_mapping).length}
                    </div>
                  </div>

                  {/* Sample data */}
                  {uploadPreview.sample_data && uploadPreview.sample_data.length > 0 && (
                    <div className="mt-4">
                      <h5 className="font-medium mb-2">Primeiras linhas:</h5>
                      <div className="overflow-x-auto">
                        <table className="w-full text-xs border border-gray-200 dark:border-gray-700">
                          <thead>
                            <tr className="bg-gray-100 dark:bg-gray-700">
                              {uploadPreview.columns.slice(0, 5).map((col, i) => (
                                <th key={i} className="border px-2 py-1 text-left">{col}</th>
                              ))}
                            </tr>
                          </thead>
                          <tbody>
                            {uploadPreview.sample_data.slice(0, 3).map((row, i) => (
                              <tr key={i}>
                                {uploadPreview.columns.slice(0, 5).map((col, j) => (
                                  <td key={j} className="border px-2 py-1">{String(row[col] || '').substring(0, 30)}</td>
                                ))}
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    </div>
                  )}
                </div>

                <Button
                  onClick={executeImport}
                  disabled={importLoading}
                  className="w-full"
                  variant="default"
                >
                  {importLoading ? 'Importando...' : 'Executar Importação'}
                </Button>
              </div>
            )}

            {/* Resultado da importação */}
            {importResult && (
              <Alert className={importResult.status === 'success' ? 'border-green-200 bg-green-50' : 'border-red-200 bg-red-50'}>
                {importResult.status === 'success' ? (
                  <CheckCircle className="h-4 w-4 text-green-600" />
                ) : (
                  <AlertCircle className="h-4 w-4 text-red-600" />
                )}
                <AlertDescription className={importResult.status === 'success' ? 'text-green-800' : 'text-red-800'}>
                  {importResult.message}
                </AlertDescription>
              </Alert>
            )}
          </CardContent>
        </Card>
      </motion.div>

      {/* Google Sheets Configuration Form */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
      >
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <FileSpreadsheet className="w-5 h-5" />
              <span>Configuração Google Sheets</span>
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-6">
            {/* Planilha de Corridas */}
            <div className="space-y-2">
              <Label htmlFor="corridas">Planilha de Corridas</Label>
              <Input
                id="corridas"
                placeholder="Cole a URL ou ID da planilha de corridas"
                value={config.spreadsheet_id_corridas}
                onChange={(e) => handleUrlPaste('spreadsheet_id_corridas', e.target.value)}
                className="font-mono text-sm"
              />
              <p className="text-xs text-gray-500 dark:text-gray-400">
                Esta planilha deve conter as abas: "Corridas Concluidas", "Corridas Canceladas", "Corridas Perdidas"
              </p>
            </div>

            {/* Planilha de Metas */}
            <div className="space-y-2">
              <Label htmlFor="metas">Planilha de Metas</Label>
              <Input
                id="metas"
                placeholder="Cole a URL ou ID da planilha de metas"
                value={config.spreadsheet_id_metas}
                onChange={(e) => handleUrlPaste('spreadsheet_id_metas', e.target.value)}
                className="font-mono text-sm"
              />
              <p className="text-xs text-gray-500 dark:text-gray-400">
                Esta planilha deve conter a aba: "Metas" com as colunas de cidade e metas mensais
              </p>
            </div>

            {/* Action Buttons */}
            <div className="flex space-x-3 pt-4">
              <Button
                onClick={testConnection}
                disabled={loading || !config.spreadsheet_id_corridas || !config.spreadsheet_id_metas}
                variant="outline"
                className="flex items-center space-x-2"
              >
                <TestTube className="w-4 h-4" />
                <span>{loading ? 'Testando...' : 'Testar Conexão'}</span>
              </Button>

              <Button
                onClick={saveConfiguration}
                disabled={loading || !config.spreadsheet_id_corridas || !config.spreadsheet_id_metas}
                className="flex items-center space-x-2 bg-black text-white hover:bg-gray-800"
              >
                <Save className="w-4 h-4" />
                <span>{loading ? 'Salvando...' : 'Salvar Configuração'}</span>
              </Button>
            </div>
          </CardContent>
        </Card>
      </motion.div>

      {/* Test Results */}
      {testResult && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
        >
          <Alert className={testResult.status === 'success' ? 'border-green-200 bg-green-50 dark:bg-green-900/20' : 'border-red-200 bg-red-50 dark:bg-red-900/20'}>
            {testResult.status === 'success' ? (
              <CheckCircle className="h-4 w-4 text-green-600" />
            ) : (
              <AlertCircle className="h-4 w-4 text-red-600" />
            )}
            <AlertDescription className={testResult.status === 'success' ? 'text-green-700 dark:text-green-300' : 'text-red-700 dark:text-red-300'}>
              {testResult.message}
              {testResult.details && (
                <div className="mt-2 text-sm">
                  <p>• Corridas encontradas: {testResult.details.corridas_count}</p>
                  <p>• Metas encontradas: {testResult.details.metas_count}</p>
                </div>
              )}
            </AlertDescription>
          </Alert>
        </motion.div>
      )}

      {/* Save Results */}
      {saveResult && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
        >
          <Alert className={saveResult.status === 'success' ? 'border-green-200 bg-green-50 dark:bg-green-900/20' : 'border-red-200 bg-red-50 dark:bg-red-900/20'}>
            {saveResult.status === 'success' ? (
              <CheckCircle className="h-4 w-4 text-green-600" />
            ) : (
              <AlertCircle className="h-4 w-4 text-red-600" />
            )}
            <AlertDescription className={saveResult.status === 'success' ? 'text-green-700 dark:text-green-300' : 'text-red-700 dark:text-red-300'}>
              {saveResult.message}
            </AlertDescription>
          </Alert>
        </motion.div>
      )}

      {/* Documentation */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4 }}
      >
        <Card>
          <CardHeader>
            <CardTitle>Estrutura das Planilhas</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <h4 className="font-semibold text-gray-900 dark:text-white mb-2">Planilha 1 - Corridas</h4>
              <div className="space-y-2 text-sm text-gray-600 dark:text-gray-400">
                <div>
                  <strong>Aba "Corridas Concluidas":</strong>
                  <p>Colunas: Data, Nº ID, Nome Usuário, Tel Usuário, Municipio, Nome Motorista</p>
                </div>
                <div>
                  <strong>Aba "Corridas Canceladas":</strong>
                  <p>Colunas: Data - CC, Nº ID - CC, Nome Usuario - CC, Tel. Usuário - CC, Municipio - CC, Nome Motorista - CC, Razão - CC, Motivo - CC</p>
                </div>
                <div>
                  <strong>Aba "Corridas Perdidas":</strong>
                  <p>Colunas: Data - CP, Nº ID _CP, Nome Usuario - CP, Tel. Usuário - CP, Municipio - CP, Razão - CP, Motivo - CP</p>
                </div>
              </div>
            </div>

            <div>
              <h4 className="font-semibold text-gray-900 dark:text-white mb-2">Planilha 2 - Metas</h4>
              <div className="text-sm text-gray-600 dark:text-gray-400">
                <div>
                  <strong>Aba "Metas":</strong>
                  <p>Colunas: Cidade, Media Corridas Mês, Meta Mês 1, Meta Mês 2, Meta Mês 3, Meta Mês 4, Meta Mês 5, Meta Mês 6</p>
                </div>
              </div>
            </div>

            <div className="pt-4 border-t border-gray-200 dark:border-gray-700">
              <Button
                variant="outline"
                size="sm"
                className="flex items-center space-x-2"
                onClick={() => window.open('https://docs.google.com/spreadsheets', '_blank')}
              >
                <ExternalLink className="w-4 h-4" />
                <span>Abrir Google Sheets</span>
              </Button>
            </div>
          </CardContent>
        </Card>
      </motion.div>
    </div>
  )
}

