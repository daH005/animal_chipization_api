import unittest

from tests.baseclass import BaseTestMethod
from tests.requests_test_data import *


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


if __name__ == '__main__':
    unittest.main()
