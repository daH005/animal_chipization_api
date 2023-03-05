import unittest

from tests.baseclass import BaseTestMethod
from tests.requests_test_data import *


class TestGET(BaseTestMethod):
    urn = 'accounts/search'
    method = 'get'

    def test_200_and_accounts_if_all_right(self) -> None:
        self._create_test_accounts()

        requests_data = []
        for params in ANY_ACCOUNTS_SEARCH_PARAMS_SETS:
            requests_data.append({'query_string': params})
        self._test_requests(requests_data, 200, assert_not_empty_json=True)

    def _test_400_if_size_or_from_are_invalid(self, name: str,
                                              values: list[any],
                                              ) -> None:
        requests_data = []
        for value in values:
            requests_data.append({'query_string': {name: value}})
        self._test_requests(requests_data, 400)

    def test_400_if_from_is_invalid(self) -> None:
        self._test_400_if_size_or_from_are_invalid('from', INVALID_FROMS)

    def test_400_if_size_is_invalid(self) -> None:
        self._test_400_if_size_or_from_are_invalid('size', INVALID_SIZES)

    def test_401_if_authorization_data_is_invalid(self) -> None:
        self._test_401_if_authorization_data_is_invalid()


if __name__ == '__main__':
    unittest.main()
