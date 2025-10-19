import { useEffect, useRef } from 'react';
import L, { Map as LeafletMap } from 'leaflet';
import 'leaflet/dist/leaflet.css';
import { useNavigate } from 'react-router-dom';
import wellMarkerIcon from '@/assets/well-marker.png';

interface Well {
  id: string;
  name: string;
  position: [number, number];
  status: string;
  polygon?: [number, number][];
  serviceArea?: {
    radius: number; // in meters
    color: string;
    opacity: number;
  };
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

    // Helper function to get status color
    const getStatusColor = (status: string) => {
      switch (status) {
        case 'operational':
          return '#10b981'; // green
        case 'needs-repair':
        case 'needs_repair':
          return '#ef4444'; // red
        case 'maintenance':
          return '#f59e0b'; // yellow
        case 'broken':
          return '#dc2626'; // dark red
        default:
          return '#6b7280'; // gray
      }
    };

    // Markers and service areas
    wells.forEach((well) => {
      const marker = L.marker(well.position, { icon: customIcon }).addTo(map);
      const popupHtml = `
        <div class="text-center p-2">
          <h3 class="font-semibold text-base mb-1">${well.name}</h3>
          <p class="text-sm text-muted-foreground capitalize mb-2">Status: ${well.status.replace('-', ' ')}</p>
          ${well.serviceArea ? `<p class="text-xs text-gray-500 mb-2">Service Radius: ${well.serviceArea.radius}m</p>` : ''}
          ${well.polygon ? `<p class="text-xs text-gray-500 mb-2">Service Area: Polygon (${well.polygon.length} points)</p>` : ''}
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

      // Add polygon service area if defined
      if (well.polygon && well.polygon.length >= 3) {
        const polygon = L.polygon(well.polygon, {
          color: getStatusColor(well.status),
          fillColor: getStatusColor(well.status),
          fillOpacity: 0.2,
          weight: 2,
        }).addTo(map);
        
        // Add service area info to popup
        polygon.bindPopup(`
          <div class="text-center p-2">
            <h4 class="font-semibold text-sm mb-1">Service Area</h4>
            <p class="text-xs text-gray-600">${well.name}</p>
            <p class="text-xs text-gray-500">Polygon (${well.polygon.length} points)</p>
          </div>
        `);
      }
      // Add circular service area if defined (legacy support)
      else if (well.serviceArea) {
        const circle = L.circle(well.position, {
          radius: well.serviceArea.radius,
          color: well.serviceArea.color,
          fillColor: well.serviceArea.color,
          fillOpacity: well.serviceArea.opacity,
          weight: 2,
        }).addTo(map);
        
        // Add service area info to popup
        circle.bindPopup(`
          <div class="text-center p-2">
            <h4 class="font-semibold text-sm mb-1">Service Area</h4>
            <p class="text-xs text-gray-600">${well.name}</p>
            <p class="text-xs text-gray-500">Radius: ${well.serviceArea.radius}m</p>
          </div>
        `);
      }
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
