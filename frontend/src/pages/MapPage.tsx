import { useEffect, useState } from "react";
import { Button } from "@/components/ui/button";
import { Link } from "react-router-dom";
import { ArrowLeft, Eye, EyeOff } from "lucide-react";
import LeafletBasicMap from "@/components/LeafletBasicMap";
import { createServiceArea } from "@/lib/utils";
import 'leaflet/dist/leaflet.css';

const MapPage = () => {
  const [showServiceAreas, setShowServiceAreas] = useState(true);
  
  // UT Austin campus well locations with service areas
  const wells = [
    { 
      id: 1, 
      name: "Main Building Well", 
      position: [30.2862, -97.7394] as [number, number], 
      status: "operational",
      serviceArea: createServiceArea(500, "operational")
    },
    { 
      id: 2, 
      name: "Engineering Quad Well", 
      position: [30.2882, -97.7359] as [number, number], 
      status: "needs-repair",
      serviceArea: createServiceArea(300, "needs-repair")
    },
    { 
      id: 3, 
      name: "West Campus Well", 
      position: [30.2833, -97.7422] as [number, number], 
      status: "operational",
      serviceArea: createServiceArea(400, "operational")
    },
  ];

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
        <div className="mb-6 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Button asChild variant="outline" size="icon">
              <Link to="/">
                <ArrowLeft className="h-4 w-4" />
              </Link>
            </Button>
            <h1 className="text-3xl font-bold text-foreground">Water Wells Map</h1>
          </div>
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
          <LeafletBasicMap wells={wellsToDisplay} />
        </div>
      </div>
    </div>
  );
};

export default MapPage;
