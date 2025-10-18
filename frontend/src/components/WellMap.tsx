import { useEffect } from 'react';
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import { Button } from "@/components/ui/button";
import { Link } from "react-router-dom";
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';

// Fix for default marker icons in React Leaflet
const icon = L.icon({
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon.png',
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon-2x.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png',
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41]
});

interface Well {
  id: number;
  name: string;
  position: [number, number];
  status: string;
  serviceArea?: {
    radius: number; // in meters
    color: string;
    opacity: number;
  };
}

interface WellMapProps {
  wells: Well[];
}

const WellMap = ({ wells }: WellMapProps) => {
  useEffect(() => {
    // Ensure Leaflet is properly initialized
    delete (L.Icon.Default.prototype as any)._getIconUrl;
  }, []);

  return (
    <MapContainer
      center={[37.7749, -122.4194]}
      zoom={13}
      scrollWheelZoom={true}
      style={{ height: '100%', width: '100%' }}
    >
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />
      {wells.map((well) => (
        <Marker key={well.id} position={well.position} icon={icon}>
          <Popup>
            <div className="text-center p-2">
              <h3 className="font-semibold text-base mb-1">{well.name}</h3>
              <p className="text-sm text-muted-foreground capitalize mb-2">
                Status: {well.status.replace('-', ' ')}
              </p>
              <Button asChild size="sm" variant="outline">
                <Link to="/report">Report Issue</Link>
              </Button>
            </div>
          </Popup>
        </Marker>
      ))}
    </MapContainer>
  );
};

export default WellMap;
