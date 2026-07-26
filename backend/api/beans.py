import os
from datetime import datetime, timezone, timedelta
from typing import Annotated

import redis
from fastapi import APIRouter, Depends, HTTPException, Security, status, BackgroundTasks
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from db.database import get_db
from db.models import Bean, Store
from db.schemas import CoffeeBeanOut, Response, StoreOut
from celery_stuff.celery_app import _refresh_db

router = APIRouter()

security = HTTPBearer()

def verify_scraper_api_key(
    credentials: Annotated[HTTPAuthorizationCredentials, Security(security)]
) -> str:
    expected_api_key = os.getenv("SCRAPER_API_KEY")
    if not expected_api_key:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="SCRAPER_API_KEY is not configured on the server",
        )
    if credentials.credentials != expected_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key credential",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return credentials.credentials


@router.post("/beans/scrape", status_code=status.HTTP_202_ACCEPTED)
async def trigger_scrape(
    background_tasks: BackgroundTasks,
    _: Annotated[str, Depends(verify_scraper_api_key)],
):
    background_tasks.add_task(_refresh_db)
    return {"message": "Scraper job initiated successfully", "status": "processing"}


@router.get("/beans", response_model=Response)
async def list_beans(db: Annotated[AsyncSession, Depends(get_db)]) -> Response:

    result = await db.execute(
        select(Store).options(
            selectinload(Store.beans).selectinload(Bean.variants)
        )
    )
    stores = result.scalars().unique().all()
    stores_out: list[StoreOut] = []

    for store in stores:
        active_beans = [
            CoffeeBeanOut.model_validate(bean)
            for bean in store.beans
            if bean.is_active
        ]
        stores_out.append(
            StoreOut(
                id=store.id,
                name=store.name,
                url=store.url,
                beans=active_beans,
            )
        )

    return Response(stores=stores_out)