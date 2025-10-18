import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

// Service area utility functions
export interface ServiceAreaConfig {
  radius: number; // in meters
  color: string;
  opacity: number;
}

export const getServiceAreaColor = (status: string): string => {
  switch (status) {
    case 'operational':
      return '#10b981'; // green
    case 'needs-repair':
      return '#ef4444'; // red
    case 'maintenance':
      return '#f59e0b'; // yellow
    default:
      return '#6b7280'; // gray
  }
};

export const createServiceArea = (
  radius: number, 
  status: string, 
  opacity: number = 0.2
): ServiceAreaConfig => ({
  radius,
  color: getServiceAreaColor(status),
  opacity
});
