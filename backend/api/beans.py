from typing import Annotated

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from fastapi import APIRouter, Depends

from db.database import get_db
from db.models import Bean, Store
from db.schemas import CoffeeBeanOut, Response, StoreOut


router = APIRouter()


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
