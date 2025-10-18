import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { ArrowLeft, Search, CheckCircle, AlertTriangle, Clock } from "lucide-react";
import { Link } from "react-router-dom";

// Mock data for demonstration
const mockWells = [
  {
    id: "WELL-001",
    location: "North Field A",
    status: "operational",
    lastMaintenance: "2025-09-15",
    issuesCount: 0,
  },
  {
    id: "WELL-002",
    location: "South Field B",
    status: "needs-attention",
    lastMaintenance: "2025-08-20",
    issuesCount: 2,
    issues: [
      { type: "Low Water Pressure", reportedAt: "2025-10-15", priority: "medium" },
      { type: "Mechanical Issue", reportedAt: "2025-10-14", priority: "high" },
    ],
  },
  {
    id: "WELL-003",
    location: "East Field C",
    status: "operational",
    lastMaintenance: "2025-09-30",
    issuesCount: 0,
  },
  {
    id: "WELL-004",
    location: "West Field D",
    status: "critical",
    lastMaintenance: "2025-07-10",
    issuesCount: 1,
    issues: [
      { type: "No Water Flow", reportedAt: "2025-10-16", priority: "critical" },
    ],
  },
  {
    id: "WELL-005",
    location: "Central Field E",
    status: "operational",
    lastMaintenance: "2025-10-01",
    issuesCount: 0,
  },
];

const AdminDashboard = () => {
  const [searchTerm, setSearchTerm] = useState("");

  const filteredWells = mockWells.filter(
    (well) =>
      well.id.toLowerCase().includes(searchTerm.toLowerCase()) ||
      well.location.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const getStatusBadge = (status: string) => {
    switch (status) {
      case "operational":
        return (
          <Badge className="bg-accent/20 text-accent-foreground hover:bg-accent/30">
            <CheckCircle className="mr-1 h-3 w-3" />
            Operational
          </Badge>
        );
      case "needs-attention":
        return (
          <Badge className="bg-primary/20 text-primary hover:bg-primary/30">
            <Clock className="mr-1 h-3 w-3" />
            Needs Attention
          </Badge>
        );
      case "critical":
        return (
          <Badge className="bg-destructive/20 text-destructive hover:bg-destructive/30">
            <AlertTriangle className="mr-1 h-3 w-3" />
            Critical
          </Badge>
        );
      default:
        return <Badge variant="outline">{status}</Badge>;
    }
  };

  const getPriorityBadge = (priority: string) => {
    switch (priority) {
      case "critical":
        return <Badge variant="destructive">Critical</Badge>;
      case "high":
        return <Badge className="bg-destructive/70 hover:bg-destructive/80">High</Badge>;
      case "medium":
        return <Badge className="bg-primary/70 hover:bg-primary/80">Medium</Badge>;
      default:
        return <Badge variant="outline">{priority}</Badge>;
    }
  };

  const stats = {
    total: mockWells.length,
    operational: mockWells.filter((w) => w.status === "operational").length,
    needsAttention: mockWells.filter((w) => w.status === "needs-attention").length,
    critical: mockWells.filter((w) => w.status === "critical").length,
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
          <h1 className="text-xl font-bold text-foreground">Admin Dashboard</h1>
          <div className="w-24" /> {/* Spacer */}
        </div>
      </header>

      {/* Dashboard Content */}
      <section className="container mx-auto px-4 py-8">
        {/* Stats Overview */}
        <div className="mb-8 grid gap-4 md:grid-cols-4">
          <Card className="p-6">
            <div className="text-2xl font-bold text-foreground">{stats.total}</div>
            <div className="text-sm text-muted-foreground">Total Wells</div>
          </Card>
          <Card className="p-6">
            <div className="text-2xl font-bold text-accent-foreground">{stats.operational}</div>
            <div className="text-sm text-muted-foreground">Operational</div>
          </Card>
          <Card className="p-6">
            <div className="text-2xl font-bold text-primary">{stats.needsAttention}</div>
            <div className="text-sm text-muted-foreground">Needs Attention</div>
          </Card>
          <Card className="p-6">
            <div className="text-2xl font-bold text-destructive">{stats.critical}</div>
            <div className="text-sm text-muted-foreground">Critical Issues</div>
          </Card>
        </div>

        {/* Search Bar */}
        <div className="mb-6">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 h-5 w-5 -translate-y-1/2 text-muted-foreground" />
            <Input
              placeholder="Search by well ID or location..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10"
            />
          </div>
        </div>

        {/* Wells List */}
        <div className="space-y-4">
          {filteredWells.map((well) => (
            <Card key={well.id} className="p-6">
              <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
                <div className="space-y-2">
                  <div className="flex items-center gap-3">
                    <h3 className="text-xl font-semibold text-foreground">{well.id}</h3>
                    {getStatusBadge(well.status)}
                  </div>
                  <p className="text-muted-foreground">{well.location}</p>
                  <p className="text-sm text-muted-foreground">
                    Last Maintenance: {new Date(well.lastMaintenance).toLocaleDateString()}
                  </p>
                </div>

                <div className="flex items-center gap-4">
                  <div className="text-right">
                    <div className="text-sm text-muted-foreground">Active Issues</div>
                    <div className="text-2xl font-bold text-foreground">{well.issuesCount}</div>
                  </div>
                  <Button variant="hero">View Details</Button>
                </div>
              </div>

              {/* Issues List */}
              {well.issues && well.issues.length > 0 && (
                <div className="mt-4 space-y-2 border-t pt-4">
                  <h4 className="text-sm font-medium text-foreground">Recent Issues:</h4>
                  {well.issues.map((issue, idx) => (
                    <div
                      key={idx}
                      className="flex items-center justify-between rounded-md bg-muted/50 p-3"
                    >
                      <div>
                        <div className="font-medium text-foreground">{issue.type}</div>
                        <div className="text-sm text-muted-foreground">
                          Reported: {new Date(issue.reportedAt).toLocaleDateString()}
                        </div>
                      </div>
                      {getPriorityBadge(issue.priority)}
                    </div>
                  ))}
                </div>
              )}
            </Card>
          ))}
        </div>

        {filteredWells.length === 0 && (
          <Card className="p-12 text-center">
            <p className="text-muted-foreground">No wells found matching your search.</p>
          </Card>
        )}
      </section>
    </div>
  );
};

export default AdminDashboard;
