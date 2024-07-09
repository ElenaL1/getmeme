import os

from dotenv import load_dotenv
from fastapi import (APIRouter, Depends, File, Form,
                     HTTPException, Response, UploadFile)
from fastapi_pagination import Page, paginate
from httpx import AsyncClient, HTTPStatusError
from sqlalchemy.ext.asyncio import AsyncSession
import uuid

from app.core.db import get_async_session
from app.crud import (create_meme, delete_meme, get_meme_by_id,
                      get_meme_id_by_name, read_all_memes_from_db, update_meme)
from app.models import Meme
from app.schemas import MemeFull, MemeUpdate

load_dotenv('.env')

router = APIRouter()

BASE_URL = f"{os.getenv('s3_api')}:{os.getenv('s3_api_port')}"
BUCKET_NAME = os.getenv('bucket_name')


# Получить список всех мемов (с пагинацией)
@router.get("/memes", response_model=Page[MemeFull])
async def get_memes(
    session: AsyncSession = Depends(get_async_session)
) -> Page[MemeFull]:
    all_memes = await read_all_memes_from_db(session)
    return paginate(all_memes)


# Получить конкретный мем по его ID
@router.get("/memes/{meme_id}", response_class=Response)
async def get_meme(
    meme_id: int,
    session: AsyncSession = Depends(get_async_session)
):
    meme = await get_meme_by_id(meme_id, session)
    try:
        async with AsyncClient() as client:
            response = await client.get(
                f"http://{BASE_URL}/download/{BUCKET_NAME}/{meme.image_url}/"
            )
        response.raise_for_status()
        data = response.content
        headers = {"Content-Disposition":
                   f"attachment; filename={meme.image_url}"}
        return Response(content=data,
                        headers=headers,
                        media_type='application/octet-stream')
    except HTTPStatusError as http_err:
        raise HTTPException(
            status_code=http_err.response.status_code,
            detail=f"HTTP error occurred: {http_err}"
        )
    except Exception as err:
        raise HTTPException(
            status_code=500,
            detail=f"Error occurred while communicating with minio_api: {err}"
        )


# Добавить новый мем
@router.post("/memes/", response_model=MemeFull)
async def create_new_meme(
    name: str = Form(...),
    image: UploadFile = File(...),
    session: AsyncSession = Depends(get_async_session)
):
    meme_id = await get_meme_id_by_name(name, session)
    if meme_id is not None:
        raise HTTPException(
            status_code=422,
            detail='Мем с таким названием уже существует!',
        )
    try:
        async with AsyncClient() as client:
            file_name = str(uuid.uuid4())  # Генерируем уникальное имя файла
            files = {'file': (file_name, image.file, image.content_type)}
            response = await client.post(
                "http://" + BASE_URL + "/upload/",
                files=files,
                headers={'accept': 'application/json'}
            )
        response.raise_for_status()
    except HTTPStatusError as http_err:
        raise HTTPException(
            status_code=http_err.response.status_code,
            detail=f"HTTP error occurred: {http_err}"
        )
    except Exception as err:
        raise HTTPException(
            status_code=500,
            detail=f"Error occurred while communicating with minio_api: {err}"
        )
    new_meme = await create_meme(
        name=name,
        image_url=file_name,
        session=session)
    return new_meme


# Обновить существующий мем
@router.put("/memes/{meme_id}", response_model=MemeFull)
async def put_meme(
    meme_id: int,
    obj_in: MemeUpdate,
    session: AsyncSession = Depends(get_async_session)
):
    db_meme = await get_meme_by_id(meme_id, session)
    if obj_in.name is not None:
        await check_name_duplicate(obj_in.name, session)
    meme = await update_meme(db_meme, obj_in, session)
    return meme


# Удалить мем
@router.delete("/memes/{meme_id}")
async def remove_meme(
        meme_id: int,
        session: AsyncSession = Depends(get_async_session),
):
    meme = await check_meme_exists(meme_id, session)
    # Удаляем мем из MinIO
    try:
        async with AsyncClient() as client:
            response = await client.delete(
                f"http://{BASE_URL}/delete/{BUCKET_NAME}/{meme.image_url}/"
            )
        response.raise_for_status()
    except HTTPStatusError as http_err:
        raise HTTPException(
            status_code=http_err.response.status_code,
            detail=f"HTTP error occurred: {http_err}"
        )
    except Exception as err:
        raise HTTPException(
            status_code=500,
            detail=f"Error occurred while communicating with minio_api: {err}"
        )
    meme = await delete_meme(meme, session)
    return meme


async def check_meme_exists(
        meme_id: int,
        session: AsyncSession,
) -> Meme:
    db_meme = await get_meme_by_id(meme_id, session)
    if not db_meme:
        raise HTTPException(status_code=404, detail="Такого мема нет!")
    return db_meme


async def check_name_duplicate(
        meme_name: str,
        session: AsyncSession,
) -> None:
    meme_id = await get_meme_id_by_name(meme_name, session)
    if meme_id is not None:
        raise HTTPException(
            status_code=422,
            detail='Мем с таким именем уже существует!',
        )
