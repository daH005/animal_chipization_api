import pydantic
from flask import request
from flask_restful import abort, fields, Api, Resource
from http import HTTPStatus
from pydantic import ValidationError
from typing import Callable
from functools import wraps

from webapi.db_models import *

__all__ = (
    'account_resource_fields',
    'location_resource_fields',
    'animal_type_resource_fields',
    'animal_resource_fields',
    'resource_route',
    'get_authorized_account',
    'set_attrs_of_model_instance',
    'authorization_data_must_be_valid_or_none',
    'authorization_required',
    'id_validation',
    'request_json_validation',
    'request_args_validation',
    'order_by_id_and_cut_results',
)

# Словари-аргументы для `@marshal_with(...)`.

# Для объектов `Account`.
account_resource_fields = {
    'id': fields.Integer,
    'firstName': fields.String(attribute='first_name'),
    'lastName': fields.String(attribute='last_name'),
    'email': fields.String,
}

# Для объектов `Location`.
location_resource_fields = {
    'id': fields.Integer,
    'latitude': fields.Integer,
    'longitude': fields.Integer,
}

# Для объектов `AnimalType`.
animal_type_resource_fields = {
    'id': fields.Integer,
    'type': fields.String,
}

# Для объектов `Animal`.
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
    тем самым сразу присваивая им URN'ы, которые они обрабатывают.
    """
    def class_decorator(_type: type[Resource]) -> type[Resource]:
        api.add_resource(_type, urn)
        return _type
    return class_decorator


def get_authorized_account() -> Account | None:
    """
    Возвращает объект `Account` по авторизационным данным (email + пароль).
    Иначе - None.
    """
    if request.authorization is not None:
        return Account.query.filter_by(email=request.authorization['username'],
                                       password=request.authorization['password']).first()


def authorization_data_must_be_valid_or_none(method: Callable) -> Callable:
    @wraps(method)
    def wrapper(*args, **kwargs):
        if request.authorization is not None and not get_authorized_account():
            abort(HTTPStatus.UNAUTHORIZED)
        return method(*args, **kwargs)
    return wrapper


def authorization_required(pass_account: bool = False) -> Callable:
    def decorator(method: Callable) -> Callable:
        @wraps(method)
        def wrapper(*args, **kwargs):
            if not request.authorization:
                abort(HTTPStatus.UNAUTHORIZED)
            authorized_account = get_authorized_account()
            if not authorized_account:
                abort(HTTPStatus.UNAUTHORIZED)

            if pass_account:
                kwargs['authorized_account'] = authorized_account
            return method(*args, **kwargs)
        return wrapper
    return decorator


def id_validation(method: Callable) -> Callable:
    @wraps(method)
    def wrapper(*args, **kwargs):
        if kwargs['_id'] <= 0:
            abort(HTTPStatus.BAD_REQUEST)
        return method(*args, **kwargs)
    return wrapper


def request_json_validation(model: type[pydantic.BaseModel]) -> Callable:
    def decorator(method: Callable) -> Callable:
        @wraps(method)
        def wrapper(*args, **kwargs):
            try:
                data = model(**request.json)
            except ValidationError:
                return abort(HTTPStatus.BAD_REQUEST)
            kwargs['valid_json_data'] = data
            return method(*args, **kwargs)
        return wrapper
    return decorator


def request_args_validation(model: type[pydantic.BaseModel]) -> Callable:
    def decorator(method: Callable) -> Callable:
        @wraps(method)
        def wrapper(*args, **kwargs):
            try:
                data = model(**request.args)
            except ValidationError:
                return abort(HTTPStatus.BAD_REQUEST)
            kwargs['valid_args_data'] = data
            return method(*args, **kwargs)
        return wrapper
    return decorator


def order_by_id_and_cut_results(method: Callable) -> Callable:
    @wraps(method)
    def wrapper(*args, **kwargs):
        results, from_, size = method(*args, **kwargs)
        return list(results.order_by('id'))[from_:from_ + size], HTTPStatus.OK
    return wrapper


def set_attrs_of_model_instance(instance: db.Model, attrs_dict: dict[str, any]) -> None:
    for column_key, value in attrs_dict.items():
        setattr(instance, column_key, value)
