import unittest

from tests.baseclass import BaseTestMethod
from tests.requests_test_data import *


class TestPOST(BaseTestMethod):
    urn = 'animals/types'
    method = 'post'

    def test_201_and_animal_type_if_all_right(self) -> None:
        self._create_test_accounts()
        headers = self._headers_with_authorization(ACCOUNTS_FOR_ORM[0]['email'],
                                                   ACCOUNTS_FOR_ORM[0]['password'])

        requests_data = []
        for payload in VALID_ANIMALS_TYPES_PAYLOADS:
            requests_data.append({'json': payload})
        self._test_requests(requests_data, 201, headers, True)

    def test_400_if_type_is_invalid(self) -> None:
        self._create_test_accounts()
        headers = self._headers_with_authorization(ACCOUNTS_FOR_ORM[0]['email'],
                                                   ACCOUNTS_FOR_ORM[0]['password'])

        requests_data = []
        for _type in INVALID_STRING_VALUES:
            requests_data.append({'json': {'type': _type}})
        self._test_requests(requests_data, 400, headers)

    def test_401_if_authorization_data_is_invalid(self) -> None:
        self._test_401_if_authorization_data_is_invalid()

    def test_401_if_authorization_header_is_none(self) -> None:
        self._test_401_if_authorization_header_is_none()

    def test_409_if_type_is_taken(self) -> None:
        self._create_test_accounts()
        headers = self._headers_with_authorization(ACCOUNTS_FOR_ORM[0]['email'],
                                                   ACCOUNTS_FOR_ORM[0]['password'])
        self._create_test_animals_types()

        requests_data = []
        for payload in VALID_ANIMALS_TYPES_PAYLOADS:
            requests_data.append({'json': payload})
        self._test_requests(requests_data, 409, headers)


if __name__ == '__main__':
    unittest.main()
