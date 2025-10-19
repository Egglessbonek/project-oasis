import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { useToast } from "@/components/ui/use-toast";
import { ArrowLeft } from "lucide-react";
import { Link, useNavigate } from "react-router-dom";
import WellSelector from "@/components/WellSelector";

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:3001/api';

const SubmitAttendance = () => {
  const { toast } = useToast();
  const navigate = useNavigate();
  const [selectedWellId, setSelectedWellId] = useState("");
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!selectedWellId) {
      toast({
        title: "Missing Information",
        description: "Please select a well.",
        variant: "destructive",
      });
      return;
    }

    setSubmitting(true);
    try {
      const response = await fetch(`${API_BASE_URL}/wells/${selectedWellId}/attendance`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        }
      });

      if (response.ok) {
        const data = await response.json();
        
        toast({
          title: "Attendance Submitted",
          description: data.is_near_capacity 
            ? "Warning: This well is nearing capacity!"
            : "Your attendance has been recorded.",
          variant: data.is_near_capacity ? "destructive" : "default"
        });

        // Reset form
        setSelectedWellId("");
      } else {
        const error = await response.json();
        throw new Error(error.error || 'Failed to submit attendance');
      }
    } catch (error) {
      toast({
        title: "Error",
        description: error instanceof Error ? error.message : 'Failed to submit attendance',
        variant: "destructive",
      });
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b bg-card">
        <div className="container mx-auto flex items-center justify-between px-4 py-4">
          <Link to="/" className="flex items-center gap-2 text-foreground transition-colors hover:text-primary">
            <ArrowLeft className="h-5 w-5" />
            <span className="font-medium">Back to Home</span>
          </Link>
          <h1 className="text-xl font-bold text-foreground">Submit Attendance</h1>
          <div className="w-24" /> {/* Spacer for alignment */}
        </div>
      </header>

      {/* Form Section */}
      <section className="container mx-auto px-4 py-12">
        <div className="mx-auto max-w-2xl">
          <Card className="p-8">
            <div className="mb-6">
              <h2 className="text-2xl font-bold text-foreground">Record Your Visit</h2>
              <p className="mt-2 text-muted-foreground">
                Select your well to record your attendance. If you're experiencing any issues,
                you can report them using the button below.
              </p>
            </div>

            <form onSubmit={handleSubmit} className="space-y-6">
              <div>
                <WellSelector onWellSelect={setSelectedWellId} />
              </div>

              <div className="flex flex-col gap-4 pt-4">
                <Button 
                  type="submit" 
                  variant="hero" 
                  disabled={submitting}
                >
                  {submitting ? "Submitting..." : "Submit Attendance"}
                </Button>
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => navigate('/report', { state: { wellId: selectedWellId } })}
                >
                  Need Help? Report an Issue
                </Button>
              </div>
            </form>
          </Card>
        </div>
      </section>
    </div>
  );
};

export default SubmitAttendance;
