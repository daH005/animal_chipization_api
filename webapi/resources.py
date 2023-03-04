from flask import request
from flask_restful import Api, Resource, abort, marshal_with
from http import HTTPStatus
from typing import Iterable
from pydantic import ValidationError
from datetime import datetime

from webapi.db_models import *
from webapi.validation_models import *
from webapi.resources_utils import *

__all__ = (
    'api',
)

api = Api()


@resource_route(api, '/registration')
class Registration(Resource):
    """Набор обработчиков URN '/registration'."""

    @marshal_with(account_resource_fields)
    def post(self) -> tuple[Account, HTTPStatus] | None:
        """Регистрация нового аккаунта."""
        # Если пользователь авторизован, то вызовем `abort` со статус-кодом = 403.
        abort_with_forbidden_if_user_is_authorized()
        # Валидация входящего JSON. Если он невалиден, то вызовем `abort` со статус-кодом = 400.
        new_account_data = account_registration_or_updating_or_abort_with_bad_request()
        # Если email, указанный во входящем JSON уже занят, то вызовем `abort` со статус-кодом = 409.
        if Account.query.filter_by(email=new_account_data.email).first():
            abort(HTTPStatus.CONFLICT)
        else:
            # Создаём новый аккаунт и добавляем его в БД.
            new_account = Account(**new_account_data.dict())
            db.session.add(new_account)
            db.session.commit()

            # Возвращаем созданный аккаунт + статус-код = 201.
            # `@marshal_with(...)` преобразует `account` в JSON.
            return new_account, HTTPStatus.CREATED


@resource_route(api, '/accounts/<string:_id>')
class AccountsID(Resource):
    """Набор обработчиков URN '/accounts/<str:_id>'."""

    @marshal_with(account_resource_fields)
    def get(self, _id: str) -> tuple[Account, HTTPStatus] | None:
        """Выдаёт аккаунт по его ID."""
        # Если авторизационные данные (email + пароль) невалидны, то вызовем `abort` со статус-кодом = 401.
        abort_with_unauthorized_if_authorization_data_is_invalid()
        # Если входящий ID искомого аккаунта невалиден, то вызовем `abort` со статус-кодом = 400.
        abort_with_bad_request_if_id_is_invalid(_id)
        # Пробуем найти аккаунт по ID.
        found_account: Account = Account.query.filter_by(id=_id).first()
        # Если аккаунт найден, то возвращаем его + статус-код = 200.
        # В противном случае вызовем `abort` со статус-кодом = 404.
        if found_account:
            # `@marshal_with(...)` преобразует `account` в JSON.
            return found_account, HTTPStatus.OK
        else:
            return abort(HTTPStatus.NOT_FOUND)

    @marshal_with(account_resource_fields)
    def put(self, _id: str) -> tuple[Account, HTTPStatus] | None:
        """Обновляет данные аккаунта с указанным ID."""
        # Если Header "Authorization' = None, то вызовем `abort` со статус-кодом = 401.
        abort_with_unauthorized_if_authorization_header_is_none()
        # Если авторизационные данные (email + пароль) невалидны, то вызовем `abort` со статус-кодом = 401.
        authorizated_account = abort_with_unauthorized_if_authorization_data_is_invalid()
        # Если входящий ID искомого аккаунта невалиден, то вызовем `abort` со статус-кодом = 400.
        abort_with_bad_request_if_id_is_invalid(_id)
        # Валидация входящего JSON. Если он невалиден, то вызовем `abort` со статус-кодом = 400.
        account_new_data = account_registration_or_updating_or_abort_with_bad_request()

        # Пробуем найти аккаунт по ID.
        found_account: Account = Account.query.filter_by(id=_id).first()
        # Если аккаунт найден и этот аккаунт - тот же самый, под которым пользователь
        # авторизован, то продолжим обработку.
        # В противном случае вызовем `abort` со статус-кодом = 403.
        if found_account and found_account == authorizated_account:
            # Пробуем найти аккаунт с email, который указан в JSON запроса.
            account_with_auth_email = Account.query.filter_by(email=account_new_data.email).first()
            # Если такого аккаунта нет или этот аккаунт - тот же самый, под которым
            # авторизован пользователь, то продолжим обработку.
            # В противном случае вызовем `abort` со статус-кодом = 409.
            if (account_with_auth_email is None) or (account_with_auth_email == found_account):
                # Изменяем значения свойств аккаунта (экземпляра ORM-модели),
                # после чего обновляем БД.
                set_attrs_of_model_instance(found_account, account_new_data.dict())
                db.session.commit()
                # Возвращаем обновленный аккаунт и статус-код = 200.
                # `@marshal_with(...)` преобразует `account` в JSON.
                return found_account, HTTPStatus.OK
            else:
                return abort(HTTPStatus.CONFLICT)
        else:
            return abort(HTTPStatus.FORBIDDEN)

    def delete(self, _id: str) -> tuple[dict, HTTPStatus] | None:
        """Удаляет аккаунт с указанным ID."""
        # Если Header "Authorization' = None, то вызовем `abort` со статус-кодом = 401.
        abort_with_unauthorized_if_authorization_header_is_none()
        # Если авторизационные данные (email + пароль) невалидны, то вызовем `abort` со статус-кодом = 401.
        authorizated_account = abort_with_unauthorized_if_authorization_data_is_invalid()
        # Если входящий ID искомого аккаунта невалиден, то вызовем `abort` со статус-кодом = 400.
        abort_with_bad_request_if_id_is_invalid(_id)

        # Пробуем найти аккаунт по ID.
        found_account: Account = Account.query.filter_by(id=_id).first()

        # ToDo: Добавить проверку: "Аккаунт связан с животным".

        # Если аккаунт найден и этот аккаунт - тот же самый, под которым пользователь
        # авторизован, то удалим его.
        # В противном случае вызовем `abort` со статус-кодом = 403.
        if found_account and found_account == authorizated_account:
            db.session.delete(found_account)
            db.session.commit()
            return dict(), HTTPStatus.OK
        else:
            return abort(HTTPStatus.FORBIDDEN)


