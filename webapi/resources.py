from flask_restful import Api, Resource, abort, marshal_with
from http import HTTPStatus
from typing import Iterable
from datetime import datetime, timezone
from sqlalchemy import or_ as sql_or

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
        if not Account.query.filter_by(email=valid_json_data.email).first():
            # Создаём новый аккаунт в БД.
            new_account = Account(**valid_json_data.dict())
            db.session.add(new_account)
            db.session.commit()
            return new_account, HTTPStatus.CREATED
        else:
            abort(HTTPStatus.CONFLICT)


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
        # Проверка: удалять можно только свой аккаунт.
        if found_account and found_account == authorized_account:
            # Проверка: нельзя удалять аккаунт, который связан с животным.
            if Animal.query.filter_by(chipper_id=found_account.id).first():
                abort(HTTPStatus.BAD_REQUEST)

            # Удаляем аккаунт из БД.
            db.session.delete(found_account)
            db.session.commit()
            return dict(), HTTPStatus.OK
        else:
            return abort(HTTPStatus.FORBIDDEN)


@resource_route(api, '/accounts/search')
class AccountsSearch(Resource):

    @marshal_with(account_resource_fields)  # Преобразование возвращаемого списка объектов `Account` в JSON.
    @cut_results  # Срез результатов поиска.
    @authorization_data_must_be_valid_or_none  # Проверка авторизационных данных: либо их нет, либо они корректны.
    @request_args_validation(AccountsSearch)  # Валидация входящих GET-параметров.
    def get(self,
            valid_args_data: AccountsSearch,
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

        return (Account.query.filter(*filter_args).order_by('id'),
                valid_args_data.from_, valid_args_data.size)


@resource_route(api, '/locations')
class Locations(Resource):

    @marshal_with(location_resource_fields)  # Преобразование возвращаемого объекта `Location` в JSON.
    @authorization_required()  # Проверка авторизации (она обязательна).
    @request_json_validation(LocationCreatingOrUpdating)  # Валидация входящего JSON.
    def post(self, valid_json_data: LocationCreatingOrUpdating,
             ) -> tuple[Location, HTTPStatus] | None:
        """Создаёт новую точку локации."""
        # Проверка: указанные координаты не должны быть заняты другой локацией.
        if not Location.query.filter_by(**valid_json_data.dict()).first():
            # Создаём новую точку в БД.
            new_location = Location(**valid_json_data.dict())
            db.session.add(new_location)
            db.session.commit()
            return new_location, HTTPStatus.CREATED
        else:
            abort(HTTPStatus.CONFLICT)


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
                # Обновляем точку локации в БД.
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
        if found_location:
            # Проверка: нельзя удалять точку локации, связанную с животным.
            if (VisitedLocation.query.filter_by(location_id=found_location.id).first() or
                Animal.query.filter_by(chipping_location_id=found_location.id).first()):
                abort(HTTPStatus.BAD_REQUEST)

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
        if not AnimalType.query.filter_by(type=valid_json_data.type).first():
            # Создаём новый тип животного в БД.
            new_animal_type = AnimalType(**valid_json_data.dict())
            db.session.add(new_animal_type)
            db.session.commit()
            return new_animal_type, HTTPStatus.CREATED
        else:
            abort(HTTPStatus.CONFLICT)


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
        found_animal_type = AnimalType.query.filter_by(id=_id).first()
        if found_animal_type:
            # Проверка: нельзя удалять тип, если он есть у хотя бы одного животного.
            if Animal.query.filter(Animal.animal_types.contains([_id])).first():
                abort(HTTPStatus.BAD_REQUEST)

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
            new_animal_data_dict['chipping_datetime'] = datetime.now(timezone.utc)

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

        found_animal: Animal = Animal.query.filter_by(id=_id).first()
        if found_animal:
            # Проверка: новая точка чипирования не должна совпадать с первой посещённой.
            if len(found_animal.visited_locations) > 0:
                if valid_json_data.chipping_location_id == VisitedLocation.query.filter_by(
                        id=found_animal.visited_locations[0]).first().location_id:
                    abort(HTTPStatus.BAD_REQUEST)
            new_animal_data_dict = valid_json_data.dict()
            # Проверка: нельзя сменять статус "DEAD" на "ALIVE".
            if found_animal.life_status == 'DEAD' and valid_json_data.life_status == 'ALIVE':
                abort(HTTPStatus.BAD_REQUEST)
            # Если мы сменяем "ALIVE" на "DEAD", то указываем текущие дату и время
            # как дату и время смерти животного.
            if found_animal.life_status == 'ALIVE' and valid_json_data.life_status == 'DEAD':
                new_animal_data_dict['death_datetime'] = datetime.now(timezone.utc)

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
        found_animal = Animal.query.filter_by(id=_id).first()
        if found_animal:
            # Проверка: для удаления животное должно находиться в точке чипирования.
            if len(found_animal.visited_locations) > 0:
                if VisitedLocation.query.filter_by(
                        id=found_animal.visited_locations[-1]).first().location_id != found_animal.chipping_location_id:
                    abort(HTTPStatus.BAD_REQUEST)

            # Удаляем животное из БД.
            db.session.delete(found_animal)
            db.session.commit()
            return dict(), HTTPStatus.OK
        else:
            abort(HTTPStatus.NOT_FOUND)


@resource_route(api, '/animals/search')
class AnimalsSearch(Resource):

    @marshal_with(animal_resource_fields)  # Преобразование возвращаемого списка объектов `Animal` в JSON.
    @cut_results  # Срез результатов поиска.
    @authorization_data_must_be_valid_or_none  # Проверка авторизационных данных: либо их нет, либо они корректны.
    @request_args_validation(AnimalsSearch)  # Валидация входящих GET-параметров.
    def get(self, valid_args_data: AnimalsSearch,
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

        return (Animal.query.filter(*filter_args).order_by('id'),
                valid_args_data.from_, valid_args_data.size)


@resource_route(api, '/animals/<signed_int:animal_id>/types/<signed_int:animal_type_id>')
class AnimalsIDTypesID(Resource):

    @marshal_with(animal_resource_fields)  # Преобразование возвращаемого объекта `Animal` в JSON.
    @authorization_required()  # Проверка авторизации (она обязательна).
    @ids_validation('animal_id', 'animal_type_id')  # Валидация входящих ID животного и его типа.
    def post(self, animal_id: int, animal_type_id: int) -> tuple[Animal, HTTPStatus] | None:
        """Добавляем тип с указанным ID животному с указанным ID."""
        found_animal: Animal = Animal.query.filter_by(id=animal_id).first()
        # Проверка: животное с указанным ID должно существовать в БД.
        if not found_animal:
            abort(HTTPStatus.NOT_FOUND)
        # Проверка: тип животного с указанным ID должен существовать в БД.
        if not AnimalType.query.filter_by(id=animal_type_id).first():
            abort(HTTPStatus.NOT_FOUND)
        # Проверка: указанного ID типа животного не должно быть в "animalTypes" животного.
        if animal_type_id in found_animal.animal_types:
            abort(HTTPStatus.CONFLICT)

        # Добавляем новый тип животному и обновляем БД.
        found_animal.animal_types = [*found_animal.animal_types, animal_type_id]
        db.session.commit()
        return found_animal, HTTPStatus.CREATED

    @marshal_with(animal_resource_fields)  # Преобразование возвращаемого объекта `Animal` в JSON.
    @authorization_required()  # Проверка авторизации (она обязательна).
    @ids_validation('animal_id', 'animal_type_id')  # Валидация входящих ID животного и его типа.
    def delete(self, animal_id: int, animal_type_id: int) -> tuple[dict, HTTPStatus] | None:
        """Удаляет тип с указанным ID у животного с указанным ID."""
        found_animal: Animal = Animal.query.filter_by(id=animal_id).first()
        # Проверка: животное с указанным ID должно существовать в БД.
        if not found_animal:
            abort(HTTPStatus.NOT_FOUND)
        # Проверка: тип животного с указанным ID должен существовать в БД.
        if not AnimalType.query.filter_by(id=animal_type_id).first():
            abort(HTTPStatus.NOT_FOUND)
        # Проверка: указанный ID типа животного должен быть в "animalTypes" животного.
        if animal_type_id not in found_animal.animal_types:
            abort(HTTPStatus.NOT_FOUND)
        # Проверка: мы не можем удалить тип, если у животного он один.
        if found_animal.animal_types == [animal_type_id]:
            abort(HTTPStatus.BAD_REQUEST)

        # Удаляем тип у животного и обновляем БД.
        updated_animal_types = list(found_animal.animal_types)
        updated_animal_types.remove(animal_type_id)
        found_animal.animal_types = updated_animal_types
        db.session.commit()
        return found_animal, HTTPStatus.OK


@resource_route(api, '/animals/<signed_int:_id>/types')
class AnimalsIDTypes(Resource):

    @marshal_with(animal_resource_fields)  # Преобразование возвращаемого объекта `Animal` в JSON.
    @authorization_required()  # Проверка авторизации (она обязательна).
    @id_validation  # Валидация входящего ID животного.
    @request_json_validation(AnimalTypeUpdatingForAnimal)  # Валидация входящего JSON.
    def put(self, _id: int,
            valid_json_data: AnimalTypeUpdatingForAnimal,
            ) -> tuple[Animal, HTTPStatus] | None:
        """Обновляет тип у животного с указанным ID."""
        found_animal: Animal = Animal.query.filter_by(id=_id).first()
        # Проверка: животное с указанным ID должно существовать в БД.
        if not found_animal:
            abort(HTTPStatus.NOT_FOUND)
        # Проверка: старый и новый типы должны существовать в БД.
        if (not AnimalType.query.filter_by(id=valid_json_data.old_type_id).first() or
            not AnimalType.query.filter_by(id=valid_json_data.new_type_id).first()):
            abort(HTTPStatus.NOT_FOUND)
        # Проверка: старый тип должен быть в списке "animalTypes".
        if valid_json_data.old_type_id not in found_animal.animal_types:
            abort(HTTPStatus.NOT_FOUND)
        # Проверка: нового типа не должно быть в списке "animalTypes".
        if valid_json_data.new_type_id in found_animal.animal_types:
            abort(HTTPStatus.CONFLICT)

        # Обновляем тип у животного.
        updated_animal_types = list(found_animal.animal_types)
        updated_animal_types.remove(valid_json_data.old_type_id)
        updated_animal_types.append(valid_json_data.new_type_id)
        found_animal.animal_types = updated_animal_types
        db.session.commit()
        return found_animal, HTTPStatus.OK


@resource_route(api, '/animals/<signed_int:animal_id>/locations/<signed_int:location_id>')
class AnimalsIDLocationsID(Resource):

    @marshal_with(visited_location_resource_fields)  # Преобразование возвращаемого объекта `VisitedLocation` в JSON.
    @authorization_required()  # Проверка авторизации (она обязательна).
    @ids_validation('animal_id', 'location_id')  # Валидация входящих ID животного и точки локации.
    def post(self, animal_id: int, location_id: int) -> tuple[VisitedLocation, HTTPStatus] | None:
        """Добавляет животному посещённую точку локации."""
        found_animal: Animal = Animal.query.filter_by(id=animal_id).first()
        # Проверка: животное с указанным ID должно существовать в БД.
        if not found_animal:
            abort(HTTPStatus.NOT_FOUND)
        # Проверка: локация с указанным ID должна существовать в БД.
        if not Location.query.filter_by(id=location_id).first():
            abort(HTTPStatus.NOT_FOUND)
        # Проверка: нельзя добавить новую посещённую точку умершему животному.
        if found_animal.life_status == 'DEAD':
            abort(HTTPStatus.BAD_REQUEST)
        # Проверка: первая посещённая точка не должна быть равна точке чипирования.
        if not found_animal.visited_locations and location_id == found_animal.chipping_location_id:
            abort(HTTPStatus.BAD_REQUEST)
        # Проверка: новая точка не должна быть равна точке, в которой животное уже находится.
        if found_animal.visited_locations:
            if VisitedLocation.query.filter_by(id=found_animal.visited_locations[-1]).first().location_id == location_id:
                abort(HTTPStatus.BAD_REQUEST)

        # Добавляем новую посещённую точку в БД и указываем её для животного.
        new_visited_location = VisitedLocation(visit_datetime=datetime.now(timezone.utc),
                                               location_id=location_id)
        db.session.add(new_visited_location)
        db.session.commit()
        found_animal.visited_locations = [*found_animal.visited_locations, new_visited_location.id]
        db.session.commit()
        return new_visited_location, HTTPStatus.CREATED

    @authorization_required()  # Проверка авторизации (она обязательна).
    @ids_validation('animal_id', 'location_id')  # Валидация входящих ID животного и точки локации посещённой животным.
    def delete(self, animal_id: int, location_id: int) -> tuple[dict, HTTPStatus] | None:
        """Удаляет посещённую точку у животного."""
        # Здесь используется ID посещённой точки, а не обычной точки локации.
        # Во избежание путаницы переименовал ссылку.
        visited_location_id = location_id

        found_animal: Animal = Animal.query.filter_by(id=animal_id).first()
        # Проверка: животное с указанным ID должно существовать в БД.
        if not found_animal:
            abort(HTTPStatus.NOT_FOUND)
        # Проверка: посещённая точка с указанным ID должна существовать в БД.
        found_visited_location: VisitedLocation = VisitedLocation.query.filter_by(id=visited_location_id).first()
        if not found_visited_location:
            abort(HTTPStatus.NOT_FOUND)
        # Проверка: посещённая точка должна быть в списке "visitedLocations".
        if visited_location_id not in found_animal.visited_locations:
            abort(HTTPStatus.NOT_FOUND)

        # Удаляем посещённую точку из БД и из "visitedLocations" животного.
        new_visited_locations = list(found_animal.visited_locations)
        new_visited_locations.remove(visited_location_id)
        if len(new_visited_locations) > 0:
            # Если после удаления, 0-я в списке точка равна точке чипирования, то удалим и её.
            if VisitedLocation.query.filter_by(id=new_visited_locations[0]).first().location_id == found_animal.chipping_location_id:
                del new_visited_locations[0]
        found_animal.visited_locations = new_visited_locations
        db.session.commit()
        db.session.delete(found_visited_location)
        db.session.commit()
        return dict(), HTTPStatus.OK


@resource_route(api, '/animals/<signed_int:_id>/locations')
class AnimalsIDLocations(Resource):

    @marshal_with(visited_location_resource_fields)  # Преобразование возвращаемого списка объектов `VisitedLocation` в JSON.
    @cut_results  # Срез результатов поиска.
    @authorization_data_must_be_valid_or_none  # Проверка авторизационных данных: либо они корректны, либо их нет.
    @id_validation  # Валидация входящего ID животного.
    @request_args_validation(VisitedLocationsSearch)  # Валидация входящих GET-параметров.
    def get(self, _id: int,
            valid_args_data: VisitedLocationsSearch,
            ) -> tuple[list[VisitedLocation], int, int] | None:
        """Выдаёт список посещённых животным точек по параметрам (диапазону даты и времени)."""
        found_animal: Animal = Animal.query.filter_by(id=_id).first()
        # Проверка: животное с указанным ID должно существовать в БД.
        if not found_animal:
            abort(HTTPStatus.NOT_FOUND)

        # Если список "visitedLocations" пуст, то соответственно вернём пустой список.
        if not found_animal.visited_locations:
            return [], valid_args_data.from_, valid_args_data.size

        # Параметры фильтрации для отбора из БД посещённых точек, указанных в "visitedLocations" у животного.
        visited_locations_filter_args = [VisitedLocation.id == __id for __id in found_animal.visited_locations]
        # Отдельно формируем параметры для фильтрации по дате и времени.
        datetime_filter_args = []
        if valid_args_data.start_datetime:
            # Дата от (включительно).
            datetime_filter_args.append(VisitedLocation.visit_datetime >= valid_args_data.start_datetime)
            # Дата до (включительно).
        if valid_args_data.end_datetime:
            datetime_filter_args.append(VisitedLocation.visit_datetime <= valid_args_data.end_datetime)

        found_visited_locations = VisitedLocation.query.filter(sql_or(*visited_locations_filter_args)).filter(*datetime_filter_args)
        return (found_visited_locations.order_by('visit_datetime'),
                valid_args_data.from_,
                valid_args_data.size)

    @marshal_with(visited_location_resource_fields)  # Преобразование возвращаемого объекта `VisitedLocation` в JSON.
    @authorization_required()  # Проверка авторизации (она обязательна).
    @id_validation  # Валидация входящего ID животного.
    @request_json_validation(VisitedLocationUpdating)  # Валидация входящего JSON.
    def put(self, _id: int,
            valid_json_data: VisitedLocationUpdating,
            ) -> tuple[VisitedLocation, HTTPStatus] | None:
        """Обновляет посещённую животным точку."""
        found_animal: Animal = Animal.query.filter_by(id=_id).first()
        # Проверка: животное с указанным ID должно существовать в БД.
        if not found_animal:
            abort(HTTPStatus.NOT_FOUND)
        # Проверка: обновляемая посещённая точка должна быть в списке "visitedLocations" животного.
        if valid_json_data.visited_location_id not in found_animal.visited_locations:
            abort(HTTPStatus.NOT_FOUND)
        # Проверка: заменяемая точка локации должна существовать в БД.
        if not Location.query.filter_by(id=valid_json_data.location_id).first():
            abort(HTTPStatus.NOT_FOUND)
        # Проверка: обновляемая посещённая точка должна существовать в БД.
        found_visited_location: VisitedLocation = VisitedLocation.query.filter_by(id=valid_json_data.visited_location_id).first()
        if not found_visited_location:
            abort(HTTPStatus.NOT_FOUND)
        # Проверка: если обновляется первая точка, то она не должна быть равная точке чипирования.
        if (found_animal.visited_locations.index(found_visited_location.id) == 0 and
            valid_json_data.location_id == found_animal.chipping_location_id):
            abort(HTTPStatus.BAD_REQUEST)
        # Проверка: нельзя заменить точку локации на саму себя.
        if found_visited_location.location_id == valid_json_data.location_id:
            abort(HTTPStatus.BAD_REQUEST)

        if len(found_animal.visited_locations) > 1:
            # Проверка: новая точка локации не должна быть такой же, как предыдущая добавленная.
            _index = found_animal.visited_locations.index(valid_json_data.visited_location_id)
            if _index != len(found_animal.visited_locations) - 1:
                if VisitedLocation.query.filter_by(id=found_animal.visited_locations[_index + 1]).first().location_id == valid_json_data.location_id:
                    abort(HTTPStatus.BAD_REQUEST)
            # Проверка: новая точка локации не должна быть такой же, как последующая добавленная.
            if _index != 0:
                if VisitedLocation.query.filter_by(
                        id=found_animal.visited_locations[_index - 1]).first().location_id == valid_json_data.location_id:
                    abort(HTTPStatus.BAD_REQUEST)
        # Обновляем посещённую точку локации.
        found_visited_location.location_id = valid_json_data.location_id
        db.session.commit()
        return found_visited_location, HTTPStatus.OK
