from unittest.mock import MagicMock, patch

import pytest

from emailer_utils import load_smtp_config, send_an_email


class TestLoadSmtpConfig:
    """Test suite for load_smtp_config function."""

    @patch("emailer_utils.load_dotenv")
    def test_returns_config_when_all_vars_present(self, mock_load_dotenv, monkeypatch):
        monkeypatch.setenv("SMTP_SENDER", "sender@example.com")
        monkeypatch.setenv("SMTP_SENDER_NAME", "Sender Name")
        monkeypatch.setenv("SMTP_APP_PASSWORD", "secret")
        monkeypatch.setenv("SMTP_HOST", "smtp.example.com")
        monkeypatch.setenv("SMTP_PORT", "587")

        config = load_smtp_config()

        assert config == ("sender@example.com", "Sender Name", "secret", "smtp.example.com", 587)
        assert isinstance(config[4], int)

    @patch("emailer_utils.load_dotenv")
    def test_raises_when_config_incomplete(self, mock_load_dotenv, monkeypatch):
        monkeypatch.delenv("SMTP_SENDER", raising=False)
        monkeypatch.delenv("SMTP_SENDER_NAME", raising=False)
        monkeypatch.delenv("SMTP_APP_PASSWORD", raising=False)
        monkeypatch.delenv("SMTP_HOST", raising=False)
        monkeypatch.delenv("SMTP_PORT", raising=False)

        with pytest.raises(ValueError, match="SMTP configuration is incomplete"):
            load_smtp_config()

    @patch("emailer_utils.load_dotenv")
    def test_falls_back_to_sender_when_sender_name_missing(self, mock_load_dotenv, monkeypatch):
        monkeypatch.setenv("SMTP_SENDER", "sender@example.com")
        monkeypatch.delenv("SMTP_SENDER_NAME", raising=False)
        monkeypatch.setenv("SMTP_APP_PASSWORD", "secret")
        monkeypatch.setenv("SMTP_HOST", "smtp.example.com")
        monkeypatch.setenv("SMTP_PORT", "587")

        config = load_smtp_config()

        assert config[1] == "sender@example.com"

    @patch("emailer_utils.load_dotenv")
    def test_raises_when_port_is_not_numeric(self, mock_load_dotenv, monkeypatch):
        monkeypatch.setenv("SMTP_SENDER", "sender@example.com")
        monkeypatch.setenv("SMTP_SENDER_NAME", "Sender Name")
        monkeypatch.setenv("SMTP_APP_PASSWORD", "secret")
        monkeypatch.setenv("SMTP_HOST", "smtp.example.com")
        monkeypatch.setenv("SMTP_PORT", "not-a-number")

        with pytest.raises(ValueError, match="SMTP_PORT must be a valid integer"):
            load_smtp_config()

    @patch("emailer_utils.load_dotenv")
    def test_strips_whitespace_from_port(self, mock_load_dotenv, monkeypatch):
        monkeypatch.setenv("SMTP_SENDER", "sender@example.com")
        monkeypatch.setenv("SMTP_SENDER_NAME", "Sender Name")
        monkeypatch.setenv("SMTP_APP_PASSWORD", "secret")
        monkeypatch.setenv("SMTP_HOST", "smtp.example.com")
        monkeypatch.setenv("SMTP_PORT", " 587 ")

        config = load_smtp_config()

        assert config[4] == 587

    @patch("emailer_utils.load_dotenv")
    @pytest.mark.parametrize(
        "missing_var",
        ["SMTP_SENDER", "SMTP_APP_PASSWORD", "SMTP_HOST", "SMTP_PORT"],
    )
    def test_raises_when_a_single_required_var_is_missing(
        self, mock_load_dotenv, missing_var, monkeypatch
    ):
        monkeypatch.setenv("SMTP_SENDER", "sender@example.com")
        monkeypatch.setenv("SMTP_SENDER_NAME", "Sender Name")
        monkeypatch.setenv("SMTP_APP_PASSWORD", "secret")
        monkeypatch.setenv("SMTP_HOST", "smtp.example.com")
        monkeypatch.setenv("SMTP_PORT", "587")
        monkeypatch.delenv(missing_var, raising=False)

        with pytest.raises(ValueError, match="SMTP configuration is incomplete"):
            load_smtp_config()


