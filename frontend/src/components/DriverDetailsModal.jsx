import React, { useState, useEffect } from 'react';
import { X, User, Phone, Mail, MapPin, Car, Star, TrendingUp, DollarSign, Clock, Calendar, Award, AlertCircle } from 'lucide-react';

const DriverDetailsModal = ({ isOpen, onClose, driverId, driverName }) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [driverDetails, setDriverDetails] = useState(null);

  // Função para buscar detalhes do motorista
  const fetchDriverDetails = async (id) => {
    if (!id) return;
    
    console.log('🚀 INICIANDO fetchDriverDetails para ID:', id);
    console.log('🚀 Nome do motorista:', driverName);
    
    try {
      setLoading(true);
      setError(null);
      
      const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
      
      console.log('🔍 Buscando dados para driver ID:', id);
      
      // PRIORIDADE 1: Tentar endpoint específico de personal-details primeiro
      let personalData = null;
      let personalAnalytics = null;
      
      try {
        console.log('🎯 Tentando endpoint específico primeiro:', `${API_URL}/api/drivers/personal-details/${id}`);
        const specificPersonalResponse = await fetch(`${API_URL}/api/drivers/personal-details/${id}`);
        
        if (specificPersonalResponse.ok) {
          personalData = await specificPersonalResponse.json();
          console.log('✅ DADOS ESPECÍFICOS ENCONTRADOS:', personalData);
          
          // Se encontrou dados específicos, pular busca na lista geral
          if (personalData && (personalData.personal_data || personalData.rides_history)) {
            console.log('🎯 Usando dados específicos completos!');
          }
        } else {
          console.log('⚠️ Endpoint específico não funcionou, status:', specificPersonalResponse.status);
        }
      } catch (e) {
        console.log('⚠️ Erro no endpoint específico:', e.message);
      }
      
      // FALLBACK: Buscar da lista analytics e fazer match inteligente (apenas se não encontrou dados específicos)
      // 1. Buscar dados analytics (dados coletivos da lista)
      const analyticsResponse = await fetch(`${API_URL}/api/drivers/analytics`);
      const analyticsData = await analyticsResponse.json();
      
      console.log('📊 DADOS COMPLETOS DA API ANALYTICS:', analyticsData);
      
      // Encontrar o motorista específico na lista analytics
      const driverFromAnalytics = analyticsData.drivers?.find(d => d.driver_id === id);
      console.log('📊 Driver encontrado em analytics:', driverFromAnalytics);
      
      if (!driverFromAnalytics) {
        throw new Error('Motorista não encontrado na base de dados');
      }
      
      console.log('📊 ESTRUTURA DETALHADA DO DRIVER:', {
        driver_id: driverFromAnalytics.driver_id,
        name: driverFromAnalytics.name,
        phone: driverFromAnalytics.phone,
        mobile: driverFromAnalytics.mobile,
        city: driverFromAnalytics.city,
        vehicle: driverFromAnalytics.vehicle,
        email: driverFromAnalytics.email,
        status: driverFromAnalytics.status,
        join_date: driverFromAnalytics.join_date,
        data: driverFromAnalytics.data,
        // VERIFICAR ESTRUTURA DENTRO DE DATA
        data_profile: driverFromAnalytics.data?.profile,
        data_original: driverFromAnalytics.data?.original_data,
        data_metrics: driverFromAnalytics.data?.metrics
      });
      
      // 2. Buscar dados pessoais usando match inteligente (apenas se não encontrou dados específicos)
      
      // Tentar buscar dados pessoais por vários métodos (apenas se personalData ainda for null)
      if (!personalData || !personalData.personal_data) {
        try {
          // Método 1: Buscar todos os dados pessoais e fazer match por nome
          const allPersonalResponse = await fetch(`${API_URL}/api/drivers/personal-details?limit=100`);
          if (allPersonalResponse.ok) {
            const allPersonal = await allPersonalResponse.json();
            
            // Tentar match por nome (removendo espaços extras e normalizando)
            const driverName = driverFromAnalytics.name?.trim().toLowerCase().replace(/\s+/g, ' ');
            console.log('🔍 Procurando por nome:', driverName);
            
            const foundPersonalData = allPersonal.drivers?.find(d => {
              const personalName = d.personal_data?.driver_name?.trim().toLowerCase().replace(/\s+/g, ' ');
              if (!personalName || !driverName) return false;
              
              // Match exato
              if (personalName === driverName) return true;
              
              // Match parcial (primeiro e último nome)
              const driverWords = driverName.split(' ');
              const personalWords = personalName.split(' ');
              
              if (driverWords.length >= 2 && personalWords.length >= 2) {
                const firstMatch = driverWords[0] === personalWords[0];
                const lastMatch = driverWords[driverWords.length - 1] === personalWords[personalWords.length - 1];
                return firstMatch && lastMatch;
              }
              
              return false;
            });
            
            // Só sobrescrever se não tínhamos dados ou se encontrou dados melhores
            if (foundPersonalData && (!personalData || foundPersonalData.personal_data)) {
              personalData = foundPersonalData;
              console.log('✅ Match encontrado na lista geral:', personalData?.driver_id, personalData?.personal_data?.driver_name);
            }
          }
        } catch (e) {
          console.log('⚠️ Erro na busca por dados pessoais:', e.message);
        }
      }
      
      // 3. Buscar analytics individuais se temos personal_data
      if (personalData) {
        try {
          console.log('📈 Tentando buscar analytics individuais para driver_id:', personalData.driver_id);
          const personalAnalyticsResponse = await fetch(`${API_URL}/api/drivers/analytics/${personalData.driver_id}`);
          console.log('📈 Status da resposta analytics individuais:', personalAnalyticsResponse.status);
          
          if (personalAnalyticsResponse.ok) {
            personalAnalytics = await personalAnalyticsResponse.json();
            console.log('📈 ANALYTICS PESSOAIS ENCONTRADOS:', personalAnalytics);
            console.log('📈 Estrutura analytics pessoais:', {
              data: personalAnalytics.data,
              profile: personalAnalytics.profile,
              metrics: personalAnalytics.metrics
            });
          } else {
            console.log('⚠️ Analytics individuais não disponíveis');
          }
        } catch (e) {
          console.log('⚠️ Erro ao buscar analytics específicos:', e.message);
        }
      } else {
        console.log('⚠️ Sem personal_data, pulando busca de analytics individuais');
      }
      
      // 4. Processar dados pessoais se encontrados
      let processedPersonalData = {};
      let processedRidesHistory = [];
      let processedWalletTransactions = [];
      
      if (personalData) {
        console.log('📋 PROCESSANDO DADOS PESSOAIS:', personalData);
        
        // Parse do personal_data
        processedPersonalData = personalData.personal_data;
        console.log('📋 Personal data original:', processedPersonalData);
        
        if (typeof processedPersonalData === 'string') {
          try {
            processedPersonalData = JSON.parse(processedPersonalData);
            console.log('📋 Personal data após parse JSON:', processedPersonalData);
          } catch (e) {
            console.log('❌ Erro ao fazer parse do personal_data:', e.message);
            processedPersonalData = {};
          }
        }
        
        console.log('📋 DADOS PESSOAIS PROCESSADOS:', processedPersonalData);
        
        // Parse do rides_history
        processedRidesHistory = personalData.rides_history;
        if (typeof processedRidesHistory === 'string') {
          try {
            processedRidesHistory = JSON.parse(processedRidesHistory);
          } catch (e) {
            processedRidesHistory = [];
          }
        }
        
        // Parse do wallet_transactions
        processedWalletTransactions = personalData.wallet_transactions;
        if (typeof processedWalletTransactions === 'string') {
          try {
            processedWalletTransactions = JSON.parse(processedWalletTransactions);
          } catch (e) {
            processedWalletTransactions = [];
          }
        }
      }
      
      // 5. Combinar dados de forma inteligente e preencher todos os campos esperados
      const metrics = driverFromAnalytics.data?.metrics || {};
      const originalMetrics = driverFromAnalytics.data?.original_data || {};
      
      console.log('📊 DADOS PARA MÉTRICAS:', {
        metrics,
        originalMetrics,
        total_rides_metrics: metrics.total_rides,
        rides_last_30_original: originalMetrics['Rides in Last 30 Days'],
        driver_ratings_original: originalMetrics['Driver Ratings'],
        status_original: originalMetrics.Status
      });
      
      const analyticsMergedData = {
        total_earnings: metrics.total_earnings ?? 0,
        total_rides: originalMetrics['Rides in Last 30 Days'] || (metrics.total_rides ?? 0),
        average_rating: originalMetrics['Driver Ratings'] || (metrics.rating ?? 3.5),
        completion_rate: metrics.success_rate ?? 0,
        completed_rides: originalMetrics['Rides in Last 30 Days'] || (metrics.success_rides ?? 0),
        cancelled_rides: (metrics.user_cancelled ?? 0) + (metrics.driver_cancelled ?? 0),
        average_ride_value: metrics.total_earnings && metrics.total_rides ? (metrics.total_earnings / metrics.total_rides) : 0,
        first_ride_date: metrics.first_ride_date ?? null,
        last_ride_date: metrics.last_ride_date ?? null,
        active_days: metrics.active_days ?? 0,
        total_distance: metrics.total_distance ?? 0,
        total_duration: metrics.online_hours ? Math.round(metrics.online_hours * 60) : 0, // minutos
        current_subscription: metrics.current_subscription ?? null
      };

      // Se personalAnalytics existir, sobrescreve campos acima
      if (personalAnalytics && typeof personalAnalytics === 'object') {
        Object.assign(analyticsMergedData, personalAnalytics);
      }

      // Dados pessoais: usar o que vier do personalData, senão usar fallback do analytics
      // EXTRAIR DADOS REAIS DO OBJETO DATA
      const driverData = driverFromAnalytics.data || {};
      const profileData = driverData.profile || {};
      const originalData = driverData.original_data || {};
      const metricsData = driverData.metrics || {};
      
      console.log('🔍 EXTRAINDO DADOS REAIS:', {
        profileData,
        originalData,
        metricsData,
        email_profile: profileData.email,
        email_original: originalData.Email,
        city_profile: profileData.city,
        city_original: originalData.City,
        vehicle_profile: profileData.vehicle,
        vehicle_original: originalData['Vehicle Number'],
        join_date_original: originalData['Registered On'],
        mobile_original: originalData.Mobile,
        status_original: originalData.Status,
        rides_last_30: originalData['Rides in Last 30 Days'],
        driver_ratings: originalData['Driver Ratings']
      });
      
      const personalDataObj = personalData ? {
        ...personalData,
        personal_data: processedPersonalData,
        rides_history: processedRidesHistory,
        wallet_transactions: processedWalletTransactions
      } : {
        driver_id: id,
        city: originalData.City || profileData.city || driverFromAnalytics.city || 'N/A',
        personal_data: {
          driver_name: driverFromAnalytics.name,
          phone_no: originalData.Mobile || driverFromAnalytics.mobile || driverFromAnalytics.phone || '',
          email: originalData.Email || profileData.email || driverFromAnalytics.email || '',
          city: originalData.City || profileData.city || driverFromAnalytics.city || '',
          status: originalData.Status || profileData.status || driverFromAnalytics.status || '',
          joining_date: originalData['Registered On'] || driverFromAnalytics.join_date || '',
          vehicle: originalData['Vehicle Number'] || profileData.vehicle || driverFromAnalytics.vehicle || '',
          vehicle_no: originalData['Vehicle Number'] || profileData.vehicle || driverFromAnalytics.vehicle_no || '',
          credit_wallet_balance: metrics.credit_wallet_balance ?? 0,
          last_ride_on: metrics.last_ride_date ?? '',
        },
        rides_history: [],
        wallet_transactions: []
      };

      const combinedData = {
        listData: driverFromAnalytics,
        personal: personalDataObj,
        analytics: analyticsMergedData
      };

      console.log('✅ Dados combinados finais:', combinedData);
      console.log('🔍 DEBUG - Dados para o modal:');
      console.log('📊 listData (analytics):', combinedData.listData);
      console.log('👤 personal:', combinedData.personal);
      console.log('📈 analytics:', combinedData.analytics);
      console.log('📋 Campos específicos:');
      console.log('- Nome:', combinedData.personal.personal_data?.name || combinedData.personal.personal_data?.driver_name || combinedData.listData?.name);
      console.log('- Email:', combinedData.personal.personal_data?.email || combinedData.listData?.email);
      console.log('- Cidade:', combinedData.personal.city || combinedData.personal.personal_data?.city || combinedData.listData?.city);
      console.log('- Veículo:', combinedData.personal.personal_data?.vehicle || combinedData.personal.personal_data?.vehicle_no || combinedData.listData?.vehicle);
      console.log('- Data de ingresso:', combinedData.personal.personal_data?.join_date || combinedData.personal.personal_data?.joining_date || combinedData.listData?.join_date);
      console.log('- Total de corridas:', combinedData.analytics.total_rides || combinedData.listData?.data?.metrics?.total_rides);
      console.log('- Rating:', combinedData.analytics.average_rating || combinedData.listData?.data?.metrics?.rating || combinedData.listData?.driver_ratings);
      
      console.log('🎯 VALORES FINAIS QUE SERÃO EXIBIDOS:');
      console.log('🎯 Nome final:', combinedData.personal.personal_data?.name || combinedData.personal.personal_data?.driver_name || combinedData.listData?.name || 'N/A');
      console.log('🎯 Email final:', combinedData.personal.personal_data?.email || combinedData.listData?.email || 'N/A');
      console.log('🎯 Telefone final:', combinedData.personal.personal_data?.phone_no || combinedData.listData?.phone || combinedData.listData?.mobile || 'N/A');
      console.log('🎯 Cidade final:', combinedData.personal.city || combinedData.personal.personal_data?.city || combinedData.listData?.city || 'N/A');
      console.log('🎯 Veículo final:', combinedData.personal.personal_data?.vehicle || combinedData.personal.personal_data?.vehicle_no || combinedData.listData?.vehicle || 'N/A');
      console.log('🎯 Data ingresso final:', combinedData.personal.personal_data?.joining_date || combinedData.personal.personal_data?.join_date || combinedData.listData?.join_date || 'N/A');
      console.log('🎯 Total corridas final:', combinedData.analytics.total_rides || combinedData.listData?.data?.metrics?.total_rides || 0);
      console.log('🎯 Rating final:', combinedData.analytics.average_rating || combinedData.listData?.data?.metrics?.rating || combinedData.listData?.driver_ratings || 'N/A');
      
      console.log('🚀 CHAMANDO setDriverDetails com:', combinedData);
      
      setDriverDetails(combinedData);

    } catch (err) {
      setError(err.message);
      console.error('Erro ao buscar detalhes do motorista:', err);
    } finally {
      setLoading(false);
    }
  };

  // Buscar dados quando o modal abrir
  useEffect(() => {
    if (isOpen && driverId) {
      fetchDriverDetails(driverId);
    }
  }, [isOpen, driverId]);

  // Fechar modal
  const handleClose = () => {
    setDriverDetails(null);
    setError(null);
    onClose();
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl shadow-2xl max-w-4xl w-full max-h-[90vh] overflow-hidden">
        
        {/* Header do Modal */}
        <div className="bg-gradient-to-r from-blue-600 to-purple-600 text-white p-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 bg-white/20 rounded-full flex items-center justify-center">
                <User className="w-6 h-6" />
              </div>
              <div>
                <h2 className="text-2xl font-bold">{driverName}</h2>
                <p className="text-blue-100">ID: {driverId}</p>
              </div>
            </div>
            <button
              onClick={handleClose}
              className="w-10 h-10 bg-white/20 rounded-full flex items-center justify-center hover:bg-white/30 transition-colors"
            >
              <X className="w-6 h-6" />
            </button>
          </div>
        </div>

        {/* Conteúdo do Modal */}
        <div className="p-6 overflow-y-auto max-h-[calc(90vh-120px)]">
          
          {loading && (
            <div className="flex items-center justify-center py-12">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
              <span className="ml-3 text-gray-600">Carregando dados...</span>
            </div>
          )}

          {error && (
            <div className="bg-red-50 border border-red-200 rounded-xl p-6 mb-6">
              <div className="flex items-center gap-3">
                <AlertCircle className="w-6 h-6 text-red-500" />
                <div>
                  <h3 className="font-semibold text-red-800">Erro ao carregar dados</h3>
                  <p className="text-red-600">{error}</p>
                </div>
              </div>
            </div>
          )}

          {driverDetails && (
            <div className="space-y-6">
              
              {/* Informações Pessoais */}
              <div className="bg-gradient-to-r from-blue-50 to-indigo-50 border border-blue-200 rounded-xl p-6">
                <h3 className="text-lg font-semibold text-blue-800 mb-4 flex items-center gap-2">
                  <User className="w-5 h-5" />
                  Informações Pessoais
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="flex items-center gap-3">
                    <User className="w-5 h-5 text-gray-500" />
                    <div>
                      <p className="text-sm text-gray-500">Nome</p>
                      <p className="font-medium">{(() => {
                        const nome = driverDetails.personal.personal_data?.name
                          || driverDetails.personal.personal_data?.driver_name
                          || driverDetails.listData?.name
                          || driverName
                          || 'N/A';
                        console.log('🖥️ RENDERIZANDO Nome:', nome);
                        console.log('🖥️ Opções de nome:', {
                          'personal.personal_data.name': driverDetails.personal.personal_data?.name,
                          'personal.personal_data.driver_name': driverDetails.personal.personal_data?.driver_name,
                          'listData.name': driverDetails.listData?.name,
                          'driverName': driverName
                        });
                        return nome;
                      })()}</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-3">
                    <Phone className="w-5 h-5 text-gray-500" />
                    <div>
                      <p className="text-sm text-gray-500">Telefone</p>
                      <p className="font-medium">{(() => {
                        const telefone = driverDetails.personal.personal_data?.phone
                          || driverDetails.personal.personal_data?.phone_no
                          || driverDetails.listData?.mobile
                          || driverDetails.listData?.phone
                          || 'N/A';
                        console.log('🖥️ RENDERIZANDO Telefone:', telefone);
                        console.log('🖥️ Opções de telefone:', {
                          'personal.personal_data.phone': driverDetails.personal.personal_data?.phone,
                          'personal.personal_data.phone_no': driverDetails.personal.personal_data?.phone_no,
                          'listData.mobile': driverDetails.listData?.mobile,
                          'listData.phone': driverDetails.listData?.phone
                        });
                        return telefone;
                      })()}</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-3">
                    <Mail className="w-5 h-5 text-gray-500" />
                    <div>
                      <p className="text-sm text-gray-500">Email</p>
                      <p className="font-medium">{(() => {
                        const email = driverDetails.personal.personal_data?.email
                          || driverDetails.listData?.email
                          || 'N/A';
                        console.log('🖥️ RENDERIZANDO Email:', email);
                        console.log('🖥️ Opções de email:', {
                          'personal.personal_data.email': driverDetails.personal.personal_data?.email,
                          'listData.email': driverDetails.listData?.email,
                          'listData.data.original_data.Email': driverDetails.listData?.data?.original_data?.Email,
                          'listData.data.profile.email': driverDetails.listData?.data?.profile?.email
                        });
                        return email;
                      })()}</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-3">
                    <MapPin className="w-5 h-5 text-gray-500" />
                    <div>
                      <p className="text-sm text-gray-500">Cidade</p>
                      <p className="font-medium">{
                        driverDetails.personal.city
                        || driverDetails.personal.personal_data?.city
                        || driverDetails.listData?.city
                        || 'N/A'
                      }</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-3">
                    <Car className="w-5 h-5 text-gray-500" />
                    <div>
                      <p className="text-sm text-gray-500">Status</p>
                      <p className="font-medium">
                        <span className={`inline-flex px-2 py-1 text-xs font-medium rounded-full ${
                          (driverDetails.personal.personal_data?.status 
                            || driverDetails.listData?.status
                            || '').toLowerCase().includes('active') || 
                          (driverDetails.personal.personal_data?.status 
                            || driverDetails.listData?.status
                            || '').toLowerCase().includes('online')
                            ? 'bg-green-100 text-green-800' 
                            : 'bg-red-100 text-red-800'
                        }`}>
                          {driverDetails.personal.personal_data?.status
                            || driverDetails.listData?.status
                            || 'Offline'}
                        </span>
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center gap-3">
                    <Calendar className="w-5 h-5 text-gray-500" />
                    <div>
                      <p className="text-sm text-gray-500">Data de Ingresso</p>
                      <p className="font-medium">{
                        driverDetails.personal.personal_data?.join_date
                        || driverDetails.personal.personal_data?.joining_date
                        || driverDetails.listData?.join_date
                        || driverDetails.listData?.joining_date
                        || 'N/A'
                      }</p>
                    </div>
                  </div>
                </div>
              </div>

              {/* Métricas de Performance */}
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                
                <div className="bg-green-50 border border-green-200 rounded-xl p-4">
                  <div className="flex items-center gap-3 mb-2">
                    <DollarSign className="w-5 h-5 text-green-600" />
                    <span className="text-sm font-medium text-green-800">Ganhos Totais</span>
                  </div>
                  <p className="text-2xl font-bold text-green-700">
                    R$ {Number(
                      driverDetails.analytics.total_earnings 
                      || driverDetails.listData?.data?.metrics?.total_earnings 
                      || 0
                    ).toLocaleString('pt-BR', { minimumFractionDigits: 2 })}
                  </p>
                </div>

                <div className="bg-blue-50 border border-blue-200 rounded-xl p-4">
                  <div className="flex items-center gap-3 mb-2">
                    <Car className="w-5 h-5 text-blue-600" />
                    <span className="text-sm font-medium text-blue-800">Total de Corridas</span>
                  </div>
                  <p className="text-2xl font-bold text-blue-700">{
                    driverDetails.analytics.total_rides 
                    || driverDetails.listData?.data?.metrics?.total_rides 
                    || driverDetails.listData?.data?.metrics?.rides_last_30_days
                    || 0
                  }</p>
                </div>

                <div className="bg-yellow-50 border border-yellow-200 rounded-xl p-4">
                  <div className="flex items-center gap-3 mb-2">
                    <Star className="w-5 h-5 text-yellow-600" />
                    <span className="text-sm font-medium text-yellow-800">Rating Médio</span>
                  </div>
                  <p className="text-2xl font-bold text-yellow-700">
                    {(
                      driverDetails.analytics.average_rating 
                      || driverDetails.listData?.data?.metrics?.rating 
                      || driverDetails.listData?.driver_ratings
                      || 3.5
                    )} ⭐
                  </p>
                </div>

                <div className="bg-purple-50 border border-purple-200 rounded-xl p-4">
                  <div className="flex items-center gap-3 mb-2">
                    <TrendingUp className="w-5 h-5 text-purple-600" />
                    <span className="text-sm font-medium text-purple-800">Taxa Conclusão</span>
                  </div>
                  <p className="text-2xl font-bold text-purple-700">
                    {Number(driverDetails.analytics.completion_rate || 0).toFixed(1)}%
                  </p>
                </div>

              </div>

              {/* Estatísticas Detalhadas */}
              <div className="bg-gradient-to-r from-gray-50 to-slate-50 border border-gray-200 rounded-xl p-6">
                <h3 className="text-lg font-semibold text-gray-800 mb-4 flex items-center gap-2">
                  <Award className="w-5 h-5 text-yellow-600" />
                  Estatísticas Detalhadas
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                  
                  <div>
                    <h4 className="font-medium text-gray-700 mb-3">Performance das Corridas</h4>
                    <div className="space-y-2">
                      <div className="flex justify-between">
                        <span className="text-gray-600">Completadas:</span>
                        <span className="font-medium">{driverDetails.analytics.completed_rides || 0}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">Canceladas:</span>
                        <span className="font-medium">{driverDetails.analytics.cancelled_rides || 0}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">Valor médio:</span>
                        <span className="font-medium">R$ {Number(driverDetails.analytics.average_ride_value || 0).toFixed(2)}</span>
                      </div>
                    </div>
                  </div>

                  <div>
                    <h4 className="font-medium text-gray-700 mb-3">Dados Temporais</h4>
                    <div className="space-y-2">
                      <div className="flex justify-between">
                        <span className="text-gray-600">Primeira corrida:</span>
                        <span className="font-medium">
                          {driverDetails.analytics.first_ride_date ? 
                            new Date(driverDetails.analytics.first_ride_date).toLocaleDateString('pt-BR') : 'N/A'}
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">Última corrida:</span>
                        <span className="font-medium">
                          {driverDetails.analytics.last_ride_date ? 
                            new Date(driverDetails.analytics.last_ride_date).toLocaleDateString('pt-BR') : 'N/A'}
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">Dias ativos:</span>
                        <span className="font-medium">{driverDetails.analytics.active_days || 0}</span>
                      </div>
                    </div>
                  </div>

                  <div>
                    <h4 className="font-medium text-gray-700 mb-3">Dados Operacionais</h4>
                    <div className="space-y-2">
                      <div className="flex justify-between">
                        <span className="text-gray-600">Distância total:</span>
                        <span className="font-medium">{Number(driverDetails.analytics.total_distance || 0).toFixed(1)} km</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">Tempo total:</span>
                        <span className="font-medium">{Math.floor((driverDetails.analytics.total_duration || 0) / 60)}h {(driverDetails.analytics.total_duration || 0) % 60}min</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">Saldo carteira:</span>
                        <span className="font-medium">
                          R$ {Number(driverDetails.personal.personal_data?.credit_wallet_balance || 0).toFixed(2)}
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">Última corrida:</span>
                        <span className="font-medium">
                          {driverDetails.personal.personal_data?.last_ride_on || 'N/A'}
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">Veículo:</span>
                        <span className="font-medium">
                          {driverDetails.personal.personal_data?.vehicle
                            || driverDetails.personal.personal_data?.vehicle_no
                            || driverDetails.listData?.vehicle
                            || driverDetails.listData?.vehicle_no
                            || 'N/A'}
                        </span>
                      </div>
                    </div>
                  </div>

                </div>
              </div>

              {/* Histórico de Corridas Recentes */}
              {driverDetails.personal.rides_history && driverDetails.personal.rides_history.length > 0 && (
                <div className="bg-white border border-gray-200 rounded-xl p-6">
                  <h3 className="text-lg font-semibold text-gray-800 mb-4 flex items-center gap-2">
                    <Clock className="w-5 h-5 text-blue-600" />
                    Últimas Corridas ({Math.min(5, driverDetails.personal.rides_history.length)})
                  </h3>
                  <div className="overflow-x-auto">
                    <table className="w-full">
                      <thead className="bg-gray-50">
                        <tr>
                          <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Data</th>
                          <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Origem</th>
                          <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Destino</th>
                          <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Distância</th>
                          <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Valor</th>
                          <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Rating</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-gray-200">
                        {driverDetails.personal.rides_history.slice(0, 5).map((ride, index) => (
                          <tr key={index} className="hover:bg-gray-50">
                            <td className="px-4 py-3 text-sm text-gray-900">
                              {ride.drop_time || 'N/A'}
                            </td>
                            <td className="px-4 py-3 text-sm text-gray-900 max-w-32 truncate" title={ride.origin}>
                              {ride.origin || 'N/A'}
                            </td>
                            <td className="px-4 py-3 text-sm text-gray-900 max-w-32 truncate" title={ride.destination}>
                              {ride.destination || 'N/A'}
                            </td>
                            <td className="px-4 py-3 text-sm text-gray-900">
                              {ride.google_distance ? `${Number(ride.google_distance).toFixed(1)} km` : 'N/A'}
                            </td>
                            <td className="px-4 py-3 text-sm font-medium text-green-600">
                              R$ {Number(ride.fare || 0).toFixed(2)}
                            </td>
                            <td className="px-4 py-3 text-sm text-gray-900">
                              {ride.driver_rating !== '--' ? ride.driver_rating : 'N/A'}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}

              {/* Assinatura Atual */}
              {driverDetails.analytics.current_subscription && (
                <div className="bg-gradient-to-r from-purple-50 to-pink-50 border border-purple-200 rounded-xl p-6">
                  <h3 className="text-lg font-semibold text-purple-800 mb-4 flex items-center gap-2">
                    <Award className="w-5 h-5" />
                    Assinatura Atual
                  </h3>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div>
                      <p className="text-sm text-purple-600">Plano</p>
                      <p className="font-medium text-purple-800">{driverDetails.analytics.current_subscription.plan_type || 'N/A'}</p>
                    </div>
                    <div>
                      <p className="text-sm text-purple-600">Status</p>
                      <p className="font-medium text-purple-800">{driverDetails.analytics.current_subscription.status || 'N/A'}</p>
                    </div>
                    <div>
                      <p className="text-sm text-purple-600">Preço</p>
                      <p className="font-medium text-purple-800">
                        {driverDetails.analytics.current_subscription.price ? 
                          `R$ ${Number(driverDetails.analytics.current_subscription.price).toFixed(2)}` : 'N/A'}
                      </p>
                    </div>
                  </div>
                </div>
              )}

            </div>
          )}
        </div>

        {/* Footer do Modal */}
        <div className="bg-gray-50 px-6 py-4 flex justify-end">
          <button
            onClick={handleClose}
            className="px-6 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors"
          >
            Fechar
          </button>
        </div>

      </div>
    </div>
  );
};

export default DriverDetailsModal;
