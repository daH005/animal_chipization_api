from typing import Final
from humps import decamelize

# Корректные JSON'ы для регистрации тестовых аккаунтов.
VALID_ACCOUNTS_REGISTRATIONS_PAYLOADS: Final = [
    {
        'firstName': 'Ivan',
        'lastName': 'Ivanov',
        'email': 'ivan.ivanov@mail.ru',
        'password': 'password'
    },
    {
        'firstName': 'Danil',
        'lastName': 'Danilov',
        'email': 'danil.danilov@yandex.ru',
        'password': '1234'
    },
    {
        'firstName': 'Admin',
        'lastName': 'Adminov',
        'email': 'admin.adminov@google.com',
        'password': 'ADMIN'
    },
    {
        'firstName': 'Test',
        'lastName': 'Testov',
        'email': 'test.testov@mail.ru',
        'password': 'test'
    },
    {
        'firstName': 'aleksandr',
        'lastName': 'aleksandrov',
        'email': 'aleks.aleksandrov@anymail.lalala',
        'password': 'aleks_hacker62'
    },
]
ACCOUNTS_FOR_ORM: Final = decamelize(VALID_ACCOUNTS_REGISTRATIONS_PAYLOADS)

INVALID_AUTHORIZATIONS: Final = [
    ('TEST_EMAIL', 'TEST_PASSWORD'),
    ('XXX', 'YYY'),
    ('1234', '5678'),
]

INVALID_STRING_VALUES: Final = [
    None,
    '',
    ' ',
    '  ',
    ' ' * 20,
]

INVALID_EMAILS: Final = [
    *INVALID_STRING_VALUES,
    'invalid_email@@ruru',
    'invalid_email@com',
]

ANY_ACCOUNTS_SEARCH_PARAMS_SETS: Final = [
    {'firstName': 'al'},
    {'lastName': 'dan'},
    {'email': 'test.testov', 'size': 15},
    {'size': 10},
    {'from': 1},
    {'firstName': 'danil', 'email': 'danil', 'size': 10},
    {'XXX': 123, 'YYY': None}
]

INVALID_FROMS: Final = [
    -10,
    '-10',
    'XXX',
    'YYY',
]

INVALID_SIZES: Final = [
    *INVALID_FROMS,
    0
]

INVALID_IDS: Final = [
    '0',
    0,
    -1,
    -2,
    '-1',
    -1000,
]

NON_EXISTENT_IDS: Final = [
    1000,
    '1000',
    1200,
    '1999',
    '9999',
    9099,
    6000,
]

VALID_LOCATIONS_PAYLOADS: Final = [
    {'latitude': 0, 'longitude': 0},
    {'latitude': -90, 'longitude': 0},
    {'latitude': 90, 'longitude': 0},
    {'latitude': 0, 'longitude': -180},
    {'latitude': 0, 'longitude': 180},
    {'latitude': -90, 'longitude': 180},
    {'latitude': 90, 'longitude': -180},
    {'latitude': -90, 'longitude': -180},
    {'latitude': 45, 'longitude': 45},
    {'latitude': 90, 'longitude': 90},
    {'latitude': -90, 'longitude': -90},
    {'latitude': 60, 'longitude': 5},
    {'latitude': 1, 'longitude': 2},
]

INVALID_LATITUDES: Final = [
    -91,
    91,
    1000,
    -1000,
    -92,
    92,
    -100,
    100,
    None,
]

INVALID_LONGITUDES = [
    -181,
    181,
    1000,
    -1000,
    -182,
    182,
    -200,
    200,
    None,
]

VALID_ANIMALS_TYPES_PAYLOADS: Final = [
    {'type': 'mammals'},
    {'type': 'fish'},
    {'type': 'air'},
    {'type': 'amphibians'},
    {'type': 'cat'},
    {'type': 'dog'},
]

