import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Button } from "@/components/ui/button";
import { ChevronDown } from "lucide-react";

interface WellCommentsProps {
  comments: string[];
}

const WellComments = ({ comments }: WellCommentsProps) => {
  const hasComments = comments && comments.length > 0;

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="outline" size="sm">
          {hasComments ? `View Reports (${comments.length})` : 'No Reports'} <ChevronDown className="ml-2 h-4 w-4" />
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent className="w-[400px] p-2">
        {hasComments ? (
          <div className="space-y-2">
            {comments.map((comment, index) => (
              <div
                key={index}
                className="rounded-md border bg-muted/30 p-2 text-sm"
              >
                {comment}
              </div>
            ))}
          </div>
        ) : (
          <div className="p-2 text-sm text-muted-foreground text-center">
            No reports available for this well
          </div>
        )}
      </DropdownMenuContent>
    </DropdownMenu>
  );
};

export default WellComments;