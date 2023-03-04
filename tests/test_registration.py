import unittest

from tests.baseclass import BaseTestMethod
from tests.requests_test_data import *


class TestPOST(BaseTestMethod):
    urn = 'registration'
    method = 'post'

    def test_201_and_account_if_all_right(self) -> None:
        requests_data = []
        for payload in VALID_ACCOUNTS_REGISTRATIONS_PAYLOADS:
            requests_data.append({'json': payload})
        self._test_requests(requests_data, 201, assert_not_empty_json=True)

    def _test_400_if_any_param_is_invalid(self, name: str,
                                          values: list[any],
                                          ) -> None:
        requests_data = []
        for value in values:
            requests_data.append({'json': {**VALID_ACCOUNTS_REGISTRATIONS_PAYLOADS[0],
                                           name: value}})
        self._test_requests(requests_data, 400)

    def test_400_if_first_name_is_invalid(self) -> None:
        self._test_400_if_any_param_is_invalid('firstName', INVALID_STRING_VALUES)

    def test_400_if_last_name_is_invalid(self) -> None:
        self._test_400_if_any_param_is_invalid('lastName', INVALID_STRING_VALUES)

    def test_400_if_email_is_invalid(self) -> None:
        self._test_400_if_any_param_is_invalid('email', INVALID_EMAILS)

    def test_400_if_password_is_invalid(self) -> None:
        self._test_400_if_any_param_is_invalid('password', INVALID_STRING_VALUES)

    def test_403_if_user_is_authorizated(self) -> None:
        self._create_test_accounts([ACCOUNTS_FOR_ORM[0]])
        headers = self._headers_with_authorization(ACCOUNTS_FOR_ORM[0]['email'],
                                                   ACCOUNTS_FOR_ORM[0]['password'])
        requests_data = []
        for payload in VALID_ACCOUNTS_REGISTRATIONS_PAYLOADS[1:]:
            requests_data.append({'json': payload})
        self._test_requests(requests_data, 403, headers)

    def test_409_if_email_is_taken(self) -> None:
        self._create_test_accounts()
        requests_data = []
        for payload in VALID_ACCOUNTS_REGISTRATIONS_PAYLOADS:
            requests_data.append({'json': payload})
        self._test_requests(requests_data, 409)


if __name__ == '__main__':
    unittest.main()
