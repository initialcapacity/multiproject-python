from unittest import TestCase

from authentication.allowed_emails import AllowedEmails


class TestAllowedEmails(TestCase):
    def test_include_empty(self) -> None:
        self.assertTrue(
            AllowedEmails(domains="", addresses="").include("test@example.com")
        )

    def test_include(self) -> None:
        self.assertTrue(
            AllowedEmails("", "test@example.com").include("test@example.com")
        )
        self.assertTrue(
            AllowedEmails("ok.example.com,example.com", "").include("test@example.com")
        )
        self.assertFalse(
            AllowedEmails("ok.example.com,example.com", "not_a_match").include(
                "test@other.example.com"
            )
        )
