import { useEffect, useRef } from 'react';
import L, { Map as LeafletMap } from 'leaflet';
import 'leaflet/dist/leaflet.css';
import { useNavigate } from 'react-router-dom';
import wellMarkerIcon from '@/assets/well-marker.png';

interface Well {
  id: number;
  name: string;
  position: [number, number];
  status: string;
}

interface LeafletBasicMapProps {
  wells: Well[];
  center?: [number, number];
  zoom?: number;
}

const LeafletBasicMap = ({ wells, center = [30.2849, -97.7341], zoom = 15 }: LeafletBasicMapProps) => {
  const mapRef = useRef<HTMLDivElement | null>(null);
  const mapInstance = useRef<LeafletMap | null>(null);
  const navigate = useNavigate();

  useEffect(() => {
    if (!mapRef.current) return;

    // Custom icon for well markers
    const customIcon = L.icon({
      iconUrl: wellMarkerIcon,
      iconSize: [32, 32],
      iconAnchor: [16, 16],
      popupAnchor: [0, -16],
    });

    // Initialize map
    const map = L.map(mapRef.current, {
      center,
      zoom,
      zoomControl: true,
      scrollWheelZoom: true,
    });
    mapInstance.current = map;

    // Tile layer
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
    }).addTo(map);

    // Markers
    wells.forEach((well) => {
      const marker = L.marker(well.position, { icon: customIcon }).addTo(map);
      const popupHtml = `
        <div class="text-center p-2">
          <h3 class="font-semibold text-base mb-1">${well.name}</h3>
          <p class="text-sm text-muted-foreground capitalize mb-2">Status: ${well.status.replace('-', ' ')}</p>
          <button id="report-${well.id}" class="px-3 py-1 border rounded text-sm">Report Issue</button>
        </div>
      `;
      marker.bindPopup(popupHtml);
      marker.on('popupopen', () => {
        const btn = document.getElementById(`report-${well.id}`);
        if (btn) {
          btn.addEventListener('click', () => navigate('/report'), { once: true });
        }
      });
    });

    // Cleanup
    return () => {
      map.remove();
      mapInstance.current = null;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [JSON.stringify(wells), center[0], center[1], zoom]);

  return (
    <div className="w-full h-full">
      <div ref={mapRef} className="w-full h-full rounded-lg" />
    </div>
  );
};

export default LeafletBasicMap;
