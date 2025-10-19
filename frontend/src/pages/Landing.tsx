import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Droplets, AlertCircle, BarChart3, QrCode, Map, UserCheck, Heart, Shield, Clock } from "lucide-react";
import { Link } from "react-router-dom";
import MapSlider from "@/components/MapSlider";

const Landing = () => {
  return (
    <div className="min-h-screen bg-background">
      {/* Hero Section */}
      <section className="relative overflow-hidden">
        <div className="absolute inset-0 bg-[var(--gradient-hero)]" />
        {/* Oasis Background Image */}
        <div 
          className="absolute inset-0 bg-cover bg-center bg-no-repeat opacity-20"
          style={{ backgroundImage: 'url(/oasis.jpg)' }}
        />
        <div className="container relative mx-auto px-4 py-12 md:py-24">
          <div className="mx-auto max-w-3xl text-center">
            <div className="mb-6 inline-flex items-center gap-2 rounded-full bg-primary/10 px-4 py-2 text-sm font-medium text-primary animate-fade-in-up">
              <Droplets className="h-4 w-4 animate-pulse" />
              Water Well Management
            </div>
            <h1 className="mb-6 text-4xl font-bold tracking-tight text-foreground md:text-6xl animate-fade-in-up animation-delay-200">
              Streamline Your Water Well Management
            </h1>
            <p className="mb-8 text-lg text-muted-foreground md:text-xl animate-fade-in-up animation-delay-400">
              Track, maintain, and resolve well issues efficiently with our modern management system. 
              QR code enabled for instant issue reporting.
            </p>
            <div className="flex flex-col gap-4 sm:flex-row sm:justify-center animate-fade-in-up animation-delay-600">
              <Button asChild variant="hero" size="lg" className="transform transition-all duration-300 hover:scale-105 hover:shadow-lg">
                <Link to="/attendance">Get Started</Link>
              </Button>
              <Button asChild variant="outline" size="lg" className="transform transition-all duration-300 hover:scale-105 hover:shadow-lg">
                <Link to="/map">View Map</Link>
              </Button>
            </div>
          </div>
        </div>
      </section>

      {/* Our Mission Section */}
      <section className="container mx-auto px-4 py-20">
        <div className="mx-auto max-w-4xl text-center">
          <div className="mb-6 inline-flex items-center gap-2 rounded-full bg-primary/10 px-4 py-2 text-sm font-medium text-primary animate-fade-in-up">
            <Heart className="h-4 w-4 animate-pulse" />
            Our Mission
          </div>
          <h2 className="mb-8 text-3xl font-bold text-foreground md:text-4xl animate-fade-in-up animation-delay-200">
            Ensuring Water Security Through Proactive Management
          </h2>
          <p className="mb-12 text-lg text-muted-foreground md:text-xl animate-fade-in-up animation-delay-400">
            Water resources are the foundation of life, yet they face constant challenges that threaten communities worldwide. 
            When wells break down or maintenance fails, entire populations lose access to this vital resource.
          </p>
        </div>

        {/* Mission Hero Image */}
        <div className="mb-16 animate-fade-in-up animation-delay-600">
          <div className="relative mx-auto max-w-2xl overflow-hidden rounded-2xl shadow-2xl transform transition-all duration-500 hover:scale-[1.02] hover:shadow-3xl">
            <img 
              src="/water-joy.jpg" 
              alt="A young girl joyfully playing with clean water from a well pipe, representing the pure happiness that reliable water access brings to communities"
              className="h-[400px] w-full object-cover transition-transform duration-700 hover:scale-105"
            />
            <div className="absolute inset-0 bg-gradient-to-t from-black/20 to-transparent" />
            <div className="absolute bottom-6 left-6 right-6 text-center animate-fade-in-up animation-delay-800">
              <p className="text-lg font-semibold text-white drop-shadow-lg">
                This is why every well matters
              </p>
              <p className="text-sm text-white/90 drop-shadow-md">
                Clean water brings joy, health, and hope to communities
              </p>
            </div>
          </div>
        </div>

        <div className="grid gap-8 md:grid-cols-3">
          <Card className="p-8 text-center transition-all duration-300 hover:shadow-[var(--shadow-hover)] hover:scale-105 animate-fade-in-up animation-delay-200 group">
            <div className="mb-6 inline-flex h-16 w-16 items-center justify-center rounded-full bg-destructive/10 transition-all duration-300 group-hover:scale-110 group-hover:bg-destructive/20">
              <AlertCircle className="h-8 w-8 text-destructive animate-pulse" />
            </div>
            <h3 className="mb-4 text-xl font-semibold text-foreground">
              The Critical Challenge
            </h3>
            <p className="text-muted-foreground">
              Water wells often break down due to lack of maintenance, poor monitoring, and delayed response to issues. 
              When this happens, communities face immediate water scarcity, affecting health, education, and economic stability.
            </p>
          </Card>

          <Card className="p-8 text-center transition-all duration-300 hover:shadow-[var(--shadow-hover)] hover:scale-105 animate-fade-in-up animation-delay-400 group">
            <div className="mb-6 inline-flex h-16 w-16 items-center justify-center rounded-full bg-orange-500/10 transition-all duration-300 group-hover:scale-110 group-hover:bg-orange-500/20">
              <Clock className="h-8 w-8 text-orange-500 animate-pulse" />
            </div>
            <h3 className="mb-4 text-xl font-semibold text-foreground">
              Information Gap
            </h3>
            <p className="text-muted-foreground">
              Without proper tracking and reporting systems, well failures go unnoticed for days or weeks. 
              Critical maintenance information gets lost, making repairs more expensive and time-consuming.
            </p>
          </Card>

          <Card className="p-8 text-center transition-all duration-300 hover:shadow-[var(--shadow-hover)] hover:scale-105 animate-fade-in-up animation-delay-600 group">
            <div className="mb-6 inline-flex h-16 w-16 items-center justify-center rounded-full bg-primary/10 transition-all duration-300 group-hover:scale-110 group-hover:bg-primary/20">
              <Shield className="h-8 w-8 text-primary animate-pulse" />
            </div>
            <h3 className="mb-4 text-xl font-semibold text-foreground">
              Our Solution
            </h3>
            <p className="text-muted-foreground">
              We provide real-time monitoring, instant issue reporting, and comprehensive maintenance tracking 
              to prevent breakdowns and ensure rapid response when problems occur. Every well matters.
            </p>
          </Card>
        </div>

        <div className="mt-16 rounded-lg bg-gradient-to-r from-primary/5 to-secondary/5 p-8 text-center animate-fade-in-up animation-delay-800 transform transition-all duration-500 hover:scale-[1.01]">
          <h3 className="mb-4 text-2xl font-bold text-foreground">
            Why This Matters
          </h3>
          <p className="mx-auto max-w-3xl text-lg text-muted-foreground">
            Every child deserves the joy of clean water. Every family deserves reliable access to this life-giving resource. 
            A single broken well can affect hundreds of families, but with proper maintenance tracking and 
            immediate issue reporting, we can prevent these failures and ensure that the simple pleasure of 
            clean water remains a constant in communities worldwide.
          </p>
        </div>
      </section>

      {/* Impact Map Section */}
      <section className="container mx-auto px-4 py-20">
        <h2 className="mb-6 text-center text-3xl font-bold text-foreground animate-fade-in-up">
          Interactive Well Mapping
        </h2>
        <p className="mb-12 text-center text-lg text-muted-foreground animate-fade-in-up animation-delay-200">
          Explore our comprehensive mapping system that provides real-time insights into water well locations, 
          performance analytics, and maintenance status across communities.
        </p>
        <div className="mx-auto max-w-4xl animate-fade-in-up animation-delay-400">
          <MapSlider />
        </div>
      </section>

      {/* Features Section */}
      <section className="container mx-auto px-4 py-20">
        <h2 className="mb-12 text-center text-3xl font-bold text-foreground animate-fade-in-up">
          How It Works
        </h2>
        <div className="grid gap-8 md:grid-cols-3">
          <Card className="p-6 transition-all duration-300 hover:shadow-[var(--shadow-hover)] hover:scale-105 animate-fade-in-up animation-delay-200 group">
            <div className="mb-4 inline-flex h-12 w-12 items-center justify-center rounded-lg bg-primary/10 transition-all duration-300 group-hover:scale-110 group-hover:bg-primary/20">
              <UserCheck className="h-6 w-6 text-primary animate-pulse" />
            </div>
            <h3 className="mb-2 text-xl font-semibold text-foreground">
              Easy Attendance
            </h3>
            <p className="text-muted-foreground">
              Submit your attendance quickly and easily. Get instant feedback if a well is nearing capacity.
            </p>
          </Card>

          <Card className="p-6 transition-all duration-300 hover:shadow-[var(--shadow-hover)] hover:scale-105 animate-fade-in-up animation-delay-400 group">
            <div className="mb-4 inline-flex h-12 w-12 items-center justify-center rounded-lg bg-destructive/10 transition-all duration-300 group-hover:scale-110 group-hover:bg-destructive/20">
              <AlertCircle className="h-6 w-6 text-destructive animate-pulse" />
            </div>
            <h3 className="mb-2 text-xl font-semibold text-foreground">
              Quick Reporting
            </h3>
            <p className="text-muted-foreground">
              Users can report well issues in seconds with our simple, intuitive form interface.
            </p>
          </Card>

          <Card className="p-6 transition-all duration-300 hover:shadow-[var(--shadow-hover)] hover:scale-105 animate-fade-in-up animation-delay-600 group">
            <div className="mb-4 inline-flex h-12 w-12 items-center justify-center rounded-lg bg-accent/20 transition-all duration-300 group-hover:scale-110 group-hover:bg-accent/30">
              <BarChart3 className="h-6 w-6 text-secondary animate-pulse" />
            </div>
            <h3 className="mb-2 text-xl font-semibold text-foreground">
              Administrator
            </h3>
            <p className="text-muted-foreground">
              Monitor all wells, track issues, and prioritize maintenance with comprehensive dashboard tools.
            </p>
          </Card>
        </div>
      </section>

      {/* Feature Showcase Section */}
      <section className="container mx-auto px-4 py-20">
        <h2 className="mb-12 text-center text-3xl font-bold text-foreground animate-fade-in-up">
          See It In Action
        </h2>
        <p className="mb-16 text-center text-lg text-muted-foreground animate-fade-in-up animation-delay-200">
          Experience the complete workflow from issue submission to resolution management
        </p>

        <div className="grid gap-12 lg:grid-cols-2">
          {/* Submit Feature */}
          <div className="animate-fade-in-up animation-delay-400">
            <Card className="overflow-hidden transition-all duration-500 hover:shadow-xl">
              <div className="aspect-[4/3] w-full overflow-hidden bg-muted">
                <img 
                  src="/Submit.png" 
                  alt="Submit attendance and report issues interface"
                  className="h-full w-full object-contain transition-transform duration-700 hover:scale-105"
                />
              </div>
              <div className="p-8">
                <div className="mb-4 flex items-center gap-3">
                  <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-primary/10">
                    <QrCode className="h-6 w-6 text-primary" />
                  </div>
                  <h3 className="text-2xl font-bold text-foreground">Easy Issue Reporting</h3>
                </div>
                <p className="mb-6 text-muted-foreground">
                  Users can quickly submit attendance and report well issues through our intuitive interface. 
                  QR code scanning makes it even faster to access the right well and submit reports.
                </p>
                <div className="space-y-3">
                  <div className="flex items-center gap-3">
                    <div className="h-2 w-2 rounded-full bg-primary"></div>
                    <span className="text-sm text-muted-foreground">One-click attendance submission</span>
                  </div>
                  <div className="flex items-center gap-3">
                    <div className="h-2 w-2 rounded-full bg-primary"></div>
                    <span className="text-sm text-muted-foreground">Quick issue reporting with photos</span>
                  </div>
                  <div className="flex items-center gap-3">
                    <div className="h-2 w-2 rounded-full bg-primary"></div>
                    <span className="text-sm text-muted-foreground">Real-time status updates</span>
                  </div>
                </div>
              </div>
            </Card>
          </div>

          {/* Dashboard Feature */}
          <div className="animate-fade-in-up animation-delay-600">
            <Card className="overflow-hidden transition-all duration-500 hover:shadow-xl">
              <div className="aspect-[4/3] w-full overflow-hidden bg-muted">
                <img 
                  src="/dashboard.png" 
                  alt="Administrator dashboard showing well management and ticket resolution"
                  className="h-full w-full object-contain transition-transform duration-700 hover:scale-105"
                />
              </div>
              <div className="p-8">
                <div className="mb-4 flex items-center gap-3">
                  <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-accent/20">
                    <BarChart3 className="h-6 w-6 text-secondary" />
                  </div>
                  <h3 className="text-2xl font-bold text-foreground">Administrator Dashboard</h3>
                </div>
                <p className="mb-6 text-muted-foreground">
                  Administrators get a comprehensive view of all wells, real-time issue tracking, 
                  and powerful tools to manage maintenance, resolve tickets, and monitor system health.
                </p>
                <div className="space-y-3">
                  <div className="flex items-center gap-3">
                    <div className="h-2 w-2 rounded-full bg-accent"></div>
                    <span className="text-sm text-muted-foreground">Real-time well status monitoring</span>
                  </div>
                  <div className="flex items-center gap-3">
                    <div className="h-2 w-2 rounded-full bg-accent"></div>
                    <span className="text-sm text-muted-foreground">Issue ticket management and resolution</span>
                  </div>
                  <div className="flex items-center gap-3">
                    <div className="h-2 w-2 rounded-full bg-accent"></div>
                    <span className="text-sm text-muted-foreground">Comprehensive analytics and reporting</span>
                  </div>
                </div>
              </div>
            </Card>
          </div>
        </div>

        {/* Workflow Description */}
        <div className="mt-16 rounded-lg bg-gradient-to-r from-primary/5 to-secondary/5 p-8 text-center animate-fade-in-up animation-delay-800">
          <h3 className="mb-4 text-2xl font-bold text-foreground">
            Complete Workflow
          </h3>
          <p className="mx-auto max-w-3xl text-lg text-muted-foreground">
            From the moment a user reports an issue through our simple interface, 
            administrators can immediately see, prioritize, and resolve problems through 
            the comprehensive dashboard. This seamless workflow ensures rapid response 
            times and efficient well maintenance.
          </p>
        </div>
      </section>

      {/* CTA Section */}
      <section className="container mx-auto px-4 py-20">
        <Card className="relative overflow-hidden bg-gradient-to-br from-primary/10 to-secondary/10 p-12 text-center animate-fade-in-up transform transition-all duration-500 hover:scale-[1.01] hover:shadow-2xl">
          <h2 className="mb-4 text-3xl font-bold text-foreground animate-fade-in-up animation-delay-200">
            Ready to Get Started?
          </h2>
          <p className="mb-8 text-lg text-muted-foreground animate-fade-in-up animation-delay-400">
            Begin managing your water wells more efficiently today.
          </p>
          <div className="flex flex-col gap-4 sm:flex-row sm:justify-center animate-fade-in-up animation-delay-600">
            <Button asChild variant="hero" size="lg" className="transform transition-all duration-300 hover:scale-105 hover:shadow-lg">
              <Link to="/attendance">Submit Attendance</Link>
            </Button>
            <Button asChild variant="outline" size="lg" className="transform transition-all duration-300 hover:scale-105 hover:shadow-lg">
              <Link to="/map">Explore Map</Link>
            </Button>
          </div>
        </Card>
      </section>
    </div>
  );
};

export default Landing;