@resource_route(api, '/accounts/search')
class AccountsSearch(Resource):
    """Набор обработчиков URN '/accounts/search'."""

    @marshal_with(account_resource_fields)
    def get(self) -> tuple[Account, HTTPStatus] | None:
        """Производит поиск аккаунтов по параметрам."""
        # Если авторизационные данные (email + пароль) невалидны, то вызовем `abort` со статус-кодом = 401.
        abort_with_unauthorized_if_authorization_data_is_invalid()

        # Копируем GET-параметры (оборачиваем в `dict(...)`), чтобы работать с независимым объектом `dict`.
        get_params = dict(request.args)
        try:
            # Два параметра, отвечающие за срез результатов поиска.
            # Сохраняем их в переменные и удаляем из `get_params` для того,
            # что бы в нём остались только параметры, подлежащие валидации в `AccountSearch`.
            from_ = int(get_params.pop('from', 0))
            size = int(get_params.pop('size', 10))
        # `ValueError` может возникнуть в случае, если "from" или "size" не являются строковыми
        # представлениями чисел.
        # В таком случае вызовем `abort` со статус-кодом = 400.
        except ValueError:
            return abort(HTTPStatus.BAD_REQUEST)

        # Если параметры среза некорректны, то
        # вызовем `abort` со статус-кодом = 400.
        if from_ < 0 or size <= 0:
            return abort(HTTPStatus.BAD_REQUEST)

        # Формируем словарь поисковых параметров.
        # Если какой-то ожидаемый GET-параметр отсутствует, то он не добавляется в словарь поисковых параметров.
        # `AccountSearch` не обрабатывает левые GET-параметры, поэтому "SQL-инъекции" исключены.
        # `exclude_unset` = True - исключает параметры = None для того, чтобы они не участвовали в фильтрации.
        search_params = AccountSearch(**get_params).dict(exclude_unset=True)
        # Заранее подготавливаем параметры фильтрации.
        filter_args = []
        for param_name, value in search_params.items():
            # Фильтрация каждого параметра происходит без учёта регистра
            # и с учётом только части значения.
            filter_arg = getattr(Account, param_name).icontains(value)
            filter_args.append(filter_arg)

        # Производим фильтрацию по подготовленным параметрам `filter_args`;
        # Упорядочиваем список результатов в порядке возрастания "id";
        # Берём нужный кусок результатов из общего списка (производим пагинацию).
        search_results: Iterable[Account] = Account.query.filter(*filter_args).order_by('id').paginate(page=from_,
                                                                                                       per_page=size,
                                                                                                       error_out=False)
        # Преобразуем `search_results` в `list` для корректной обработки в `@marshal_with(...)`,
        # после чего возвращаем этот список + статус-код = 200.
        # `@marshal_with(...)` преобразует список объектов `Account` в JSON.
        return list(search_results), HTTPStatus.OK


