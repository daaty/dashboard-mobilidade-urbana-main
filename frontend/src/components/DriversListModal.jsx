import React, { useState, useEffect } from 'react';
import { X, User, Phone, Mail, MapPin, Star, TrendingUp, DollarSign, Clock, Calendar, Award, AlertCircle, Filter, Search, Users, Smartphone, CheckCircle, Loader, RefreshCw, Car, Activity } from 'lucide-react';
import DriverDetailsModal from './DriverDetailsModal';

const DriversListModal = ({ isOpen, onClose }) => {
  // Estados
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [driversList, setDriversList] = useState([]);
  const [allDrivers, setAllDrivers] = useState([]); // Lista completa sem filtro de busca
  const [searchLoading, setSearchLoading] = useState(false);

  // Filtros
  const [cities, setCities] = useState([]);
  const [selectedCity, setSelectedCity] = useState('');
  const [searchTerm, setSearchTerm] = useState('');
  const [debouncedSearchTerm, setDebouncedSearchTerm] = useState('');

  // Modal de detalhes
  const [isDetailsModalOpen, setIsDetailsModalOpen] = useState(false);
  const [selectedDriverId, setSelectedDriverId] = useState(null);
  const [selectedDriverName, setSelectedDriverName] = useState('');

  const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

  // Função para buscar lista de motoristas
  const fetchDriversList = async () => {
    try {
      setSearchLoading(true);
      setError(null);

      const params = new URLSearchParams();
      params.append('limit', '100'); // Buscar até 100 motoristas
      params.append('offset', '0');
      
      if (selectedCity && selectedCity !== 'all' && selectedCity !== '') {
        params.append('city', selectedCity);
        console.log('🏙️ Filtrando por cidade no backend:', selectedCity);
      }
      
      // Não enviamos searchTerm para o backend - filtro será feito no frontend

      const url = `${API_URL}/api/drivers/list?${params.toString()}`;
      console.log('🌐 URL completa da requisição:', url);

      const response = await fetch(url);

      if (!response.ok) {
        throw new Error(`Erro HTTP: ${response.status}`);
      }

      const result = await response.json();
      console.log('✅ Resposta da API:', result);
      
      // Extrair array de motoristas da resposta
      if (result.success && result.data && result.data.drivers) {
        setAllDrivers(result.data.drivers); // Salvar lista completa
        setDriversList(result.data.drivers); // Exibir lista completa inicialmente
        console.log(`✅ ${result.data.drivers.length} motoristas carregados do backend (total disponível: ${result.data.total_count})`);
      } else {
        setAllDrivers([]);
        setDriversList([]);
        console.log('⚠️ Nenhum motorista encontrado na resposta');
      }
    } catch (error) {
      console.error('❌ Erro ao buscar lista de motoristas:', error);
      setError(error.message);
      setDriversList([]);
    } finally {
      setSearchLoading(false);
    }
  };

  // Buscar dados quando o modal abre
  useEffect(() => {
    if (isOpen) {
      fetchDriversList();
      fetchFiltersData();
    }
  }, [isOpen]);

  // Debounce para o searchTerm (espera 500ms após o usuário parar de digitar)
  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedSearchTerm(searchTerm);
    }, 500);

    return () => clearTimeout(timer);
  }, [searchTerm]);

  // Atualizar lista quando cidade muda (busca no backend)
  useEffect(() => {
    if (isOpen) {
      fetchDriversList();
    }
  }, [selectedCity]);

  // Filtrar localmente quando o termo de busca muda
  useEffect(() => {
    if (!debouncedSearchTerm.trim()) {
      setDriversList(allDrivers);
      return;
    }

    console.log('🔍 Filtrando localmente por:', debouncedSearchTerm);
    const searchLower = debouncedSearchTerm.toLowerCase().trim();
    
    const filtered = allDrivers.filter(driver => {
      const name = driver.name?.toLowerCase() || '';
      const driverId = driver.driver_id?.toString() || '';
      
      return name.includes(searchLower) || driverId.includes(searchLower);
    });

    console.log(`✅ ${filtered.length} motoristas encontrados com o filtro "${debouncedSearchTerm}"`);
    setDriversList(filtered);
  }, [debouncedSearchTerm, allDrivers]);

  // Buscar dados para filtros
  const fetchFiltersData = async () => {
    try {
      const citiesRes = await fetch(`${API_URL}/api/drivers/cities`);

      if (citiesRes.ok) {
        const citiesData = await citiesRes.json();
        console.log('🏙️ Dados de cidades recebidos:', citiesData);
        
        // A API retorna { success: true, data: [...] }
        const citiesList = citiesData.data || citiesData.cities || [];
        console.log('🏙️ Lista de cidades:', citiesList);
        setCities(citiesList);
      }
    } catch (error) {
      console.error('❌ Erro ao buscar dados para filtros:', error);
    }
  };

  // Função para destacar texto da busca
  const highlightText = (text, search) => {
    if (!search.trim() || !text) return text;
    
    const parts = text.split(new RegExp(`(${search})`, 'gi'));
    return parts.map((part, index) => 
      part.toLowerCase() === search.toLowerCase() ? 
        <span key={index} className="bg-yellow-200 dark:bg-yellow-600 font-semibold">{part}</span> : 
        part
    );
  };

  // Função para abrir modal de detalhes
  const handleDriverClick = (driver) => {
    setSelectedDriverId(driver.driver_id);
    setSelectedDriverName(driver.name || `Motorista ${driver.driver_id}`);
    setIsDetailsModalOpen(true);
  };

  // Função para fechar modal de detalhes
  const handleCloseDetailsModal = () => {
    setIsDetailsModalOpen(false);
    setSelectedDriverId(null);
    setSelectedDriverName('');
  };

  if (!isOpen) return null;

  return (
    <>
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4 animate-in fade-in duration-200">
        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-2xl max-w-6xl w-full max-h-[90vh] overflow-y-auto animate-in slide-in-from-bottom-4 duration-300">
          {/* Header */}
          <div className="flex items-center justify-between p-6 border-b border-gray-200 dark:border-gray-700">
            <div className="flex items-center space-x-3">
              <Users className="w-8 h-8 text-blue-600" />
              <div>
                <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
                  Lista de Motoristas
                </h2>
                <p className="text-gray-600 dark:text-gray-400">
                  Visualize todos os motoristas cadastrados
                </p>
              </div>
            </div>
            <div className="flex items-center space-x-2">
              <button
                onClick={() => fetchDriversList()}
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
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  <Filter className="w-4 h-4 inline mr-1" />
                  Filtrar por Cidade
                </label>
                <select
                  value={selectedCity}
                  onChange={(e) => {
                    console.log('🏙️ Cidade selecionada:', e.target.value);
                    setSelectedCity(e.target.value);
                  }}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                >
                  <option value="">Todas as cidades</option>
                  {cities.map((city, index) => (
                    <option key={`${city}-${index}`} value={city}>{city}</option>
                  ))}
                </select>
                {selectedCity && (
                  <p className="text-xs text-gray-500 mt-1">
                    Filtrando por: {selectedCity}
                  </p>
                )}
              </div>

              <div className="md:col-span-2">
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  <Search className="w-4 h-4 inline mr-1" />
                  Buscar por Nome ou ID
                </label>
                <div className="relative">
                  <input
                    type="text"
                    value={searchTerm}
                    onChange={(e) => {
                      console.log('🔍 Digitando busca:', e.target.value);
                      setSearchTerm(e.target.value);
                    }}
                    placeholder="Digite o nome ou ID do motorista..."
                    className="w-full px-3 py-2 pr-10 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                  />
                  {searchTerm && searchTerm !== debouncedSearchTerm && (
                    <div className="absolute right-3 top-1/2 transform -translate-y-1/2">
                      <Loader className="w-4 h-4 animate-spin text-blue-600" />
                    </div>
                  )}
                  {searchTerm && searchTerm === debouncedSearchTerm && (
                    <div className="absolute right-3 top-1/2 transform -translate-y-1/2">
                      <CheckCircle className="w-4 h-4 text-green-600" />
                    </div>
                  )}
                </div>
                {searchTerm && (
                  <p className="text-xs text-gray-500 mt-1">
                    {searchTerm === debouncedSearchTerm 
                      ? `Buscando por: "${searchTerm}"` 
                      : 'Digitando...'}
                  </p>
                )}
              </div>
            </div>

            {(loading || searchLoading) && (
              <div className="space-y-4">
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                  {searchLoading ? 'Buscando motoristas...' : 'Carregando motoristas...'}
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

            {!loading && !searchLoading && (
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                    Motoristas Encontrados ({driversList.length})
                    {allDrivers.length > 0 && driversList.length < allDrivers.length && (
                      <span className="ml-2 text-sm font-normal text-gray-500">
                        de {allDrivers.length} total
                      </span>
                    )}
                  </h3>
                  {(selectedCity || searchTerm) && (
                    <button
                      onClick={() => {
                        setSelectedCity('');
                        setSearchTerm('');
                        setDebouncedSearchTerm('');
                        console.log('🔄 Filtros limpos');
                      }}
                      className="flex items-center gap-2 px-3 py-1.5 text-sm bg-gray-100 hover:bg-gray-200 dark:bg-gray-700 dark:hover:bg-gray-600 text-gray-700 dark:text-gray-300 rounded-lg transition-colors"
                    >
                      <X className="w-4 h-4" />
                      Limpar Filtros
                    </button>
                  )}
                </div>

                {driversList.length === 0 ? (
                  <div className="flex flex-col items-center justify-center py-12 text-center">
                    <Users className="w-16 h-16 text-gray-400 mb-4" />
                    <h4 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
                      Nenhum motorista encontrado
                    </h4>
                    <p className="text-gray-600 dark:text-gray-400">
                      {searchTerm || selectedCity ? 
                        'Tente ajustar os filtros de busca para encontrar motoristas.' :
                        'Não há motoristas cadastrados no momento.'
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
                  <div className="grid gap-4 max-h-[500px] overflow-y-auto">
                    {driversList.map((driver, index) => (
                      <div
                        key={`${driver.driver_id}-${index}`}
                        className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4 border border-gray-200 dark:border-gray-600 hover:border-blue-300 hover:shadow-md dark:hover:border-blue-600 transition-all duration-200 cursor-pointer transform hover:scale-[1.02]"
                        onClick={() => handleDriverClick(driver)}
                      >
                        <div className="flex items-center justify-between">
                          <div className="flex items-center space-x-3">
                            <div className="p-2 bg-blue-100 dark:bg-blue-900 rounded-full">
                              <User className="w-6 h-6 text-blue-600 dark:text-blue-400" />
                            </div>
                            <div>
                              <h4 className="font-medium text-gray-900 dark:text-white">
                                {debouncedSearchTerm 
                                  ? highlightText(driver.name || `Motorista ${driver.driver_id}`, debouncedSearchTerm)
                                  : (driver.name || `Motorista ${driver.driver_id}`)}
                              </h4>
                              <p className="text-sm text-gray-600 dark:text-gray-400">
                                ID: {debouncedSearchTerm 
                                  ? highlightText(driver.driver_id, debouncedSearchTerm)
                                  : driver.driver_id}
                              </p>
                            </div>
                          </div>
                          <div className="text-right">
                            <div className="flex items-center space-x-2">
                              <Star className="w-4 h-4 text-yellow-500" />
                              <span className="text-sm font-medium text-gray-900 dark:text-white">
                                {driver.estimated_rating?.toFixed(1) || '0.0'}
                              </span>
                            </div>
                            <p className="text-sm text-gray-600 dark:text-gray-400">
                              {driver.total_rides || 0} corridas
                            </p>
                          </div>
                        </div>
                        <div className="mt-3 grid grid-cols-2 md:grid-cols-4 gap-2">
                          <div className="flex items-center text-sm text-gray-600 dark:text-gray-400">
                            <MapPin className="w-4 h-4 mr-1 text-red-500" />
                            <span className="truncate">{driver.city || 'N/A'}</span>
                          </div>
                          <div className="flex items-center text-sm text-gray-600 dark:text-gray-400">
                            <Phone className="w-4 h-4 mr-1 text-green-500" />
                            <span className="truncate">{driver.data?.personal_data?.phone_no || 'N/A'}</span>
                          </div>
                          <div className="flex items-center text-sm text-gray-600 dark:text-gray-400">
                            <Activity className="w-4 h-4 mr-1 text-purple-500" />
                            <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                              driver.status === 'active'
                                ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
                                : 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200'
                            }`}>
                              {driver.status === 'active' ? 'Ativo' : 'Inativo'}
                            </span>
                          </div>
                          <div className="flex items-center text-sm">
                            <Car className="w-4 h-4 mr-1 text-blue-500" />
                            <span className="text-xs text-gray-600 dark:text-gray-400 truncate">
                              {driver.data?.personal_data?.vehicle_no || 'N/A'}
                            </span>
                          </div>
                        </div>
                        {driver.data?.metrics && (
                          <div className="mt-3 pt-3 border-t border-gray-200 dark:border-gray-600">
                            <div className="grid grid-cols-3 gap-4 text-center">
                              <div>
                                <p className="text-xs text-gray-600 dark:text-gray-400">Receita</p>
                                <p className="text-sm font-semibold text-green-600 dark:text-green-400">
                                  R$ {Number(driver.revenue || 0).toFixed(2)}
                                </p>
                              </div>
                              <div>
                                <p className="text-xs text-gray-600 dark:text-gray-400">Horas Online</p>
                                <p className="text-sm font-semibold text-blue-600 dark:text-blue-400">
                                  {Number(driver.hours_online || 0).toFixed(1)}h
                                </p>
                              </div>
                              <div>
                                <p className="text-xs text-gray-600 dark:text-gray-400">Rating</p>
                                <p className="text-sm font-semibold text-purple-600 dark:text-purple-400 flex items-center justify-center">
                                  <Star className="w-3 h-3 mr-1" />
                                  {Number(driver.rating || 0).toFixed(1)}
                                </p>
                              </div>
                            </div>
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Modal de Detalhes do Motorista */}
      <DriverDetailsModal
        isOpen={isDetailsModalOpen}
        onClose={handleCloseDetailsModal}
        driverId={selectedDriverId}
        driverName={selectedDriverName}
      />
    </>
  );
};

export default DriversListModal;
