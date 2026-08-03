#!/usr/bin/env python3
"""
Test runner for link checker Python modules
"""

import sys
import os
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

    def test_legitimate_domain_protected_on_timeout(self):
        """A listed domain is protected on timeout, not only connection error

        Regression test: the legitimate_domains branch previously required the
        literal string 'Connection Error', so it could never fire on a timeout.
        """
        for error in ('Connection Error', 'timeout'):
            with self.subTest(error=error):
                self.assertTrue(
                    link_checker.is_likely_bot_blocked('https://github.com/x', error=error))

    def test_unlisted_domain_not_protected_on_timeout(self):
        """Widening the branch must not silence unknown hosts"""
        self.assertFalse(
            link_checker.is_likely_bot_blocked('https://unknown-domain.example/', error='timeout'))

    def test_status_zero_can_be_silenced_via_silent_codes(self):
        """silent-codes reaches the network-failure path, where 0 is reported"""
        loud = link_checker.network_failure_result(
            'https://unknown-domain.example/', 'Timeout', [403, 503])
        self.assertTrue(loud['broken'])
        self.assertFalse(loud['silent'])

        quiet = link_checker.network_failure_result(
            'https://unknown-domain.example/', 'Timeout', [0, 403, 503])
        self.assertFalse(quiet['broken'])
        self.assertTrue(quiet['silent'])

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