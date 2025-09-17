from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from db.database import get_db
from db.models import Bean
from db.schemas import BeansResponse


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

# Legacy endpoints (disabled)
# @router.post("/refresh")
# def refresh_cache():
#     return {"message": "Not implemented"}
#
# @router.get("/exec")
# async def exec_celery():
#     return {"message":"Not implemented yet"}
