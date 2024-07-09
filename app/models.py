from sqlalchemy import Column, String

# Импортируем базовый класс для моделей.
from app.core.db import Base


class Meme(Base):
    __tablename__ = 'meme'
    name = Column(String(100), unique=True, nullable=False)
    image_url = Column(String, nullable=False)
