from pydantic import BaseSettings

from app.core.external_functions import check_work_mode


class Settings(BaseSettings):
    database_url: str = check_work_mode('TEST_MODE')

    class Config:
        env_file = '.env'


settings = Settings()
