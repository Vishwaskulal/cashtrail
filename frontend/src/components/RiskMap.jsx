import React, { useEffect } from 'react';
import { MapContainer, TileLayer, CircleMarker, Popup, useMap } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';

// Fix for default Leaflet icon paths in React if needed
import L from 'leaflet';

const getRiskColor = (level) => {
  switch (level) {
    case 'LOW':
      return '#3b82f6'; // Blue
    case 'MEDIUM':
      return '#f59e0b'; // Amber
    case 'HIGH':
      return '#ef4444'; // Red
    case 'CRITICAL':
      return '#7f1d1d'; // Dark Red
    default:
      return '#6b7280'; // Gray
  }
};

const MapBoundsUpdater = ({ locations }) => {
  const map = useMap();
  useEffect(() => {
    if (locations && locations.length > 0) {
      const bounds = L.latLngBounds(locations.map(loc => [loc.latitude, loc.longitude]));
      map.fitBounds(bounds, { padding: [50, 50] });
    }
  }, [locations, map]);
  return null;
};

const RiskMap = ({ locations, modelVersion }) => {
  if (!locations || locations.length === 0) {
    return (
      <div className="w-full h-96 flex items-center justify-center bg-gray-100 rounded-lg border border-gray-300">
        <p className="text-gray-500">No potential withdrawal-risk locations available.</p>
      </div>
    );
  }

  // Calculate center safely
  const defaultCenter = [
    locations[0].latitude || 20.5937,
    locations[0].longitude || 78.9629
  ];

  return (
    <div className="w-full h-[500px] rounded-lg overflow-hidden border border-gray-200 shadow-sm relative z-0">
      <MapContainer 
        center={defaultCenter} 
        zoom={12} 
        scrollWheelZoom={true} 
        style={{ height: '100%', width: '100%' }}
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        
        <MapBoundsUpdater locations={locations} />

        {locations.map((loc) => (
          <CircleMarker
            key={loc.location_id}
            center={[loc.latitude, loc.longitude]}
            radius={loc.risk_level === 'CRITICAL' ? 14 : loc.risk_level === 'HIGH' ? 12 : 10}
            pathOptions={{
              color: getRiskColor(loc.risk_level),
              fillColor: getRiskColor(loc.risk_level),
              fillOpacity: 0.6,
              weight: 2
            }}
          >
            <Popup>
              <div className="p-1">
                <h3 className="font-bold text-gray-800 mb-1">Potential Withdrawal-Risk Location</h3>
                <div className="text-sm space-y-1 mb-2">
                  <p><strong>Name:</strong> {loc.location_name}</p>
                  <p><strong>City:</strong> {loc.city}</p>
                  <p><strong>District:</strong> {loc.district}</p>
                  <p><strong>State:</strong> {loc.state}</p>
                </div>
                <div className="bg-gray-50 p-2 rounded text-sm mb-2">
                  <p><strong>Risk Score:</strong> {loc.risk_score ? loc.risk_score.toFixed(4) : 'N/A'}</p>
                  <p><strong>Confidence:</strong> {loc.confidence_score ? loc.confidence_score.toFixed(4) : 'N/A'}</p>
                  <p><strong>Risk Level:</strong> <span style={{ color: getRiskColor(loc.risk_level), fontWeight: 'bold' }}>{loc.risk_level}</span></p>
                </div>
                {modelVersion && <p className="text-xs text-gray-500 mt-1">Model Version: {modelVersion}</p>}
                <p className="text-[10px] text-gray-400 mt-2 italic leading-tight border-t pt-1">
                  Model-generated potential risk location. Not a guaranteed withdrawal location.
                </p>
              </div>
            </Popup>
          </CircleMarker>
        ))}
      </MapContainer>
    </div>
  );
};

export default RiskMap;
