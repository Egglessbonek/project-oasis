import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { useToast } from "@/hooks/use-toast";
import { ArrowLeft, Send } from "lucide-react";
import { Link, useSearchParams } from "react-router-dom";
import LoadingSpinner from "@/components/LoadingSpinner";
import WellSelector from "@/components/WellSelector";

const ReportIssue = () => {
  const { toast } = useToast();
  const [searchParams] = useSearchParams();
  const [formData, setFormData] = useState({
    wellId: "",
    issueType: "",
    description: "",
    contactName: "",
    contactPhone: "",
  });

  const [submitting, setSubmitting] = useState(false);

  // Set initial well ID from URL query parameter
  useEffect(() => {
    const wellId = searchParams.get('wellId');
    if (wellId) {
      setFormData(prev => ({ ...prev, wellId }));
    }
  }, [searchParams]);
  const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:3001/api';

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    // Validate form
    if (!formData.wellId || !formData.issueType || !formData.description) {
      toast({
        title: "Missing Information",
        description: "Please fill in all required fields.",
        variant: "destructive",
      });
      return;
    }

    setSubmitting(true);
    try {
      const response = await fetch(`${API_BASE_URL}/reports`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      });

      if (response.ok) {
        toast({
          title: "Issue Reported",
          description: "Your issue has been submitted successfully. We'll address it soon.",
        });

        // Reset form
        setFormData({
          wellId: "",
          issueType: "",
          description: "",
          contactName: "",
          contactPhone: "",
        });
      } else {
        const error = await response.json();
        throw new Error(error.error || 'Failed to submit report');
      }
    } catch (error) {
      toast({
        title: "Error",
        description: error instanceof Error ? error.message : 'Failed to submit report',
        variant: "destructive",
      });
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen bg-background">

      {/* Form Section */}
      <section className="container mx-auto px-4 py-12">
        <div className="mx-auto max-w-2xl">
          <Card className="p-8">
            <div className="mb-6">
              <h2 className="text-2xl font-bold text-foreground">Submit an Issue</h2>
              <p className="mt-2 text-muted-foreground">
                Fill out the form below to report a problem with your water well. We'll respond as quickly as possible.
              </p>
            </div>

            <form onSubmit={handleSubmit} className="space-y-6">
              <div>
                <Label>Select Well *</Label>
                <div className="mt-2">
                  <WellSelector 
                    onWellSelect={(wellId) => setFormData({ ...formData, wellId })}
                    initialWellId={formData.wellId}
                  />
                </div>
              </div>

              <div>
                <Label htmlFor="issueType">Issue Type *</Label>
                <Select
                  value={formData.issueType}
                  onValueChange={(value) => setFormData({ ...formData, issueType: value })}
                >
                  <SelectTrigger className="mt-2">
                    <SelectValue placeholder="Select issue type" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="no-water">No Water Flow</SelectItem>
                    <SelectItem value="low-pressure">Low Water Pressure</SelectItem>
                    <SelectItem value="contamination">Water Contamination</SelectItem>
                    <SelectItem value="mechanical">Mechanical Issue</SelectItem>
                    <SelectItem value="electrical">Electrical Problem</SelectItem>
                    <SelectItem value="leak">Leak or Damage</SelectItem>
                    <SelectItem value="other">Other</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div>
                <Label htmlFor="description">Description *</Label>
                <Textarea
                  id="description"
                  placeholder="Describe the issue in detail..."
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  className="mt-2 min-h-32"
                  required
                />
              </div>

              <div className="grid gap-6 sm:grid-cols-2">
                <div>
                  <Label htmlFor="contactName">Your Name</Label>
                  <Input
                    id="contactName"
                    placeholder="John Doe"
                    value={formData.contactName}
                    onChange={(e) => setFormData({ ...formData, contactName: e.target.value })}
                    className="mt-2"
                  />
                </div>

                <div>
                  <Label htmlFor="contactPhone">Phone Number</Label>
                  <Input
                    id="contactPhone"
                    type="tel"
                    placeholder="(555) 123-4567"
                    value={formData.contactPhone}
                    onChange={(e) => setFormData({ ...formData, contactPhone: e.target.value })}
                    className="mt-2"
                  />
                </div>
              </div>

              <div className="flex gap-4 pt-4">
                <Button 
                  type="submit" 
                  variant="hero" 
                  className="flex-1 relative"
                  disabled={submitting}
                >
                  {submitting ? (
                    <>
                      <LoadingSpinner size="sm" className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2" />
                      <span className="opacity-0">
                        <Send className="mr-2 h-4 w-4" />
                        Submit Report
                      </span>
                    </>
                  ) : (
                    <>
                      <Send className="mr-2 h-4 w-4" />
                      Submit Report
                    </>
                  )}
                </Button>
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => setFormData({
                    wellId: "",
                    issueType: "",
                    description: "",
                    contactName: "",
                    contactPhone: "",
                  })}
                >
                  Clear Form
                </Button>
              </div>
            </form>
          </Card>
        </div>
      </section>
    </div>
  );
};

export default ReportIssue;
