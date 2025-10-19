import { Link, useLocation } from "react-router-dom";
import { cn } from "@/lib/utils";
import { MapPin, ClipboardList, AlertTriangle, UserCog } from "lucide-react";

const Navbar = () => {
  const location = useLocation();

  const navItems = [
    {
      name: "Submit Attendance",
      path: "/attendance",
      icon: ClipboardList,
    },
    {
      name: "Report an Issue",
      path: "/report",
      icon: AlertTriangle,
    },
    {
      name: "View Map",
      path: "/map",
      icon: MapPin,
    },
    {
      name: "Administrator Dashboard",
      path: "/admin",
      icon: UserCog,
    },
  ];

  return (
    <nav className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="container flex h-14 max-w-screen-2xl items-center">
        <Link 
          to="/" 
          className="mr-8 flex items-center space-x-2 font-bold"
        >
          <span className="text-primary">Project Oasis</span>
        </Link>
        <div className="flex flex-1 items-center justify-between space-x-2 md:justify-end">
          <div className="flex-1 md:flex md:items-center md:space-x-2">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = location.pathname === item.path;
              
              return (
                <Link
                  key={item.path}
                  to={item.path}
                  className={cn(
                    "inline-flex items-center whitespace-nowrap rounded-md px-3 py-2 text-sm font-medium transition-colors hover:bg-accent hover:text-accent-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:pointer-events-none disabled:opacity-50",
                    isActive && "bg-accent text-accent-foreground"
                  )}
                >
                  <Icon className="mr-2 h-4 w-4" />
                  {item.name}
                </Link>
              );
            })}
          </div>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
