# Usage Examples for AI-Powered Link Checker

This document provides practical examples for different use cases of the AI-Powered Link Checker action.

## Example 1: Weekly Scheduled Link Check

Replace the existing lychee-based link checker with AI-powered functionality:

```yaml
name: Weekly Link Check
on:
  schedule:
    # Run every Monday at 9 AM UTC (early morning in Australia)
    - cron: '0 9 * * 1'
  workflow_dispatch:

permissions:
  contents: read
  issues: write

jobs:
  link-check:
    name: AI-Powered Link Checking
    runs-on: ubuntu-latest
    steps:
      # Checkout the published site (HTML)
      - name: Checkout
        uses: actions/checkout@v4
        with:
          ref: gh-pages
      
      - name: AI-Powered Link Check
        uses: QuantEcon/meta/.github/actions/link-checker@main
        with:
          html-path: '.'
          mode: 'full'
          fail-on-broken: 'false'  # Don't fail on schedule, just report
          ai-suggestions: 'true'
          silent-codes: '403,503,429'
          create-issue: 'true'
          issue-title: 'Weekly Link Check Report'
          notify: 'maintainer1,maintainer2'
          create-artifact: 'true'
          artifact-name: 'weekly-link-report'
```

## Example 2: Pull Request Link Validation

Check links in documentation changes during PR review:

```yaml
name: PR Documentation Check
on:
  pull_request:
    branches: [ main ]
    paths: 
      - 'lectures/**'
      - '_build/**'
      - '**.md'

permissions:
  contents: read
  pull-requests: write

jobs:
  docs-and-links:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install jupyter-book myst-parser
      
      - name: Build Jupyter Book
        run: |
          jupyter-book build lectures/
      
      - name: Check links in changed files
        uses: QuantEcon/meta/.github/actions/link-checker@main
        with:
          html-path: './lectures/_build/html'
          mode: 'changed'  # Only check files changed in this PR
          fail-on-broken: 'true'  # Fail PR if broken links
          ai-suggestions: 'true'
          silent-codes: '403,503'
          timeout: '20'
```

## Example 3: Comprehensive Documentation Build

Full documentation build with link checking and AI suggestions:

```yaml
name: Build and Validate Documentation
on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

permissions:
  contents: read
  issues: write
  pull-requests: write
  actions: read

jobs:
  build-and-check:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
      
      - name: Build documentation
        run: |
          jupyter-book build .
      
      - name: AI-Powered Link Check
        uses: QuantEcon/meta/.github/actions/link-checker@main
        with:
          html-path: './_build/html'
          mode: ${{ github.event_name == 'pull_request' && 'changed' || 'full' }}
          fail-on-broken: ${{ github.event_name == 'push' }}
          ai-suggestions: 'true'
          create-issue: ${{ github.event_name == 'push' }}
          create-artifact: 'true'
          silent-codes: '403,503,429,502'
          issue-title: 'Documentation Link Issues - ${{ github.ref_name }}'
          notify: 'docs-team,maintainers'
          artifact-name: 'link-check-report-${{ github.run_number }}'
```

## Example 4: Multi-Project Link Checking

Check links across multiple related documentation projects:

```yaml
name: Cross-Project Link Check
on:
  schedule:
    - cron: '0 2 * * 0'  # Sunday at 2 AM UTC
  workflow_dispatch:

jobs:
  check-projects:
    strategy:
      matrix:
        project:
          - { name: 'python-programming', ref: 'gh-pages' }
          - { name: 'datascience', ref: 'gh-pages' }
          - { name: 'game-theory', ref: 'gh-pages' }
    runs-on: ubuntu-latest
    steps:
      - name: Checkout ${{ matrix.project.name }}
        uses: actions/checkout@v4
        with:
          repository: 'QuantEcon/${{ matrix.project.name }}.myst'
          ref: ${{ matrix.project.ref }}
      
      - name: Link Check - ${{ matrix.project.name }}
        uses: QuantEcon/meta/.github/actions/link-checker@main
        with:
          html-path: '.'
          fail-on-broken: 'false'
          ai-suggestions: 'true'
          create-issue: 'true'
          issue-title: 'Link Check Report - ${{ matrix.project.name }}'
          notify: 'quantecon-team'
```

