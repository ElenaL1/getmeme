from typing import Optional

from fastapi import HTTPException
from fastapi.encoders import jsonable_encoder
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .models import Meme
from .schemas import MemeUpdate


async def create_meme(
        name: str,
        image_url: str,
        session: AsyncSession,
) -> Meme:
    new_meme_data = {
       'name': name,
       'image_url': image_url
    }
    db_meme = Meme(**new_meme_data)
    session.add(db_meme)
    await session.commit()
    await session.refresh(db_meme)
    return db_meme


async def get_meme_id_by_name(
        meme_name: str,
        session: AsyncSession) -> Optional[int]:
    db_meme_id = await session.execute(
        select(Meme.id).where(Meme.name == meme_name)
        )
    db_meme_id = db_meme_id.scalars().first()
    return db_meme_id


async def get_meme_by_id(
        meme_id: int,
        session: AsyncSession,
) -> Meme:
    db_meme = await session.get(Meme, meme_id)
    if db_meme is None:
        raise HTTPException(status_code=404, detail="Такого мема нет!")
    return db_meme


async def read_all_memes_from_db(
        session: AsyncSession):
    """Fetches all memes from the database."""
    memes = await session.execute(select(Meme))
    return memes.scalars().all()


async def update_meme(
        db_meme: Meme,
        meme_in: MemeUpdate,
        session: AsyncSession,
) -> Meme:
    obj_data = jsonable_encoder(db_meme)
    update_data = meme_in.dict(exclude_unset=True)
    for field in obj_data:
        if field in update_data:
            setattr(db_meme, field, update_data[field])
    session.add(db_meme)
    await session.commit()
    await session.refresh(db_meme)
    return db_meme


async def delete_meme(
        db_meme: Meme,
        session: AsyncSession,
) -> Meme:
    await session.delete(db_meme)
    await session.commit()
    return db_meme
