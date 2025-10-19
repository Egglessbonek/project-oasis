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
  service_area_coords?: [number, number][];
}

interface AreaBoundary {
  id: string;
  name: string;
  boundary_coords: [number, number][];
}

interface LeafletBasicMapProps {
  wells: Well[];
  areaBoundaries?: AreaBoundary[];
  center?: [number, number];
  zoom?: number;
}

const LeafletBasicMap = ({ wells, areaBoundaries = [], center = [30.2672, -97.7431], zoom = 13 }: LeafletBasicMapProps) => {
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
    const markers: L.Marker[] = [];
    wells.forEach((well) => {
      const marker = L.marker(well.position, { icon: createWellIcon(well) }).addTo(map);
      markers.push(marker);
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
      if (well.serviceArea || well.service_area_coords) {
        let serviceAreaLayer;
        
        // Use service area coordinates if available
        if (well.service_area_coords && well.service_area_coords.length > 0) {
          try {
            serviceAreaLayer = L.polygon(well.service_area_coords, {
              color: well.status_color || '#10B981',
              fillColor: well.status_color || '#10B981',
              fillOpacity: 0.2,
              weight: 2,
            }).addTo(map);
          } catch (error) {
            console.error(`Error rendering service area for well ${well.id}:`, error);
          }
        } else if (typeof well.serviceArea === 'string') {
          // Parse PostGIS POLYGON string
          const coordsMatch = well.serviceArea.match(/\(\((.*?)\)\)/);
          if (coordsMatch) {
            const coords: [number, number][] = coordsMatch[1].split(',').map(pair => {
              const [lng, lat] = pair.trim().split(' ').map(Number);
              return [lat, lng] as [number, number];
            });
            serviceAreaLayer = L.polygon(coords, {
              color: well.status_color || '#10B981',
              fillColor: well.status_color || '#10B981',
              fillOpacity: 0.2,
              weight: 2,
            }).addTo(map);
          }
        } else if (well.serviceArea && typeof well.serviceArea === 'object') {
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

    // Add area boundaries with shading
    areaBoundaries.forEach((area) => {
      if (area.boundary_coords && area.boundary_coords.length > 0) {
        const areaPolygon = L.polygon(area.boundary_coords, {
          color: '#1E40AF',
          weight: 3,
          opacity: 0.9,
          fillColor: '#3B82F6',
          fillOpacity: 0.3,  // Increased opacity for better shading
          fillRule: 'evenodd'
        }).addTo(map);
        
        // Add popup for area boundary
        areaPolygon.bindPopup(`
          <div class="text-center p-2">
            <h4 class="font-semibold text-sm mb-1">Administrative Area</h4>
            <p class="text-xs text-gray-600">${area.name}</p>
            <p class="text-xs text-gray-500">Area ID: ${area.id}</p>
          </div>
        `);
      }
    });

    // Fit map bounds to show all wells and service areas
    const allLayers: any[] = [...markers];
    
    // Add service area layers to bounds calculation
    wells.forEach((well) => {
      if (well.service_area_coords && well.service_area_coords.length > 0) {
        try {
          const serviceAreaLayer = L.polygon(well.service_area_coords);
          allLayers.push(serviceAreaLayer);
        } catch (error) {
          console.error(`Error creating service area layer for bounds:`, error);
        }
      }
    });
    
    // Add area boundary layers to bounds calculation
    areaBoundaries.forEach((area) => {
      if (area.boundary_coords && area.boundary_coords.length > 0) {
        try {
          const areaLayer = L.polygon(area.boundary_coords);
          allLayers.push(areaLayer);
        } catch (error) {
          console.error(`Error creating area boundary layer for bounds:`, error);
        }
      }
    });
    
    if (allLayers.length > 0) {
      const group = L.featureGroup(allLayers);
      map.fitBounds(group.getBounds().pad(0.1));
    } else {
      // If no layers, ensure we're showing the default center (Austin)
      map.setView(center, zoom);
    }

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