## Example 5: Advanced Configuration with Custom Timeouts

For projects with many external links or slow-responding sites:

```yaml
- name: Patient Link Checker
  uses: QuantEcon/meta/.github/actions/link-checker@main
  with:
    html-path: './_build/html'
    timeout: '60'           # 60 seconds per link
    max-redirects: '10'     # Follow up to 10 redirects
    silent-codes: '403,503,429,502,520,521,522,523,524'
    fail-on-broken: 'false'
    ai-suggestions: 'true'
    create-issue: 'true'
    issue-title: 'Comprehensive Link Analysis'
```

## Example 6: Development Mode with Artifacts

For debugging and development of documentation:

```yaml
- name: Development Link Check
  uses: QuantEcon/meta/.github/actions/link-checker@main
  with:
    html-path: './_build/html'
    fail-on-broken: 'false'  # Don't fail during development
    ai-suggestions: 'true'
    create-artifact: 'true'  # Always create artifacts for review
    artifact-name: 'dev-link-report'
    timeout: '15'
```

## Example 7: Integration with Existing Warning Check

Combine with the existing warning checker for comprehensive quality control:

```yaml
name: Documentation Quality Check
on:
  pull_request:
    branches: [ main ]

jobs:
  quality-check:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      pull-requests: write
    steps:
      - name: Checkout
        uses: actions/checkout@v4
      
      - name: Build documentation
        run: jupyter-book build .
      
      - name: Check for Python warnings
        uses: QuantEcon/meta/.github/actions/check-warnings@main
        with:
          html-path: './_build/html'
          fail-on-warning: 'true'
      
      - name: Check for broken links
        uses: QuantEcon/meta/.github/actions/link-checker@main
        with:
          html-path: './_build/html'
          mode: 'changed'
          fail-on-broken: 'true'
          ai-suggestions: 'true'
```

## Example 8: Silent Monitoring

For continuous monitoring without disrupting development:

```yaml
name: Silent Link Monitoring
on:
  schedule:
    - cron: '0 12 * * *'  # Daily at noon

jobs:
  monitor:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4
        with:
          ref: gh-pages
      
      - name: Silent Link Check
        uses: QuantEcon/meta/.github/actions/link-checker@main
        with:
          html-path: '.'
          fail-on-broken: 'false'  # Never fail
          ai-suggestions: 'true'
          create-artifact: 'true'   # Just create reports
          artifact-name: 'daily-link-monitoring'
          silent-codes: '403,503,429,502,520,521,522,523,524'
```

## Migration Guide from Lychee

### Before (using lychee):
```yaml
- name: Link Checker
  id: lychee
  uses: lycheeverse/lychee-action@v2
  with:
    fail: false
    args: --accept 403,503 *.html

- name: Create Issue From File
  if: steps.lychee.outputs.exit_code != 0
  uses: peter-evans/create-issue-from-file@v5
  with:
    title: Link Checker Report
    content-filepath: ./lychee/out.md
    labels: report, automated issue, linkchecker
```

### After (using AI-powered link checker):
```yaml
- name: AI-Powered Link Checker
  uses: QuantEcon/meta/.github/actions/link-checker@main
  with:
    html-path: '.'
    fail-on-broken: 'false'
    silent-codes: '403,503'
    ai-suggestions: 'true'
    create-issue: 'true'
    issue-title: 'AI-Enhanced Link Check Report'
    notify: 'maintainer-team'
```

## Benefits Over Lychee

1. **AI Suggestions**: Automatically suggests fixes for broken links
2. **Redirect Optimization**: Recommends updating redirected links
3. **Better Integration**: Native GitHub Actions integration
4. **Flexible Reporting**: Multiple output formats (issues, artifacts, PR comments)
5. **Smart Filtering**: Context-aware link analysis
6. **Performance**: Configurable timeouts and rate limiting