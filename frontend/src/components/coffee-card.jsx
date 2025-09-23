import { Card } from "@/components/ui/card";

export function CoffeeCard({ name, imageUrl }) {
  return (
    <Card
      className="
        group
        overflow-hidden rounded-lg border bg-card text-card-foreground
        transition-transform duration-200 ease-out will-change-[transform]
        hover:-translate-y-1 hover:shadow-lg
        motion-reduce:transition-none motion-reduce:hover:transform-none
        focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring
        w-full aspect-[3/4]   /* responsive, keeps ratio */
      "
      tabIndex={0}
    >
      {/* Image */}
      <div className="relative w-full h-3/4">
        {imageUrl ? (
          <img
            src={imageUrl}
            alt={name}
            loading="lazy"
            className="
              h-full w-full object-cover
              transform-gpu transition-transform duration-300 ease-out will-change-transform
              group-hover:scale-[1.03]
            "
          />
        ) : (
          <div className="h-full w-full bg-gradient-to-br from-muted to-background flex items-center justify-center">
            <span className="text-sm text-muted-foreground">No image</span>
          </div>
        )}
      </div>

      {/* Name */}
      <div className="border-t bg-card flex items-center justify-center px-2 py-2 sm:px-3 sm:py-3 h-1/4"  title={name}>
        <span className="text-sm sm:text-base font-semibold text-foreground text-center truncate">
          {name}
        </span>
      </div>
    </Card>
  );
}


export default CoffeeCard;
