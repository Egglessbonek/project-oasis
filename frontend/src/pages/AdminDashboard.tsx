import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { ArrowLeft, Search, CheckCircle, AlertTriangle, Clock, LogOut, User } from "lucide-react";
import { Link } from "react-router-dom";
import { useAuth } from "@/contexts/AuthContext";

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:3001/api';

interface Well {
  id: string;
  location: string;
  status: string;
  capacity: number;
  current_load: number;
  area_id: string;
  service_area: string;
  created_at: string;
  updated_at: string;
  issue_count: number;
}

interface Report {
  id: string;
  summary: string;
  status: string;
  fix_priority: number;
  created_at: string;
  image_url?: string;
  well_id: string;
  well_longitude: number;
  well_latitude: number;
}

interface DashboardData {
  wells: Well[];
  reports: Report[];
  stats: {
    total: number;
    operational: number;
    broken: number;
    maintenance: number;
    building: number;
    draft: number;
  };
}

const AdminDashboard = () => {
  const [searchTerm, setSearchTerm] = useState("");
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const { user, token, logout } = useAuth();

  // Fetch dashboard data
  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/admin/dashboard`, {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
          credentials: 'include',
        });

        if (response.ok) {
          const data = await response.json();
          setDashboardData(data);
        } else {
          setError('Failed to load dashboard data');
        }
      } catch (err) {
        setError('Network error. Please try again.');
      } finally {
        setLoading(false);
      }
    };

    if (token) {
      fetchDashboardData();
    }
  }, [token]);

  const filteredWells = dashboardData?.wells.filter(
    (well) =>
      well.id.toLowerCase().includes(searchTerm.toLowerCase())
  ) || [];

  const getStatusBadge = (status: string) => {
    switch (status) {
      case "completed":
        return (
          <Badge className="bg-accent/20 text-accent-foreground hover:bg-accent/30">
            <CheckCircle className="mr-1 h-3 w-3" />
            Operational
          </Badge>
        );
      case "broken":
        return (
          <Badge className="bg-destructive/20 text-destructive hover:bg-destructive/30">
            <AlertTriangle className="mr-1 h-3 w-3" />
            Broken
          </Badge>
        );
      case "under_maintenance":
        return (
          <Badge className="bg-primary/20 text-primary hover:bg-primary/30">
            <Clock className="mr-1 h-3 w-3" />
            Maintenance
          </Badge>
        );
      case "building":
        return (
          <Badge className="bg-yellow-500/20 text-yellow-600 hover:bg-yellow-500/30">
            <Clock className="mr-1 h-3 w-3" />
            Building
          </Badge>
        );
      case "draft":
        return (
          <Badge variant="outline">
            Draft
          </Badge>
        );
      default:
        return <Badge variant="outline">{status}</Badge>;
    }
  };

  const getPriorityBadge = (priority: number) => {
    if (priority >= 1000) {
      return <Badge variant="destructive">Critical</Badge>;
    } else if (priority >= 500) {
      return <Badge className="bg-destructive/70 hover:bg-destructive/80">High</Badge>;
    } else if (priority >= 100) {
      return <Badge className="bg-primary/70 hover:bg-primary/80">Medium</Badge>;
    } else {
      return <Badge variant="outline">Low</Badge>;
    }
  };

  const handleLogout = async () => {
    await logout();
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-center space-y-4">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto"></div>
          <p className="text-muted-foreground">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-center space-y-4">
          <AlertTriangle className="h-12 w-12 text-destructive mx-auto" />
          <p className="text-destructive">{error}</p>
          <Button onClick={() => window.location.reload()}>Retry</Button>
        </div>
      </div>
    );
  }

  const stats = dashboardData?.stats || {
    total: 0,
    operational: 0,
    broken: 0,
    maintenance: 0,
    building: 0,
    draft: 0,
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
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2 text-sm text-muted-foreground">
              <User className="h-4 w-4" />
              <span>{user?.email}</span>
            </div>
            <Button variant="outline" size="sm" onClick={handleLogout}>
              <LogOut className="h-4 w-4 mr-2" />
              Logout
            </Button>
          </div>
        </div>
      </header>

      {/* Dashboard Content */}
      <section className="container mx-auto px-4 py-8">
        {/* Stats Overview */}
        <div className="mb-8 grid gap-4 md:grid-cols-6">
          <Card className="p-6">
            <div className="text-2xl font-bold text-foreground">{stats.total}</div>
            <div className="text-sm text-muted-foreground">Total Wells</div>
          </Card>
          <Card className="p-6">
            <div className="text-2xl font-bold text-accent-foreground">{stats.operational}</div>
            <div className="text-sm text-muted-foreground">Operational</div>
          </Card>
          <Card className="p-6">
            <div className="text-2xl font-bold text-destructive">{stats.broken}</div>
            <div className="text-sm text-muted-foreground">Broken</div>
          </Card>
          <Card className="p-6">
            <div className="text-2xl font-bold text-primary">{stats.maintenance}</div>
            <div className="text-sm text-muted-foreground">Maintenance</div>
          </Card>
          <Card className="p-6">
            <div className="text-2xl font-bold text-yellow-600">{stats.building}</div>
            <div className="text-sm text-muted-foreground">Building</div>
          </Card>
          <Card className="p-6">
            <div className="text-2xl font-bold text-muted-foreground">{stats.draft}</div>
            <div className="text-sm text-muted-foreground">Draft</div>
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
                  <p className="text-muted-foreground">
                    Location: {well.location}
                  </p>
                  <p className="text-sm text-muted-foreground">
                    Capacity: {well.capacity} | Load: {well.current_load}
                  </p>
                  <p className="text-sm text-muted-foreground">
                    Updated: {new Date(well.updated_at).toLocaleDateString()}
                  </p>
                </div>

                <div className="flex items-center gap-4">
                  <div className="text-right">
                    <div className="text-sm text-muted-foreground">Active Issues</div>
                    <div className="text-2xl font-bold text-foreground">{well.issue_count}</div>
                  </div>
                  <Button variant="hero">View Details</Button>
                </div>
              </div>
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
