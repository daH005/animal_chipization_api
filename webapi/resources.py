from flask_restful import Api, Resource, abort, marshal_with
from http import HTTPStatus
from typing import Iterable
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

    @marshal_with(account_resource_fields)  # Преобразование возвращаемого объекта `Account` в JSON.
    @request_json_validation(AccountRegistrationOrUpdating)  # Валидация входящего JSON.
    def post(self, valid_json_data: AccountRegistrationOrUpdating,
             ) -> tuple[Account, HTTPStatus] | None:
        """Регистрирует новый аккаунт."""
        # Проверка: пользователь не должен быть авторизован.
        if get_authorized_account():
            abort(HTTPStatus.FORBIDDEN)

        # Проверка: email не должен быть занят.
        if Account.query.filter_by(email=valid_json_data.email).first():
            abort(HTTPStatus.CONFLICT)
        else:
            # Создаём новый аккаунт в БД.
            new_account = Account(**valid_json_data.dict())
            db.session.add(new_account)
            db.session.commit()
            return new_account, HTTPStatus.CREATED


@resource_route(api, '/accounts/<signed_int:_id>')
class AccountsID(Resource):

    @marshal_with(account_resource_fields)  # Преобразование возвращаемого объекта `Account` в JSON.
    @authorization_data_must_be_valid_or_none  # Проверка авторизационных данных: либо их нет, либо они корректны.
    @id_validation  # Валидация входящего ID аккаунта.
    def get(self, _id: int) -> tuple[Account, HTTPStatus] | None:
        """Выдаёт аккаунт по его ID."""
        found_account: Account = Account.query.filter_by(id=_id).first()
        if found_account:
            return found_account, HTTPStatus.OK
        else:
            return abort(HTTPStatus.NOT_FOUND)

    @marshal_with(account_resource_fields)  # Преобразование возвращаемого объекта `Account` в JSON.
    @authorization_required(pass_account=True)  # Проверка авторизации (она обязательна).
    @id_validation  # Валидация входящего ID аккаунта.
    @request_json_validation(AccountRegistrationOrUpdating)  # Валидация входящего JSON.
    def put(self, _id: int,
            authorized_account: Account,
            valid_json_data: AccountRegistrationOrUpdating,
            ) -> tuple[Account, HTTPStatus] | None:
        """Обновляет данные аккаунта с указанным ID."""
        found_account: Account = Account.query.filter_by(id=_id).first()
        # Проверка: обновлять можно только свой аккаунт.
        if found_account and found_account == authorized_account:
            # Пробуем найти аккаунт с email, который указан в `valid_json_data`.
            account_with_auth_email = Account.query.filter_by(email=valid_json_data.email).first()
            # Если такого аккаунта нет или этот аккаунт - тот же самый, под которым
            # авторизован пользователь, то продолжим обработку.
            if (account_with_auth_email is None) or (account_with_auth_email == found_account):
                # Обновляем аккаунт в БД.
                set_attrs_of_model_instance(found_account, valid_json_data.dict())
                db.session.commit()
                return found_account, HTTPStatus.OK
            else:
                return abort(HTTPStatus.CONFLICT)
        else:
            return abort(HTTPStatus.FORBIDDEN)

    @authorization_required(pass_account=True)  # Проверка авторизации (она обязательна).
    @id_validation  # Валидация входящего ID аккаунта.
    def delete(self, _id: int,
               authorized_account: Account,
               ) -> tuple[dict, HTTPStatus] | None:
        """Удаляет аккаунт с указанным ID."""
        found_account: Account = Account.query.filter_by(id=_id).first()

        # ToDo: Добавить проверку: "Аккаунт связан с животным".

        # Проверка: удалять можно только свой аккаунт.
        if found_account and found_account == authorized_account:
            # Удаляем аккаунт из БД.
            db.session.delete(found_account)
            db.session.commit()
            return dict(), HTTPStatus.OK
        else:
            return abort(HTTPStatus.FORBIDDEN)


@resource_route(api, '/accounts/search')
class AccountsSearch(Resource):

    @marshal_with(account_resource_fields)  # Преобразование возвращаемого списка объектов `Account` в JSON.
    @order_by_id_and_cut_results  # Упорядочивание результатов поиска по ID + срез.
    @authorization_data_must_be_valid_or_none  # Проверка авторизационных данных: либо их нет, либо они корректны.
    @request_args_validation(AccountSearch)  # Валидация входящих GET-параметров.
    def get(self,
            valid_args_data: AccountSearch,
            ) -> tuple[Iterable[Account], int, int]:
        """Производит поиск аккаунтов по параметрам."""
        # Формируем параметры фильтрации для ORM.
        filter_args = []
        for param_name, value in valid_args_data.dict(exclude={'from_', 'size'},
                                                      exclude_none=True,
                                                      ).items():
            # Фильтрация каждого параметра происходит без учёта регистра
            # и с учётом только части значения.
            filter_arg = getattr(Account, param_name).icontains(value)
            filter_args.append(filter_arg)

        return (Account.query.filter(*filter_args),
                valid_args_data.from_, valid_args_data.size)


