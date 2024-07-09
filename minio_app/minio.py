import io
import os

from dotenv import load_dotenv
from fastapi import FastAPI, File, HTTPException, Response, UploadFile
from fastapi.responses import JSONResponse
from minio import Minio
from minio.error import S3Error

app = FastAPI()

load_dotenv('.env')


MINIO_ENDPOINT = os.getenv("S3_HOSTNAME", "minio")
ACCESS_KEY = os.getenv("access_key")
SECRET_KEY = os.getenv("secret_key")
MINIO_PORT = os.getenv("minio_port")
BUCKET_NAME = os.getenv("bucket_name", "getmeme")


client = Minio(
    f'{MINIO_ENDPOINT}:{MINIO_PORT}',
    secure=False
)


@app.post("/upload/",
          tags=['Внутренее API для загрузки файлов в MinIO'])
async def upload_file(file: UploadFile = File(...)):
    try:
        # Сохраняем файл в MinIO
        file_data = await file.read()  # Чтение данных файла в память
        file_data_io = io.BytesIO(file_data)
        # Загружаем файл в бакет MinIO
        client.put_object(
            bucket_name=BUCKET_NAME,
            object_name=file.filename,
            data=file_data_io,
            length=len(file_data),
            content_type=file.content_type
        )
        return JSONResponse(content={
            "filename": file.filename, "content_type": file.content_type})
    except S3Error as err:
        raise HTTPException(
            status_code=500,
            detail=(f"Failed to upload object {file.filename}"
                    f" to bucket {BUCKET_NAME}: {err}")
        )


@app.get("/download/{bucket_name}/{object}/",
         tags=['Внутренее API для загрузки файлов в MinIO'])
async def download_file(
    object: str,
    bucket_name: str
):
    try:
        # Загрузка данных из MinIO
        object_data = client.get_object(bucket_name, object)
        data = object_data.read()
        headers = {"Content-Disposition": f"attachment; filename={object}"}
        return Response(content=data,
                        headers=headers,
                        media_type='application/octet-stream')
    except Exception as err:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to download file from bucket {BUCKET_NAME}: {err}")


@app.delete("/delete/{bucket_name}/{object}/",
            tags=['Внутренее API для загрузки файлов в MinIO'])
async def delete_object(
    bucket_name: str,
    object: str
):
    try:
        # Удаление данных из MinIO
        client.remove_object(bucket_name, object)
        return {"message":
                f"Deleted object {object} from bucket {BUCKET_NAME}"}
    except Exception as err:
        raise HTTPException(
            status_code=500,
            detail=(f"Failed to delete object {object}"
                    f" from bucket {BUCKET_NAME}: {err}")
        )
