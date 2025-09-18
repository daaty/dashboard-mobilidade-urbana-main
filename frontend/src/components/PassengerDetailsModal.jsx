import React, { useState, useEffect } from 'react';
import { X, User, Phone, Mail, MapPin, Star, TrendingUp, DollarSign, Clock, Calendar, Award, AlertCircle, Edit, Save, Filter, Search, Users, Smartphone } from 'lucide-react';

const PassengerDetailsModal = ({ isOpen, onClose, passengerId, passengerName }) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [passengersList, setPassengersList] = useState([]);
  const [selectedPassenger, setSelectedPassenger] = useState(null);
  const [isEditing, setIsEditing] = useState(false);
  const [editedData, setEditedData] = useState({});

  // Filtros
  const [cities, setCities] = useState([]);
  const [selectedCity, setSelectedCity] = useState('');
  const [searchTerm, setSearchTerm] = useState('');

  const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

  // Função para buscar lista de passageiros
  const fetchPassengersList = async () => {
    try {
      setLoading(true);
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
      setLoading(false);
    }
  };

  // Função para buscar detalhes do passageiro selecionado
  const fetchPassengerDetails = async (id) => {
    if (!id) return;

    try {
      setLoading(true);
      setError(null);

      console.log('🔍 Buscando dados para passenger ID:', id);

      const response = await fetch(`${API_URL}/api/passengers/find-personal-data/${id}`);

      if (!response.ok) {
        throw new Error(`Erro HTTP: ${response.status}`);
      }

      const personalData = await response.json();
      console.log('✅ DADOS ENCONTRADOS:', personalData);

      if (!personalData) {
        throw new Error('Nenhum dado retornado pelo servidor');
      }

      const passengerFromData = {
        passenger_id: personalData.passenger_id,
        name: personalData.personal_data?.user_name || personalData.personal_data?.passenger_name || 'Não informado',
        phone: personalData.personal_data?.user_phone || personalData.personal_data?.phone_no || 'Não informado',
        email: personalData.personal_data?.user_email || personalData.personal_data?.email || 'Não informado',
        city: personalData.city || personalData.personal_data?.city || 'Não informado',
        status: personalData.personal_data?.blocked === 'Yes' ? 'Bloqueado' : 'Ativo',
        join_date: personalData.personal_data?.date_registered || personalData.personal_data?.registration_date || null,
        app_version: personalData.personal_data?.app_version || 'Não informado',
        device_type: personalData.personal_data?.device_type || 'Não informado',
        wallet_balance: personalData.personal_data?.internal_wallet_balance || '0',
        remaining_coupons: personalData.personal_data?.remaining_coupons || '0',
        date_of_birth: personalData.personal_data?.date_of_birth !== 'N/A' ? personalData.personal_data?.date_of_birth : null,
        data: {
          profile: personalData.personal_data
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
      
      // Recarregar a lista para mostrar as mudanças, mas manter os filtros atuais
      setTimeout(() => {
        fetchPassengersList();
      }, 100);
      
      alert('Dados salvos com sucesso!');
    } catch (error) {
      console.error('Erro ao salvar:', error);
      alert('Erro ao salvar alterações: ' + error.message);
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
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-2xl max-w-6xl w-full max-h-[90vh] overflow-y-auto">
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
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
          >
            <X className="w-6 h-6" />
          </button>
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
                <Search className="w-4 h-4 inline mr-1" />
                Buscar por Nome
              </label>
              <input
                type="text"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                placeholder="Digite o nome do passageiro..."
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-700 dark:border-gray-600 dark:text-white"
              />
            </div>
          </div>

          {loading && (
            <div className="flex items-center justify-center py-12">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
              <span className="ml-3 text-gray-600 dark:text-gray-400">Carregando passageiros...</span>
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

          {!selectedPassenger && !loading && (
            <div className="space-y-4">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                Lista de Passageiros ({passengersList.length})
              </h3>

              <div className="grid gap-4 max-h-96 overflow-y-auto">
                {passengersList.map((passenger, index) => (
                  <div
                    key={`${passenger.passenger_id}-${index}`}
                    className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4 border border-gray-200 dark:border-gray-600 hover:border-blue-300 dark:hover:border-blue-600 transition-colors cursor-pointer"
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
                  className="flex items-center px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
                >
                  ← Voltar para lista
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
                      className="flex items-center px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
                    >
                      <Save className="w-4 h-4 mr-2" />
                      Salvar
                    </button>
                  </div>
                )}
              </div>

              {/* Informações do Passageiro */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="space-y-4">
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-white flex items-center">
                    <User className="w-5 h-5 mr-2" />
                    Informações Pessoais
                  </h3>

                  <div className="space-y-3">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                        Nome
                      </label>
                      {isEditing ? (
                        <input
                          type="text"
                          value={editedData.user_name || ''}
                          onChange={(e) => handleFieldChange('user_name', e.target.value)}
                          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        />
                      ) : (
                        <p className="text-gray-900 dark:text-white bg-gray-50 dark:bg-gray-700 px-3 py-2 rounded-lg">
                          {selectedPassenger.name}
                        </p>
                      )}
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                        Telefone
                      </label>
                      {isEditing ? (
                        <input
                          type="text"
                          value={editedData.user_phone || ''}
                          onChange={(e) => handleFieldChange('user_phone', e.target.value)}
                          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        />
                      ) : (
                        <p className="text-gray-900 dark:text-white bg-gray-50 dark:bg-gray-700 px-3 py-2 rounded-lg flex items-center">
                          <Phone className="w-4 h-4 mr-2 text-gray-500" />
                          {selectedPassenger.phone}
                        </p>
                      )}
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                        Email
                      </label>
                      {isEditing ? (
                        <input
                          type="email"
                          value={editedData.user_email || ''}
                          onChange={(e) => handleFieldChange('user_email', e.target.value)}
                          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        />
                      ) : (
                        <p className="text-gray-900 dark:text-white bg-gray-50 dark:bg-gray-700 px-3 py-2 rounded-lg flex items-center">
                          <Mail className="w-4 h-4 mr-2 text-gray-500" />
                          {selectedPassenger.email}
                        </p>
                      )}
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                        Cidade
                      </label>
                      {isEditing ? (
                        <input
                          type="text"
                          value={editedData.city || ''}
                          onChange={(e) => handleFieldChange('city', e.target.value)}
                          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        />
                      ) : (
                        <p className="text-gray-900 dark:text-white bg-gray-50 dark:bg-gray-700 px-3 py-2 rounded-lg flex items-center">
                          <MapPin className="w-4 h-4 mr-2 text-gray-500" />
                          {selectedPassenger.city}
                        </p>
                      )}
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                        Status
                      </label>
                      {isEditing ? (
                        <select
                          value={editedData.blocked === 'Yes' ? 'Bloqueado' : 'Ativo'}
                          onChange={(e) => handleFieldChange('blocked', e.target.value === 'Bloqueado' ? 'Yes' : 'No')}
                          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        >
                          <option value="Ativo">Ativo</option>
                          <option value="Bloqueado">Bloqueado</option>
                        </select>
                      ) : (
                        <p className={`px-3 py-2 rounded-lg text-sm font-medium ${
                          selectedPassenger.status === 'Ativo'
                            ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
                            : 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'
                        }`}>
                          {selectedPassenger.status}
                        </p>
                      )}
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                        Data de Cadastro
                      </label>
                      <p className="text-gray-900 dark:text-white bg-gray-50 dark:bg-gray-700 px-3 py-2 rounded-lg flex items-center">
                        <Calendar className="w-4 h-4 mr-2 text-gray-500" />
                        {selectedPassenger.join_date || 'Não informado'}
                      </p>
                    </div>
                  </div>
                </div>

                {/* Informações Adicionais */}
                <div className="space-y-4">
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-white flex items-center">
                    <Smartphone className="w-5 h-5 mr-2" />
                    Informações Adicionais
                  </h3>

                  <div className="space-y-3">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                        Versão do App
                      </label>
                      <p className="text-gray-900 dark:text-white bg-gray-50 dark:bg-gray-700 px-3 py-2 rounded-lg">
                        {selectedPassenger.app_version}
                      </p>
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                        Dispositivo
                      </label>
                      <p className="text-gray-900 dark:text-white bg-gray-50 dark:bg-gray-700 px-3 py-2 rounded-lg">
                        {selectedPassenger.device_type}
                      </p>
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                        Saldo da Carteira
                      </label>
                      <p className="text-gray-900 dark:text-white bg-gray-50 dark:bg-gray-700 px-3 py-2 rounded-lg flex items-center">
                        <DollarSign className="w-4 h-4 mr-2 text-gray-500" />
                        R$ {selectedPassenger.wallet_balance}
                      </p>
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                        Cupons Restantes
                      </label>
                      <p className="text-gray-900 dark:text-white bg-gray-50 dark:bg-gray-700 px-3 py-2 rounded-lg flex items-center">
                        <Star className="w-4 h-4 mr-2 text-gray-500" />
                        {selectedPassenger.remaining_coupons}
                      </p>
                    </div>

                    {selectedPassenger.date_of_birth && (
                      <div>
                        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                          Data de Nascimento
                        </label>
                        <p className="text-gray-900 dark:text-white bg-gray-50 dark:bg-gray-700 px-3 py-2 rounded-lg flex items-center">
                          <Calendar className="w-4 h-4 mr-2 text-gray-500" />
                          {selectedPassenger.date_of_birth}
                        </p>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default PassengerDetailsModal;