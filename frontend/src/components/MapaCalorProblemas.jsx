import React, { useEffect, useState, useRef } from "react";
import { GoogleMap, useJsApiLoader } from "@react-google-maps/api";

// Chave da API Google Maps (use variável de ambiente Vite)
const GOOGLE_MAPS_API_KEY = import.meta.env.VITE_GOOGLE_MAPS_API_KEY || "SUA_CHAVE_AQUI";

const mapContainerStyle = {
  width: "100%",
  height: "500px"
};
const defaultCenter = { lat: -15.7801, lng: -47.9292 }; // Centro do Brasil

// Função utilitária para geocodificar endereço usando Google Maps Geocoding API
async function geocodeAddress(address) {
  try {
    const url = `https://maps.googleapis.com/maps/api/geocode/json?address=${encodeURIComponent(address)}&region=br&key=${GOOGLE_MAPS_API_KEY}`;
    const resp = await fetch(url);
    const data = await resp.json();

    if (data.status === "OK" && data.results.length > 0) {
      const { lat, lng } = data.results[0].geometry.location;

      // Validar se coordenadas estão dentro do território brasileiro aproximado
      if (lat >= -34 && lat <= 6 && lng >= -74 && lng <= -34) {
        return { lat, lng };
      }
    }

    // Log de endereços que falharam na geocodificação
    console.warn(`Geocodificação falhou para endereço: ${address}`);
    return null;
  } catch (error) {
    console.error(`Erro na geocodificação: ${error.message}`);
    return null;
  }
}

// Função para validar coordenadas brasileiras
function isValidBrazilianCoordinate(lat, lng) {
  // Limites aproximados do Brasil
  return lat >= -34 && lat <= 6 && lng >= -74 && lng <= -34;
}

// Função para geocodificar múltiplos endereços em paralelo com limite de concorrência
async function geocodeAddressesBatch(addresses, concurrencyLimit = 5) {
  const results = [];
  const cache = JSON.parse(localStorage.getItem("geocode_cache") || "{}");

  // Processar em lotes para evitar sobrecarga da API
  for (let i = 0; i < addresses.length; i += concurrencyLimit) {
    const batch = addresses.slice(i, i + concurrencyLimit);
    const batchPromises = batch.map(async (item, index) => {
      const globalIndex = i + index;
      let enderecoCompleto = "";

      if (item.endereco) enderecoCompleto += item.endereco + ", ";
      if (item.bairro) enderecoCompleto += item.bairro + ", ";
      if (item.cidade) enderecoCompleto += item.cidade + ", ";
      if (item.estado) enderecoCompleto += item.estado + ", ";
      enderecoCompleto += "Brasil";

      const cacheKey = enderecoCompleto;
      let coords = cache[cacheKey];

      if (!coords) {
        coords = await geocodeAddress(enderecoCompleto);
        if (coords) {
          cache[cacheKey] = coords;
          localStorage.setItem("geocode_cache", JSON.stringify(cache));
        }
      }

      if (coords && isValidBrazilianCoordinate(coords.lat, coords.lng)) {
        return {
          ...item,
          location: coords
        };
      }

      return null;
    });

    const batchResults = await Promise.all(batchPromises);
    results.push(...batchResults.filter(result => result !== null));
  }

  return results;
}

