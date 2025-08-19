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
  const url = `https://maps.googleapis.com/maps/api/geocode/json?address=${encodeURIComponent(address)}&region=br&key=${GOOGLE_MAPS_API_KEY}`;
  const resp = await fetch(url);
  const data = await resp.json();
  if (data.status === "OK" && data.results.length > 0) {
    const { lat, lng } = data.results[0].geometry.location;
    return { lat, lng };
  }
  return null;
}

export default function MapaCalorProblemas() {
  const [pontos, setPontos] = useState([]);
  const [loading, setLoading] = useState(true);
  const [tipo, setTipo] = useState('todas');
  const mapRef = useRef(null);
  const heatmapRef = useRef(null);
  const { isLoaded } = useJsApiLoader({
    googleMapsApiKey: GOOGLE_MAPS_API_KEY,
    libraries: ["visualization"]
  });

  useEffect(() => {
    async function fetchAndGeocode() {
      setLoading(true);
      const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
      const resp = await fetch(`${API_URL}/api/mapa-calor-problemas`);
      const json = await resp.json();
      const pontosApi = json.pontos || [];
      const cache = JSON.parse(localStorage.getItem("geocode_cache") || "{}")
      const geocoded = [];
      for (const item of pontosApi) {
        let enderecoCompleto = "";
        if (item.endereco) enderecoCompleto += item.endereco + ", ";
        if (item.bairro) enderecoCompleto += item.bairro + ", ";
        if (item.cidade) enderecoCompleto += item.cidade + ", ";
        if (item.estado) enderecoCompleto += item.estado + ", ";
        enderecoCompleto += "Brasil";
        let cacheKey = enderecoCompleto;
        let coords = cache[cacheKey];
        if (!coords) {
          coords = await geocodeAddress(enderecoCompleto);
          if (coords) {
            cache[cacheKey] = coords;
            localStorage.setItem("geocode_cache", JSON.stringify(cache));
          }
        }
        if (coords) {
          geocoded.push({
            ...item,
            location: coords
          });
        }
      }
      setPontos(geocoded);
      setLoading(false);
    }
    fetchAndGeocode();
  }, []);

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
      <div style={{ marginBottom: 16, display: 'flex', gap: 8 }}>
        <button onClick={() => setTipo('todas')} style={{ background: tipo === 'todas' ? '#3B82F6' : '#eee', color: tipo === 'todas' ? '#fff' : '#333', border: 'none', borderRadius: 4, padding: '6px 12px', cursor: 'pointer' }}>Todas</button>
        <button onClick={() => setTipo('concluida')} style={{ background: tipo === 'concluida' ? '#10B981' : '#eee', color: tipo === 'concluida' ? '#fff' : '#333', border: 'none', borderRadius: 4, padding: '6px 12px', cursor: 'pointer' }}>Concluídas</button>
        <button onClick={() => setTipo('cancelada')} style={{ background: tipo === 'cancelada' ? '#EF4444' : '#eee', color: tipo === 'cancelada' ? '#fff' : '#333', border: 'none', borderRadius: 4, padding: '6px 12px', cursor: 'pointer' }}>Canceladas</button>
        <button onClick={() => setTipo('perdida')} style={{ background: tipo === 'perdida' ? '#F59E0B' : '#eee', color: tipo === 'perdida' ? '#fff' : '#333', border: 'none', borderRadius: 4, padding: '6px 12px', cursor: 'pointer' }}>Perdidas</button>
      </div>
      <GoogleMap
        mapContainerStyle={mapContainerStyle}
        center={defaultCenter}
        zoom={5}
        onLoad={map => { mapRef.current = map; }}
      />
    </div>
  );
}