@resource_route(api, '/locations')
class Locations(Resource):

    @marshal_with(location_resource_fields)  # Преобразование возвращаемого объекта `Location` в JSON.
    @authorization_required()  # Проверка авторизации (она обязательна).
    @request_json_validation(LocationCreatingOrUpdating)  # Валидация входящего JSON.
    def post(self, valid_json_data: LocationCreatingOrUpdating,
             ) -> tuple[Location, HTTPStatus] | None:
        """Создаёт новую точку локации."""
        # Проверка: указанные координаты должны быть свободны.
        if Location.query.filter_by(**valid_json_data.dict()).first():
            abort(HTTPStatus.CONFLICT)
        else:
            # Создаём новую точку в БД.
            new_location = Location(**valid_json_data.dict())
            db.session.add(new_location)
            db.session.commit()
            return new_location, HTTPStatus.CREATED


@resource_route(api, '/locations/<signed_int:_id>')
class LocationsID(Resource):

    @marshal_with(location_resource_fields)  # Преобразование возвращаемого объекта `Location` в JSON.
    @authorization_data_must_be_valid_or_none  # Проверка авторизационных данных: либо их нет, либо они корректны.
    @id_validation  # Валидация входящего ID локации.
    def get(self, _id: int) -> tuple[Location, HTTPStatus] | None:
        """Выдаёт точку локации по её ID."""
        found_location = Location.query.filter_by(id=_id).first()
        if found_location:
            return found_location, HTTPStatus.OK
        else:
            abort(HTTPStatus.NOT_FOUND)

    @marshal_with(location_resource_fields)  # Преобразование возвращаемого объекта `Location` в JSON.
    @authorization_required()  # Проверка авторизации (она обязательна).
    @id_validation  # Валидация входящего ID локации.
    @request_json_validation(LocationCreatingOrUpdating)  # Валидация входящего JSON.
    def put(self, _id: int,
            valid_json_data: LocationCreatingOrUpdating,
            ) -> tuple[Location, HTTPStatus] | None:
        """Обновляет координаты локации с указанным ID."""
        found_location = Location.query.filter_by(id=_id).first()
        if found_location:
            # Пробуем найти локацию с указанными в `valid_json_data` координатами.
            location_with_taken_coords = Location.query.filter_by(**valid_json_data.dict()).first()
            # Если такой локации нет, либо это та же самая локация, которая обновляется,
            # то продолжим обработку.
            if not location_with_taken_coords or location_with_taken_coords == found_location:
                # Обновляем точку в БД.
                set_attrs_of_model_instance(found_location, valid_json_data.dict())
                db.session.commit()
                return found_location, HTTPStatus.OK
            else:
                abort(HTTPStatus.CONFLICT)
        else:
            abort(HTTPStatus.NOT_FOUND)

    @authorization_required()  # Проверка авторизации (она обязательна).
    @id_validation  # Валидация входящего ID локации.
    def delete(self, _id: int) -> tuple[dict, HTTPStatus] | None:
        """Удаляет точку локации с указанным ID."""
        found_location = Location.query.filter_by(id=_id).first()

        # ToDo: Добавить проверку: точка связана с животным.

        if found_location:
            # Удаляем точку локации из БД.
            db.session.delete(found_location)
            db.session.commit()
            return dict(), HTTPStatus.OK
        else:
            abort(HTTPStatus.NOT_FOUND)


@resource_route(api, '/animals/types')
class AnimalsTypes(Resource):

    @marshal_with(animal_type_resource_fields)  # Преобразование возвращаемого объекта `AnimalType` в JSON.
    @authorization_required()  # Проверка авторизации (она обязательна).
    @request_json_validation(AnimalTypeCreatingOrUpdating)  # Валидация входящего JSON.
    def post(self, valid_json_data: AnimalTypeCreatingOrUpdating,
             ) -> tuple[AnimalType, HTTPStatus] | None:
        """Создаёт новый тип животного."""
        # Проверка: указанный тип животного должен быть свободен.
        if AnimalType.query.filter_by(type=valid_json_data.type).first():
            abort(HTTPStatus.CONFLICT)
        else:
            # Создаём новый тип животного в БД.
            new_animal_type = AnimalType(**valid_json_data.dict())
            db.session.add(new_animal_type)
            db.session.commit()
            return new_animal_type, HTTPStatus.CREATED


