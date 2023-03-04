import unittest
from base64 import b64encode

from webapi import app, configure_app_and_db
from webapi.config import TestConfig
from webapi.db_models import *
from tests.requests_test_data import *

__all__ = (
    'BaseTestMethod',
)

# Настраивает приложение в тестовом режиме.
# По сути, только подключается к тестовой БД.
configure_app_and_db(TestConfig)
# Объект, позволяющий отправлять запросы к приложению в рамках теста.
client = app.test_client()


class BaseTestMethod(unittest.TestCase):
    urn: str = ''
    method: str

    @classmethod
    def setUpClass(cls) -> None:
        cls.client = client

    def setUp(self) -> None:
        # Создаём временные таблицы в тестовой БД.
        db.create_all()

    def tearDown(self) -> None:
        # Закрываем сессию соединения с тестовой БД.
        db.session.remove()
        # Удаляем временные таблицы из тестовой БД.
        db.drop_all()

    @staticmethod
    def _headers_with_authorization(email: str,
                                    password: str,
                                    ) -> dict:
        auth = 'Basic ' + b64encode(f'{email}:{password}'.encode('ascii')).decode('ascii')
        return {'Authorization': auth}

    @staticmethod
    def _create_test_accounts(payloads: list[dict] | None = None) -> None:
        if not payloads:
            payloads = ACCOUNTS_FOR_ORM

        for payload in payloads:
            db.session.add(Account(**payload))
            db.session.commit()

    @staticmethod
    def _create_test_locations(lat_range=(0, 11),
                               lon_range=(0, 11),
                               ) -> None:
        for lat in range(*lat_range):
            for lon in range(*lon_range):
                db.session.add(Location(latitude=lat, longitude=lon))
                db.session.commit()

    @staticmethod
    def _create_test_animals_types(payloads: list[dict] | None = None) -> None:
        if not payloads:
            payloads = VALID_ANIMALS_TYPES_PAYLOADS

        for payload in payloads:
            db.session.add(AnimalType(**payload))
            db.session.commit()

    def _test_requests(self, requests_data: list[dict],
                       asserted_status_code: int,
                       common_headers: dict | None = None,
                       assert_not_empty_json: bool = False,
                       ) -> None:
        for i, data in enumerate(requests_data):
            with self.subTest(i=i,
                              data=dict(data),
                              common_headers=common_headers,
                              assert_not_empty_json=assert_not_empty_json):  # type: ignore
                current_urn = data.pop('urn', self.urn)
                if 'headers' not in data and common_headers:
                    data['headers'] = common_headers

                response = getattr(self.client, self.method)(current_urn, **data)  # type: ignore
                self.assertEqual(asserted_status_code, response.status_code,
                                 msg=f'Вернулся не ожидаемый статус-код (ожидался {asserted_status_code}).')  # type: ignore
                if assert_not_empty_json:
                    # Ожидаем, что ответ от сервера - содержательный.
                    self.assertTrue(response.json,
                                    msg='Ожидалось, что вернётся содержательный JSON.')  # type: ignore
                    if type(response.json) == dict:
                        self.assertNotEqual(list(response.json.keys()), ['message'],
                                            msg='Ожидалось, что вернётся содержательный JSON '
                                                '(не сообщение об ошибке).')

    def _test_401_if_authorization_data_is_invalid(self, urn: str = '') -> None:
        self._create_test_accounts()
        requests_data = []
        for email, password in INVALID_AUTHORIZATIONS:
            requests_data.append({'headers': self._headers_with_authorization(email, password)})
            if urn:
                requests_data[-1]['urn'] = urn
        self._test_requests(requests_data, 401)

    def _test_401_if_authorization_header_is_none(self, urn: str = '') -> None:
        self._create_test_accounts()
        requests_data = [{'headers': None}]
        if urn:
            requests_data[-1]['urn'] = urn
        self._test_requests(requests_data, 401)
