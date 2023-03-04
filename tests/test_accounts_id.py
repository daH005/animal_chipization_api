import unittest

from tests.baseclass import BaseTestMethod
from tests.requests_test_data import *


class TestGET(BaseTestMethod):
    method = 'get'

    def test_200_and_account_if_all_right(self) -> None:
        self._create_test_accounts()

        requests_data = []
        for i in range(len(VALID_ACCOUNTS_REGISTRATIONS_PAYLOADS)):
            requests_data.append({'urn': f'accounts/{i + 1}'})
        self._test_requests(requests_data, 200, assert_not_empty_json=True)

    def test_400_if_account_id_is_invalid(self) -> None:
        self._create_test_accounts()

        requests_data = []
        for _id in INVALID_IDS:
            requests_data.append({'urn': f'accounts/{_id}'})
        self._test_requests(requests_data, 400)

    def test_401_if_authorization_data_is_invalid(self) -> None:
        self._test_401_if_authorization_data_is_invalid('accounts/1')

    def test_404_if_account_not_found(self) -> None:
        self._create_test_accounts()

        requests_data = []
        for _id in NON_EXISTENT_IDS:
            requests_data.append({'urn': f'accounts/{_id}'})
        self._test_requests(requests_data, 404)


class TestPUT(BaseTestMethod):
    method = 'put'

    def test_200_and_account_if_all_right(self) -> None:
        self._create_test_accounts([ACCOUNTS_FOR_ORM[0]])
        headers = self._headers_with_authorization(ACCOUNTS_FOR_ORM[0]['email'],
                                                   ACCOUNTS_FOR_ORM[0]['password'])
        requests_data = []
        for payload in VALID_ACCOUNTS_REGISTRATIONS_PAYLOADS[1:]:
            requests_data.append({'urn': 'accounts/1',
                                  'json': payload,
                                  'headers': headers})
            headers = self._headers_with_authorization(payload['email'], payload['password'])
        self._test_requests(requests_data, 200, assert_not_empty_json=True)

    def test_400_if_account_id_is_invalid(self) -> None:
        self._create_test_accounts([ACCOUNTS_FOR_ORM[0]])
        headers = self._headers_with_authorization(ACCOUNTS_FOR_ORM[0]['email'],
                                                   ACCOUNTS_FOR_ORM[0]['password'])
        requests_data = []
        for _id in INVALID_IDS:
            requests_data.append({'urn': f'accounts/{_id}'})
        self._test_requests(requests_data, 400, headers)

    def _test_400_if_any_param_is_invalid(self, name: str,
                                          values: list[any],
                                          ) -> None:
        self._create_test_accounts([ACCOUNTS_FOR_ORM[0]])
        headers = self._headers_with_authorization(ACCOUNTS_FOR_ORM[0]['email'],
                                                   ACCOUNTS_FOR_ORM[0]['password'])

        requests_data = []
        for value in values:
            requests_data.append({'urn': 'accounts/1',
                                  'json': {**VALID_ACCOUNTS_REGISTRATIONS_PAYLOADS[0],
                                           name: value}})
        self._test_requests(requests_data, 400, headers)

    def test_400_if_first_name_is_invalid(self) -> None:
        self._test_400_if_any_param_is_invalid('firstName', INVALID_STRING_VALUES)

    def test_400_if_last_name_is_invalid(self) -> None:
        self._test_400_if_any_param_is_invalid('lastName', INVALID_STRING_VALUES)

    def test_400_if_email_is_invalid(self) -> None:
        self._test_400_if_any_param_is_invalid('email', INVALID_EMAILS)

    def test_400_if_password_is_invalid(self) -> None:
        self._test_400_if_any_param_is_invalid('password', INVALID_STRING_VALUES)

    def test_401_if_authorization_data_is_invalid(self) -> None:
        self._test_401_if_authorization_data_is_invalid('accounts/1')

    def test_401_if_authorization_header_is_none(self) -> None:
        self._test_401_if_authorization_header_is_none('accounts/1')

    def test_403_if_account_not_found(self) -> None:
        self._create_test_accounts([ACCOUNTS_FOR_ORM[0]])
        headers = self._headers_with_authorization(ACCOUNTS_FOR_ORM[0]['email'],
                                                   ACCOUNTS_FOR_ORM[0]['password'])

        requests_data = []
        for _id in NON_EXISTENT_IDS:
            requests_data.append({'urn': f'accounts/{_id}',
                                  'json': VALID_ACCOUNTS_REGISTRATIONS_PAYLOADS[1]})
        self._test_requests(requests_data, 403, headers)

    def test_403_if_account_does_not_belong_to_user(self) -> None:
        self._create_test_accounts()
        headers = self._headers_with_authorization(ACCOUNTS_FOR_ORM[0]['email'],
                                                   ACCOUNTS_FOR_ORM[0]['password'])

        requests_data = []
        for i in range(1, len(VALID_ACCOUNTS_REGISTRATIONS_PAYLOADS[1:]) + 1):
            requests_data.append({'urn': f'accounts/{i + 1}', 'json': VALID_ACCOUNTS_REGISTRATIONS_PAYLOADS[1]})
        self._test_requests(requests_data, 403, headers)

    def test_409_if_email_is_taken(self) -> None:
        self._create_test_accounts()
        headers = self._headers_with_authorization(ACCOUNTS_FOR_ORM[0]['email'],
                                                   ACCOUNTS_FOR_ORM[0]['password'])

        requests_data = []
        for payload in VALID_ACCOUNTS_REGISTRATIONS_PAYLOADS[1:]:
            requests_data.append({'urn': f'accounts/1', 'json': payload})
        self._test_requests(requests_data, 409, headers)


class TestDELETE(BaseTestMethod):
    method = 'delete'

    def test_200_if_all_right(self) -> None:
        self._create_test_accounts()

        requests_data = []
        for i, payload in enumerate(VALID_ACCOUNTS_REGISTRATIONS_PAYLOADS):
            requests_data.append({'urn': f'accounts/{i + 1}',
                                  'headers': self._headers_with_authorization(payload['email'],
                                                                              payload['password'])})
        self._test_requests(requests_data, 200)

    def test_400_if_account_id_is_invalid(self) -> None:
        TestPUT.test_400_if_account_id_is_invalid(self)

    def test_401_if_authorization_data_is_invalid(self) -> None:
        self._test_401_if_authorization_data_is_invalid('accounts/1')

    def test_401_if_authorization_header_is_none(self) -> None:
        self._test_401_if_authorization_header_is_none('accounts/1')

    def test_403_if_account_not_found(self) -> None:
        TestPUT.test_403_if_account_not_found(self)

    def test_403_if_account_does_not_belong_to_user(self) -> None:
        TestPUT.test_403_if_account_does_not_belong_to_user(self)


if __name__ == '__main__':
    unittest.main()
