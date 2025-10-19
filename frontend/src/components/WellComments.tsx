import { ChevronDown } from "lucide-react";
import { cn } from "@/lib/utils";
import { useState } from "react";

interface WellCommentsProps {
  comments: string[];
}

const WellComments = ({ comments }: WellCommentsProps) => {
  const [isOpen, setIsOpen] = useState(false);
  const hasComments = comments && comments.length > 0;

  if (!hasComments) return null;

  return (
    <div className="w-full border-t mt-4 pt-2">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center justify-between w-full py-2 text-sm font-medium text-left text-muted-foreground hover:text-foreground"
      >
        <span>View Reports ({comments.length})</span>
        <ChevronDown
          className={cn(
            "h-4 w-4 transition-transform duration-200",
            isOpen && "transform rotate-180"
          )}
        />
      </button>
      <div
        className={cn(
          "overflow-hidden transition-all duration-300 ease-in-out",
          isOpen ? "max-h-[500px] opacity-100" : "max-h-0 opacity-0"
        )}
      >
        <div className="space-y-2 py-2">
          {comments.map((comment, index) => (
            <div
              key={index}
              className="rounded-md border bg-muted/30 p-3 text-sm"
            >
              {comment}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default WellComments;