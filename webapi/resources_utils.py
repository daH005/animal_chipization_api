from flask import request
from flask_restful import abort, fields, Api, Resource
from http import HTTPStatus
from pydantic import ValidationError
from typing import Callable

from webapi.db_models import *
from webapi.validation_models import *

__all__ = (
    'account_resource_fields',
    'location_resource_fields',
    'animal_type_resource_fields',
    'animal_resource_fields',
    'resource_route',
    'authorizated_account',
    'abort_with_forbidden_if_user_is_authorized',
    'account_registration_or_updating_or_abort_with_bad_request',
    'abort_with_unauthorized_if_authorization_data_is_invalid',
    'abort_with_unauthorized_if_authorization_header_is_none',
    'abort_with_bad_request_if_id_is_invalid',
    'location_creating_or_updating_or_abort_with_bad_request',
    'set_attrs_of_model_instance',
    'animal_type_creating_or_updating_or_abort_with_bad_request',
)

# Словари-аргументы для `@marshal_with(...)`.

# Позволяет преобразовывать объекты `Account` в JSON.
account_resource_fields = {
    'id': fields.Integer,
    'firstName': fields.String(attribute='first_name'),
    'lastName': fields.String(attribute='last_name'),
    'email': fields.String,
}

# Позволяет преобразовывать объекты `Location` в JSON.
location_resource_fields = {
    'id': fields.Integer,
    'latitude': fields.Integer,
    'longitude': fields.Integer,
}

animal_type_resource_fields = {
    'id': fields.Integer,
    'type': fields.String,
}

animal_resource_fields = {
    'id': fields.Integer,
    'animalTypes': fields.List(fields.Integer, attribute='animal_types'),
    'weight': fields.Float,
    'length': fields.Float,
    'height': fields.Float,
    'gender': fields.String,
    'lifeStatus': fields.String(attribute='life_status'),
    'chippingDateTime': fields.DateTime(attribute='chipping_datetime', dt_format='iso8601'),
    'chipperId': fields.Integer(attribute='chipper_id'),
    'chippingLocationId': fields.Integer(attribute='chipping_location_id'),
    'visitedLocations': fields.List(fields.Integer, attribute='visited_locations'),
    'deathDateTime': fields.DateTime(attribute='death_datetime', dt_format='iso8601')
}


def resource_route(api: Api, urn: str) -> Callable:
    """
    Синтаксический сахар, заменяющий написание "api.add_resource(Resource, URN)"
    после определения каждого класса `Resource`.
    С помощью данной функции можно декорировать классы `Resource`,
    тем самым сразу присваивая URN'ы, которые они обрабатывают.
    """
    def class_decorator(_type: type[Resource]) -> type[Resource]:
        api.add_resource(_type, urn)
        return _type
    return class_decorator


def authorizated_account() -> Account | None:
    """
    Возвращает объект `Account` по авторизационным данным (email + пароль).
    Иначе - None.
    """
    if request.authorization is not None:
        return Account.query.filter_by(email=request.authorization['username'],
                                       password=request.authorization['password']).first()


def abort_with_forbidden_if_user_is_authorized() -> None:
    """
    Вызывает `abort` со статус-кодом = 403 в случае, если
    входящие авторизационные данные (email + пароль) верны
    и пользователь действительно авторизован.
    """
    if request.authorization is not None:
        if authorizated_account():
            abort(HTTPStatus.FORBIDDEN)


def account_registration_or_updating_or_abort_with_bad_request() -> AccountRegistrationOrUpdating | None:
    """
    Возвращает объект `AccountRegistrationOrUpdating` при успешной валидации
    входящего JSON.
    Иначе - вызывает `abort` со статус-кодом = 400.
    """
    try:
        return AccountRegistrationOrUpdating(**request.json)
    except ValidationError:
        abort(HTTPStatus.BAD_REQUEST)


def abort_with_unauthorized_if_authorization_data_is_invalid() -> Account | None:
    """
    Вызывает `abort` со статус-кодом = 401, если авторизационные данные (email + пароль)
    неверны.
    Иначе возвращает объект `Account`.
    """
    if request.authorization is not None:
        account = authorizated_account()
        if not account:
            abort(HTTPStatus.UNAUTHORIZED)
        else:
            return account


def abort_with_unauthorized_if_authorization_header_is_none() -> None:
    """
    Вызывает `abort` со статус-кодом = 401, если авторизационных данных
    нет вовсе и Header "Authorization" = None.
    """
    if request.authorization is None:
        abort(HTTPStatus.UNAUTHORIZED)


def abort_with_bad_request_if_id_is_invalid(_id: str) -> None:
    """Вызывает `abort` со статус-кодом = 400, если переданный ID невалиден."""
    if not _id:
        abort(HTTPStatus.BAD_REQUEST)

    # Если `_id` является строковым представлением числа,
    # то конвертируем его в `int`.
    # Важно: `.isdigit()` не работает для отрицательного числа в строке, например "-1".
    # То есть, возвращает `False`, хотя это число.
    # На корректном результате, к счастью, не сказывается (фича?).
    if _id.isdigit():
        _id: int = int(_id)
        # Если `_id` <= 0, то он невалиден.
        if _id <= 0:
            abort(HTTPStatus.BAD_REQUEST)
    else:
        # Если `_id` не является числом, то он невалиден.
        abort(HTTPStatus.BAD_REQUEST)


def location_creating_or_updating_or_abort_with_bad_request() -> LocationCreatingOrUpdating | None:
    try:
        return LocationCreatingOrUpdating(**request.json)
    except ValidationError:
        abort(HTTPStatus.BAD_REQUEST)


def set_attrs_of_model_instance(instance: db.Model, attrs_dict: dict[str, any]) -> None:
    for column_key, value in attrs_dict.items():
        setattr(instance, column_key, value)


def animal_type_creating_or_updating_or_abort_with_bad_request() -> AnimalTypeCreatingOrUpdating | None:
    try:
        return AnimalTypeCreatingOrUpdating(**request.json)
    except ValidationError:
        abort(HTTPStatus.BAD_REQUEST)
