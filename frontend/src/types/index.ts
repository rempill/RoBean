export interface Store {
  id: number;
  name: string;
  websiteUrl: string;
}

export interface Variant {
  id: number;
  weightGrams: number;
  price: number;
  pricePerGram: number;
}

export interface Bean {
  id: number;
  storeId: number;
  storeName: string;
  storeUrl: string;
  name: string;
  url: string;
  imageUrl: string;
  variants: Variant[];
}
