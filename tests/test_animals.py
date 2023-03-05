import unittest

from tests.baseclass import BaseTestMethod
from tests.requests_test_data import *


class TestPOST(BaseTestMethod):
    urn = 'animals'
    method = 'post'

    def test_201_and_animal_if_all_right(self) -> None:
        self._create_test_accounts()
        headers = self._headers_with_authorization(ACCOUNTS_FOR_ORM[0]['email'],
                                                   ACCOUNTS_FOR_ORM[0]['password'])
        self._create_test_locations()
        self._create_test_animals_types()

        requests_data = []
        for payload in VALID_ANIMALS_PAYLOADS:
            requests_data.append({'json': payload})
        self._test_requests(requests_data, 201, headers, True)

    def _test_status_code_if_any_param_is_invalid(self, name: str,
                                                  values: list[any],
                                                  asserted_status_code: int = 400,
                                                  ) -> None:
        self._create_test_accounts()
        headers = self._headers_with_authorization(ACCOUNTS_FOR_ORM[0]['email'],
                                                   ACCOUNTS_FOR_ORM[0]['password'])
        self._create_test_locations()
        self._create_test_animals_types()

        requests_data = []
        for value in values:
            requests_data.append({'json': {**VALID_ANIMALS_PAYLOADS[0],
                                           name: value}})
        self._test_requests(requests_data, asserted_status_code, headers)

    def test_400_if_animal_types_is_invalid(self) -> None:
        self._test_status_code_if_any_param_is_invalid('animalTypes', INVALID_ANIMALS_TYPES)

    def test_400_if_weight_is_invalid(self) -> None:
        self._test_status_code_if_any_param_is_invalid('weight', INVALID_NUMBERS)

    def test_400_if_length_is_invalid(self) -> None:
        self._test_status_code_if_any_param_is_invalid('length', INVALID_NUMBERS)

    def test_400_if_height_is_invalid(self) -> None:
        self._test_status_code_if_any_param_is_invalid('height', INVALID_NUMBERS)

    def test_400_if_gender_is_invalid(self) -> None:
        self._test_status_code_if_any_param_is_invalid('gender', INVALID_GENDERS)

    def test_400_if_chipper_id_is_invalid(self) -> None:
        self._test_status_code_if_any_param_is_invalid('chipperId', INVALID_NUMBERS)

    def test_400_if_chipping_location_id_is_invalid(self) -> None:
        self._test_status_code_if_any_param_is_invalid('chippingLocationId', INVALID_NUMBERS)

    def test_401_if_authorization_data_is_invalid(self) -> None:
        self._test_401_if_authorization_data_is_invalid()

    def test_401_if_authorization_header_is_none(self) -> None:
        self._test_401_if_authorization_header_is_none()

    def test_404_if_animal_type_is_not_found(self) -> None:
        self._test_status_code_if_any_param_is_invalid('animalTypes', NON_EXISTENT_ANIMALS_TYPES, 404)

    def test_404_if_chipper_id_is_not_found(self) -> None:
        self._test_status_code_if_any_param_is_invalid('chipperId', NON_EXISTENT_IDS, 404)

    def test_404_if_chipping_location_id_is_not_found(self) -> None:
        self._test_status_code_if_any_param_is_invalid('chippingLocationId', NON_EXISTENT_IDS, 404)

    def test_409_if_animal_type_contains_duplicates(self) -> None:
        self._test_status_code_if_any_param_is_invalid('animalTypes', INVALID_ANIMALS_TYPES_WITH_DUPLICATES, 409)


if __name__ == '__main__':
    unittest.main()
