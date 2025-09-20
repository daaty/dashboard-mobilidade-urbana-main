import React, { useState, useEffect } from 'react';
import { X, User, Phone, Mail, MapPin, Star, TrendingUp, DollarSign, Clock, Calendar, Award, AlertCircle, Edit, Save, Filter, Search, Users, Smartphone, CheckCircle, Loader, RefreshCw } from 'lucide-react';

const PassengerDetailsModal = ({ isOpen, onClose, passengerId, passengerName }) => {
  // Estados
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [passengersList, setPassengersList] = useState([]);
  const [selectedPassenger, setSelectedPassenger] = useState(null);
  const [isEditing, setIsEditing] = useState(false);
  const [editedData, setEditedData] = useState({});
  const [saving, setSaving] = useState(false);
  const [searchLoading, setSearchLoading] = useState(false);
  const [successMessage, setSuccessMessage] = useState('');

  // Filtros
  const [cities, setCities] = useState([]);
  const [selectedCity, setSelectedCity] = useState('');
  const [searchTerm, setSearchTerm] = useState('');

  const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

  // Função para buscar lista de passageiros
  const fetchPassengersList = async () => {
    try {
      setSearchLoading(true);
      setError(null);

      let url = `${API_URL}/api/passengers/list?limit=100`;

      // Aplicar filtros
      if (selectedCity) url += `&city=${encodeURIComponent(selectedCity)}`;
      if (searchTerm) url += `&search=${encodeURIComponent(searchTerm)}`;

      const response = await fetch(url);

      if (!response.ok) {
        throw new Error(`Erro HTTP: ${response.status}`);
      }

      const data = await response.json();
      setPassengersList(data || []);
    } catch (error) {
      console.error('Erro ao buscar lista de passageiros:', error);
      setError(error.message);
    } finally {
      setSearchLoading(false);
    }
  };

  // Função para buscar detalhes do passageiro selecionado
  const fetchPassengerDetails = async (id) => {
    if (!id) return;

    try {
      setLoading(true);
      setError(null);

      console.log('🔍 Buscando dados para passenger ID:', id);

      const response = await fetch(`${API_URL}/api/passengers/${id}`);

      if (!response.ok) {
        throw new Error(`Erro HTTP: ${response.status}`);
      }

      const passengerData = await response.json();
      console.log('✅ DADOS ENCONTRADOS:', passengerData);

      if (!passengerData) {
        throw new Error('Nenhum dado retornado pelo servidor');
      }

      const passengerFromData = {
        passenger_id: passengerData.passenger_id,
        name: passengerData.personal_info?.user_name || 'Não informado',
        phone: passengerData.personal_info?.user_phone || 'Não informado',
        email: passengerData.personal_info?.user_email || 'Não informado',
        city: passengerData.city || 'Não informado',
        status: passengerData.personal_info?.blocked === 'Yes' ? 'Bloqueado' : 'Ativo',
        join_date: passengerData.personal_info?.date_registered || null,
        rides_summary: passengerData.rides_summary || {},
        rides_details: passengerData.rides_details || [],
        data: {
          profile: passengerData.personal_info
        }
      };

      setSelectedPassenger(passengerFromData);
      setEditedData(passengerFromData.data?.profile || {});

    } catch (error) {
      console.error('❌ Erro ao buscar dados do passageiro:', error);
      setError(error.message);
    } finally {
      setLoading(false);
    }
  };

  // Buscar dados quando o modal abre
  useEffect(() => {
    if (isOpen) {
      fetchPassengersList();
      fetchFiltersData();
    }
  }, [isOpen]);

  // Atualizar lista quando filtros mudam
  useEffect(() => {
    if (isOpen) {
      fetchPassengersList();
    }
  }, [selectedCity, searchTerm]);

  // Buscar dados para filtros
  const fetchFiltersData = async () => {
    try {
      const citiesRes = await fetch(`${API_URL}/api/metrics/cities`);

      if (citiesRes.ok) {
        const citiesData = await citiesRes.json();
        setCities(citiesData.cities || []);
      }
    } catch (error) {
      console.error('Erro ao buscar dados para filtros:', error);
    }
  };

  // Função para salvar alterações
  const handleSave = async () => {
    try {
      setSaving(true);
      setError(null);
      
      const response = await fetch(`${API_URL}/api/passengers/${selectedPassenger.passenger_id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(editedData)  // Enviar os dados diretamente
      });

      if (!response.ok) {
        throw new Error('Erro ao salvar alterações');
      }

      // Atualizar dados locais e recarregar a lista
      setSelectedPassenger(prev => ({
        ...prev,
        ...editedData  // Atualizar com os novos dados
      }));

      setIsEditing(false);
      
      // Mostrar mensagem de sucesso
      setSuccessMessage('Dados salvos com sucesso!');
      setTimeout(() => setSuccessMessage(''), 3000);
      
      // Recarregar a lista para mostrar as mudanças, mas manter os filtros atuais
      setTimeout(() => {
        fetchPassengersList();
      }, 100);
      
    } catch (error) {
      console.error('Erro ao salvar:', error);
      setError('Erro ao salvar alterações: ' + error.message);
    } finally {
      setSaving(false);
    }
  };

  // Função para atualizar campo editado
  const handleFieldChange = (field, value) => {
    setEditedData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4 animate-in fade-in duration-200">
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-2xl max-w-6xl w-full max-h-[90vh] overflow-y-auto animate-in slide-in-from-bottom-4 duration-300">
        {/* Notificação de sucesso */}
        {successMessage && (
          <div className="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded-t-xl flex items-center animate-in slide-in-from-top-2 duration-300">
            <CheckCircle className="w-5 h-5 mr-2" />
            <span>{successMessage}</span>
          </div>
        )}
        
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200 dark:border-gray-700">
          <div className="flex items-center space-x-3">
            <Users className="w-8 h-8 text-blue-600" />
            <div>
              <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
                Gerenciamento de Passageiros
              </h2>
              <p className="text-gray-600 dark:text-gray-400">
                Visualize e edite dados detalhados dos passageiros
              </p>
            </div>
          </div>
          <div className="flex items-center space-x-2">
            <button
              onClick={() => fetchPassengersList()}
              disabled={loading || searchLoading}
              className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              title="Atualizar lista"
            >
              <RefreshCw className={`w-5 h-5 ${(loading || searchLoading) ? 'animate-spin' : ''}`} />
            </button>
            <button
              onClick={onClose}
              className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
            >
              <X className="w-6 h-6" />
            </button>
          </div>
        </div>

        {/* Content */}
        <div className="p-6">
          {/* Filtros */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                <Filter className="w-4 h-4 inline mr-1" />
                Filtrar por Cidade
              </label>
              <select
                value={selectedCity}
                onChange={(e) => setSelectedCity(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-700 dark:border-gray-600 dark:text-white"
              >
                <option value="">Todas as cidades</option>
                {cities.map((city, index) => (
                  <option key={`${city}-${index}`} value={city}>{city}</option>
                ))}
              </select>
            </div>

            <div className="md:col-span-2">
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                {searchLoading ? (
                  <Loader className="w-4 h-4 inline mr-1 animate-spin text-blue-600" />
                ) : (
                  <Search className="w-4 h-4 inline mr-1" />
                )}
                Buscar por Nome
              </label>
              <div className="relative">
                <input
                  type="text"
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  placeholder="Digite o nome do passageiro..."
                  className="w-full px-3 py-2 pr-10 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                />
                {searchLoading && (
                  <div className="absolute right-3 top-1/2 transform -translate-y-1/2">
                    <Loader className="w-4 h-4 animate-spin text-blue-600" />
                  </div>
                )}
              </div>
            </div>
          </div>

          {(loading || searchLoading) && (
            <div className="space-y-4">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                {searchLoading ? 'Buscando passageiros...' : 'Carregando passageiros...'}
              </h3>
              
              {/* Skeleton Loading */}
              <div className="grid gap-4 max-h-96 overflow-y-auto">
                {[...Array(5)].map((_, index) => (
                  <div
                    key={index}
                    className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4 border border-gray-200 dark:border-gray-600 animate-pulse"
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-3">
                        <div className="w-8 h-8 bg-gray-300 dark:bg-gray-600 rounded-full"></div>
                        <div>
                          <div className="h-4 bg-gray-300 dark:bg-gray-600 rounded w-32 mb-1"></div>
                          <div className="h-3 bg-gray-300 dark:bg-gray-600 rounded w-20"></div>
                        </div>
                      </div>
                      <div className="text-right">
                        <div className="h-4 bg-gray-300 dark:bg-gray-600 rounded w-20 mb-1"></div>
                        <div className="h-3 bg-gray-300 dark:bg-gray-600 rounded w-16"></div>
                      </div>
                    </div>
                    <div className="mt-2 flex items-center justify-between">
                      <div className="h-3 bg-gray-300 dark:bg-gray-600 rounded w-24"></div>
                      <div className="h-6 bg-gray-300 dark:bg-gray-600 rounded-full w-16"></div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {error && (
            <div className="bg-red-50 dark:bg-red-900 border border-red-200 dark:border-red-700 rounded-lg p-4 mb-6">
              <div className="flex items-center">
                <AlertCircle className="w-5 h-5 text-red-600 dark:text-red-400 mr-2" />
                <span className="text-red-800 dark:text-red-200">{error}</span>
              </div>
            </div>
          )}

          {!selectedPassenger && !loading && !searchLoading && (
            <div className="space-y-4">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                Lista de Passageiros ({passengersList.length})
              </h3>

              {passengersList.length === 0 ? (
                <div className="flex flex-col items-center justify-center py-12 text-center">
                  <Users className="w-16 h-16 text-gray-400 mb-4" />
                  <h4 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
                    Nenhum passageiro encontrado
                  </h4>
                  <p className="text-gray-600 dark:text-gray-400">
                    {searchTerm || selectedCity ? 
                      'Tente ajustar os filtros de busca para encontrar passageiros.' :
                      'Não há passageiros cadastrados no momento.'
                    }
                  </p>
                  {(searchTerm || selectedCity) && (
                    <button
                      onClick={() => {
                        setSearchTerm('');
                        setSelectedCity('');
                      }}
                      className="mt-4 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                    >
                      Limpar Filtros
                    </button>
                  )}
                </div>
              ) : (
                <div className="grid gap-4 max-h-96 overflow-y-auto">
                  {passengersList.map((passenger, index) => (
                  <div
                    key={`${passenger.passenger_id}-${index}`}
                    className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4 border border-gray-200 dark:border-gray-600 hover:border-blue-300 hover:shadow-md dark:hover:border-blue-600 transition-all duration-200 cursor-pointer transform hover:scale-105"
                    onClick={() => fetchPassengerDetails(passenger.passenger_id)}
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-3">
                        <User className="w-8 h-8 text-blue-600" />
                        <div>
                          <h4 className="font-medium text-gray-900 dark:text-white">
                            {passenger.user_name || `Passageiro ${passenger.passenger_id}`}
                          </h4>
                          <p className="text-sm text-gray-600 dark:text-gray-400">
                            ID: {passenger.passenger_id}
                          </p>
                        </div>
                      </div>
                      <div className="text-right">
                        <p className="text-sm font-medium text-gray-900 dark:text-white">
                          {passenger.total_rides} corridas
                        </p>
                        <p className="text-sm text-gray-600 dark:text-gray-400">
                          R$ {passenger.total_spent?.toFixed(2) || '0.00'}
                        </p>
                      </div>
                    </div>
                    <div className="mt-2 flex items-center justify-between text-sm">
                      <span className="flex items-center text-gray-600 dark:text-gray-400">
                        <MapPin className="w-4 h-4 mr-1" />
                        {passenger.city}
                      </span>
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                        passenger.status === 'active'
                          ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
                          : 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200'
                      }`}>
                        {passenger.status || 'Ativo'}
                      </span>
                    </div>
                  </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {selectedPassenger && (
            <div className="space-y-6">
              {/* Botões de navegação */}
              <div className="flex justify-between items-center">
                <button
                  onClick={() => {
                    setSelectedPassenger(null);
                    setIsEditing(false);
                  }}
                  className="flex items-center px-4 py-2 bg-gray-100 hover:bg-gray-200 dark:bg-gray-700 dark:hover:bg-gray-600 text-gray-700 dark:text-gray-300 rounded-lg transition-all duration-200 hover:scale-105 shadow-sm hover:shadow-md"
                >
                  <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                  </svg>
                  Voltar para lista
                </button>

                {!isEditing ? (
                  <button
                    onClick={() => {
                      setIsEditing(true);
                      // Carregar os dados atuais do passageiro para edição
                      setEditedData({
                        user_name: selectedPassenger.name || '',
                        user_phone: selectedPassenger.phone || '',
                        user_email: selectedPassenger.email || '',
                        city: selectedPassenger.city || '',
                        blocked: selectedPassenger.status === 'Bloqueado' ? 'Yes' : 'No'
                      });
                    }}
                    className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                  >
                    <Edit className="w-4 h-4 mr-2" />
                    Editar
                  </button>
                ) : (
                  <div className="flex space-x-3">
                    <button
                      onClick={() => {
                        setIsEditing(false);
                        setEditedData(selectedPassenger.data?.profile || {});
                      }}
                      className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
                    >
                      Cancelar
                    </button>
                    <button
                      onClick={handleSave}
                      disabled={saving}
                      className="flex items-center px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:bg-green-400 disabled:cursor-not-allowed transition-colors"
                    >
                      {saving ? (
                        <Loader className="w-4 h-4 mr-2 animate-spin" />
                      ) : (
                        <Save className="w-4 h-4 mr-2" />
                      )}
                      {saving ? 'Salvando...' : 'Salvar'}
                    </button>
                  </div>
                )}
              </div>

              {/* Informações do Passageiro */}
              <div className="space-y-8">
                <div className="bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-gray-800 dark:to-gray-700 rounded-xl p-6 shadow-sm border border-blue-100 dark:border-gray-600">
                  <h3 className="text-xl font-bold text-gray-900 dark:text-white flex items-center mb-6">
                    <div className="p-2 bg-blue-100 dark:bg-blue-900 rounded-lg mr-3">
                      <User className="w-6 h-6 text-blue-600 dark:text-blue-400" />
                    </div>
                    Informações Pessoais
                  </h3>

                  {/* Grid responsivo para informações pessoais */}
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    <div className="group">
                      <label className="block text-sm font-semibold text-gray-600 dark:text-gray-300 mb-2 flex items-center">
                        <User className="w-4 h-4 mr-2 text-blue-500" />
                        Nome
                      </label>
                      {isEditing ? (
                        <input
                          type="text"
                          value={editedData.user_name || ''}
                          onChange={(e) => handleFieldChange('user_name', e.target.value)}
                          className="w-full px-4 py-3 border-2 border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all duration-200 bg-white dark:bg-gray-800 dark:border-gray-600 dark:text-white"
                        />
                      ) : (
                        <div className="text-gray-900 dark:text-white bg-white dark:bg-gray-800 px-4 py-3 rounded-lg border-2 border-gray-100 dark:border-gray-600 font-medium text-lg group-hover:border-blue-200 transition-colors">
                          {selectedPassenger.name || 'Não informado'}
                        </div>
                      )}
                    </div>

                    <div className="group">
                      <label className="block text-sm font-semibold text-gray-600 dark:text-gray-300 mb-2 flex items-center">
                        <Phone className="w-4 h-4 mr-2 text-green-500" />
                        Telefone
                      </label>
                      {isEditing ? (
                        <input
                          type="text"
                          value={editedData.user_phone || ''}
                          onChange={(e) => handleFieldChange('user_phone', e.target.value)}
                          className="w-full px-4 py-3 border-2 border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all duration-200 bg-white dark:bg-gray-800 dark:border-gray-600 dark:text-white"
                        />
                      ) : (
                        <a
                          href={`https://wa.me/${selectedPassenger.phone?.replace(/[^0-9]/g, '')}`}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-gray-900 dark:text-white bg-white dark:bg-gray-800 px-4 py-3 rounded-lg border-2 border-gray-100 dark:border-gray-600 flex items-center font-medium text-lg group-hover:border-green-200 transition-all duration-200 hover:bg-green-50 dark:hover:bg-green-900 hover:border-green-300 cursor-pointer transform hover:scale-[1.02]"
                          title={`Abrir conversa no WhatsApp com ${selectedPassenger.name}`}
                        >
                          <Phone className="w-5 h-5 mr-3 text-green-500" />
                          <span className="flex-1">{selectedPassenger.phone || 'Não informado'}</span>
                          <svg className="w-5 h-5 ml-2 text-green-600" fill="currentColor" viewBox="0 0 24 24">
                            <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893A11.821 11.821 0 0020.885 3.488"/>
                          </svg>
                        </a>
                      )}
                    </div>

                    <div className="group">
                      <label className="block text-sm font-semibold text-gray-600 dark:text-gray-300 mb-2 flex items-center">
                        <Mail className="w-4 h-4 mr-2 text-purple-500" />
                        Email
                      </label>
                      {isEditing ? (
                        <input
                          type="email"
                          value={editedData.user_email || ''}
                          onChange={(e) => handleFieldChange('user_email', e.target.value)}
                          className="w-full px-4 py-3 border-2 border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all duration-200 bg-white dark:bg-gray-800 dark:border-gray-600 dark:text-white"
                        />
                      ) : (
                        <div className="text-gray-900 dark:text-white bg-white dark:bg-gray-800 px-4 py-3 rounded-lg border-2 border-gray-100 dark:border-gray-600 flex items-center font-medium group-hover:border-purple-200 transition-colors">
                          <Mail className="w-5 h-5 mr-3 text-purple-500" />
                          {selectedPassenger.email || 'Não informado'}
                        </div>
                      )}
                    </div>

                    <div className="group">
                      <label className="block text-sm font-semibold text-gray-600 dark:text-gray-300 mb-2 flex items-center">
                        <MapPin className="w-4 h-4 mr-2 text-red-500" />
                        Cidade
                      </label>
                      {isEditing ? (
                        <input
                          type="text"
                          value={editedData.city || ''}
                          onChange={(e) => handleFieldChange('city', e.target.value)}
                          className="w-full px-4 py-3 border-2 border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all duration-200 bg-white dark:bg-gray-800 dark:border-gray-600 dark:text-white"
                        />
                      ) : (
                        <div className="text-gray-900 dark:text-white bg-white dark:bg-gray-800 px-4 py-3 rounded-lg border-2 border-gray-100 dark:border-gray-600 flex items-center font-medium group-hover:border-red-200 transition-colors">
                          <MapPin className="w-5 h-5 mr-3 text-red-500" />
                          {selectedPassenger.city || 'Não informado'}
                        </div>
                      )}
                    </div>

                    <div className="group">
                      <label className="block text-sm font-semibold text-gray-600 dark:text-gray-300 mb-2 flex items-center">
                        <svg className="w-4 h-4 mr-2 text-emerald-500" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                        </svg>
                        Status
                      </label>
                      {isEditing ? (
                        <select
                          value={editedData.blocked === 'Yes' ? 'Bloqueado' : 'Ativo'}
                          onChange={(e) => handleFieldChange('blocked', e.target.value === 'Bloqueado' ? 'Yes' : 'No')}
                          className="w-full px-4 py-3 border-2 border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all duration-200 bg-white dark:bg-gray-800 dark:border-gray-600 dark:text-white"
                        >
                          <option value="Ativo">Ativo</option>
                          <option value="Bloqueado">Bloqueado</option>
                        </select>
                      ) : (
                        <div className={`px-4 py-3 rounded-lg text-sm font-bold text-center border-2 transition-all duration-200 ${
                          selectedPassenger.status === 'Ativo'
                            ? 'bg-gradient-to-r from-green-100 to-emerald-100 text-green-800 border-green-200 dark:bg-gradient-to-r dark:from-green-900 dark:to-emerald-900 dark:text-green-200 dark:border-green-700'
                            : 'bg-gradient-to-r from-red-100 to-pink-100 text-red-800 border-red-200 dark:bg-gradient-to-r dark:from-red-900 dark:to-pink-900 dark:text-red-200 dark:border-red-700'
                        }`}>
                          <span className="flex items-center justify-center">
                            {selectedPassenger.status === 'Ativo' ? (
                              <svg className="w-4 h-4 mr-2" fill="currentColor" viewBox="0 0 20 20">
                                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                              </svg>
                            ) : (
                              <svg className="w-4 h-4 mr-2" fill="currentColor" viewBox="0 0 20 20">
                                <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
                              </svg>
                            )}
                            {selectedPassenger.status}
                          </span>
                        </div>
                      )}
                    </div>

                    <div className="group">
                      <label className="block text-sm font-semibold text-gray-600 dark:text-gray-300 mb-2 flex items-center">
                        <Calendar className="w-4 h-4 mr-2 text-indigo-500" />
                        Data de Cadastro
                      </label>
                      <div className="text-gray-900 dark:text-white bg-white dark:bg-gray-800 px-4 py-3 rounded-lg border-2 border-gray-100 dark:border-gray-600 flex items-center font-medium group-hover:border-indigo-200 transition-colors">
                        <Calendar className="w-5 h-5 mr-3 text-indigo-500" />
                        {selectedPassenger.join_date || 'Não informado'}
                      </div>
                    </div>
                  </div>
                </div>

                {/* Histórico de Corridas */}
                {selectedPassenger.rides_details && selectedPassenger.rides_details.length > 0 && (
                  <div className="bg-gradient-to-r from-indigo-50 to-purple-50 dark:from-gray-800 dark:to-gray-700 rounded-xl p-6 shadow-sm border border-indigo-100 dark:border-gray-600">
                    <h3 className="text-xl font-bold text-gray-900 dark:text-white flex items-center mb-6">
                      <div className="p-2 bg-indigo-100 dark:bg-indigo-900 rounded-lg mr-3">
                        <Clock className="w-6 h-6 text-indigo-600 dark:text-indigo-400" />
                      </div>
                      Histórico de Corridas ({selectedPassenger.rides_details.length})
                    </h3>

                    {/* Resumo das Corridas */}
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
                      <div className="bg-white dark:bg-gray-800 rounded-lg p-4 border border-gray-200 dark:border-gray-600">
                        <div className="flex items-center">
                          <TrendingUp className="w-5 h-5 text-green-600 mr-2" />
                          <div>
                            <p className="text-sm text-gray-600 dark:text-gray-400">Total Arrecadado</p>
                            <p className="text-lg font-bold text-gray-900 dark:text-white">
                              R$ {selectedPassenger.rides_summary?.total_revenue?.toFixed(2) || '0.00'}
                            </p>
                          </div>
                        </div>
                      </div>
                      
                      <div className="bg-white dark:bg-gray-800 rounded-lg p-4 border border-gray-200 dark:border-gray-600">
                        <div className="flex items-center">
                          <MapPin className="w-5 h-5 text-blue-600 mr-2" />
                          <div>
                            <p className="text-sm text-gray-600 dark:text-gray-400">Distância Total</p>
                            <p className="text-lg font-bold text-gray-900 dark:text-white">
                              {selectedPassenger.rides_summary?.total_distance?.toFixed(1) || '0.0'} km
                            </p>
                          </div>
                        </div>
                      </div>
                      
                      <div className="bg-white dark:bg-gray-800 rounded-lg p-4 border border-gray-200 dark:border-gray-600">
                        <div className="flex items-center">
                          <Star className="w-5 h-5 text-yellow-500 mr-2" />
                          <div>
                            <p className="text-sm text-gray-600 dark:text-gray-400">Avaliação Média</p>
                            <p className="text-lg font-bold text-gray-900 dark:text-white">
                              {selectedPassenger.rides_summary?.avg_rating || '0.0'} ★
                            </p>
                          </div>
                        </div>
                      </div>
                      
                      <div className="bg-white dark:bg-gray-800 rounded-lg p-4 border border-gray-200 dark:border-gray-600">
                        <div className="flex items-center">
                          <DollarSign className="w-5 h-5 text-purple-600 mr-2" />
                          <div>
                            <p className="text-sm text-gray-600 dark:text-gray-400">Valor Médio</p>
                            <p className="text-lg font-bold text-gray-900 dark:text-white">
                              R$ {selectedPassenger.rides_summary?.avg_fare?.toFixed(2) || '0.00'}
                            </p>
                          </div>
                        </div>
                      </div>
                    </div>

                    {/* Lista de Corridas */}
                    <div className="max-h-96 overflow-y-auto">
                      <div className="grid gap-4">
                        {selectedPassenger.rides_details.map((ride, index) => (
                          <div
                            key={index}
                            className="bg-white dark:bg-gray-800 rounded-lg p-4 border border-gray-200 dark:border-gray-600 hover:shadow-md transition-shadow"
                          >
                            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                              {/* Coluna 1: Data e Motorista */}
                              <div>
                                <div className="flex items-center mb-2">
                                  <Calendar className="w-4 h-4 text-indigo-500 mr-2" />
                                  <span className="text-sm font-semibold text-gray-900 dark:text-white">
                                    {ride.date || 'Data não informada'}
                                  </span>
                                </div>
                                <div className="flex items-center mb-2">
                                  <User className="w-4 h-4 text-blue-500 mr-2" />
                                  <span className="text-sm text-gray-700 dark:text-gray-300">
                                    {ride.driver_name || 'Motorista não informado'}
                                  </span>
                                </div>
                                <div className="flex items-center">
                                  <span className="text-xs text-gray-500 dark:text-gray-400">
                                    ID: {ride.driver_id || 'N/A'}
                                  </span>
                                </div>
                              </div>

                              {/* Coluna 2: Valores e Distância */}
                              <div>
                                <div className="flex items-center mb-2">
                                  <DollarSign className="w-4 h-4 text-green-600 mr-2" />
                                  <span className="text-lg font-bold text-green-600">
                                    R$ {ride.user_fare?.toFixed(2) || '0.00'}
                                  </span>
                                </div>
                                <div className="flex items-center mb-2">
                                  <MapPin className="w-4 h-4 text-blue-500 mr-2" />
                                  <span className="text-sm text-gray-700 dark:text-gray-300">
                                    {ride.ride_distance?.toFixed(1) || '0.0'} km
                                  </span>
                                </div>
                                <div className="flex items-center text-xs text-gray-500 dark:text-gray-400">
                                  <Clock className="w-3 h-3 mr-1" />
                                  Tempo: {ride.ride_time || '0'} min
                                </div>
                              </div>

                              {/* Coluna 3: Rating e Pagamento */}
                              <div>
                                <div className="flex items-center mb-2">
                                  <Star className="w-4 h-4 text-yellow-500 mr-2" />
                                  <span className="text-sm font-semibold text-gray-900 dark:text-white">
                                    {ride.user_rating !== '--' ? ride.user_rating : 'Não avaliado'}
                                  </span>
                                </div>
                                <div className="flex items-center mb-2">
                                  <span className={`px-2 py-1 rounded text-xs font-medium ${
                                    ride.preferred_mode === 'Cash' ? 
                                    'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200' : 
                                    'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200'
                                  }`}>
                                    {ride.preferred_mode || 'N/A'}
                                  </span>
                                </div>
                                <div className="text-xs text-gray-500 dark:text-gray-400">
                                  Cash: R$ {ride.paid_using_cash?.toFixed(2) || '0.00'} |
                                  Wallet: R$ {ride.paid_using_wallet?.toFixed(2) || '0.00'}
                                </div>
                              </div>
                            </div>

                            {/* Informações adicionais */}
                            <div className="mt-3 pt-3 border-t border-gray-200 dark:border-gray-600">
                              <div className="flex flex-wrap items-center gap-4 text-xs text-gray-500 dark:text-gray-400">
                                <span>Engajamento: {ride.engagement_id || 'N/A'}</span>
                                <span>Cupom: {ride.coupon_title !== 'NA' ? ride.coupon_title : 'Nenhum'}</span>
                                <span className={`px-2 py-1 rounded ${
                                  ride.start_end_case_issue_reported === 'NO' ? 
                                  'bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-300' : 
                                  'bg-red-100 text-red-700 dark:bg-red-900 dark:text-red-300'
                                }`}>
                                  {ride.start_end_case_issue_reported === 'NO' ? 'Sem problemas' : 'Com problemas'}
                                </span>
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default PassengerDetailsModal;