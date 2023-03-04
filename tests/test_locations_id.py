import unittest

from tests.baseclass import BaseTestMethod
from tests.requests_test_data import *


class TestGET(BaseTestMethod):
    method = 'get'

    def test_200_and_location_if_all_right(self) -> None:
        self._create_test_locations()
        requests_data = []
        for i in range(11 * 11):
            requests_data.append({'urn': f'locations/{i + 1}'})
        self._test_requests(requests_data, 200, assert_not_empty_json=True)

    def test_400_if_location_id_is_invalid(self) -> None:
        self._create_test_locations()

        requests_data = []
        for _id in INVALID_IDS:
            requests_data.append({'urn': f'locations/{_id}'})
        self._test_requests(requests_data, 400)

    def test_401_if_authorization_data_is_invalid(self) -> None:
        self._create_test_locations()
        self._test_401_if_authorization_data_is_invalid('locations/1')

    def test_404_if_location_is_not_found(self) -> None:
        self._create_test_locations()

        requests_data = []
        for _id in NON_EXISTENT_IDS:
            requests_data.append({'urn': f'locations/{_id}'})
        self._test_requests(requests_data, 404)


class TestPUT(BaseTestMethod):
    method = 'put'

    def test_200_and_location_if_all_right(self) -> None:
        self._create_test_accounts()
        headers = self._headers_with_authorization(ACCOUNTS_FOR_ORM[0]['email'],
                                                   ACCOUNTS_FOR_ORM[0]['password'])

        self._create_test_locations((0, 1), (0, 1))

        requests_data = []
        for payload in VALID_LOCATIONS_PAYLOADS:
            requests_data.append({'urn': 'locations/1', 'json': payload})
        self._test_requests(requests_data, 200, headers, True)

    def test_400_if_location_id_is_invalid(self) -> None:
        self._create_test_accounts()
        headers = self._headers_with_authorization(ACCOUNTS_FOR_ORM[0]['email'],
                                                   ACCOUNTS_FOR_ORM[0]['password'])

        requests_data = []
        for _id in INVALID_IDS:
            requests_data.append({'urn': f'locations/{_id}'})
        self._test_requests(requests_data, 400, headers)

    def _test_400_if_coord_is_invalid(self, coord_name: str,
                                      values: list[any],
                                      ) -> None:
        self._create_test_accounts()
        headers = self._headers_with_authorization(ACCOUNTS_FOR_ORM[0]['email'],
                                                   ACCOUNTS_FOR_ORM[0]['password'])
        self._create_test_locations()

        requests_data = []
        for value in values:
            _json = {'latitude': 0, 'longitude': 0, coord_name: value}
            requests_data.append({'urn': 'locations/1', 'json': _json})
        self._test_requests(requests_data, 400, headers)

    def test_400_if_latitude_is_invalid(self) -> None:
        self._test_400_if_coord_is_invalid('latitude', INVALID_LATITUDES)

    def test_400_if_longitude_is_invalid(self) -> None:
        self._test_400_if_coord_is_invalid('longitude', INVALID_LONGITUDES)

    def test_401_if_authorization_data_is_invalid(self) -> None:
        self._test_401_if_authorization_data_is_invalid('locations/1')

    def test_401_if_authorization_header_is_none(self) -> None:
        self._test_401_if_authorization_header_is_none('locations/1')

    def test_404_if_location_is_not_found(self) -> None:
        self._create_test_accounts()
        headers = self._headers_with_authorization(ACCOUNTS_FOR_ORM[0]['email'],
                                                   ACCOUNTS_FOR_ORM[0]['password'])
        self._create_test_locations()

        requests_data = []
        for _id in NON_EXISTENT_IDS:
            requests_data.append({'urn': f'locations/{_id}',
                                  'json': VALID_LOCATIONS_PAYLOADS[0]})
        self._test_requests(requests_data, 404, headers)

    def test_409_if_latitude_or_longitude_are_taken(self) -> None:
        self._create_test_accounts()
        headers = self._headers_with_authorization(ACCOUNTS_FOR_ORM[0]['email'],
                                                   ACCOUNTS_FOR_ORM[0]['password'])
        self._create_test_locations()

        requests_data = []
        for lat in range(1, 11):
            for lon in range(0, 11):
                requests_data.append({'urn': 'locations/1',
                                      'json': {'latitude': lat,
                                               'longitude': lon}})
        self._test_requests(requests_data, 409, headers)


class TestDELETE(BaseTestMethod):
    method = 'delete'

    def test_200_if_all_right(self) -> None:
        self._create_test_accounts()
        headers = self._headers_with_authorization(ACCOUNTS_FOR_ORM[0]['email'],
                                                   ACCOUNTS_FOR_ORM[0]['password'])
        self._create_test_locations()

        _id = 1
        requests_data = []
        for lat in range(0, 11):
            for lon in range(0, 11):
                requests_data.append({'urn': f'locations/{_id}'})
                _id += 1
        self._test_requests(requests_data, 200, headers)

    def test_400_if_location_id_is_invalid(self) -> None:
        TestPUT.test_400_if_location_id_is_invalid(self)

    def test_401_if_authorization_data_is_invalid(self) -> None:
        self._test_401_if_authorization_data_is_invalid('locations/1')

    def test_401_if_authorization_header_is_none(self) -> None:
        self._test_401_if_authorization_header_is_none('locations/1')

    def test_404_if_location_is_not_found(self) -> None:
        TestPUT.test_404_if_location_is_not_found(self)


if __name__ == '__main__':
    unittest.main()
