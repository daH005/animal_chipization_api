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

ANY_SEARCH_PARAMS_SETS: Final = [
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
    'null',
    '0',
    0,
    '-11',
    -11,
    None,
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
]
