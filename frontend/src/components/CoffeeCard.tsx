import { Card } from "@/components/ui/card";
import { Bean, Variant } from "@/types";

interface CoffeeCardProps {
  bean: Bean;
}

const getLowestPriceVariant = (variants: Variant[]): Variant | null => {
  if (!variants || variants.length === 0) return null;
  return variants.reduce((lowest, current) => 
    current.pricePerGram < lowest.pricePerGram ? current : lowest
  );
};

export function CoffeeCard({ bean }: CoffeeCardProps) {
  const lowestPriceVariant = getLowestPriceVariant(bean.variants);

  return (
    <Card
      className="
        group
        overflow-hidden rounded-lg border bg-card text-card-foreground
        transition-transform duration-200 ease-out will-change-[transform]
        hover:-translate-y-1 hover:shadow-lg
        motion-reduce:transition-none motion-reduce:hover:transform-none
        focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring
        w-full flex flex-col pt-6 pb-0  /* responsive, keeps ratio */
      "
      tabIndex={0}
    >
      {/* Image */}
      <div className="relative w-full aspect-[3/4]">
        {bean.imageUrl ? (
          <img
            src={bean.imageUrl}
            alt={bean.name}
            loading="lazy"
            className="
              absolute inset-0 h-full w-full object-cover
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

      {/* Name + Price */}
      <div className="border-t bg-card flex flex-col items-center justify-center px-2 py-2 sm:px-3 sm:py-3" title={bean.name}>
        <span className="text-sm sm:text-base font-semibold text-foreground text-center truncate w-full">
          {bean.name}
        </span>
        {lowestPriceVariant && (
          <span className="text-[11px] sm:text-sm text-muted-foreground mt-0.5 line-clamp-1">
            Starting at {lowestPriceVariant.price.toFixed(2)} RON
          </span>
        )}
        {lowestPriceVariant && (
          <span className="text-[10px] sm:text-[11px] text-muted-foreground/80 mt-0.5 line-clamp-1">
            {lowestPriceVariant.pricePerGram.toFixed(3)} RON/g
          </span>
        )}
      </div>
    </Card>
  );
}

export default CoffeeCard;
