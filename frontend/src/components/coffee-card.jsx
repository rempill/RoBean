import { Card } from "@/components/ui/card";

export function CoffeeCard({ name, imageUrl }) {
  return (
    <Card
      className="
        group
        h-[320px]
        grid grid-rows-[4fr_1fr]
        overflow-hidden rounded-lg border bg-card text-card-foreground
        transition-transform duration-200 ease-out will-change-[transform]
        hover:-translate-y-1 hover:shadow-lg
        motion-reduce:transition-none motion-reduce:hover:transform-none
        focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring
      "
      tabIndex={0}
    >
      <div className="relative h-full w-full">
        {imageUrl ? (
          <img
            src={imageUrl}
            alt={name}
            loading="lazy"
            className="h-full w-full object-cover transform-gpu transition-transform duration-300 ease-out will-change-transform group-hover:scale-[1.03]"
          />
        ) : (
          <div className="h-full w-full bg-gradient-to-br from-muted to-background flex items-center justify-center">
            <span className="text-sm text-muted-foreground">No image</span>
          </div>
        )}
      </div>

      <div className="border-t px-4 py-3 flex items-center justify-center bg-card">
        <span className="text-sm font-semibold text-foreground text-center truncate w-full">
          {name}
        </span>
      </div>
    </Card>
  );
}

export default CoffeeCard;
