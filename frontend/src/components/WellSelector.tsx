import { useEffect, useState } from "react";
import { Card } from "@/components/ui/card";
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";
import { Label } from "@/components/ui/label";

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
}

const WellSelector = ({ onWellSelect }: WellSelectorProps) => {
  const [wells, setWells] = useState<Well[]>([]);
  const [selectedWell, setSelectedWell] = useState<string>('');
  const [error, setError] = useState<string>('');

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
      }
    };

    fetchWells();
  }, []);

  const handleWellSelect = (wellId: string) => {
    setSelectedWell(wellId);
    onWellSelect(wellId);
  };

  if (error) {
    return (
      <Card className="p-4 text-center text-destructive">
        {error}
      </Card>
    );
  }

  return (
    <Card className="p-6">
      <h3 className="text-lg font-semibold mb-4">Select a Well</h3>
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
      {wells.length === 0 && !error && (
        <p className="text-center text-muted-foreground mt-4">
          No wells available for reporting
        </p>
      )}
    </Card>
  );
};

export default WellSelector;