@resource_route(api, '/locations')
class Locations(Resource):

    @marshal_with(location_resource_fields)
    def post(self) -> tuple[Location, HTTPStatus] | None:
        # Если Header "Authorization' = None, то вызовем `abort` со статус-кодом = 401.
        abort_with_unauthorized_if_authorization_header_is_none()
        # Если авторизационные данные (email + пароль) невалидны, то вызовем `abort` со статус-кодом = 401.
        abort_with_unauthorized_if_authorization_data_is_invalid()
        new_location_data = location_creating_or_updating_or_abort_with_bad_request()

        if Location.query.filter_by(**new_location_data.dict()).first():
            abort(HTTPStatus.CONFLICT)
        else:
            new_location = Location(**new_location_data.dict())
            db.session.add(new_location)
            db.session.commit()
            return new_location, HTTPStatus.CREATED


@resource_route(api, '/locations/<string:_id>')
class LocationsID(Resource):

    @marshal_with(location_resource_fields)
    def get(self, _id: str) -> tuple[Location, HTTPStatus] | None:
        # Если авторизационные данные (email + пароль) невалидны, то вызовем `abort` со статус-кодом = 401.
        abort_with_unauthorized_if_authorization_data_is_invalid()
        # Если входящий ID искомой точки невалиден, то вызовем `abort` со статус-кодом = 400.
        abort_with_bad_request_if_id_is_invalid(_id)

        found_location = Location.query.filter_by(id=_id).first()
        if found_location:
            return found_location, HTTPStatus.OK
        else:
            abort(HTTPStatus.NOT_FOUND)

    @marshal_with(location_resource_fields)
    def put(self, _id: str) -> tuple[Location, HTTPStatus] | None:
        # Если Header "Authorization' = None, то вызовем `abort` со статус-кодом = 401.
        abort_with_unauthorized_if_authorization_header_is_none()
        # Если авторизационные данные (email + пароль) невалидны, то вызовем `abort` со статус-кодом = 401.
        abort_with_unauthorized_if_authorization_data_is_invalid()
        # Если входящий ID искомой точки невалиден, то вызовем `abort` со статус-кодом = 400.
        abort_with_bad_request_if_id_is_invalid(_id)
        location_new_data = location_creating_or_updating_or_abort_with_bad_request()

        found_location = Location.query.filter_by(id=_id).first()
        if found_location:
            location_with_taken_coords = Location.query.filter_by(**location_new_data.dict()).first()
            if not location_with_taken_coords or location_with_taken_coords == found_location:
                set_attrs_of_model_instance(found_location, location_new_data.dict())
                db.session.commit()
                return found_location, HTTPStatus.OK
            else:
                abort(HTTPStatus.CONFLICT)
        else:
            abort(HTTPStatus.NOT_FOUND)

    def delete(self, _id: str) -> tuple[dict, HTTPStatus] | None:
        # Если Header "Authorization' = None, то вызовем `abort` со статус-кодом = 401.
        abort_with_unauthorized_if_authorization_header_is_none()
        # Если авторизационные данные (email + пароль) невалидны, то вызовем `abort` со статус-кодом = 401.
        abort_with_unauthorized_if_authorization_data_is_invalid()
        # Если входящий ID искомой точки невалиден, то вызовем `abort` со статус-кодом = 400.
        abort_with_bad_request_if_id_is_invalid(_id)

        found_location = Location.query.filter_by(id=_id).first()

        # ToDo: Добавить проверку: точка связана с животным.

        if found_location:
            db.session.delete(found_location)
            db.session.commit()
            return dict(), HTTPStatus.OK
        else:
            abort(HTTPStatus.NOT_FOUND)


@resource_route(api, '/animals/types')
class AnimalsTypes(Resource):

    @marshal_with(animal_type_resource_fields)
    def post(self) -> tuple[AnimalType, HTTPStatus] | None:
        # Если Header "Authorization' = None, то вызовем `abort` со статус-кодом = 401.
        abort_with_unauthorized_if_authorization_header_is_none()
        # Если авторизационные данные (email + пароль) невалидны, то вызовем `abort` со статус-кодом = 401.
        abort_with_unauthorized_if_authorization_data_is_invalid()
        new_animal_type_data = animal_type_creating_or_updating_or_abort_with_bad_request()

        if AnimalType.query.filter_by(type=new_animal_type_data.type).first():
            abort(HTTPStatus.CONFLICT)
        else:
            new_animal_type = AnimalType(**new_animal_type_data.dict())
            db.session.add(new_animal_type)
            db.session.commit()
            return new_animal_type, HTTPStatus.CREATED


