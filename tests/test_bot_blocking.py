#!/usr/bin/env python3
"""
Tests for the bot-blocking detection logic in link_checker.py
"""
import sys
import os
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from link_checker import is_likely_bot_blocked


class TestBotBlockingDetection(unittest.TestCase):

    def test_major_sites_that_block_bots(self):
        """Sites known to block automated requests are never reported broken"""
        cases = [
            ("https://www.netflix.com/", True),
            ("https://www.amazon.com/", True),
            ("https://www.wikipedia.org/wiki/Test", True),
            ("https://code.tutsplus.com/tutorial/something", False),
            ("https://example.com/", False),
            ("https://github.com/user/repo", False),
        ]
        for url, expected in cases:
            with self.subTest(url=url):
                self.assertEqual(is_likely_bot_blocked(url), expected)

    def test_error_and_status_code_signals(self):
        """Encoding errors and rate-limit style status codes are absorbed"""
        cases = [
            ("https://www.netflix.com/", None, "encoding issue", True),
            ("https://example.com/", None, "timeout", False),
            ("https://example.com/", 429, None, True),
            ("https://example.com/", 503, None, True),
        ]
        for url, status_code, error, expected in cases:
            with self.subTest(url=url, status_code=status_code, error=error):
                self.assertEqual(
                    is_likely_bot_blocked(url, None, status_code, error), expected)

    def test_legitimate_domains_on_transport_failure(self):
        """A listed domain is protected when the request never reached the server

        Both a timeout and a connection error are symptoms of a host that will
        not answer a datacenter IP, so both are treated alike. An unlisted
        domain stays reported.
        """
        cases = [
            ("https://www.python.org/", True),
            ("https://jupyter.org/", True),
            ("https://docs.python.org/3/", True),
            ("https://github.com/user/repo", True),
            ("https://unknown-domain.com/", False),
        ]
        for error in ("Connection Error", "Timeout"):
            for url, expected in cases:
                with self.subTest(url=url, error=error):
                    self.assertEqual(
                        is_likely_bot_blocked(url, None, None, error,
                                              network_failure=True),
                        expected)

    def test_legitimate_domains_not_protected_without_transport_failure(self):
        """The allowance is keyed on the handler, not on the error text

        Any exception reaching the catch-all handler can carry the word
        'timeout' in its message without the request having failed in transit.
        """
        for url in ("https://www.python.org/", "https://github.com/user/repo"):
            with self.subTest(url=url):
                self.assertFalse(
                    is_likely_bot_blocked(url, None, None,
                                          "ValueError: connect timeout to 0"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
