import unittest

from tests.baseclass import BaseTestMethod
from tests.requests_test_data import *


class TestPOST(BaseTestMethod):
    urn = 'locations'
    method = 'post'

    def test_201_and_location_if_all_right(self) -> None:
        self._create_test_accounts()
        headers = self._headers_with_authorization(ACCOUNTS_FOR_ORM[0]['email'],
                                                   ACCOUNTS_FOR_ORM[0]['password'])

        requests_data = []
        for payload in VALID_LOCATIONS_PAYLOADS:
            requests_data.append({'json': payload})
        self._test_requests(requests_data, 201, headers, True)

    def _test_400_if_coord_is_invalid(self, coord_name: str,
                                      values: list[any],
                                      ) -> None:
        self._create_test_accounts()
        headers = self._headers_with_authorization(ACCOUNTS_FOR_ORM[0]['email'],
                                                   ACCOUNTS_FOR_ORM[0]['password'])
        requests_data = []
        for value in values:
            _json = {'latitude': 0, 'longitude': 0, coord_name: value}
            requests_data.append({'json': _json})
        self._test_requests(requests_data, 400, headers)

    def test_400_if_latitude_is_invalid(self) -> None:
        self._test_400_if_coord_is_invalid('latitude', INVALID_LATITUDES)

    def test_400_if_longitude_is_invalid(self) -> None:
        self._test_400_if_coord_is_invalid('longitude', INVALID_LONGITUDES)

    def test_401_if_authorization_data_is_invalid(self) -> None:
        self._test_401_if_authorization_data_is_invalid()

    def test_401_if_authorization_header_is_none(self) -> None:
        self._test_401_if_authorization_header_is_none()

    def test_409_if_latitude_and_longitude_are_taken(self) -> None:
        self._create_test_accounts()
        headers = self._headers_with_authorization(ACCOUNTS_FOR_ORM[0]['email'],
                                                   ACCOUNTS_FOR_ORM[0]['password'])
        self._create_test_locations()
        requests_data = []
        for lat in range(0, 11):
            for lon in range(0, 11):
                requests_data.append({'json': {'latitude': lat,
                                               'longitude': lon}})
        self._test_requests(requests_data, 409, headers)


if __name__ == '__main__':
    unittest.main()
