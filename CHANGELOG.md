# Changelog

All notable changes to the AI-Powered Link Checker action will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- `ignore-patterns` input: newline-separated regular expressions for URLs to skip entirely. Matching URLs are never requested, so they can be reported as neither broken nor redirected, and are counted separately via the new `ignored-count` output
- `update-existing-issue` input (default `true`): reuse the newest open issue with the same title and `broken-links` label, refreshing its body, instead of opening a duplicate on every run. New `issue-updated` output reports which path was taken
- Status `0` — a request that never completed — can now be listed in `silent-codes`. It applies to transport failures only (timeout, connection failure, a response broken mid-stream), not to malformed links or redirect loops

### Changed
- **Behaviour change:** with `create-issue: 'true'`, a recurring finding now refreshes one open issue rather than opening a new one per run. Set `update-existing-issue: 'false'` to restore the previous behaviour
- A crash in `link_checker.py` now fails the action with the checker's stderr in the job log, instead of aborting the step with no diagnostic
- `$GITHUB_OUTPUT` heredocs use a per-run delimiter, so scanned link text containing a line reading `EOF` can no longer truncate an output

### Fixed
- The `legitimate_domains` allowance in bot-blocking detection required the error string `Connection Error`, but the timeout handler passes `timeout`. A listed domain was therefore protected against connection errors and reported broken on timeouts. Both are now treated alike, keyed on which handler caught the failure rather than on the error text
- `silent-codes` was only consulted on responses that returned a status code, so it could never apply to timeouts or connection errors
- `compile_ignore_patterns` caught only `re.error`, so a pattern raising `OverflowError` (an oversized repetition count) or `RecursionError` aborted the whole run instead of being skipped as documented
- The checker's stderr was written to a file that was never displayed, so its warnings — including a skipped ignore pattern — could not reach the job log
- The test runner called `unittest.main(exit=False)` without inspecting the result, so the CI test job reported success even when tests failed
- `tests/test_bot_blocking.py` used a pre-migration `sys.path`, so it could not import the module under test; it now asserts rather than printing, and CI runs it
- Corrected the action's self-referencing links in issue bodies, PR comments, artifacts and `examples.md`, which still pointed at the pre-migration `QuantEcon/meta` path
- The generated issue body claimed later runs would refresh it in place even when `update-existing-issue` was `false`
- The temporary ignore-patterns file is removed via an `EXIT` trap, so it is not left behind when the step exits early
- The test fixtures depended on `httpstat.us` and `httpbin.org` for status codes and multi-hop redirects. Both stopped answering, so those links reported `Status: 0 (Connection Error)` and the CI step named for `silent-codes` exercised no silent-code logic at all — masked by `continue-on-error: true`. Status codes and redirect counting are now asserted against a mocked session, unreachable hosts use RFC 2606 `.invalid` names, and the live scan is labelled as the informational step it always was
- `tests/README.md` documented local commands that ran `./action.yml` as an executable, which was never possible

*(No change to the action's behaviour in the last two entries — test and documentation only.)*

## [1.0.0] - 2025-10-01

### Added
- Initial stable release migrated from QuantEcon/meta repository
- Smart link validation with configurable timeouts
- AI-powered suggestions for broken and redirected links
- Bot-blocking detection and handling
- Support for both full and PR-changed file scanning modes
- Configurable silent status codes (403, 503 by default)
- GitHub issue creation with detailed reports
- Workflow artifact generation with link analysis
- MyST Markdown and Jupyter Book compatibility
- Redirect detection and improvement suggestions
- Comprehensive JSON output with detailed link information
- Integration with GitHub Issues API for automated reporting
- Respectful rate limiting and improved timeout handling
- Full compatibility with existing workflows
- Enhanced documentation and examples
- Comprehensive test suite with Python module testing
- GitHub Marketplace listing
- Python requirements management with requirements.txt
