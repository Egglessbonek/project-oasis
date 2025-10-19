import { useEffect, useRef } from 'react';
import L, { Map as LeafletMap } from 'leaflet';
import 'leaflet/dist/leaflet.css';
import { useNavigate } from 'react-router-dom';
import wellIcon from '@/assets/well-icon.svg';

interface Well {
  id: string;
  name: string;
  position: [number, number];
  status: string;
  status_color?: string;
  capacity: number;
  current_load: number;
  usage_percentage: number;
  serviceArea?: {
    radius: number; // in meters
    color: string;
    opacity: number;
  } | string; // Can be PostGIS POLYGON string
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

    // Function to create custom icon with dynamic color
    const createWellIcon = (well: Well) => {
      // Create a colored version of the SVG
      const color = well.status_color || (well.status === 'operational' ? '#10B981' : '#EF4444');
      const svg = `<?xml version="1.0" encoding="UTF-8"?>
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <circle cx="12" cy="12" r="10" fill="white" stroke="${color}" stroke-width="2"/>
          <path d="M12 6C12 6 8 11 8 13C8 15.2091 9.79086 17 12 17C14.2091 17 16 15.2091 16 13C16 11 12 6 12 6Z" 
                fill="#0EA5E9" stroke="none"/>
          <path d="M7 10C7 10 9 11 12 11C15 11 17 10 17 10" 
                stroke="${color}" stroke-width="1.5" stroke-linecap="round"/>
        </svg>`;

      // Convert SVG to data URL
      const svgBase64 = btoa(svg);
      const dataUrl = `data:image/svg+xml;base64,${svgBase64}`;

      return L.icon({
        iconUrl: dataUrl,
        iconSize: [40, 40],
        iconAnchor: [20, 20],
        popupAnchor: [0, -20],
      });
    };

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

    // Markers and service areas
    wells.forEach((well) => {
      const marker = L.marker(well.position, { icon: createWellIcon(well) }).addTo(map);
      const popupHtml = `
        <div class="text-center p-2">
          <h3 class="font-semibold text-base mb-1">${well.name}</h3>
          <p class="text-sm text-muted-foreground capitalize mb-2">Status: ${well.status.replace('-', ' ')}</p>
          <p class="text-sm text-muted-foreground mb-2">
            Usage: ${well.current_load}/${well.capacity} (${well.usage_percentage}%)
          </p>
          <div class="flex flex-col gap-2">
            <button id="attendance-${well.id}" class="px-3 py-1 border rounded text-sm bg-primary text-primary-foreground">Submit Attendance</button>
            <button id="report-${well.id}" class="px-3 py-1 border rounded text-sm">Report Issue</button>
          </div>
        </div>
      `;
      marker.bindPopup(popupHtml);
      marker.on('popupopen', () => {
        // Report button
        const reportBtn = document.getElementById(`report-${well.id}`);
        if (reportBtn) {
          reportBtn.addEventListener('click', () => navigate(`/report?wellId=${well.id}`), { once: true });
        }
        
        // Attendance button
        const attendanceBtn = document.getElementById(`attendance-${well.id}`);
        if (attendanceBtn) {
          attendanceBtn.addEventListener('click', () => navigate(`/attendance?wellId=${well.id}`), { once: true });
        }
      });

      // Add service area if defined
      if (well.serviceArea) {
        let serviceAreaLayer;
        
        if (typeof well.serviceArea === 'string') {
          // Parse PostGIS POLYGON string
          const coordsMatch = well.serviceArea.match(/\(\((.*?)\)\)/);
          if (coordsMatch) {
            const coords = coordsMatch[1].split(',').map(pair => {
              const [lng, lat] = pair.trim().split(' ').map(Number);
              return [lat, lng];
            });
            serviceAreaLayer = L.polygon(coords, {
              color: well.status_color || '#10B981',
              fillOpacity: 0.2,
              weight: 2,
            }).addTo(map);
          }
        } else {
          // Use circle for legacy service areas
          serviceAreaLayer = L.circle(well.position, {
            radius: well.serviceArea.radius,
            color: well.serviceArea.color,
            fillColor: well.serviceArea.color,
            fillOpacity: well.serviceArea.opacity,
            weight: 2,
          }).addTo(map);
        
        }
        
        // Add service area info to popup
        if (serviceAreaLayer) {
          serviceAreaLayer.bindPopup(`
            <div class="text-center p-2">
              <h4 class="font-semibold text-sm mb-1">Service Area</h4>
              <p class="text-xs text-gray-600">${well.name}</p>
              ${typeof well.serviceArea === 'string' ? 
                `<p class="text-xs text-gray-500">Custom Service Area</p>` :
                `<p class="text-xs text-gray-500">Radius: ${well.serviceArea.radius}m</p>`
              }
            </div>
          `);
        }
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
