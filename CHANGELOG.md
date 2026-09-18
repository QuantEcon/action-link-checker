# Changelog

All notable changes to the AI-Powered Link Checker action will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- A `check-own-docs` CI job that renders this repository's Markdown and checks the links in it. It is the only job that posts a link-check comment on a pull request, and it posts one only when a link we publish is reported broken. It runs with `silent-codes: '0,403,503'`, so a transient timeout or DNS failure stays quiet and the comment is reserved for a real status such as a 404

### Changed
- The action's own steps now run on Node 24: `actions/github-script` v7 to v9 (three steps) and `actions/upload-artifact` v4 to v7. Node 20 reached end-of-life on 2026-04-30. None of the action's inputs, outputs or scripts changes. A self-hosted runner needs v2.327.1 or later to run the new pins
- CI moves to `actions/checkout` v7 and `actions/setup-python` v7, and a grouped weekly Dependabot config for GitHub Actions is added so that the pins do not fall behind again
- CI serves its own fixtures from `127.0.0.1`, so no gating step depends on the public internet any more. A clean page, a followed redirect, a reported error status and that status silenced by `silent-codes` are all asserted end to end against responses under our control. The scans of `good-links.html` and `broken-links.html` remain, as informational smoke that cannot turn CI red
- The fixture scans no longer post a link-check comment on pull requests. Their findings are true by construction, so the comment reported the same fixture on every run and carried no information

### Fixed
- The README linked a GitHub Marketplace badge to `https://github.com/marketplace/actions/ai-link-checker`, which returns 404 — the action was never published there. Found by the new `check-own-docs` job on its first run

## [1.1.0] - 2026-08-03

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
- Python requirements management with requirements.txt

> The `v1.0.0` tag points at the repository's initial commit and no GitHub Release was ever published for it, so the Marketplace listing this section originally claimed does not exist. The tag is left where it is rather than moved. Pin `v1` or `v1.1.0` instead.
