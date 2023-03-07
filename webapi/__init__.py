import os
from flask import Flask
from werkzeug.routing import IntegerConverter

from webapi.db_models import db
from webapi.resources import api
from webapi.config import *

__all__ = (
    'app',
    'start_app',
    'configure_app_and_db',
)

app = Flask(__name__)


class SignedIntConverter(IntegerConverter):
    regex = r'-?\d+'


# Добавляем новый обработчик целого числа в URL,
# который работает также с отрицательными числами.
# (стандартный "int" не включает их в себя). 
app.url_map.converters['signed_int'] = SignedIntConverter


@app.route('/', methods=['GET'])
def homepage() -> str:
    return 'Приложение работает!'


def start_app():
    configure_app_and_db()
    app.run(debug=os.environ['FLASK_DEBUG'],
            host=os.environ['FLASK_HOST'],  # Важно! Из docker-контейнера приложение работает только
                                            # при FLASK_HOST = '0.0.0.0' (не работает если, к примеру, 'localhost').
            port=os.environ['FLASK_PORT'],
            )


def configure_app_and_db(config: dict = ProductionConfig) -> None:
    """
    Настраивает приложение согласно `config`,
    соединяет приложение с БД и создаёт таблицы.
    """

    app.config.from_mapping(config)
    api.init_app(app)
    db.init_app(app)
    app.app_context().push()

    # Инструкция работает только с помощью реализации healthcheck в docker-compose файле.
    # Без неё вызов `create_all(...)` завершается исключением, поскольку postgres
    # не успевает инициализироваться.
    db.create_all()
