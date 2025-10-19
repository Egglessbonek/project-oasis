import { useEffect, useState } from "react";
import { Button } from "@/components/ui/button";
import { Link } from "react-router-dom";
import { ArrowLeft, Eye, EyeOff } from "lucide-react";
import LeafletBasicMap from "@/components/LeafletBasicMap";
import LoadingSpinner from "@/components/LoadingSpinner";
import { createServiceArea } from "@/lib/utils";
import 'leaflet/dist/leaflet.css';

const MapPage = () => {
  const [showServiceAreas, setShowServiceAreas] = useState(true);
  
  const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:3001/api';
  const [wells, setWells] = useState<any[]>([]);
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
        
        // Transform data for map display
        const transformedWells = data.map((well: any) => ({
          id: well.id,
          name: `Well ${well.id}`,
          position: [well.latitude, well.longitude] as [number, number],
          status: well.status === 'completed' ? 'operational' : 'needs-repair',
          serviceArea: well.service_area ? well.service_area : createServiceArea(300, well.status === 'completed' ? 'operational' : 'needs-repair'),
          capacity: well.capacity,
          current_load: well.current_load,
          usage_percentage: well.usage_percentage,
          status_color: well.status_color
        }));

        setWells(transformedWells);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load wells');
      } finally {
        setLoading(false);
      }
    };

    fetchWells();
  }, []);

  // Filter wells based on service area visibility
  const wellsToDisplay = showServiceAreas 
    ? wells 
    : wells.map(well => ({ ...well, serviceArea: undefined }));

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
