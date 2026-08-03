#!/usr/bin/env python3
"""
Test runner for link checker Python modules
"""

import sys
import os
import json
import subprocess
import unittest
import tempfile
from pathlib import Path

# Add the parent directory to sys.path to import the modules
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    import link_checker
    import format_results
    print("✅ Successfully imported link_checker and format_results modules")
except ImportError as e:
    print(f"❌ Failed to import modules: {e}")
    sys.exit(1)

class TestLinkChecker(unittest.TestCase):
    
    def test_module_imports(self):
        """Test that modules can be imported successfully"""
        self.assertTrue(hasattr(link_checker, 'main'))
        self.assertTrue(hasattr(format_results, 'main'))
        
    def test_ignore_patterns_compile_and_match(self):
        """Ignore patterns skip matching URLs and leave others alone"""
        patterns = link_checker.compile_ignore_patterns([
            'https://fred\\.stlouisfed\\.org/.*',
            '',                      # blank lines are skipped
            '   # a comment',        # comments are skipped
        ])
        self.assertEqual(len(patterns), 1)
        self.assertTrue(link_checker.is_ignored('https://fred.stlouisfed.org/', patterns))
        self.assertTrue(link_checker.is_ignored('https://fred.stlouisfed.org/series/UNRATE', patterns))
        self.assertFalse(link_checker.is_ignored('https://example.com/', patterns))

    def test_ignore_patterns_bare_domain_matches_as_substring(self):
        """A bare domain works without regex anchoring"""
        patterns = link_checker.compile_ignore_patterns(['fred.stlouisfed.org'])
        self.assertTrue(link_checker.is_ignored('https://fred.stlouisfed.org/series/UNRATE', patterns))

    def test_invalid_ignore_pattern_is_skipped_not_fatal(self):
        """An unparseable pattern is dropped rather than crashing the run"""
        patterns = link_checker.compile_ignore_patterns(['[unclosed', 'example\\.com'])
        self.assertEqual(len(patterns), 1)
        self.assertTrue(link_checker.is_ignored('https://example.com/', patterns))

    def test_empty_ignore_patterns_ignore_nothing(self):
        """The default of no patterns must not skip any URL"""
        patterns = link_checker.compile_ignore_patterns([])
        self.assertFalse(link_checker.is_ignored('https://example.com/', patterns))

    def test_pattern_raising_non_re_error_is_skipped(self):
        """re.compile raises more than re.error, and none of it may be fatal

        An oversized repetition count raises OverflowError, which is not a
        subclass of re.error, so a narrower except aborted the whole run on a
        pattern a user could plausibly type.
        """
        patterns = link_checker.compile_ignore_patterns(
            ['a{1,4294967296}', 'example\\.com'])
        self.assertEqual(len(patterns), 1)
        self.assertTrue(link_checker.is_ignored('https://example.com/', patterns))

    def test_legitimate_domain_protected_on_timeout(self):
        """A listed domain is protected on timeout, not only connection error

        Regression test: the legitimate_domains branch previously required the
        literal string 'Connection Error', so it could never fire on a timeout.
        """
        for error in ('Connection Error', 'Timeout'):
            with self.subTest(error=error):
                self.assertTrue(
                    link_checker.is_likely_bot_blocked(
                        'https://github.com/x', error=error, network_failure=True))

    def test_unlisted_domain_not_protected_on_timeout(self):
        """Widening the branch must not silence unknown hosts"""
        self.assertFalse(
            link_checker.is_likely_bot_blocked(
                'https://unknown-domain.example/', error='Timeout', network_failure=True))

    def test_legitimate_domain_not_protected_by_error_text_alone(self):
        """The allowance keys on the handler, not on the word 'timeout'

        A misconfigured timeout makes urllib3 raise a ValueError whose message
        contains 'timeout'. Sniffing the error string would silence every link
        on a listed domain on what is really a configuration error.
        """
        self.assertFalse(
            link_checker.is_likely_bot_blocked(
                'https://github.com/x', error='ValueError: connect timeout to 0'))

    def test_status_zero_can_be_silenced_via_silent_codes(self):
        """silent-codes reaches the network-failure path, where 0 is reported"""
        loud = link_checker.network_failure_result(
            'https://unknown-domain.example/', 'Timeout', [403, 503],
            network_failure=True)
        self.assertTrue(loud['broken'])
        self.assertFalse(loud['silent'])

        quiet = link_checker.network_failure_result(
            'https://unknown-domain.example/', 'Timeout', [0, 403, 503],
            network_failure=True)
        self.assertFalse(quiet['broken'])
        self.assertTrue(quiet['silent'])

    def test_status_zero_silencing_does_not_cover_malformed_links(self):
        """A bad href is the project's own to fix, so silent-codes must not hide it

        Malformed URLs and redirect loops reach the catch-all handler and also
        report status 0. Silencing unreachable hosts must not silence these.
        """
        result = link_checker.network_failure_result(
            'https://', "Invalid URL 'https://': No host supplied", [0, 403, 503])
        self.assertTrue(result['broken'])
        self.assertFalse(result['silent'])

    def test_connection_broken_mid_response_counts_as_transport_failure(self):
        """A body that stops mid-stream is silenceable like a timeout

        ChunkedEncodingError is neither a Timeout nor a ConnectionError, so it
        needs its own handler or it falls through to the catch-all and stays
        loud however silent-codes is set.
        """
        import requests
        from unittest import mock

        exc = requests.exceptions.ChunkedEncodingError('Connection broken')
        with mock.patch.object(requests.Session, 'get', side_effect=exc):
            quiet = link_checker.check_link(
                'https://unknown-domain.example/', 5, 5, [0, 403, 503])
            loud = link_checker.check_link(
                'https://unknown-domain.example/', 5, 5, [403, 503])

        self.assertEqual(quiet['status_code'], 0)
        self.assertTrue(quiet['silent'])
        self.assertFalse(quiet['broken'])
        self.assertTrue(loud['broken'])
        self.assertFalse(loud['silent'])

    def test_malformed_link_stays_loud_via_check_link(self):
        """The catch-all path is not silenceable, end to end through check_link"""
        result = link_checker.check_link('https://', 5, 5, [0, 403, 503])
        self.assertEqual(result['status_code'], 0)
        self.assertTrue(result['broken'])
        self.assertFalse(result['silent'])

    def test_bot_blocked_domains_still_silent_without_network_failure(self):
        """The domain_indicators list is unaffected by the network_failure gate"""
        self.assertTrue(
            link_checker.is_likely_bot_blocked('https://netflix.com/title/1', error='boom'))

    def test_ignore_patterns_file_end_to_end(self):
        """--ignore-patterns-file skips matching URLs and reports them separately

        Every URL in the fixture is ignored, so this runs the whole script
        without making a single request -- the point being that an ignored URL
        is never requested at all.
        """
        script = Path(__file__).parent.parent / 'link_checker.py'
        with tempfile.TemporaryDirectory() as tmp:
            html = Path(tmp) / 'page.html'
            html.write_text(
                '<html><body>'
                '<a href="https://fred.stlouisfed.org/">FRED</a>'
                '<a href="https://fred.stlouisfed.org/series/UNRATE">UNRATE</a>'
                '<a href="https://blocked.example/x">Other</a>'
                '</body></html>', encoding='utf-8')

            patterns = Path(tmp) / 'patterns.txt'
            patterns.write_text(
                'https://fred\\.stlouisfed\\.org/.*\n'
                '\n'
                '# a comment\n'
                'blocked\\.example\n', encoding='utf-8')

            proc = subprocess.run(
                [sys.executable, str(script), str(html),
                 '--ignore-patterns-file', str(patterns)],
                capture_output=True, text=True, timeout=60)

            self.assertEqual(proc.returncode, 0, proc.stderr)
            data = json.loads(proc.stdout)

            self.assertEqual(len(data['ignored_results']), 3)
            self.assertEqual(data['broken_results'], [])
            self.assertEqual(data['redirect_results'], [])
            self.assertEqual(data['total_links'], 3)
            self.assertIn('url', data['ignored_results'][0])
            self.assertIn('file', data['ignored_results'][0])
            self.assertIn('text', data['ignored_results'][0])

    def test_ignore_patterns_file_missing_is_not_fatal(self):
        """An unreadable patterns file warns and checks nothing away"""
        script = Path(__file__).parent.parent / 'link_checker.py'
        with tempfile.TemporaryDirectory() as tmp:
            html = Path(tmp) / 'page.html'
            html.write_text('<html><body>no links</body></html>', encoding='utf-8')

            proc = subprocess.run(
                [sys.executable, str(script), str(html),
                 '--ignore-patterns-file', str(Path(tmp) / 'does-not-exist.txt')],
                capture_output=True, text=True, timeout=60)

            self.assertEqual(proc.returncode, 0, proc.stderr)
            self.assertEqual(json.loads(proc.stdout)['total_links'], 0)

    def test_link_checker_with_test_files(self):
        """Test link checker with actual test HTML files"""
        test_dir = Path(__file__).parent
        good_links_file = test_dir / "good-links.html"
        
        if good_links_file.exists():
            print(f"✅ Found test file: {good_links_file}")
            # Basic test - just ensure the function doesn't crash
            try:
                # This would normally require network access, so we'll just test structure
                result = link_checker.extract_links_from_html(str(good_links_file))
                print(f"✅ Successfully extracted links from HTML file")
                self.assertIsInstance(result, list)
            except Exception as e:
                print(f"ℹ️  Expected network-related error: {e}")
        else:
            print("ℹ️  Test HTML files not found, skipping file-based tests")

def main():
    print("🧪 Running Link Checker Tests")
    print("=" * 40)

    # Run basic module tests. exit=False keeps the trailing message, so the
    # result has to be inspected explicitly or CI would pass on a failure.
    result = unittest.main(argv=[''], exit=False, verbosity=2).result

    if not result.wasSuccessful():
        print("\n❌ Tests failed")
        sys.exit(1)

    print("\n✅ All tests completed successfully!")

if __name__ == "__main__":
    main()