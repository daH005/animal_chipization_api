import unittest

from tests.baseclass import BaseTestMethod
from tests.requests_test_data import *
from tests import test_animals_types


class TestGET(BaseTestMethod):
    method = 'get'

    def test_200_and_animal_type_if_all_right(self) -> None:
        self._create_test_animals_types()

        requests_data = []
        for i in range(len(VALID_ANIMALS_TYPES_PAYLOADS)):
            requests_data.append({'urn': f'animals/types/{i + 1}'})
        self._test_requests(requests_data, 200, assert_not_empty_json=True)

    def test_400_if_animal_type_id_is_invalid(self) -> None:
        self._create_test_animals_types()

        requests_data = []
        for _id in INVALID_IDS:
            requests_data.append({'urn': f'animals/types/{_id}'})
        self._test_requests(requests_data, 400)

    def test_401_if_authorization_data_is_invalid(self) -> None:
        self._create_test_animals_types()
        self._test_401_if_authorization_data_is_invalid('animals/types/1')

    def test_404_if_animal_type_id_is_not_found(self) -> None:
        self._create_test_animals_types()

        requests_data = []
        for _id in NON_EXISTENT_IDS:
            requests_data.append({'urn': f'animals/types/{_id}'})
        self._test_requests(requests_data, 404)


class TestPUT(BaseTestMethod):
    method = 'put'

    def test_200_and_animal_type_if_all_right(self) -> None:
        self._create_test_accounts([ACCOUNTS_FOR_ORM[0]])
        headers = self._headers_with_authorization(ACCOUNTS_FOR_ORM[0]['email'],
                                                   ACCOUNTS_FOR_ORM[0]['password'])
        self._create_test_animals_types([VALID_ANIMALS_TYPES_PAYLOADS[0]])

        requests_data = []
        for payload in VALID_ANIMALS_TYPES_PAYLOADS[1:]:
            requests_data.append({'urn': 'animals/types/1',
                                  'json': payload})
        self._test_requests(requests_data, 200, headers, True)

    def test_400_if_animal_type_id_is_invalid(self) -> None:
        self._create_test_accounts([ACCOUNTS_FOR_ORM[0]])
        headers = self._headers_with_authorization(ACCOUNTS_FOR_ORM[0]['email'],
                                                   ACCOUNTS_FOR_ORM[0]['password'])
        self._create_test_animals_types()

        requests_data = []
        for _id in INVALID_IDS:
            requests_data.append({'urn': f'animals/types/{_id}'})
        self._test_requests(requests_data, 400, headers)

    def test_400_is_type_is_invalid(self) -> None:
        self._create_test_animals_types()
        self.urn = 'animals/types/1'
        test_animals_types.TestPOST.test_400_if_type_is_invalid(self)

    def test_401_if_authorization_data_is_invalid(self) -> None:
        self._create_test_animals_types()
        self._test_401_if_authorization_data_is_invalid('animals/types/1')

    def test_401_if_authorization_header_is_none(self) -> None:
        self._create_test_animals_types()
        self._test_401_if_authorization_header_is_none('animals/types/1')

    def test_404_if_animal_type_is_not_found(self) -> None:
        self._create_test_accounts([ACCOUNTS_FOR_ORM[0]])
        headers = self._headers_with_authorization(ACCOUNTS_FOR_ORM[0]['email'],
                                                   ACCOUNTS_FOR_ORM[0]['password'])
        self._create_test_animals_types([VALID_ANIMALS_TYPES_PAYLOADS[0]])

        requests_data = []
        for _id in NON_EXISTENT_IDS:
            requests_data.append({'urn': f'animals/types/{_id}',
                                  'json': VALID_ANIMALS_TYPES_PAYLOADS[1]})
        self._test_requests(requests_data, 404, headers)

    def test_409_if_type_is_taken(self) -> None:
        self._create_test_accounts()
        headers = self._headers_with_authorization(ACCOUNTS_FOR_ORM[0]['email'],
                                                   ACCOUNTS_FOR_ORM[0]['password'])
        self._create_test_animals_types()

        requests_data = []
        for payload in VALID_ANIMALS_TYPES_PAYLOADS[1:]:
            requests_data.append({'urn': 'animals/types/1',
                                  'json': payload})
        self._test_requests(requests_data, 409, headers)


class TestDELETE(BaseTestMethod):
    method = 'delete'

    def test_200_if_all_right(self) -> None:
        self._create_test_accounts([ACCOUNTS_FOR_ORM[0]])
        headers = self._headers_with_authorization(ACCOUNTS_FOR_ORM[0]['email'],
                                                   ACCOUNTS_FOR_ORM[0]['password'])
        self._create_test_animals_types()

        requests_data = []
        for i in range(len(VALID_ANIMALS_TYPES_PAYLOADS)):
            requests_data.append({'urn': f'animals/types/{i + 1}'})
        self._test_requests(requests_data, 200, headers)

    def test_400_if_animal_type_id_is_invalid(self) -> None:
        TestPUT.test_400_if_animal_type_id_is_invalid(self)

    def test_401_if_authorization_data_is_invalid(self) -> None:
        self._create_test_animals_types()
        self._test_401_if_authorization_data_is_invalid('animals/types/1')

    def test_401_if_authorization_header_is_none(self) -> None:
        self._create_test_animals_types()
        self._test_401_if_authorization_header_is_none('animals/types/1')

    def test_404_if_animal_type_is_not_found(self) -> None:
        TestPUT.test_404_if_animal_type_is_not_found(self)


if __name__ == '__main__':
    unittest.main()
