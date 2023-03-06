import os
from typing import Final
from dotenv import load_dotenv

# Загружаем переменные окружения из файла ".env".
load_dotenv()

__all__ = (
    'ProductionConfig',
    'TestConfig',
)

ProductionConfig: Final = dict(
    SQLALCHEMY_DATABASE_URI=f'postgresql://'
                            f'{os.environ["POSTGRES_USER"]}:'
                            f'{os.environ["POSTGRES_PASSWORD"]}@'
                            f'{os.environ["POSTGRES_HOST"]}:'
                            f'{os.environ["POSTGRES_PORT"]}/'
                            f'{os.environ["POSTGRES_DB"]}',
)

TestConfig: Final = dict(
    SQLALCHEMY_DATABASE_URI=f'postgresql://'
                            f'{os.environ["POSTGRES_USER"]}:'
                            f'{os.environ["POSTGRES_PASSWORD"]}@'
                            f'{os.environ["POSTGRES_HOST"]}:'
                            f'{os.environ["POSTGRES_PORT"]}/'
                            f'{os.environ["POSTGRES_TEST_DB"]}',  # Тестовая БД.
)