@resource_route(api, '/animals/types/<signed_int:_id>')
class AnimalsTypesID(Resource):

    @marshal_with(animal_type_resource_fields)  # Преобразование возвращаемого объекта `AnimalType` в JSON.
    @authorization_data_must_be_valid_or_none  # Проверка авторизационных данных: либо их нет, либо они корректны.
    @id_validation  # Валидация входящего ID типа животного.
    def get(self, _id: int) -> tuple[AnimalType, HTTPStatus] | None:
        """Выдаёт тип животного по его ID."""
        found_animal_type = AnimalType.query.filter_by(id=_id).first()
        if found_animal_type:
            return found_animal_type, HTTPStatus.OK
        else:
            abort(HTTPStatus.NOT_FOUND)

    @marshal_with(animal_type_resource_fields)  # Преобразование возвращаемого объекта `AnimalType` в JSON.
    @authorization_required()  # Проверка авторизации (она обязательна).
    @id_validation  # Валидация входящего ID типа животного.
    @request_json_validation(AnimalTypeCreatingOrUpdating)  # Валидация входящего JSON.
    def put(self, _id: int, valid_json_data: AnimalTypeCreatingOrUpdating,
            ) -> tuple[AnimalType, HTTPStatus] | None:
        """Обновляет тип животного с указанным ID."""
        found_animal_type = AnimalType.query.filter_by(id=_id).first()
        if found_animal_type:
            # Пробуем найти уже существующий указанный тип животного.
            animal_type_with_taken_type = AnimalType.query.filter_by(type=valid_json_data.type).first()
            # Если такого нет, либо он тот же самый, который обновляется,
            # то продолжим обработку.
            if not animal_type_with_taken_type or animal_type_with_taken_type == found_animal_type:
                # Обновляем тип животного в БД.
                set_attrs_of_model_instance(found_animal_type, valid_json_data.dict())
                db.session.commit()
                return found_animal_type, HTTPStatus.OK
            else:
                abort(HTTPStatus.CONFLICT)
        else:
            abort(HTTPStatus.NOT_FOUND)

    @authorization_required()  # Проверка авторизации (она обязательна).
    @id_validation  # Валидация входящего ID типа животного.
    def delete(self, _id: int) -> tuple[dict, HTTPStatus] | None:
        """Удаляет тип животного с указанным ID."""
        # ToDo: Добавить проверку: Есть животные с типом с typeId.

        found_animal_type = AnimalType.query.filter_by(id=_id).first()
        if found_animal_type:
            # Удаляем тип животного из БД.
            db.session.delete(found_animal_type)
            db.session.commit()
            return dict(), HTTPStatus.OK
        else:
            abort(HTTPStatus.NOT_FOUND)


@resource_route(api, '/animals')
class Animals(Resource):

    @marshal_with(animal_resource_fields)  # Преобразование возвращаемого объекта `Animal` в JSON.
    @authorization_required()  # Проверка авторизации (она обязательна).
    @request_json_validation(AnimalCreating)  # Валидация входящего JSON.
    def post(self, valid_json_data: AnimalCreating,
             ) -> tuple[Animal, HTTPStatus] | None:
        """Создаёт новое животное."""
        # Проверка списка "animalTypes" на наличие дубликатов.
        if len(valid_json_data.animal_types) != len(set(valid_json_data.animal_types)):
            abort(HTTPStatus.CONFLICT)

        # Проверка: каждый ID в "animalTypes" должен существовать.
        for type_id in valid_json_data.animal_types:
            if not AnimalType.query.filter_by(id=type_id).first():
                abort(HTTPStatus.NOT_FOUND)

        # Проверка: аккаунт с ID = "chipperId" должен существовать.
        if not Account.query.filter_by(id=valid_json_data.chipper_id).first():
            abort(HTTPStatus.NOT_FOUND)
        # Проверка: локация с ID = "chippingLocationId" должна существовать.
        elif not Location.query.filter_by(id=valid_json_data.chipping_location_id).first():
            abort(HTTPStatus.NOT_FOUND)
        else:
            new_animal_data_dict = valid_json_data.dict()
            # Указываем текущие дату и время как дату и время создания (чипирования) животного.
            new_animal_data_dict['chipping_datetime'] = datetime.now()

            # Добавляем животное в БД.
            new_animal = Animal(**new_animal_data_dict)
            db.session.add(new_animal)
            db.session.commit()
            return new_animal, HTTPStatus.CREATED


