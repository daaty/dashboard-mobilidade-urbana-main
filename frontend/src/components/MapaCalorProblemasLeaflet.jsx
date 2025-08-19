import React, { useEffect, useState } from "react";
import { MapContainer, TileLayer, useMap } from "react-leaflet";
import L from "leaflet";
import "leaflet/dist/leaflet.css";
import "leaflet.heat";

// Componente para adicionar o heatmap ao mapa
function HeatmapLayer({ points }) {
  const map = useMap();
  useEffect(() => {
    if (!map || !window.L || !points.length) return;
    // Remove heatmap anterior
    if (map._heatLayer) {
      map.removeLayer(map._heatLayer);
    }
    // Cria heatmap
    const heat = window.L.heatLayer(points, {
      radius: 40,
      blur: 25,
      maxZoom: 17,
      minOpacity: 0.5,
      gradient: { 0.4: 'blue', 0.65: 'lime', 1: 'red' }
    }).addTo(map);
    map._heatLayer = heat;
    return () => {
      if (map._heatLayer) map.removeLayer(map._heatLayer);
    };
  }, [map, points]);
  return null;

const defaultCenter = [-15.7801, -47.9292];
function MapaCalorProblemasLeaflet() {
  const [pontos, setPontos] = useState([]);
  const [loading, setLoading] = useState(true);
  const [aba, setAba] = useState('todas');

  useEffect(() => {
    async function fetchAndGeocode() {
      setLoading(true);
      try {
        const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
        const resp = await fetch(`${API_URL}/api/mapa-calor-problemas`);
        const json = await resp.json();
        const pontosApi = json.pontos || [];
        // Geocodificar todos (usa cache local)
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
            // Tenta pegar do próprio item se já tem lat/lng
            if (item.lat && item.lng) {
              coords = { lat: item.lat, lng: item.lng };
            }
          }
          if (coords) {
            geocoded.push({ ...item, location: coords });
          }
        }
        setPontos(geocoded);
      } catch (e) {
        setPontos([]);
      } finally {
        setLoading(false);
      }
    }
    fetchAndGeocode();
  }, []);

  // Filtro de pontos por aba
  let pontosFiltrados = pontos;
  if (aba === 'concluida') pontosFiltrados = pontos.filter(p => p.status === 'concluida');
  if (aba === 'cancelada') pontosFiltrados = pontos.filter(p => p.status === 'cancelada');
  if (aba === 'perdida') pontosFiltrados = pontos.filter(p => p.status === 'perdida');

  // Converter para formato aceito pelo leaflet.heat: [lat, lng, weight]
  const heatmapPoints = pontosFiltrados
    .filter(p => p.location)
    .map(p => [p.location.lat, p.location.lng, 1]);

  // Renderizar apenas o MapContainer como elemento raiz, sem controles customizados
  return (
    <MapContainer center={defaultCenter} zoom={5} style={{ width: '100%', height: 500, borderRadius: 12 }} scrollWheelZoom={true}>
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />
      <HeatmapLayer points={heatmapPoints} />
    </MapContainer>
  );
}

export default MapaCalorProblemasLeaflet;