class TestSendAnEmail:
    """Test suite for send_an_email function."""

    @pytest.fixture
    def smtp_config(self):
        return ("sender@example.com", "Sender Name", "secret", "smtp.example.com", 587)

    @pytest.mark.parametrize(
        "recipient_email,subject,content",
        [
            ("", "subject", "content"),
            ("to@example.com", "", "content"),
            ("to@example.com", "subject", ""),
            (None, "subject", "content"),
            ("   ", "subject", "content"),
            ("to@example.com", "   ", "content"),
            ("to@example.com", "subject", "   "),
        ],
    )
    def test_raises_when_required_fields_missing(self, recipient_email, subject, content):
        with pytest.raises(ValueError, match="must all be provided"):
            send_an_email(recipient_email, subject, content)

    @patch("emailer_utils.load_smtp_config")
    @patch("emailer_utils.smtplib.SMTP")
    def test_sends_plain_text_email(self, mock_smtp_class, mock_load_config, smtp_config):
        mock_load_config.return_value = smtp_config
        mock_smtp = MagicMock()
        mock_smtp_class.return_value.__enter__.return_value = mock_smtp

        send_an_email("to@example.com", "Test subject", "Test content")

        mock_smtp_class.assert_called_once_with(host="smtp.example.com", port=587)
        mock_smtp.ehlo.assert_called_once()
        mock_smtp.starttls.assert_called_once()
        mock_smtp.login.assert_called_once_with("sender@example.com", "secret")

        sent_message = mock_smtp.send_message.call_args[0][0]
        assert sent_message["to"] == "to@example.com"
        assert sent_message["subject"] == "Test subject"
        assert sent_message.get_content().strip() == "Test content"
        assert sent_message.get_content_type() == "text/plain"

    @patch("emailer_utils.load_smtp_config")
    @patch("emailer_utils.smtplib.SMTP")
    def test_sends_html_email(self, mock_smtp_class, mock_load_config, smtp_config):
        mock_load_config.return_value = smtp_config
        mock_smtp = MagicMock()
        mock_smtp_class.return_value.__enter__.return_value = mock_smtp

        send_an_email("to@example.com", "Test subject", "<p>Hi</p>", is_html=True)

        sent_message = mock_smtp.send_message.call_args[0][0]
        assert sent_message.get_content_type() == "text/html"

    @patch("emailer_utils.load_smtp_config")
    @patch("emailer_utils.smtplib.SMTP")
    def test_reraises_smtp_exception(self, mock_smtp_class, mock_load_config, smtp_config):
        import smtplib

        mock_load_config.return_value = smtp_config
        mock_smtp_class.return_value.__enter__.side_effect = smtplib.SMTPException("boom")

        with pytest.raises(smtplib.SMTPException):
            send_an_email("to@example.com", "Test subject", "Test content")

    @patch("emailer_utils.load_smtp_config")
    @patch("emailer_utils.smtplib.SMTP")
    def test_reraises_non_smtp_exception_from_smtp_block(
        self, mock_smtp_class, mock_load_config, smtp_config
    ):
        mock_load_config.return_value = smtp_config
        mock_smtp = MagicMock()
        mock_smtp.login.side_effect = OSError("network unreachable")
        mock_smtp_class.return_value.__enter__.return_value = mock_smtp

        with pytest.raises(OSError, match="network unreachable"):
            send_an_email("to@example.com", "Test subject", "Test content")

    @patch("emailer_utils.load_smtp_config")
    @patch("emailer_utils.smtplib.SMTP")
    def test_reraises_error_when_host_is_unreachable(
        self, mock_smtp_class, mock_load_config, smtp_config
    ):
        import socket

        mock_load_config.return_value = smtp_config
        # Connection failures happen when SMTP() itself is constructed, before __enter__.
        mock_smtp_class.side_effect = socket.gaierror("Name or service not known")

        with pytest.raises(socket.gaierror):
            send_an_email("to@example.com", "Test subject", "Test content")

    @patch("emailer_utils.load_smtp_config")
    def test_reraises_unexpected_exception(self, mock_load_config, smtp_config):
        mock_load_config.side_effect = RuntimeError("unexpected")

        with pytest.raises(RuntimeError, match="unexpected"):
            send_an_email("to@example.com", "Test subject", "Test content")
