import os
from distutils.util import strtobool

from dotenv import load_dotenv

load_dotenv()


def check_work_mode(mode: str) -> str:
    return (
        os.getenv('SQLITE_DATABASE_URL')
        if bool(strtobool(os.getenv(mode, 'True')))
        else (
            f'postgresql+asyncpg://{os.getenv("POSTGRES_USER")}:'
            f'{os.getenv("POSTGRES_PASSWORD")}'
            f'@{os.getenv("POSTGRES_HOST")}'
            f'/{os.getenv("POSTGRES_DB")}'
        )
    )
