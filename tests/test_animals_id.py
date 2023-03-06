import unittest

from tests.baseclass import BaseTestMethod
from tests.requests_test_data import *
from tests import test_animals


class TestGET(BaseTestMethod):
    method = 'get'

    def test_200_and_animal_if_all_right(self) -> None:
        self._create_test_locations()
        self._create_test_animals_types()
        self._create_test_animals()

        requests_data = []
        for i in range(len(VALID_ANIMALS_PAYLOADS)):
            requests_data.append({'urn': f'animals/{i + 1}'})
        self._test_requests(requests_data, 200, assert_not_empty_json=True)

    def test_400_if_animal_id_is_invalid(self) -> None:
        self._create_test_locations()
        self._create_test_animals_types()
        self._create_test_animals()

        requests_data = []
        for _id in INVALID_IDS:
            requests_data.append({'urn': f'animals/{_id}'})
        self._test_requests(requests_data, 400)

    def test_401_if_authorization_data_is_invalid(self) -> None:
        self._create_test_locations()
        self._create_test_animals_types()
        self._create_test_animals()
        self._test_401_if_authorization_data_is_invalid('animals/1')

    def test_404_if_animal_is_not_found(self) -> None:
        self._create_test_locations()
        self._create_test_animals_types()
        self._create_test_animals()

        requests_data = []
        for _id in NON_EXISTENT_IDS:
            requests_data.append({'urn': f'animals/{_id}'})
        self._test_requests(requests_data, 404)


class TestPUT(BaseTestMethod):
    method = 'put'

    def test_200_and_animal_if_all_right(self) -> None:
        self._create_test_accounts()
        self._create_test_locations()
        self._create_test_animals_types()
        self._create_test_animals([ANIMALS_FOR_ORM[0]])
        headers = self._headers_with_authorization(ACCOUNTS_FOR_ORM[0]['email'],
                                                   ACCOUNTS_FOR_ORM[0]['password'])

        requests_data = []
        for payload in VALID_ANIMALS_UPDATING_PAYLOADS:
            requests_data.append({'urn': 'animals/1',
                                  'json': payload})
        self._test_requests(requests_data, 200, headers, True)

    def test_400_if_animal_id_is_invalid(self) -> None:
        self._create_test_accounts()
        self._create_test_locations()
        self._create_test_animals_types()
        self._create_test_animals()
        headers = self._headers_with_authorization(ACCOUNTS_FOR_ORM[0]['email'],
                                                   ACCOUNTS_FOR_ORM[0]['password'])

        requests_data = []
        for _id in INVALID_IDS:
            requests_data.append({'urn': f'animals/{_id}',
                                  'json': VALID_ANIMALS_UPDATING_PAYLOADS[0]})
        self._test_requests(requests_data, 400, headers)

    # def _test_status_code_if_any_param_is_invalid(self) -> None:
    #     test_animals.TestPOST._test
    # def test_400_if_weight_is_invalid(self) -> None:
    #     self.urn = 'animals/1'
    #     test_animals.TestPOST.test_400_if_weight_is_invalid(self)


if __name__ == '__main__':
    unittest.main()
