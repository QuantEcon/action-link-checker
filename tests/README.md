# Test Files for Link Checker Action

This directory contains test HTML files and scripts used to validate the link-checker action functionality.

## Test Files

### good-links.html
- Contains valid, working links that should pass all checks
- Used to test successful link validation

### broken-links.html  
- Contains intentionally broken links for testing error detection
- Tests various failure scenarios (404, 500, non-existent domains)
- Includes links that should trigger AI suggestions (HTTP→HTTPS, master→main)

### redirect-links.html
- Contains links that redirect to test redirect handling
- Tests proper following of redirects and detection of issues

### legitimate-slow-links.html
- Contains links that are slow to respond but valid
- Tests timeout handling and retry logic

### test_bot_blocking.py
- Python script to test bot-blocking detection functionality
- Tests the action's ability to handle sites that block automated requests

### test_modules.py  
- Unit tests for the Python modules (link_checker.py, format_results.py)
- Tests module imports and basic functionality

## Usage in CI

These files are automatically used by the GitHub Actions CI workflow to test:
- Link validation accuracy
- Error detection and reporting
- Timeout and retry handling  
- Bot-blocking awareness
- AI-powered suggestions
- Module functionality

## Running Tests Locally

You can test the action locally using these files:

```bash
# Test with good links (should pass)
./action.yml --html-path tests/good-links.html --fail-on-broken true

# Test with broken links (should find issues)  
./action.yml --html-path tests/broken-links.html --fail-on-broken false

# Test with silent codes for known issues
./action.yml --html-path tests --silent-codes "404,500" --fail-on-broken true

# Run Python module tests
cd tests && python test_modules.py
```

## Test Requirements

The Python tests require the same dependencies as the main action:
- requests>=2.28.0  
- beautifulsoup4>=4.11.0
- urllib3>=1.26.0