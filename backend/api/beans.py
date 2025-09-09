import asyncio

from asgiref.sync import sync_to_async
from celery import Celery
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from ..db.database import get_db
from ..db.models import Bean
from ..db.schemas import BeansResponse


router = APIRouter()


@router.get("/beans", response_model=BeansResponse)
# Scrapes all stores for coffee beans
async def list_beans(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Bean).options(
            selectinload(Bean.store),
            selectinload(Bean.variants),
        )
    )
    beans = result.scalars().unique().all()
    return {"beans": beans}

"""@router.post("/refresh")
def refresh_cache():
    beans= scrape_embu_store()
    set_cached_beans(beans)
    return JSONResponse({
        "message": "Cache refreshed successfully",
        "timestamp":get_last_updated()
    })"""

"""@router.get("/exec")
async def exec_celery():
    loop = asyncio.get_running_loop()
    task = await loop.run_in_executor(None, lambda: refresh_db.delay())
    return JSONResponse({"message":"Not implemented yet"})"""

