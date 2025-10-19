import { useEffect, useState } from "react";
import { Button } from "@/components/ui/button";
import { Link } from "react-router-dom";
import { ArrowLeft, Eye, EyeOff, Upload } from "lucide-react";
import LeafletBasicMap from "@/components/LeafletBasicMap";
import { createServiceArea } from "@/lib/utils";
import 'leaflet/dist/leaflet.css';

interface WellData {
  id: string;
  name: string;
  position: [number, number];
  status: string;
  polygon?: [number, number][];
}

const MapPage = () => {
  const [showServiceAreas, setShowServiceAreas] = useState(true);
  const [wells, setWells] = useState<WellData[]>([]);
  const [jsonData, setJsonData] = useState<string>("");
  
  // Default UT Austin campus well locations with service areas
  const defaultWells: WellData[] = [
    { 
      id: "1", 
      name: "Main Building Well", 
      position: [30.2862, -97.7394], 
      status: "operational",
      polygon: [
        [30.2862, -97.7394],
        [30.2865, -97.7391],
        [30.2865, -97.7387],
        [30.2862, -97.7384],
        [30.2859, -97.7387],
        [30.2859, -97.7391],
        [30.2862, -97.7394]
      ]
    },
    { 
      id: "2", 
      name: "Engineering Quad Well", 
      position: [30.2882, -97.7359], 
      status: "needs-repair",
      polygon: [
        [30.2882, -97.7359],
        [30.2885, -97.7356],
        [30.2885, -97.7352],
        [30.2882, -97.7349],
        [30.2859, -97.7352],
        [30.2859, -97.7356],
        [30.2882, -97.7359]
      ]
    },
    { 
      id: "3", 
      name: "West Campus Well", 
      position: [30.2833, -97.7422], 
      status: "operational",
      polygon: [
        [30.2833, -97.7422],
        [30.2836, -97.7419],
        [30.2836, -97.7415],
        [30.2833, -97.7412],
        [30.2830, -97.7415],
        [30.2830, -97.7419],
        [30.2833, -97.7422]
      ]
    },
  ];

  // Initialize with default wells
  useEffect(() => {
    setWells(defaultWells);
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
        <div className="mb-6 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Button asChild variant="outline" size="icon">
              <Link to="/">
                <ArrowLeft className="h-4 w-4" />
              </Link>
            </Button>
            <h1 className="text-3xl font-bold text-foreground">Water Wells Map</h1>
          </div>
          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              onClick={() => setShowServiceAreas(!showServiceAreas)}
              className="flex items-center gap-2"
            >
              {showServiceAreas ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
              {showServiceAreas ? "Hide Service Areas" : "Show Service Areas"}
            </Button>
          </div>
        </div>

        {/* JSON Data Input Section */}
        <div className="mb-6 p-4 border border-border rounded-lg bg-card">
          <h3 className="text-lg font-semibold mb-3">Load Well Data from JSON</h3>
          <div className="space-y-3">
            <textarea
              value={jsonData}
              onChange={(e) => setJsonData(e.target.value)}
              placeholder='Paste your JSON data here, e.g.: {"id1": [[30.2862, -97.7394], [30.2865, -97.7391], ...], "id2": [...]}'
              className="w-full h-32 p-3 border border-border rounded-md font-mono text-sm"
            />
            <div className="flex gap-2">
              <Button
                onClick={() => parseJsonData(jsonData)}
                disabled={!jsonData.trim()}
                className="flex items-center gap-2"
              >
                <Upload className="h-4 w-4" />
                Load Wells from JSON
              </Button>
              <Button
                variant="outline"
                onClick={() => {
                  const sampleData = {
                    "well-1": [
                      [30.2862, -97.7394],
                      [30.2865, -97.7391],
                      [30.2865, -97.7387],
                      [30.2862, -97.7384],
                      [30.2859, -97.7387],
                      [30.2859, -97.7391],
                      [30.2862, -97.7394]
                    ],
                    "well-2": [
                      [30.2882, -97.7359],
                      [30.2885, -97.7356],
                      [30.2885, -97.7352],
                      [30.2882, -97.7349],
                      [30.2859, -97.7352],
                      [30.2859, -97.7356],
                      [30.2882, -97.7359]
                    ],
                    "well-3": [
                      [30.2833, -97.7422],
                      [30.2836, -97.7419],
                      [30.2836, -97.7415],
                      [30.2833, -97.7412],
                      [30.2830, -97.7415],
                      [30.2830, -97.7419],
                      [30.2833, -97.7422]
                    ]
                  };
                  setJsonData(JSON.stringify(sampleData, null, 2));
                }}
              >
                Load Sample Data
              </Button>
              <Button
                variant="outline"
                onClick={() => {
                  setJsonData("");
                  setWells(defaultWells);
                }}
              >
                Reset to Default Wells
              </Button>
            </div>
            <p className="text-sm text-muted-foreground">
              Expected format: <code>{`{"id": [[lat, lng], [lat, lng], ...], "id2": [...]}`}</code>
            </p>
          </div>
        </div>

        <div className="rounded-lg overflow-hidden border border-border shadow-lg" style={{ height: '600px' }}>
          <LeafletBasicMap wells={wellsToDisplay} />
        </div>
      </div>
    </div>
  );
};

export default MapPage;
