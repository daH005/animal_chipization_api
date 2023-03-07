"""
Модуль содержит модели валидации для поступающих приложению JSON'ов и GET-параметров.
"""

from pydantic import (BaseModel, validator, validate_email, Field,
                      constr, conint, conlist, confloat, )
from datetime import datetime

__all__ = ('AccountRegistrationOrUpdating',
           'AccountsSearch',
           'LocationCreatingOrUpdating',
           'AnimalTypeCreatingOrUpdating',
           'AnimalCreating',
           'AnimalUpdating',
           'AnimalsSearch',
           'AnimalTypeUpdatingForAnimal',
           'VisitedLocationsSearch',
           'VisitedLocationUpdating',
           )


class AccountRegistrationOrUpdating(BaseModel):
    first_name: constr(min_length=1, strip_whitespace=True) = Field(alias='firstName')
    last_name: constr(min_length=1, strip_whitespace=True) = Field(alias='lastName')
    email: constr(min_length=1, strip_whitespace=True)
    password: constr(min_length=1, strip_whitespace=True)

    @validator('email')
    def email_must_be_valid(cls, value: str) -> str:
        return validate_email(value)[1]


class AccountsSearch(BaseModel):
    from_: conint(ge=0) = Field(alias='from', default=0)
    size: conint(gt=0) = Field(default=10)
    first_name: str | None = Field(alias='firstName')
    last_name: str | None = Field(alias='lastName')
    email: str | None


class LocationCreatingOrUpdating(BaseModel):
    latitude: confloat(ge=-90, le=90)
    longitude: confloat(ge=-180, le=180)


class AnimalTypeCreatingOrUpdating(BaseModel):
    type: constr(min_length=1, strip_whitespace=True)


class AnimalCreating(BaseModel):
    animal_types: conlist(conint(gt=0), min_items=1) = Field(alias='animalTypes')
    weight: confloat(gt=0)
    length: confloat(gt=0)
    height: confloat(gt=0)
    gender: str
    chipper_id: conint(gt=0) = Field(alias='chipperId')
    chipping_location_id: conint(gt=0) = Field(alias='chippingLocationId')

    @validator('gender')
    def gender_value_must_be_male_or_female_or_other(cls, value: str) -> str:
        if value in ['MALE', 'FEMALE', 'OTHER']:
            return value
        else:
            raise ValueError()


class AnimalUpdating(BaseModel):
    weight: confloat(gt=0)
    length: confloat(gt=0)
    height: confloat(gt=0)
    gender: str
    life_status: str | None = Field(alias='lifeStatus')
    chipper_id: conint(gt=0) = Field(alias='chipperId')
    chipping_location_id: conint(gt=0) = Field(alias='chippingLocationId')

    @validator('life_status')
    def life_status_must_be_alive_or_dead(cls, value: str) -> str:
        if value in ['ALIVE', 'DEAD']:
            return value
        else:
            raise ValueError()

    @validator('gender')
    def gender_value_must_be_male_or_female_or_other(cls, value: str) -> str:
        if value in ['MALE', 'FEMALE', 'OTHER']:
            return value
        else:
            raise ValueError()


class AnimalsSearch(BaseModel):
    from_: conint(ge=0) = Field(alias='from', default=0)
    size: conint(gt=0) = Field(default=10)
    start_datetime: datetime | None = Field(alias='startDateTime')
    end_datetime: datetime | None = Field(alias='endDateTime')
    chipper_id: conint(gt=0) | None = Field(alias='chipperId')
    chipping_location_id: conint(gt=0) | None = Field(alias='chippingLocationId')
    life_status: str | None = Field(alias='lifeStatus')
    gender: str | None

    @validator('life_status')
    def life_status_must_be_alive_or_dead(cls, value: str) -> str:
        if value in ['ALIVE', 'DEAD']:
            return value
        else:
            raise ValueError()

    @validator('gender')
    def gender_value_must_be_male_or_female_or_other(cls, value: str) -> str:
        if value in ['MALE', 'FEMALE', 'OTHER']:
            return value
        else:
            raise ValueError()


class AnimalTypeUpdatingForAnimal(BaseModel):
    old_type_id: conint(gt=0) = Field(alias='oldTypeId')
    new_type_id: conint(gt=0) = Field(alias='newTypeId')


class VisitedLocationsSearch(BaseModel):
    from_: conint(ge=0) = Field(alias='from', default=0)
    size: conint(gt=0) = Field(default=10)
    start_datetime: datetime | None = Field(alias='startDateTime')
    end_datetime: datetime | None = Field(alias='endDateTime')


class VisitedLocationUpdating(BaseModel):
    visited_location_id: conint(gt=0) = Field(alias='visitedLocationPointId')
    location_id: conint(gt=0) = Field(alias='locationPointId')