@resource_route(api, '/animals/<signed_int:_id>')
class AnimalsID(Resource):

    @marshal_with(animal_resource_fields)  # Преобразование возвращаемого объекта `Animal` в JSON.
    @authorization_data_must_be_valid_or_none  # Проверка авторизационных данных: либо их нет, либо они корректны.
    @id_validation  # Валидация входящего ID животного.
    def get(self, _id: int) -> tuple[Animal, HTTPStatus] | None:
        """Выдаёт животное по его ID."""
        found_animal = Animal.query.filter_by(id=_id).first()
        if found_animal:
            return found_animal, HTTPStatus.OK
        else:
            abort(HTTPStatus.NOT_FOUND)

    @marshal_with(animal_resource_fields)  # Преобразование возвращаемого объекта `Animal` в JSON.
    @authorization_required()  # Проверка авторизации (она обязательна).
    @id_validation  # Валидация входящего ID животного.
    @request_json_validation(AnimalUpdating)  # Валидация входящего JSON.
    def put(self, _id: int,
            valid_json_data: AnimalUpdating,
            ) -> tuple[Animal, HTTPStatus] | None:
        """Обновляет данные животного с указанным ID."""
        # Проверка: аккаунт с ID = "chipperId" должен существовать.
        if not Account.query.filter_by(id=valid_json_data.chipper_id).first():
            abort(HTTPStatus.NOT_FOUND)
        # Проверка: локация с ID = "chippingLocationId" должна существовать.
        elif not Location.query.filter_by(id=valid_json_data.chipping_location_id).first():
            abort(HTTPStatus.NOT_FOUND)

        # ToDo: Добавить проверку: Новая точка чипирования совпадает с первой посещенной точкой локации.

        found_animal: Animal = Animal.query.filter_by(id=_id).first()
        if found_animal:
            new_animal_data_dict = valid_json_data.dict()
            # Проверка: нельзя сменять статус "DEAD" на "ALIVE".
            if found_animal.life_status == 'DEAD' and valid_json_data.life_status == 'ALIVE':
                abort(HTTPStatus.BAD_REQUEST)
            # Если мы сменяем "ALIVE" на "DEAD", то указываем текущие дату и время
            # как время смерти животного.
            if found_animal.life_status == 'ALIVE' and valid_json_data.life_status == 'DEAD':
                new_animal_data_dict['deathDateTime'] = datetime.now()

            # Обновляем животное в БД.
            set_attrs_of_model_instance(found_animal, new_animal_data_dict)
            db.session.commit()
            return found_animal, HTTPStatus.OK
        else:
            abort(HTTPStatus.NOT_FOUND)

    @authorization_required()  # Проверка авторизации (она обязательна).
    @id_validation  # Валидация входящего ID животного.
    def delete(self, _id: int) -> tuple[dict, HTTPStatus] | None:
        """Удаляет животное с указанным ID."""
        # ToDo: Добавить проверку: Животное покинуло локацию чипирования, при этом
        #  есть другие посещенные точки

        found_animal = Animal.query.filter_by(id=_id).first()
        if found_animal:
            # Удаляем животное из БД.
            db.session.delete(found_animal)
            db.session.commit()
            return dict(), HTTPStatus.OK
        else:
            abort(HTTPStatus.NOT_FOUND)


@resource_route(api, '/animals/search')
class AnimalsSearch(Resource):

    @marshal_with(animal_resource_fields)  # Преобразование возвращаемого списка объектов `Animal` в JSON.
    @order_by_id_and_cut_results  # Упорядочивание результатов по ID + срез.
    @authorization_data_must_be_valid_or_none  # Проверка авторизационных данных: либо их нет, либо они корректны.
    @request_args_validation(AnimalSearch)  # Валидация входящих GET-параметров.
    def get(self, valid_args_data: AnimalSearch,
            ) -> tuple[Iterable[Animal], int, int]:
        """Производит поиск животных по параметрам."""
        # Формируем параметры фильтрации для ORM.
        filter_args = []
        # Обрабатываем "startDateTime" и "endDateTime" отдельно от остальных параметров.
        if valid_args_data.start_datetime:
            # Дата от (включительно).
            filter_args.append(Animal.chipping_datetime >= valid_args_data.start_datetime)
        if valid_args_data.end_datetime:
            # Дата до (включительно).
            filter_args.append(Animal.chipping_datetime <= valid_args_data.end_datetime)
        for param_name, value in valid_args_data.dict(exclude={'from_', 'size',
                                                               'start_datetime', 'end_datetime'},
                                                      exclude_none=True,
                                                      ).items():
            # Остальные значения должны быть строго равны указанным.
            filter_arg = getattr(Animal, param_name) == value
            filter_args.append(filter_arg)

        return (Animal.query.filter(*filter_args),
                valid_args_data.from_, valid_args_data.size)
