import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { useToast } from "@/components/ui/use-toast";
import { Plus } from "lucide-react";
import LocationPicker from "./LocationPicker";

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:3001/api';

interface WellFormData {
  latitude: number;
  longitude: number;
  status: string;
  capacity: number;
  current_load: number;
  service_area: string;
}

interface ServiceAreaPoint {
  lat: number;
  lng: number;
}

interface WellManagementProps {
  token: string;
  onWellAdded: () => void;
}

const WellManagement = ({ token, onWellAdded }: WellManagementProps) => {
  const { toast } = useToast();
  const [isAdding, setIsAdding] = useState(false);
  const [serviceAreaPoints, setServiceAreaPoints] = useState<ServiceAreaPoint[]>([
    { lat: 0, lng: 0 },
    { lat: 0, lng: 0 },
    { lat: 0, lng: 0 }
  ]);
  const [formData, setFormData] = useState<WellFormData>({
    latitude: 0,
    longitude: 0,
    status: 'draft',
    capacity: 0,
    current_load: 0,
    service_area: ''
  });

  const updateServiceAreaPoint = (index: number, field: 'lat' | 'lng', value: number) => {
    const newPoints = [...serviceAreaPoints];
    newPoints[index] = { ...newPoints[index], [field]: value };
    setServiceAreaPoints(newPoints);

    // Convert points to PostGIS POLYGON format
    // Add the first point again to close the polygon
    const coordinates = [...newPoints, newPoints[0]]
      .map(point => `${point.lng} ${point.lat}`)
      .join(', ');
    const polygonString = `POLYGON((${coordinates}))`;
    setFormData({ ...formData, service_area: polygonString });
  };

  const addServiceAreaPoint = () => {
    setServiceAreaPoints([...serviceAreaPoints, { lat: 0, lng: 0 }]);
  };

  const removeServiceAreaPoint = (index: number) => {
    if (serviceAreaPoints.length > 3) {
      const newPoints = serviceAreaPoints.filter((_, i) => i !== index);
      setServiceAreaPoints(newPoints);
      
      // Update polygon string after removing point
      const coordinates = [...newPoints, newPoints[0]]
        .map(point => `${point.lng} ${point.lat}`)
        .join(', ');
      const polygonString = `POLYGON((${coordinates}))`;
      setFormData({ ...formData, service_area: polygonString });
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const response = await fetch(`${API_BASE_URL}/admin/wells`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData)
      });

      if (response.ok) {
        toast({
          title: "Success",
          description: "Well added successfully",
        });
        setIsAdding(false);
        setFormData({
          latitude: 0,
          longitude: 0,
          status: 'draft',
          capacity: 0,
          current_load: 0,
          service_area: ''
        });
        setServiceAreaPoints([
          { lat: 0, lng: 0 },
          { lat: 0, lng: 0 },
          { lat: 0, lng: 0 }
        ]);
        onWellAdded();
      } else {
        const error = await response.json();
        throw new Error(error.error || 'Failed to add well');
      }
    } catch (error) {
      toast({
        variant: "destructive",
        title: "Error",
        description: error instanceof Error ? error.message : 'Failed to add well',
      });
    }
  };

  if (!isAdding) {
    return (
      <Button onClick={() => setIsAdding(true)} className="mb-6">
        <Plus className="mr-2 h-4 w-4" />
        Add New Well
      </Button>
    );
  }

  return (
    <Card className="p-6 mb-6">
      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="space-y-2">
          <Label>Location</Label>
          <div className="space-y-2">
            <div className="grid grid-cols-2 gap-2">
              <div>
                <Label htmlFor="latitude" className="text-sm">Latitude</Label>
                <Input
                  id="latitude"
                  type="number"
                  step="any"
                  placeholder="30.2672"
                  value={formData.latitude || ''}
                  onChange={(e) => setFormData({ ...formData, latitude: parseFloat(e.target.value) })}
                  required
                />
              </div>
              <div>
                <Label htmlFor="longitude" className="text-sm">Longitude</Label>
                <Input
                  id="longitude"
                  type="number"
                  step="any"
                  placeholder="-97.7431"
                  value={formData.longitude || ''}
                  onChange={(e) => setFormData({ ...formData, longitude: parseFloat(e.target.value) })}
                  required
                />
              </div>
            </div>
            <LocationPicker 
              onLocationSelect={(lat, lng) => setFormData({ 
                ...formData, 
                latitude: lat, 
                longitude: lng
              })}
              initialLat={formData.latitude || undefined}
              initialLng={formData.longitude || undefined}
            />
          </div>
          <p className="text-sm text-muted-foreground mt-1">
            Enter coordinates or pick a location on the map.
          </p>
        </div>

        <div className="space-y-2">
          <Label>Service Area Coordinates</Label>
          <div className="space-y-4">
            {serviceAreaPoints.map((point, index) => (
              <div key={index} className="grid grid-cols-2 gap-2">
                <div>
                  <Label htmlFor={`point-${index}-lat`} className="text-sm">Point {index + 1} Latitude</Label>
                  <Input
                    id={`point-${index}-lat`}
                    type="number"
                    step="any"
                    value={point.lat || ''}
                    onChange={(e) => updateServiceAreaPoint(index, 'lat', parseFloat(e.target.value))}
                    required
                  />
                </div>
                <div className="flex gap-2">
                  <div className="flex-1">
                    <Label htmlFor={`point-${index}-lng`} className="text-sm">Point {index + 1} Longitude</Label>
                    <Input
                      id={`point-${index}-lng`}
                      type="number"
                      step="any"
                      value={point.lng || ''}
                      onChange={(e) => updateServiceAreaPoint(index, 'lng', parseFloat(e.target.value))}
                      required
                    />
                  </div>
                  {serviceAreaPoints.length > 3 && (
                    <Button
                      type="button"
                      variant="outline"
                      className="mt-6"
                      onClick={() => removeServiceAreaPoint(index)}
                    >
                      Remove
                    </Button>
                  )}
                </div>
              </div>
            ))}
            <Button
              type="button"
              variant="outline"
              onClick={addServiceAreaPoint}
            >
              Add Point
            </Button>
          </div>
          <p className="text-sm text-muted-foreground">
            Add at least 3 points to define the service area polygon. Points will be connected in order.
          </p>
        </div>

        <div className="space-y-2">
          <Label htmlFor="status">Status</Label>
          <Select
            value={formData.status}
            onValueChange={(value) => setFormData({ ...formData, status: value })}
          >
            <SelectTrigger>
              <SelectValue placeholder="Select status" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="draft">Draft</SelectItem>
              <SelectItem value="building">Building</SelectItem>
              <SelectItem value="completed">Completed</SelectItem>
              <SelectItem value="broken">Broken</SelectItem>
              <SelectItem value="under_maintenance">Under Maintenance</SelectItem>
            </SelectContent>
          </Select>
        </div>

        <div className="space-y-2">
          <Label htmlFor="capacity">Capacity</Label>
          <Input
            id="capacity"
            type="number"
            min="0"
            value={formData.capacity}
            onChange={(e) => setFormData({ ...formData, capacity: parseInt(e.target.value) })}
            required
          />
        </div>

        <div className="space-y-2">
          <Label htmlFor="current_load">Current Load</Label>
          <Input
            id="current_load"
            type="number"
            min="0"
            value={formData.current_load}
            onChange={(e) => setFormData({ ...formData, current_load: parseInt(e.target.value) })}
            required
          />
        </div>

        <div className="flex gap-2">
          <Button type="submit">Add Well</Button>
          <Button type="button" variant="outline" onClick={() => setIsAdding(false)}>
            Cancel
          </Button>
        </div>
      </form>
    </Card>
  );
};

export default WellManagement;