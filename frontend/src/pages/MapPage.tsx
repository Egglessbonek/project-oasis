import { useEffect, useState } from "react";
import { Button } from "@/components/ui/button";
import { Link } from "react-router-dom";
import { ArrowLeft, Eye, EyeOff, Upload } from "lucide-react";
import LeafletBasicMap from "@/components/LeafletBasicMap";
import LoadingSpinner from "@/components/LoadingSpinner";
import { createServiceArea } from "@/lib/utils";
import 'leaflet/dist/leaflet.css';

interface WellData {
  id: string;
  name: string;
  position: [number, number];
  status: string;
  status_color?: string;
  capacity: number;
  current_load: number;
  usage_percentage: number;
  serviceArea?: {
    radius: number;
    color: string;
    opacity: number;
  } | string;
  service_area_coords?: [number, number][];
  polygon?: [number, number][];
}

const MapPage = () => {
  const [showServiceAreas, setShowServiceAreas] = useState(true);
  const [wells, setWells] = useState<WellData[]>([]);
  const [areaBoundaries, setAreaBoundaries] = useState<any[]>([]);
  const [jsonData, setJsonData] = useState<string>("");
  
  const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:3001/api';
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchWells = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/wells/map`);
        if (!response.ok) {
          throw new Error('Failed to fetch wells');
        }
        const data = await response.json();

        console.log(data);
        
        // Handle new response structure with wells and area_boundaries
        const wellsData = data.wells || data; // Support both old and new format
        const areaBoundaries = data.area_boundaries || [];
        
        // Transform wells data for map display
        const transformedWells = wellsData.map((well: any) => ({
          id: well.id,
          name: `Well ${well.id}`,
          position: [well.latitude, well.longitude] as [number, number],
          status: well.status === 'completed' ? 'operational' : 'needs-repair',
          status_color: well.status_color || (well.status === 'completed' ? '#10B981' : '#EF4444'),
          capacity: well.capacity || 0,
          current_load: well.current_load || 0,
          usage_percentage: well.usage_percentage || 0,
          // Backend returns ST_AsText(w.service_area) as service_area_text
          serviceArea: well.service_area_text || well.service_area || createServiceArea(300, well.status === 'completed' ? 'operational' : 'needs-repair'),
          service_area_coords: well.service_area_coords || []
        }));

        setWells(transformedWells);
        setAreaBoundaries(areaBoundaries);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load wells');
      } finally {
        setLoading(false);
      }
    };

    fetchWells();
  }, []);


  // Parse JSON data and convert to well format
  const parseJsonData = (jsonString: string) => {
    try {
      const data = JSON.parse(jsonString);
      const parsedWells: WellData[] = [];
      
      Object.entries(data).forEach(([id, coordinates]) => {
        if (Array.isArray(coordinates) && coordinates.length > 0) {
          // Calculate center point from polygon coordinates
          const centerLat = coordinates.reduce((sum, coord) => sum + coord[0], 0) / coordinates.length;
          const centerLng = coordinates.reduce((sum, coord) => sum + coord[1], 0) / coordinates.length;
          
          parsedWells.push({
            id,
            name: `Well ${id}`,
            position: [centerLat, centerLng],
            status: "operational", // Default status
            status_color: "#10B981",
            capacity: 0,
            current_load: 0,
            usage_percentage: 0,
            serviceArea: createServiceArea(300, "operational"),
            polygon: coordinates as [number, number][]
          });
        }
      });
      
      setWells(parsedWells);
    } catch (error) {
      console.error("Error parsing JSON data:", error);
      alert("Invalid JSON format. Please check your data.");
    }
  };

  // Filter wells based on service area visibility
  const wellsToDisplay = showServiceAreas 
    ? wells 
    : wells.map(well => ({ ...well, polygon: undefined }));

  useEffect(() => {
    document.title = "Water Wells Map | Water Well Management";
    const metaDescName = 'description';
    let metaDesc = document.querySelector(`meta[name="${metaDescName}"]`) as HTMLMetaElement | null;
    if (!metaDesc) {
      metaDesc = document.createElement('meta');
      metaDesc.name = metaDescName;
      document.head.appendChild(metaDesc);
    }
    metaDesc.content = 'Interactive Leaflet map of water wells for issue reporting and tracking.';

    let canonical = document.querySelector('link[rel="canonical"]') as HTMLLinkElement | null;
    if (!canonical) {
      canonical = document.createElement('link');
      canonical.rel = 'canonical';
      document.head.appendChild(canonical);
    }
    const url = `${window.location.origin}/map`;
    canonical.href = url;
  }, []);

  return (
    <div className="min-h-screen bg-background">
      <div className="container mx-auto px-4 py-8">
        <div className="mb-6 flex items-center justify-end">
          <Button
            variant="outline"
            onClick={() => setShowServiceAreas(!showServiceAreas)}
            className="flex items-center gap-2"
          >
            {showServiceAreas ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
            {showServiceAreas ? "Hide Service Areas" : "Show Service Areas"}
          </Button>
        </div>

        <div className="rounded-lg overflow-hidden border border-border shadow-lg" style={{ height: '600px' }}>
          {loading ? (
            <LoadingSpinner />
          ) : error ? (
            <div className="flex min-h-[200px] flex-col items-center justify-center gap-4 p-4 text-center">
              <p className="text-destructive">{error}</p>
              <Button variant="outline" onClick={() => window.location.reload()}>
                Try Again
              </Button>
            </div>
          ) : (
            <LeafletBasicMap wells={wellsToDisplay} />
          )}
        </div>
      </div>
    </div>
  );
};

export default MapPage;
