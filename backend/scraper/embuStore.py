import asyncio

import httpx
from bs4 import BeautifulSoup
from pydantic import HttpUrl

from models import CoffeeBean
import json

# Scrapes product variants from a product page
def parse_product_variant(html):
    soup=BeautifulSoup(html,'html.parser')
    script_tags=soup.find_all("script",type="application/ld+json")
    target_data=None
    for tag in script_tags:
        try:
            data= json.loads(tag.string)
            if "hasVariant" in data:
                target_data=data
                break
        except json.JSONDecodeError:
            continue
    if not target_data:
        return []

    variants_data=target_data.get("hasVariant",[])
    boabe_variants=[]
    for variant in variants_data:
        name=variant.get("name","")
        if "Boabe" in name and "None" in name:
            offer= variant.get("offers",{})
            price_str= offer.get("price","0")
            grams_str= name.split("-")[1].strip() # extract grams from name
            grams_str= grams_str.split(" ")[0]
            grams= int(grams_str.lower().replace("kg","000").replace("g",""))
            if grams <= 0:
                continue
            price=float(price_str)
            price_per_gram=round(price/ grams,3)
            boabe_variants.append({
                "grams": grams,
                "price": price,
                "price_per_gram": price_per_gram
            })
    return boabe_variants

async def scrape_product_variant(url):
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
    if response.status_code != 200:
        print(f"Failed to retrieve product page: {response.status_code}")
        return []
    return parse_product_variant(response.text)

# Scrapes the Embu Coffee store for coffee beans
async def scrape_embu_store():
    base_url="https://embu-coffee.ro"
    page_url=f"{base_url}/collections/all"
    async with httpx.AsyncClient() as client:
        response = await client.get(page_url)
    if response.status_code!= 200:
        print(f"Failed to retrieve page: {response.status_code}")
        return []

    soup = BeautifulSoup(response.text, 'html.parser')
    product_grid= soup.find("ul",id="product-grid")
    if not product_grid:
        print("No products found on the page.")
        return []

    product_items=product_grid.find_all("li",class_="grid__item")
    beans=[]
    async def process_bean(product):
        name=product.select_one("h3.card__heading a").text.strip()
        url= product.select_one("h3.card__heading a")["href"]
        full_url=base_url+url
        image=product.select_one("img")["src"]
        variants=await scrape_product_variant(full_url)
        if not variants:
            print(f"No variants found for {full_url}")
            return
        beans.append(CoffeeBean(
            name=name,
            store="Embu Coffee",
            url=HttpUrl(full_url),
            image=HttpUrl("https:"+image) if image else None,
            variants=variants
        ))

    await asyncio.gather(*(process_bean(p) for p in product_items))
    return beans

