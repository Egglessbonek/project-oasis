import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { useToast } from "@/hooks/use-toast";
import { ArrowLeft, Send } from "lucide-react";
import { Link } from "react-router-dom";

const ReportIssue = () => {
  const { toast } = useToast();
  const [formData, setFormData] = useState({
    wellId: "",
    issueType: "",
    description: "",
    contactName: "",
    contactPhone: "",
  });

  const handleSubmit = (e: React.FormEvent) => {
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

    // Success toast
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
          <h1 className="text-xl font-bold text-foreground">Report Well Issue</h1>
          <div className="w-24" /> {/* Spacer for alignment */}
        </div>
      </header>

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
                <Label htmlFor="wellId">Well ID *</Label>
                <Input
                  id="wellId"
                  placeholder="e.g., WELL-001"
                  value={formData.wellId}
                  onChange={(e) => setFormData({ ...formData, wellId: e.target.value })}
                  className="mt-2"
                  required
                />
                <p className="mt-1 text-sm text-muted-foreground">
                  Find this ID on your well's QR code or identification plate
                </p>
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
                <Button type="submit" variant="hero" className="flex-1">
                  <Send className="mr-2 h-4 w-4" />
                  Submit Report
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
