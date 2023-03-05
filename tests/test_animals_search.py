import unittest

from tests.baseclass import BaseTestMethod
from tests.requests_test_data import *
from tests import test_accounts_search


class TestGET(BaseTestMethod):
    urn = 'animals/search'
    method = 'get'

    def test_200_and_animals_if_all_right(self) -> None:
        self._create_test_accounts()
        self._create_test_locations()
        self._create_test_animals_types()
        self._create_test_animals()

        requests_data = []
        for params in ANY_ANIMALS_SEARCH_PARAMS_SETS:
            requests_data.append({'query_string': params})
        self._test_requests(requests_data, 200, assert_not_empty_json=True)

    def _test_400_if_size_or_from_are_invalid(self, name: str,
                                              values: list[any],
                                              ) -> None:

        test_accounts_search.TestGET._test_400_if_size_or_from_are_invalid(self, name, values)

    def test_400_if_from_is_invalid(self) -> None:
        self._create_test_accounts()
        self._create_test_locations()
        self._create_test_animals_types()
        self._create_test_animals()
        test_accounts_search.TestGET.test_400_if_from_is_invalid(self)

    def test_400_if_size_is_invalid(self) -> None:
        test_accounts_search.TestGET.test_400_if_size_is_invalid(self)

    def _test_400_if_datetime_is_invalid(self, name: str,
                                         values: list[any],
                                         ) -> None:
        self._create_test_accounts()
        self._create_test_locations()
        self._create_test_animals_types()
        self._create_test_animals()

        requests_data = []
        for value in values:
            requests_data.append({'query_string': {**ANY_ANIMALS_SEARCH_PARAMS_SETS[0],
                                                   name: value}})
        self._test_requests(requests_data, 400)

    def test_400_if_start_datetime_is_invalid(self) -> None:
        self._test_400_if_datetime_is_invalid('startDateTime', INVALID_DATETIMES)

    def test_400_if_end_datetime_is_invalid(self) -> None:
        self._test_400_if_datetime_is_invalid('endDateTime', INVALID_DATETIMES)

    def test_400_if_chipper_id_is_invalid(self) -> None:
        self._test_400_if_size_or_from_are_invalid('chipperId', INVALID_NUMBERS_WITHOUT_NONE)

    def test_400_if_chipping_location_id_is_invalid(self) -> None:
        self._test_400_if_size_or_from_are_invalid('chippingLocationId', INVALID_NUMBERS_WITHOUT_NONE)

    def test_400_if_life_status_is_invalid(self) -> None:
        self._test_400_if_size_or_from_are_invalid('lifeStatus', INVALID_LIFE_STATUTES)

    def test_400_if_gender_is_invalid(self) -> None:
        self._test_400_if_size_or_from_are_invalid('gender', INVALID_GENDERS)

    def test_401_if_authorization_data_is_invalid(self) -> None:
        self._test_401_if_authorization_data_is_invalid()


if __name__ == '__main__':
    unittest.main()