export default function MapaCalorProblemas({ periodo = '30d', cidade = null }) {
  const [pontos, setPontos] = useState([]);
  const [loading, setLoading] = useState(true);
  const [tipo, setTipo] = useState('todas');
  const [showCacheOptions, setShowCacheOptions] = useState(false);
  const mapRef = useRef(null);
  const heatmapRef = useRef(null);
  const { isLoaded } = useJsApiLoader({
    googleMapsApiKey: GOOGLE_MAPS_API_KEY,
    libraries: ["visualization"]
  });

  // Função para limpar cache de geocodificação
  const clearGeocodeCache = () => {
    localStorage.removeItem("geocode_cache");
    alert("Cache de geocodificação limpo! Recarregue a página para refazer as geocodificações.");
  };

  useEffect(() => {
    // Limpar estado completamente quando filtros mudam
    setPontos([]);
    setLoading(true);
    setTipo('todas');

    async function fetchAndGeocode() {
      try {
        const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

        // Construir URL com parâmetros de filtro
        const params = new URLSearchParams({
          periodo: periodo
        });
        if (cidade) {
          params.append('cidade', cidade);
        }

        const url = `${API_URL}/api/mapa-calor-problemas?${params.toString()}`;

        const resp = await fetch(url);
        const json = await resp.json();
        const pontosApi = json.pontos || [];

        if (pontosApi.length === 0) {
          setPontos([]);
          setLoading(false);
          return;
        }

        // Usar geocodificação em lote com validação
        const geocoded = await geocodeAddressesBatch(pontosApi, 3); // Limitar a 3 requisições simultâneas

        // Contar por status após geocodificação
        const statusCount = {};
        geocoded.forEach(ponto => {
          const status = ponto.status || 'desconhecido';
          statusCount[status] = (statusCount[status] || 0) + 1;
        });

        setPontos(geocoded);
      } catch (error) {
        console.error('❌ Erro ao buscar dados do mapa de calor:', error);
        setPontos([]);
      } finally {
        setLoading(false);
      }
    }
    fetchAndGeocode();
  }, [periodo, cidade]); // Re-executar quando os filtros mudarem

  // Filtro dos pontos conforme o tipo selecionado
  const pontosFiltrados = tipo === 'todas' ? pontos : pontos.filter(p => p.status === tipo);

  // Dados para o heatmap: array de google.maps.LatLng ou {location, weight}
  const heatmapData = pontosFiltrados.map(p => new window.google.maps.LatLng(p.location.lat, p.location.lng));

  // Atualizar camada de heatmap quando dados ou tipo mudam
  useEffect(() => {
    if (!isLoaded || !mapRef.current) return;
    // Remove camada anterior
    if (heatmapRef.current) {
      heatmapRef.current.setMap(null);
    }
    if (heatmapData.length > 0 && window.google && window.google.maps.visualization) {
      heatmapRef.current = new window.google.maps.visualization.HeatmapLayer({
        data: heatmapData,
        radius: 40,
        opacity: 0.7,
        dissipating: true
      });
      heatmapRef.current.setMap(mapRef.current);
    }
  }, [isLoaded, heatmapData]);

  if (!isLoaded) return <div>Carregando mapa...</div>;
  if (loading) return <div>Carregando dados do heatmap...</div>;

  return (
    <div>
      {/* Filtros com design melhorado */}
      <div className="mb-6">
        <div className="flex justify-between items-center mb-3">
          <h4 className="text-sm font-medium text-gray-700">Filtrar por Tipo de Corrida</h4>
          <button
            onClick={() => setShowCacheOptions(!showCacheOptions)}
            className="text-xs text-gray-500 hover:text-gray-700 underline"
          >
            ⚙️ Opções
          </button>
        </div>

        {/* Opções de cache */}
        {showCacheOptions && (
          <div className="mb-3 p-3 bg-gray-50 rounded-lg">
            <button
              onClick={clearGeocodeCache}
              className="px-3 py-1 bg-red-100 text-red-700 rounded text-sm hover:bg-red-200 transition-colors"
            >
              🗑️ Limpar Cache de Geocodificação
            </button>
            <p className="text-xs text-gray-500 mt-1">
              Use isso se as localizações estiverem incorretas
            </p>
          </div>
        )}

        <div className="flex flex-wrap gap-2">
          <button
            onClick={() => setTipo('todas')}
            className={`px-4 py-2 rounded-lg font-medium transition-all duration-200 ${
              tipo === 'todas'
                ? 'bg-blue-600 text-white shadow-md'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            Todas
          </button>
          <button
            onClick={() => setTipo('concluida')}
            className={`px-4 py-2 rounded-lg font-medium transition-all duration-200 ${
              tipo === 'concluida'
                ? 'bg-green-600 text-white shadow-md'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            Concluídas
          </button>
          <button
            onClick={() => setTipo('cancelada')}
            className={`px-4 py-2 rounded-lg font-medium transition-all duration-200 ${
              tipo === 'cancelada'
                ? 'bg-red-600 text-white shadow-md'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            Canceladas
          </button>
          <button
            onClick={() => setTipo('perdida')}
            className={`px-4 py-2 rounded-lg font-medium transition-all duration-200 ${
              tipo === 'perdida'
                ? 'bg-yellow-600 text-white shadow-md'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            Perdidas
          </button>
        </div>
      </div>

      {/* Mapa */}
      <div className="relative">
        <GoogleMap
          mapContainerStyle={mapContainerStyle}
          center={defaultCenter}
          zoom={5}
          onLoad={map => { mapRef.current = map; }}
          options={{
            styles: [
              {
                featureType: "poi",
                elementType: "labels",
                stylers: [{ visibility: "off" }]
              }
            ]
          }}
        />

        {/* Overlay de loading */}
        {loading && (
          <div className="absolute inset-0 bg-white/80 backdrop-blur-sm flex items-center justify-center rounded-lg">
            <div className="text-center">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-2"></div>
              <p className="text-gray-600">Processando localizações...</p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
