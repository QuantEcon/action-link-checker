# Changelog

All notable changes to the AI-Powered Link Checker action will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- `ignore-patterns` input: newline-separated regular expressions for URLs to skip entirely. Matching URLs are never requested, so they can be reported as neither broken nor redirected, and are counted separately via the new `ignored-count` output
- `update-existing-issue` input (default `true`): reuse the newest open issue with the same title and `broken-links` label, refreshing its body, instead of opening a duplicate on every run. New `issue-updated` output reports which path was taken
- Status `0` — a request that failed before the server answered — can now be listed in `silent-codes`

### Fixed
- The `legitimate_domains` allowance in bot-blocking detection required the error string `Connection Error`, but the timeout handler passes `timeout`. A listed domain was therefore protected against connection errors and reported broken on timeouts. Both are now treated alike
- `silent-codes` was only consulted on responses that returned a status code, so it could never apply to timeouts or connection errors
- The test runner called `unittest.main(exit=False)` without inspecting the result, so the CI test job reported success even when tests failed
- Corrected the action's self-referencing links in issue bodies, PR comments and artifacts, which still pointed at the pre-migration `QuantEcon/meta` path

### Changed
- **Behaviour change:** with `create-issue: 'true'`, a recurring finding now refreshes one open issue rather than opening a new one per run. Set `update-existing-issue: 'false'` to restore the previous behaviour

### Previously unreleased
- Initial release of the AI-Powered Link Checker action
- Smart link validation with configurable timeouts
- AI-powered suggestions for broken and redirected links
- Bot-blocking detection and handling
- Support for both full and PR-changed file scanning modes
- Configurable silent status codes (403, 503 by default)
- GitHub issue creation with detailed reports
- Workflow artifact generation with link analysis
- MyST Markdown and Jupyter Book compatibility

### Features
- Enhanced robustness compared to traditional link checkers
- Respectful rate limiting and improved timeout handling
- Redirect detection and improvement suggestions
- Comprehensive JSON output with detailed link information
- Integration with GitHub Issues API for automated reporting
- Performance optimizations for large documentation sites

## [1.0.0] - 2025-10-01

### Added
- Initial stable release migrated from QuantEcon/meta repository
- Full compatibility with existing workflows
- Enhanced documentation and examples  
- Comprehensive test suite with Python module testing
- GitHub Marketplace listing
- Python requirements management with requirements.txt