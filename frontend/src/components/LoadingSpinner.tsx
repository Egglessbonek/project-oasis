import { Loader2 } from "lucide-react";
import { cn } from "@/lib/utils";

interface LoadingSpinnerProps {
  className?: string;
  size?: "sm" | "default" | "lg";
  centered?: boolean;
}

const LoadingSpinner = ({ className, size = "default", centered = true }: LoadingSpinnerProps) => {
  const sizeClasses = {
    sm: "h-4 w-4",
    default: "h-8 w-8",
    lg: "h-12 w-12"
  };

  return (
    <div className={cn(
      "flex flex-col items-center gap-4",
      centered && "min-h-[200px] justify-center",
      className
    )}>
      <Loader2 className={cn(
        "animate-spin text-primary",
        sizeClasses[size]
      )} />
      <p className="text-sm text-muted-foreground">Loading...</p>
    </div>
  );
};

export default LoadingSpinner;
