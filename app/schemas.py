from typing import Optional

from pydantic import BaseModel, Field, PositiveInt, validator


class MemeBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, example='Имя мема')


class MemeUpdate(MemeBase):

    @validator('name')
    def name_cannot_be_null(cls, value):
        if value is None:
            raise ValueError('Имя мема не может быть пустым!')
        return value


class MemeFull(MemeBase):
    id: PositiveInt
    image_url: Optional[str] = Field(None, example='image_name.jpg')

    class Config:
        orm_mode = True
