import os
from typing import Final
from dotenv import load_dotenv

# Загружаем переменные окружения из файла ".env".
load_dotenv()

__all__ = (
    'ProductionConfig',
    'TestConfig',
)

_BASEDIR: Final = os.path.abspath(os.path.dirname(__file__))

# Настройки приложения в состоянии производства.
ProductionConfig = dict(
    SQLALCHEMY_DATABASE_URI=f'postgresql://'
                            f'{os.environ["POSTGRES_USER"]}:'
                            f'{os.environ["POSTGRES_PASSWORD"]}@'
                            f'{os.environ["POSTGRES_HOST"]}:'
                            f'{os.environ["POSTGRES_PORT"]}/'
                            f'{os.environ["POSTGRES_DB"]}',
)

# Настройки приложения в тестовом состоянии.
TestConfig = dict(
    SQLALCHEMY_DATABASE_URI=f'postgresql://'
                            f'{os.environ["POSTGRES_USER"]}:'
                            f'{os.environ["POSTGRES_PASSWORD"]}@'
                            f'{os.environ["POSTGRES_HOST"]}:'
                            f'{os.environ["POSTGRES_PORT"]}/'
                            f'{os.environ["POSTGRES_TEST_DB"]}',  # Тестовая БД.
)
