# AI-Powered Link Checker Action

[![CI](https://github.com/QuantEcon/action-link-checker/actions/workflows/ci.yml/badge.svg)](https://github.com/QuantEcon/action-link-checker/actions/workflows/ci.yml)
[![GitHub Marketplace](https://img.shields.io/badge/Marketplace-AI%20Link%20Checker-blue.svg?colorA=24292e&colorB=0366d6&style=flat&longCache=true&logo=data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA4AAAAOCAYAAAAfSC3RAAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAM6wAADOsB5dZE0gAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAAERSURBVCiRhZG/SsMxFEafKoEMFhyrdsFt6FYHNycunTo0Q4LgEhcnW4PgYgchGjoYiQ6ON2ARpK9nCxjUjuIFP+B+h3O/xmE2yVxPOJGkC3RgJ8qA3bQn7SiTKCQdC4J8HDW0v85CZaUHNzxhQcHdJvjZwM4mXaKJ4BdDMKxIsYoim1Smk2X6HPUdCnU5gO5D9POqvayBzY8nwoJJ+G9h9vGB0U8h8dNPgGLKlv1n6cJgAjjfY9lv1CVKq5f3oUAe5dJz9n3RkBhGA1ouJ/hT5a4c8yQQYSdF8vhN5gT1igMgZ9nJgzUqm9E1V+8rbYQhptmEURKA=)](https://github.com/marketplace/actions/ai-link-checker)

A sophisticated GitHub Action that validates web links in HTML files with AI-powered suggestions for improvements. Goes beyond traditional link checkers by providing intelligent recommendations and handling modern web challenges.

## 🎯 Features

- **🤖 AI-Powered Suggestions**: Intelligent recommendations for broken or redirected links
- **🔍 Smart Detection**: Bot-blocking awareness and enhanced robustness 
- **⚡ Performance Optimized**: Respectful rate limiting and efficient scanning
- **🎛️ Flexible Modes**: Full project or PR-changed files scanning
- **🔧 Highly Configurable**: Custom timeouts, status codes, and behaviors
- **📊 Rich Reporting**: GitHub issues, artifacts, and detailed JSON output
- **📚 Documentation Ready**: Perfect for Jupyter Book and documentation sites

## Features

- **Smart Link Validation**: Checks external web links in HTML files with configurable timeout and redirect handling
- **Enhanced Robustness**: Intelligent detection of bot-blocked sites to reduce false positives
- **AI-Powered Suggestions**: Provides intelligent recommendations for broken or redirected links
- **Two Scanning Modes**: Full project scan or PR-specific changed files only  
- **Configurable Status Codes**: Define which HTTP status codes to silently report (e.g., 403, 503)
- **Redirect Detection**: Identifies and suggests updates for redirected links
- **GitHub Integration**: Creates issues, PR comments, and workflow artifacts
- **MyST Markdown Support**: Works with Jupyter Book projects by scanning HTML output
- **Performance Optimized**: Respectful rate limiting, improved timeouts, and efficient scanning

## Usage

### Basic Usage

```yaml
- name: Check links in documentation
  uses: QuantEcon/action-link-checker@v1
```

### Weekly Full Project Scan

```yaml
name: Weekly Link Check
on:
  schedule:
    - cron: '0 9 * * 1'  # Monday at 9 AM UTC
  workflow_dispatch:

jobs:
  link-check:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      issues: write
    steps:
      - uses: actions/checkout@v4
        with:
          ref: gh-pages  # Check the published site
      
      - name: AI-powered link check
        uses: QuantEcon/action-link-checker@v1
        with:
          html-path: '.'
          mode: 'full'
          fail-on-broken: 'false'
          create-issue: 'true'
          ai-suggestions: 'true'
          silent-codes: '403,503'
          issue-title: 'Weekly Link Check Report'
          notify: 'maintainer1,maintainer2'
```

### PR-Triggered Changed Files Only

```yaml
name: PR Link Check
on:
  pull_request:
    branches: [ main ]

jobs:
  link-check:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      pull-requests: write
    steps:
      - uses: actions/checkout@v4
      
      - name: Build documentation
        run: jupyter-book build .
      
      - name: Check links in changed files
        uses: QuantEcon/action-link-checker@v1
        with:
          html-path: './_build/html'
          mode: 'changed'
          fail-on-broken: 'true'
          ai-suggestions: 'true'
          silent-codes: '403,503'
```

### Complete Advanced Usage

```yaml
- name: Comprehensive link checking
  uses: QuantEcon/action-link-checker@v1
  with:
    html-path: './_build/html'
    mode: 'full'
    silent-codes: '403,503,429'
    fail-on-broken: 'false'
    ai-suggestions: 'true'
    create-issue: 'true'
    issue-title: 'Link Check Report - Broken Links Found'
    create-artifact: 'true'
    artifact-name: 'detailed-link-report'
    notify: 'team-lead,docs-maintainer'
    timeout: '30'
    max-redirects: '5'
```

## False Positive Reduction

The action includes intelligent logic to reduce false positives for legitimate sites:

### Ignore Patterns

Some hosts throttle or block datacenter IP ranges outright, so they time out from a CI runner while working perfectly for readers. The automatic detection below catches many of these, but it cannot know which hosts a particular project depends on. Use `ignore-patterns` to declare them:

```yaml
- uses: QuantEcon/action-link-checker@v1
  with:
    html-path: '_site'
    ignore-patterns: |
      https://fred\.stlouisfed\.org/.*
      # blank lines and comments are ignored
      linkedin\.com
```

Patterns are Python regular expressions, one per line — newline-separated rather than comma-separated so that quantifiers such as `{1,3}` survive intact. Each is matched against the full URL with `re.search`, so a bare domain works as a substring without anchoring.

Ignored URLs are never requested at all. They therefore cannot be reported as broken *or* as redirects, and they are counted separately in the report and exposed as the `ignored-count` output. An invalid pattern is logged to the job log and skipped rather than failing the run.

If a project already maintains a Sphinx `linkcheck_ignore` list, those patterns can be pasted here directly. Both take Python regular expressions, so the syntax carries over unchanged; note that Sphinx anchors its patterns at the start of the URL while this action matches anywhere in it, so a pattern here may match slightly more than the same pattern does under Sphinx.

### Bot Blocking Detection
- **Major Sites**: Automatically detects common sites that block automated requests (Netflix, Amazon, Facebook, etc.)
- **Encoding Issues**: Identifies encoding errors that often indicate bot protection
- **Status Code Analysis**: Recognizes rate limiting (429) and bot blocking patterns
- **Silent Reporting**: Marks likely bot-blocked sites as silent instead of broken

### Improved Robustness
- **Browser-like Headers**: Uses realistic browser headers to reduce blocking
- **Increased Timeout**: Default 45-second timeout for slow-loading legitimate sites
- **Smart Error Handling**: Distinguishes between genuine broken links and temporary blocks

### AI Suggestion Filtering
- **Constructive Suggestions**: Only suggests fixes, not removals, for legitimate domains
- **Manual Review**: Suggests manual verification for unknown domains instead of automatic removal
- **Domain Whitelist**: Recognizes trusted domains (GitHub, Python.org, etc.) and handles them appropriately

## AI-Powered Suggestions

The action includes intelligent analysis that can suggest:

### Automatic Fixes
- **HTTPS Upgrades**: Detects `http://` links that should be `https://`
- **GitHub Branch Updates**: Finds `/master/` links that should be `/main/`
- **Documentation Migrations**: Suggests updated URLs for moved documentation sites
- **Version Updates**: Recommends newer versions of deprecated documentation

### Redirect Optimization
- **Final Destination**: Suggests updating redirected links to their final destination
- **Performance**: Eliminates unnecessary redirect chains
- **Reliability**: Reduces dependency on redirect services

### Example AI Suggestions Output:
```
🤖 http://docs.python.org/2.7/library/urllib.html
   Issue: Broken link (Status: 404)
   💡 version_update: https://docs.python.org/3/library/urllib.html
      Reason: Python 2.7 is deprecated, consider Python 3 documentation

🤖 http://github.com/user/repo/blob/master/README.md
   Issue: Redirected 1 times
   💡 redirect_update: https://github.com/user/repo/blob/main/README.md
      Reason: GitHub default branch changed from master to main
```

## How It Works

1. **File Discovery**: Scans HTML files in the specified directory
2. **Link Extraction**: Uses BeautifulSoup to extract all external links
3. **Link Validation**: Checks each link with configurable timeout and redirect handling
4. **AI Analysis**: Applies rule-based AI to suggest improvements
5. **Reporting**: Creates detailed reports with actionable suggestions

### Scanning Modes

#### Full Mode (`mode: 'full'`)
- Scans all HTML files in the target directory
- Ideal for scheduled weekly scans
- Comprehensive coverage of entire project

#### Changed Mode (`mode: 'changed'`)
- Only scans HTML files that changed in the current PR
- Efficient for PR-triggered workflows
- Falls back to full scan if no changes detected

## Configuration

### Silent Status Codes

Configure which HTTP status codes should be reported without failing:

```yaml
silent-codes: '403,503,429,502'
```

Common codes to consider:
- `403`: Forbidden (often due to bot detection)
- `503`: Service Unavailable (temporary outages)
- `429`: Too Many Requests (rate limiting)
- `502`: Bad Gateway (temporary server issues)
- `0`: The request never completed — it timed out, the connection failed (DNS failure, connection refused), or the server broke the response mid-stream. Silencing `0` suppresses every unreachable host, so prefer `ignore-patterns` when only specific hosts are affected. It applies to transport failures only: a malformed link such as `https://` and a redirect loop also report status `0`, and those stay reported however `silent-codes` is set, since they are the project's own to fix.

### Recurring Reports

When `create-issue` is enabled on a schedule, the action reuses the newest open issue carrying the same `issue-title` and the `broken-links` label, refreshing its body with the latest run instead of opening another issue. A weekly cron on a persistent finding therefore produces one issue, not one per week.

Close the issue once the links are fixed; if the finding recurs afterwards, a fresh issue is opened. To restore the previous behaviour of always opening a new issue, set `update-existing-issue: 'false'`.

Two things follow from matching on the title and the label. Give each workflow its own `issue-title` if a repository runs more than one link check, or they will overwrite each other's report. And leave the `broken-links` label in place — if it is removed from the tracking issue, later runs stop finding it and start opening duplicates again.

Note that GitHub does not send notifications for an edit to an issue body, so a refreshed report is quiet by design. Watch the scheduled workflow itself if you want to be told about every run.

### Performance Tuning

```yaml
timeout: '30'        # Timeout per link in seconds
max-redirects: '5'   # Maximum redirects to follow
```

## Integration Examples

### Replacing Lychee

**Before (using lychee):**
```yaml
- name: Link Checker
  uses: lycheeverse/lychee-action@v2
  with:
    fail: false
    args: --accept 403,503 *.html
```

**After (using AI-powered link checker):**
```yaml
- name: AI-Powered Link Checker
  uses: QuantEcon/action-link-checker@v1
  with:
    html-path: '.'
    fail-on-broken: 'false'
    silent-codes: '403,503'
    ai-suggestions: 'true'
    create-issue: 'true'
```

### MyST Markdown Projects

For Jupyter Book projects:

```yaml
- name: Build Jupyter Book
  run: jupyter-book build lectures/

- name: Check links in built documentation
  uses: QuantEcon/action-link-checker@v1
  with:
    html-path: './lectures/_build/html'
    mode: 'full'
    ai-suggestions: 'true'
```

## Outputs

Use action outputs in subsequent workflow steps:

```yaml
- name: Check links
  id: link-check
  uses: QuantEcon/action-link-checker@v1
  with:
    fail-on-broken: 'false'

- name: Report results
  run: |
    echo "Broken links: ${{ steps.link-check.outputs.broken-link-count }}"
    echo "Redirects: ${{ steps.link-check.outputs.redirect-count }}"
    echo "AI suggestions available: ${{ steps.link-check.outputs.ai-suggestions != '' }}"
```

## Permissions

Required workflow permissions depend on features used:

```yaml
permissions:
  contents: read          # Always required
  issues: write          # For create-issue: 'true'
  pull-requests: write   # For PR comments
  actions: read          # For create-artifact: 'true'
```

## Inputs

| Input | Description | Required | Default |
|-------|-------------|----------|---------|
| `html-path` | Path to HTML files directory | No | `./_build/html` |
| `mode` | Scan mode: `full` or `changed` | No | `full` |
| `silent-codes` | HTTP codes to silently report (`0` = no response) | No | `403,503` |
| `ignore-patterns` | Regex patterns for URLs to skip entirely, one per line | No | *(none)* |
| `fail-on-broken` | Fail workflow on broken links | No | `true` |
| `ai-suggestions` | Enable AI-powered suggestions | No | `true` |
| `create-issue` | Create GitHub issue for broken links | No | `false` |
| `issue-title` | Title for created issues | No | `Broken Links Found in Documentation` |
| `update-existing-issue` | Refresh the open issue with this title instead of opening a duplicate | No | `true` |
| `create-artifact` | Create workflow artifact | No | `false` |
| `artifact-name` | Name for workflow artifact | No | `link-check-report` |
| `notify` | Users to assign to created issue | No | `` |
| `timeout` | Timeout per link (seconds) | No | `45` |
| `max-redirects` | Maximum redirects to follow | No | `5` |

## Outputs

| Output | Description |
|--------|-------------|
| `broken-links-found` | Whether broken links were found |
| `broken-link-count` | Number of broken links |
| `redirect-count` | Number of redirects found |
| `ignored-count` | Number of links skipped by `ignore-patterns` |
| `link-details` | Detailed broken link information |
| `ai-suggestions` | AI-powered improvement suggestions |
| `issue-url` | URL of the created or updated GitHub issue |
| `issue-updated` | Whether an existing issue was reused rather than a new one opened |
| `artifact-path` | Path to created artifact file |

## Best Practices

1. **Weekly Scans**: Use scheduled workflows for comprehensive link checking
2. **PR Validation**: Use changed-file mode for efficient PR validation
3. **Status Code Configuration**: Adjust silent codes based on your links' typical behavior
4. **AI Suggestions**: Review and apply AI suggestions to improve link quality
5. **Issue Management**: Use automatic issue creation for tracking broken links
6. **Performance**: Set appropriate timeouts based on your link destinations

## Troubleshooting

### Common Issues

1. **Timeout Errors**: Increase `timeout` value for slow-responding sites (default is now 45s)
2. **False Positives**: The action automatically detects major sites that block bots (Netflix, Amazon, etc.)
3. **Rate Limiting**: Add `429` to `silent-codes` for rate-limited sites
4. **Bot Blocking**: Legitimate sites blocking automated requests are automatically handled gracefully
5. **Large Repositories**: Use `changed` mode for PR workflows

### False Positive Mitigation

If legitimate links are being flagged as broken:

1. **Check if it's a major site**: Netflix, Amazon, Facebook, etc. are automatically detected as likely bot-blocked
2. **Increase timeout**: Use `timeout: '60'` for slower sites like tutorials or educational content
3. **Add to silent codes**: If a site consistently returns specific error codes, add them to `silent-codes`
4. **Review AI suggestions**: The action provides constructive fix suggestions rather than suggesting removal

### Debug Output

The action provides detailed logging including:
- Number of files scanned
- Links found per file
- Status codes and errors
- AI suggestion reasoning

## Migration from Lychee

This action can directly replace `lychee` workflows with enhanced functionality:

1. Replace `lycheeverse/lychee-action` with this action
2. Update input parameters (see comparison above)  
3. Add AI suggestions and issue creation features
4. Configure silent status codes as needed

The enhanced AI capabilities provide value beyond basic link checking by suggesting improvements and maintaining link quality over time.