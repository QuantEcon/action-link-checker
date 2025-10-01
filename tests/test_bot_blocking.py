#!/usr/bin/env python3
"""
Test script to simulate bot blocking scenarios
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../.github/actions/link-checker'))

from link_checker import is_likely_bot_blocked

def test_bot_blocking_detection():
    """Test the bot blocking detection logic"""
    
    # Test major site domains that commonly block bots
    test_cases = [
        ("https://www.netflix.com/", True, "Netflix should be detected as likely bot-blocked"),
        ("https://code.tutsplus.com/tutorial/something", False, "Tutsplus should not be automatically flagged"),
        ("https://www.amazon.com/", True, "Amazon should be detected as likely bot-blocked"),
        ("https://example.com/", False, "Example.com should not be flagged"),
        ("https://github.com/user/repo", False, "GitHub should not be flagged as bot-blocked"),
        ("https://www.wikipedia.org/wiki/Test", True, "Wikipedia should be detected as likely bot-blocked"),
    ]
    
    print("Testing bot blocking detection logic:")
    print("-" * 50)
    
    for url, expected, description in test_cases:
        result = is_likely_bot_blocked(url)
        status = "✅ PASS" if result == expected else "❌ FAIL"
        print(f"{status}: {description}")
        print(f"   URL: {url}")
        print(f"   Expected: {expected}, Got: {result}")
        print()
    
    # Test encoding error detection
    print("Testing encoding error detection:")
    print("-" * 50)
    
    encoding_cases = [
        ("https://www.netflix.com/", None, None, "encoding issue", True, "Encoding error should be detected"),
        ("https://example.com/", None, None, "timeout", False, "Regular timeout should not be flagged"),
        ("https://example.com/", None, 429, None, True, "Rate limiting should be detected"),
        ("https://example.com/", None, 503, None, True, "Service unavailable should be detected"),
    ]
    
    for url, content, status_code, error, expected, description in encoding_cases:
        result = is_likely_bot_blocked(url, content, status_code, error)
        status = "✅ PASS" if result == expected else "❌ FAIL"
        print(f"{status}: {description}")
        print(f"   URL: {url}, Status: {status_code}, Error: {error}")
        print(f"   Expected: {expected}, Got: {result}")
        print()

    # Test legitimate domains with connection errors (simulating network restrictions)
    print("Testing legitimate domain protection:")
    print("-" * 50)
    
    legitimate_cases = [
        ("https://www.python.org/", None, None, "Connection Error", True, "Python.org with connection error should be protected"),
        ("https://jupyter.org/", None, None, "Connection Error", True, "Jupyter.org with connection error should be protected"),
        ("https://docs.python.org/3/", None, None, "Connection Error", True, "Python docs with connection error should be protected"),
        ("https://github.com/user/repo", None, None, "Connection Error", True, "GitHub with connection error should be protected"),
        ("https://unknown-domain.com/", None, None, "Connection Error", False, "Unknown domain with connection error should not be protected"),
    ]
    
    for url, content, status_code, error, expected, description in legitimate_cases:
        result = is_likely_bot_blocked(url, content, status_code, error)
        status = "✅ PASS" if result == expected else "❌ FAIL"
        print(f"{status}: {description}")
        print(f"   URL: {url}, Error: {error}")
        print(f"   Expected: {expected}, Got: {result}")
        print()

if __name__ == "__main__":
    test_bot_blocking_detection()