import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Droplets, AlertCircle, BarChart3, QrCode, Map } from "lucide-react";
import { Link } from "react-router-dom";

const Landing = () => {
  return (
    <div className="min-h-screen bg-background">
      {/* Hero Section */}
      <section className="relative overflow-hidden">
        <div className="absolute inset-0 bg-[var(--gradient-hero)]" />
        <div className="container relative mx-auto px-4 py-20 md:py-32">
          <div className="mx-auto max-w-3xl text-center">
            <div className="mb-6 inline-flex items-center gap-2 rounded-full bg-primary/10 px-4 py-2 text-sm font-medium text-primary">
              <Droplets className="h-4 w-4" />
              Water Well Management
            </div>
            <h1 className="mb-6 text-4xl font-bold tracking-tight text-foreground md:text-6xl">
              Streamline Your Water Well Management
            </h1>
            <p className="mb-8 text-lg text-muted-foreground md:text-xl">
              Track, maintain, and resolve well issues efficiently with our modern management system. 
              QR code enabled for instant issue reporting.
            </p>
            <div className="flex flex-col gap-4 sm:flex-row sm:justify-center">
              <Button asChild variant="hero" size="lg">
                <Link to="/report">Report an Issue</Link>
              </Button>
              <Button asChild variant="outline" size="lg">
                <Link to="/map">View Map</Link>
              </Button>
              <Button asChild variant="outline" size="lg">
                <Link to="/admin">Admin Dashboard</Link>
              </Button>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="container mx-auto px-4 py-20">
        <h2 className="mb-12 text-center text-3xl font-bold text-foreground">
          How It Works
        </h2>
        <div className="grid gap-8 md:grid-cols-3">
          <Card className="p-6 transition-all hover:shadow-[var(--shadow-hover)]">
            <div className="mb-4 inline-flex h-12 w-12 items-center justify-center rounded-lg bg-primary/10">
              <QrCode className="h-6 w-6 text-primary" />
            </div>
            <h3 className="mb-2 text-xl font-semibold text-foreground">
              QR Code Access
            </h3>
            <p className="text-muted-foreground">
              Each well has a unique QR code for instant access to report issues without any hassle.
            </p>
          </Card>

          <Card className="p-6 transition-all hover:shadow-[var(--shadow-hover)]">
            <div className="mb-4 inline-flex h-12 w-12 items-center justify-center rounded-lg bg-destructive/10">
              <AlertCircle className="h-6 w-6 text-destructive" />
            </div>
            <h3 className="mb-2 text-xl font-semibold text-foreground">
              Quick Reporting
            </h3>
            <p className="text-muted-foreground">
              Users can report well issues in seconds with our simple, intuitive form interface.
            </p>
          </Card>

          <Card className="p-6 transition-all hover:shadow-[var(--shadow-hover)]">
            <div className="mb-4 inline-flex h-12 w-12 items-center justify-center rounded-lg bg-accent/20">
              <BarChart3 className="h-6 w-6 text-secondary" />
            </div>
            <h3 className="mb-2 text-xl font-semibold text-foreground">
              Admin Tracking
            </h3>
            <p className="text-muted-foreground">
              Monitor all wells, track issues, and prioritize maintenance with comprehensive dashboard tools.
            </p>
          </Card>
        </div>
      </section>

      {/* CTA Section */}
      <section className="container mx-auto px-4 py-20">
        <Card className="relative overflow-hidden bg-gradient-to-br from-primary/10 to-secondary/10 p-12 text-center">
          <h2 className="mb-4 text-3xl font-bold text-foreground">
            Ready to Get Started?
          </h2>
          <p className="mb-8 text-lg text-muted-foreground">
            Begin managing your water wells more efficiently today.
          </p>
          <div className="flex flex-col gap-4 sm:flex-row sm:justify-center">
            <Button asChild variant="hero" size="lg">
              <Link to="/report">Report Issue</Link>
            </Button>
            <Button asChild variant="secondary" size="lg">
              <Link to="/admin">View Dashboard</Link>
            </Button>
          </div>
        </Card>
      </section>
    </div>
  );
};

export default Landing;
