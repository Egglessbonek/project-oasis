import { useEffect, useState } from "react";
import { Card } from "@/components/ui/card";
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";
import { Label } from "@/components/ui/label";
import LoadingSpinner from "@/components/LoadingSpinner";

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:3001/api';

interface Well {
  id: string;
  location: string;
  status: string;
  capacity: number;
  current_load: number;
}

interface WellSelectorProps {
  onWellSelect: (wellId: string) => void;
  initialWellId?: string;
}

const WellSelector = ({ onWellSelect, initialWellId }: WellSelectorProps) => {
  const [wells, setWells] = useState<Well[]>([]);
  const [selectedWell, setSelectedWell] = useState<string>(initialWellId || '');
  const [error, setError] = useState<string>('');
  const [loading, setLoading] = useState(true);

  // Fetch wells only once when component mounts
  useEffect(() => {
    const fetchWells = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/admin/wells/available`);
        if (response.ok) {
          const data = await response.json();
          setWells(data);
        } else {
          throw new Error('Failed to fetch wells');
        }
      } catch (error) {
        setError('Failed to load available wells');
      } finally {
        setLoading(false);
      }
    };

    fetchWells();
  }, []); // Empty dependency array - only run once

  // Handle initialWellId changes separately
  useEffect(() => {
    if (initialWellId && wells.some(well => well.id === initialWellId) && selectedWell !== initialWellId) {
      setSelectedWell(initialWellId);
    }
  }, [initialWellId, wells]);

  const handleWellSelect = (wellId: string) => {
    setSelectedWell(wellId);
    onWellSelect(wellId);
  };

  const content = () => {
    if (error) {
      return (
        <div className="text-center text-destructive">
          {error}
        </div>
      );
    }

    if (wells.length === 0 && !error) {
      return (
        <p className="text-center text-muted-foreground">
          No wells available for reporting
        </p>
      );
    }

    return (
      <RadioGroup value={selectedWell} onValueChange={handleWellSelect}>
        <div className="space-y-4">
          {wells.map((well) => (
            <div key={well.id} className="flex items-start space-x-3">
              <RadioGroupItem value={well.id} id={well.id} />
              <Label htmlFor={well.id} className="font-normal cursor-pointer">
                <div>
                  <div className="font-medium">Well {well.id}</div>
                  <div className="text-sm text-muted-foreground">
                    Location: {well.location}
                  </div>
                  <div className="text-sm text-muted-foreground">
                    Capacity: {well.capacity} | Current Load: {well.current_load}
                  </div>
                </div>
              </Label>
            </div>
          ))}
        </div>
      </RadioGroup>
    );
  };

  return (
    <Card className="p-6">
      <h3 className="text-lg font-semibold mb-4">Select a Well</h3>
      {loading ? (
        <LoadingSpinner size="sm" />
      ) : (
        content()
      )}
    </Card>
  );
};

export default WellSelector;