@resource_route(api, '/animals/types/<string:_id>')
class AnimalsTypesID(Resource):

    @marshal_with(animal_type_resource_fields)
    def get(self, _id: str) -> tuple[AnimalType, HTTPStatus] | None:
        # Если авторизационные данные (email + пароль) невалидны, то вызовем `abort` со статус-кодом = 401.
        abort_with_unauthorized_if_authorization_data_is_invalid()
        # Если входящий ID искомого типа животного невалиден, то вызовем `abort` со статус-кодом = 400.
        abort_with_bad_request_if_id_is_invalid(_id)

        found_animal_type = AnimalType.query.filter_by(id=_id).first()
        if found_animal_type:
            return found_animal_type, HTTPStatus.OK
        else:
            abort(HTTPStatus.NOT_FOUND)

    @marshal_with(animal_type_resource_fields)
    def put(self, _id: str) -> tuple[AnimalType, HTTPStatus] | None:
        # Если Header "Authorization' = None, то вызовем `abort` со статус-кодом = 401.
        abort_with_unauthorized_if_authorization_header_is_none()
        # Если авторизационные данные (email + пароль) невалидны, то вызовем `abort` со статус-кодом = 401.
        abort_with_unauthorized_if_authorization_data_is_invalid()
        # Если входящий ID искомого типа животного невалиден, то вызовем `abort` со статус-кодом = 400.
        abort_with_bad_request_if_id_is_invalid(_id)
        animal_type_new_data = animal_type_creating_or_updating_or_abort_with_bad_request()

        found_animal_type = AnimalType.query.filter_by(id=_id).first()
        if found_animal_type:
            animal_type_with_current_type = AnimalType.query.filter_by(type=animal_type_new_data.type).first()
            if not animal_type_with_current_type or animal_type_with_current_type == found_animal_type:
                set_attrs_of_model_instance(found_animal_type, animal_type_new_data.dict())
                db.session.commit()
                return found_animal_type, HTTPStatus.OK
            else:
                abort(HTTPStatus.CONFLICT)
        else:
            abort(HTTPStatus.NOT_FOUND)

    def delete(self, _id: str) -> tuple[dict, HTTPStatus] | None:
        # Если Header "Authorization' = None, то вызовем `abort` со статус-кодом = 401.
        abort_with_unauthorized_if_authorization_header_is_none()
        # Если авторизационные данные (email + пароль) невалидны, то вызовем `abort` со статус-кодом = 401.
        abort_with_unauthorized_if_authorization_data_is_invalid()
        # Если входящий ID искомого типа животного невалиден, то вызовем `abort` со статус-кодом = 400.
        abort_with_bad_request_if_id_is_invalid(_id)

        # ToDo: Добавить проверку: Есть животные с типом с typeId.

        found_animal_type = AnimalType.query.filter_by(id=_id).first()
        if found_animal_type:
            db.session.delete(found_animal_type)
            db.session.commit()
            return dict(), HTTPStatus.OK
        else:
            abort(HTTPStatus.NOT_FOUND)


@resource_route(api, '/animals')
class Animals(Resource):

    @marshal_with(animal_resource_fields)
    def post(self) -> tuple[Animal, HTTPStatus] | None:
        # Если Header "Authorization' = None, то вызовем `abort` со статус-кодом = 401.
        abort_with_unauthorized_if_authorization_header_is_none()
        # Если авторизационные данные (email + пароль) невалидны, то вызовем `abort` со статус-кодом = 401.
        abort_with_unauthorized_if_authorization_data_is_invalid()

        try:
            new_animal_data = AnimalCreating(**request.json)
        except ValidationError:
            return abort(HTTPStatus.BAD_REQUEST)

        if len(new_animal_data.animal_types) != len(set(new_animal_data.animal_types)):
            abort(HTTPStatus.CONFLICT)

        for type_id in new_animal_data.animal_types:
            if not AnimalType.query.filter_by(id=type_id).first():
                abort(HTTPStatus.NOT_FOUND)

        if not Account.query.filter_by(id=new_animal_data.chipper_id).first():
            abort(HTTPStatus.NOT_FOUND)
        elif not Location.query.filter_by(id=new_animal_data.chipping_location_id).first():
            abort(HTTPStatus.NOT_FOUND)
        else:
            new_animal_data_dict = new_animal_data.dict()
            new_animal_data_dict['life_status'] = 'ALIVE'
            new_animal_data_dict['chipping_datetime'] = datetime.now()

            new_animal = Animal(**new_animal_data_dict)
            db.session.add(new_animal)
            db.session.commit()
            return new_animal, HTTPStatus.CREATED