VALID_ANIMALS_PAYLOADS: Final = [
    {'animalTypes': [1, 2, 3],
     'weight': 1.5,
     'length': 2.5,
     'height': 3.5,
     'gender': 'MALE',
     'chipperId': 1,
     'chippingLocationId': 1},
    {'animalTypes': [6],
     'weight': 1,
     'length': 2,
     'height': 3,
     'gender': 'FEMALE',
     'chipperId': 2,
     'chippingLocationId': 3},
    {'animalTypes': [2, 4],
     'weight': 4.7,
     'length': 1.1,
     'height': 1.2,
     'gender': 'MALE',
     'chipperId': 2,
     'chippingLocationId': 2},
    {'animalTypes': [5, 6],
     'weight': 6.7,
     'length': 1.9,
     'height': 2.3,
     'gender': 'FEMALE',
     'chipperId': 4,
     'chippingLocationId': 5},
    {'animalTypes': [2, 5],
     'weight': 14.2,
     'length': 12.5,
     'height': 7.7,
     'gender': 'OTHER',
     'chipperId': 3,
     'chippingLocationId': 7},
]
ANIMALS_FOR_ORM: Final = decamelize(VALID_ANIMALS_PAYLOADS)

INVALID_ANIMALS_TYPES: Final = [
    [0],
    [None],
    [],
    None,
    [-1],
    [-1, 0, None],
]

INVALID_NUMBERS_WITHOUT_NONE: Final = [
    0,
    -1,
    -2,
    -10,
    -1000,
]

INVALID_NUMBERS: Final = [
    *INVALID_NUMBERS_WITHOUT_NONE,
    None,
]

INVALID_GENDERS: Final = [
    'MAL',
    'FEMAL',
    '_FEMALE_',
    'OTHERR',
    'MALEE',
]

INVALID_ANIMALS_TYPES_WITH_DUPLICATES: Final = [
    [1, 1, 1],
    [1, 2, 1],
    [1, 2, 3, 1],
    [2, 2, ],
    [3, 2, 1, 4, 4],
]

NON_EXISTENT_ANIMALS_TYPES: Final = [
    [10, 20, 30],
    [1000, 10, 2],
    [1, 2, 50],
]

ANY_ANIMALS_SEARCH_PARAMS_SETS: Final = [
    {'XXX': None, 'YYY': 123},
    {'gender': 'MALE'},
    {'gender': 'FEMALE'},
    {'gender': 'OTHER'},
    {'chipperId': 1},
    {'chipperId': 2},
    {'chippingLocationId': 1},
    {'chipperId': 3, 'chippingLocationId': 7},
    {'lifeStatus': 'ALIVE'},
    {'from': 1},
    {'size': 15, 'from': 2},
    {'from': 0, 'size': 200},
    {'startDateTime': '2020-01-01T22:00:00'},
    {'endDateTime': '5020-01-01T22:00:00'},
]

INVALID_DATETIMES: Final = [
    '10.12.2004',
    '2004--12--55',
    # 1,  ToDo: Узнать допускают ли такие значения тесты от симбир
    # '1',
    # 2,
]

INVALID_LIFE_STATUTES: Final = [
    'LIVE',
    'LIFE',
    'ALIFE',
    'DEATH',
    'DEADED',
    'DED',
    'LIV',
]

VALID_ANIMALS_UPDATING_PAYLOADS: Final = [
    {'weight': 1,
     'length': 2,
     'height': 1,
     'gender': 'MALE',
     'lifeStatus': 'ALIVE',
     'chipperId': 2,
     'chippingLocationId': 2},
    {'weight': 1.1,
     'length': 2,
     'height': 1.2,
     'gender': 'FEMALE',
     'lifeStatus': 'ALIVE',
     'chipperId': 2,
     'chippingLocationId': 2},
    {'weight': 1.2,
     'length': 1.9,
     'height': 1.2,
     'gender': 'OTHER',
     'lifeStatus': 'DEAD',
     'chipperId': 1,
     'chippingLocationId': 2},
    {'weight': 1.3,
     'length': 2.1,
     'height': 1,
     'gender': 'OTHER',
     'lifeStatus': 'DEAD',
     'chipperId': 2,
     'chippingLocationId': 1},
]
