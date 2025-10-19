import { useState } from "react";
import { Button } from "@/components/ui/button";
import { ChevronLeft, ChevronRight, MapPin, BarChart3 } from "lucide-react";

interface MapSlide {
  id: string;
  image: string;
  title: string;
  description: string;
  icon: React.ReactNode;
}

const MapSlider = () => {
  const [currentSlide, setCurrentSlide] = useState(0);

  const slides: MapSlide[] = [
    {
      id: "overview",
      image: "/Wells.png",
      title: "Comprehensive Well Overview",
      description: "View all water wells across your region with real-time status indicators and maintenance alerts.",
      icon: <MapPin className="h-5 w-5" />
    },
    {
      id: "analytics",
      image: "/wells2.png", 
      title: "Detailed Analytics & Insights",
      description: "Analyze well performance, usage patterns, and maintenance trends with interactive data visualizations.",
      icon: <BarChart3 className="h-5 w-5" />
    }
  ];

  const nextSlide = () => {
    setCurrentSlide((prev) => (prev + 1) % slides.length);
  };

  const prevSlide = () => {
    setCurrentSlide((prev) => (prev - 1 + slides.length) % slides.length);
  };

  const goToSlide = (index: number) => {
    setCurrentSlide(index);
  };

  return (
    <div className="relative w-full">
      {/* Main Slider Container */}
      <div className="relative overflow-hidden rounded-lg border bg-card shadow-lg">
        <div 
          className="flex transition-transform duration-500 ease-in-out"
          style={{ transform: `translateX(-${currentSlide * 100}%)` }}
        >
          {slides.map((slide, index) => (
            <div key={slide.id} className="w-full flex-shrink-0">
              <div className="aspect-[4/3] w-full overflow-hidden rounded-md bg-muted">
                <img 
                  src={slide.image}
                  alt={slide.title}
                  className="h-full w-full object-contain transition-transform duration-700 hover:scale-105"
                />
              </div>
              <div className="p-6">
                <div className="flex items-center gap-3 mb-3">
                  <div className="flex h-10 w-10 items-center justify-center rounded-full bg-primary/10">
                    {slide.icon}
                  </div>
                  <h3 className="text-lg font-semibold text-foreground">
                    {slide.title}
                  </h3>
                </div>
                <p className="text-sm text-muted-foreground">
                  {slide.description}
                </p>
              </div>
            </div>
          ))}
        </div>

        {/* Navigation Arrows */}
        <Button
          variant="outline"
          size="icon"
          className="absolute left-4 top-1/2 -translate-y-1/2 h-10 w-10 rounded-full bg-background/80 backdrop-blur-sm hover:bg-background shadow-lg"
          onClick={prevSlide}
        >
          <ChevronLeft className="h-4 w-4" />
        </Button>
        <Button
          variant="outline"
          size="icon"
          className="absolute right-4 top-1/2 -translate-y-1/2 h-10 w-10 rounded-full bg-background/80 backdrop-blur-sm hover:bg-background shadow-lg"
          onClick={nextSlide}
        >
          <ChevronRight className="h-4 w-4" />
        </Button>
      </div>

      {/* Slide Indicators */}
      <div className="flex justify-center gap-2 mt-6">
        {slides.map((_, index) => (
          <button
            key={index}
            className={`h-2 w-8 rounded-full transition-all duration-300 ${
              index === currentSlide 
                ? "bg-primary w-12" 
                : "bg-muted hover:bg-muted-foreground/50"
            }`}
            onClick={() => goToSlide(index)}
          />
        ))}
      </div>

      {/* Slide Counter */}
      <div className="text-center mt-4">
        <span className="text-sm text-muted-foreground">
          {currentSlide + 1} of {slides.length}
        </span>
      </div>
    </div>
  );
};

export default MapSlider;
