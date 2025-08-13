import React, { useEffect, useState, useCallback } from "react";
import { GoogleMap, MarkerF, useJsApiLoader, InfoWindowF } from "@react-google-maps/api";

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
  const [selected, setSelected] = useState(null);
  const { isLoaded } = useJsApiLoader({
    googleMapsApiKey: GOOGLE_MAPS_API_KEY,
    libraries: ["visualization"]
  });

  useEffect(() => {
    async function fetchAndGeocode() {
      setLoading(true);
      const resp = await fetch("/api/mapa-calor-problemas");
      const json = await resp.json();
      const pontosApi = json.pontos || [];
      const cache = JSON.parse(localStorage.getItem("geocode_cache") || "{}")
      const geocoded = [];
      for (const item of pontosApi) {
        // Montar endereço completo para geocodificação
        // Tenta usar: endereco, bairro, cidade, estado, Brasil
        let enderecoCompleto = "";
        if (item.endereco) enderecoCompleto += item.endereco + ", ";
        if (item.bairro) enderecoCompleto += item.bairro + ", ";
        if (item.cidade) enderecoCompleto += item.cidade + ", ";
        if (item.estado) enderecoCompleto += item.estado + ", ";
        enderecoCompleto += "Brasil";
        // Usar bairro como chave de cache, mas pode ser melhor usar o endereço completo
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

  if (!isLoaded) return <div>Carregando mapa...</div>;
  if (loading) return <div>Carregando dados do heatmap...</div>;

  // Cores por status
  const statusColor = {
    cancelada: "#e74c3c",
    perdida: "#f1c40f",
    concluida: "#2ecc71"
  };

  return (
    <GoogleMap
      mapContainerStyle={mapContainerStyle}
      center={defaultCenter}
      zoom={5}
    >
      {pontos.map((p, idx) => (
        <MarkerF
          key={idx}
          position={p.location}
          icon={{
            path: window.google.maps.SymbolPath.CIRCLE,
            scale: 10,
            fillColor: statusColor[p.status] || "#3498db",
            fillOpacity: 0.8,
            strokeWeight: 1,
            strokeColor: "#333"
          }}
          onClick={() => setSelected({ ...p, idx })}
        />
      ))}
      {selected && (
        <InfoWindowF
          position={selected.location}
          onCloseClick={() => setSelected(null)}
        >
          <div>
            <strong>Status:</strong> {selected.status}<br />
            {selected.motivo && <><strong>Motivo:</strong> {selected.motivo}<br /></>}
            <strong>Bairro:</strong> {selected.bairro}
          </div>
        </InfoWindowF>
      )}
    </GoogleMap>
  );
}
