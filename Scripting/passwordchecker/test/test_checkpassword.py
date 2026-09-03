import hashlib
import sys
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import pytest

sys.path.insert(0, str(Path(__file__).parents[1]))

from checkpassword import get_pwned_passwords, main, pwnedpassword_api


class TestGetPwnedPasswords:
	def test_returns_match_count_for_pwned_password(self):
		password = "password"
		password_hash = hashlib.sha1(password.encode("utf-8")).hexdigest()
		prefix, tail = password_hash[:5], password_hash[5:].upper()
		response = SimpleNamespace(status_code=200, text=f"{tail}:42\n")

		with patch("checkpassword.requests.get", return_value=response) as mock_get:
			result = get_pwned_passwords(password)

		assert result == 42
		mock_get.assert_called_once_with(pwnedpassword_api + prefix)

	def test_returns_zero_when_password_is_not_pwned(self):
		response = SimpleNamespace(status_code=200, text="ABCDEF123456:7\n")

		with patch("checkpassword.requests.get", return_value=response):
			result = get_pwned_passwords("unique-test-password")

		assert result == 0

	def test_raises_runtime_error_when_api_request_fails(self):
		response = SimpleNamespace(status_code=503, content=b"Service unavailable")

		with patch("checkpassword.requests.get", return_value=response):
			with pytest.raises(RuntimeError, match="Error fetching data: 503"):
				get_pwned_passwords("password")


class TestMain:
	def test_prints_usage_when_password_argument_is_missing(self, capsys):
		main(["checkpassword.py"])

		assert capsys.readouterr().out == "Usage: python checkpassword.py <password_to_check>\n"

	@patch("checkpassword.get_pwned_passwords", return_value=12)
	def test_prints_result(self, mock_get_pwned_passwords, capsys):
		main(["checkpassword.py", "password"])

		assert capsys.readouterr().out == "12\n"
		mock_get_pwned_passwords.assert_called_once_with("password")

	@patch("checkpassword.get_pwned_passwords", side_effect=RuntimeError("API unavailable"))
	def test_prints_runtime_error(self, mock_get_pwned_passwords, capsys):
		main(["checkpassword.py", "password"])

		assert capsys.readouterr().out == "Runtime error occurred: API unavailable\n"
		mock_get_pwned_passwords.assert_called_once_with("password")
