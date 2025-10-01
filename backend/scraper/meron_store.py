import asyncio

import httpx
from bs4 import BeautifulSoup
from pydantic import HttpUrl

from scraper.schemas import CoffeeBean
from scraper.utils import get_response
import json

async def get_grams(url):
    response=await get_response(url)
    if not response:
        return None
    soup=BeautifulSoup(response,'html.parser')
    table=soup.select("table.info-tab-tabel tr")
    for tr in table:
        tds=tr.find_all("td")
        if len(tds)<2:
            continue
        label=tds[0].get_text(strip=True).lower()
        if "gramaj" not in label:
            continue
        value=tds[1].get_text(strip=True)
        digits="".join(ch for ch in value if ch.isdigit())
        if digits:
            return int(digits)

async def scrape_meron_store():
    base_url="https://meron.ro/categorie-produs/cafea/"
    response=await get_response(base_url)
    if not response:
        return []
    soup=BeautifulSoup(response,'html.parser')
    grid_items=soup.find_all("div",class_="product-wrapper")
    if not grid_items:
        print("No products found on Meron store page.")
        return []
    beans_init=[]
    async def process_bean(product):
        title=product.select_one("h3.wd-entities-title a").text.strip().split("|")
        name=title[0].strip()
        if "Meron" in name:
            return # skip meron card
        if "Kune" in name and "House" not in name:
            name=name.replace("Blend","House Blend")
        url=product.select_one("h3.wd-entities-title a")["href"]
        image = product.select_one("img")["src"]
        if "Kune" in name:
            name=name.replace("–","-")
            grams=int(title[-1].strip().replace("g","").replace("k","000"))
        elif "Box" in name:
            grams=await get_grams(url)
        else:
            grams=int(name.split(" ")[-1].replace("g",""))
            name = " ".join(name.split(" ")[:-1])
        price = float(product.select_one("span.price bdi").find(string=True, recursive=False).replace("\xa0", "").replace(".", "").replace(",", "."))
        price_per_gram=round(price/ grams,3)
        variants=[]
        variants.append({
            "grams": grams,
            "price": price,
            "price_per_gram": price_per_gram
        })
        beans_init.append(CoffeeBean(
            name=name,
            store="Meron",
            url=HttpUrl(url),
            image=HttpUrl(image) if image else None,
            variants=variants
        ))
    beans=[]
    async def merge_variants(bean):
        for b in beans:
            if b.name==bean.name:
                b.variants.extend(bean.variants)
                b.url="https://meron.ro/?s="+bean.name.replace(" ","+")+"&post_type=product"
                if bean.variants[0].grams==250:
                    b.image=bean.image
                return
        beans.append(bean)
    await asyncio.gather(*(process_bean(p) for p in grid_items))
    await asyncio.gather(*(merge_variants(b) for b in beans_init))
    return beans

if __name__=="__main__":
    asyncio.run(scrape_meron_store())
