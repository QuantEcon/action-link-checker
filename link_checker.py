#!/usr/bin/env python3
"""
AI-Powered Link Checker Script
Checks external links in HTML files and provides AI suggestions for improvements.
"""
import re
import sys
import requests
import urllib.parse
from bs4 import BeautifulSoup
import json
import time
import os
import argparse

def is_external_link(url):
    """Check if URL is external (starts with http/https)"""
    return url.startswith(('http://', 'https://'))

def is_likely_bot_blocked(url, response_content=None, status_code=None, error=None):
    """Detect if a site is likely blocking automated requests rather than being truly broken"""
    domain_indicators = [
        'netflix.com', 'amazon.com', 'facebook.com', 'twitter.com', 'instagram.com',
        'youtube.com', 'linkedin.com', 'pinterest.com', 'reddit.com', 'wikipedia.org'
    ]
    
    # Check for well-known legitimate domains that should be treated carefully
    legitimate_domains = [
        'python.org', 'jupyter.org', 'github.com', 'docs.python.org',
        'stackoverflow.com', 'readthedocs.org', 'arxiv.org', 'doi.org',
        'numpy.org', 'scipy.org', 'matplotlib.org', 'pandas.pydata.org'
    ]
    
    # Check if it's a major site that commonly blocks bots
    for indicator in domain_indicators:
        if indicator in url.lower():
            return True
    
    # Check if it's a legitimate domain that might be blocked by network restrictions
    for domain in legitimate_domains:
        if domain in url.lower() and error and 'Connection Error' in str(error):
            return True
    
    # Check for encoding issues which often indicate bot blocking
    if error and 'encoding' in str(error).lower():
        return True
    
    # Check for specific status codes that often indicate bot blocking rather than broken links
    bot_blocking_codes = [429, 451, 503]  # Rate limited, unavailable for legal reasons, service unavailable
    if status_code in bot_blocking_codes:
        return True
    
    return False

def check_link(url, timeout, max_redirects, silent_codes):
    """Check a single link and return status info"""
    # Use a more browser-like user agent to reduce blocking
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1'
    }
    
    try:
        # Set up session with redirects tracking
        session = requests.Session()
        session.max_redirects = max_redirects
        
        response = session.get(
            url, 
            timeout=timeout,
            allow_redirects=True,
            headers=headers
        )
        
        result = {
            'url': url,
            'status_code': response.status_code,
            'final_url': response.url,
            'redirect_count': len(response.history),
            'redirected': len(response.history) > 0,
            'broken': False,
            'silent': False,
            'error': None,
            'likely_bot_blocked': False
        }
        
        # Check if this looks like bot blocking
        result['likely_bot_blocked'] = is_likely_bot_blocked(url, response.text, response.status_code)
        
        # Check if status code should be silently reported
        if response.status_code in silent_codes:
            result['silent'] = True
        elif result['likely_bot_blocked']:
            # Don't mark as broken if likely bot blocked, mark as silent instead
            result['silent'] = True
        elif not response.ok:
            result['broken'] = True
        
        return result
        
    except requests.exceptions.Timeout:
        # Check if timeout on a likely legitimate site
        likely_blocked = is_likely_bot_blocked(url, error='timeout')
        return {
            'url': url, 'status_code': 0, 'final_url': url,
            'redirect_count': 0, 'redirected': False, 'broken': not likely_blocked,
            'silent': likely_blocked, 'error': 'Timeout', 'likely_bot_blocked': likely_blocked
        }
    except requests.exceptions.ConnectionError as e:
        # Check if connection error on a likely legitimate site  
        likely_blocked = is_likely_bot_blocked(url, error='Connection Error')
        return {
            'url': url, 'status_code': 0, 'final_url': url,
            'redirect_count': 0, 'redirected': False, 'broken': not likely_blocked,
            'silent': likely_blocked, 'error': 'Connection Error', 'likely_bot_blocked': likely_blocked
        }
    except UnicodeDecodeError as e:
        # Encoding issues often indicate bot blocking
        return {
            'url': url, 'status_code': 0, 'final_url': url,
            'redirect_count': 0, 'redirected': False, 'broken': False,
            'silent': True, 'error': f'Encoding issue: {str(e)}', 'likely_bot_blocked': True
        }
    except Exception as e:
        # Check if the error suggests bot blocking
        likely_blocked = is_likely_bot_blocked(url, error=str(e))
        return {
            'url': url, 'status_code': 0, 'final_url': url,
            'redirect_count': 0, 'redirected': False, 'broken': not likely_blocked,
            'silent': likely_blocked, 'error': str(e), 'likely_bot_blocked': likely_blocked
        }

def extract_links_from_html(file_path):
    """Extract all external links from HTML file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        soup = BeautifulSoup(content, 'html.parser')
        links = []
        
        # Find all anchor tags with href
        for tag in soup.find_all('a', href=True):
            href = tag['href']
            if is_external_link(href):
                # Store link with context
                links.append({
                    'url': href,
                    'text': tag.get_text(strip=True)[:100],  # First 100 chars
                    'line': None  # We could calculate line numbers if needed
                })
        
        return links
        
    except Exception as e:
        print(f"Error parsing {file_path}: {e}", file=sys.stderr)
        return []

def generate_ai_suggestions(broken_results, redirect_results):
    """Generate AI-powered suggestions for broken and redirected links"""
    suggestions = []
    
    # Simple rule-based AI suggestions (can be enhanced with actual AI services)
    for result in broken_results:
        url = result['url']
        
        # Skip suggestions for likely bot-blocked sites
        if result.get('likely_bot_blocked', False):
            continue
            
        suggestion = {
            'original_url': url,
            'issue': f"Broken link (Status: {result['status_code']})",
            'suggestions': []
        }
        
        # Only suggest fixes, not removals, for legitimate domains
        is_legitimate_domain = any(domain in url.lower() for domain in [
            'github.com', 'python.org', 'jupyter.org', 'readthedocs.org',
            'stackoverflow.com', 'wikipedia.org', 'arxiv.org', 'doi.org'
        ])
        
        # Common URL fixes
        if 'github.com' in url:
            # GitHub-specific suggestions
            if '/blob/master/' in url:
                new_url = url.replace('/blob/master/', '/blob/main/')
                suggestion['suggestions'].append({
                    'type': 'branch_update',
                    'url': new_url,
                    'reason': 'GitHub default branch changed from master to main'
                })
            if 'github.io' in url and 'http://' in url:
                new_url = url.replace('http://', 'https://')
                suggestion['suggestions'].append({
                    'type': 'https_upgrade',
                    'url': new_url,
                    'reason': 'GitHub Pages now requires HTTPS'
                })
        
        # Documentation site migrations
        elif 'readthedocs.org' in url and 'http://' in url:
            new_url = url.replace('http://', 'https://')
            suggestion['suggestions'].append({
                'type': 'https_upgrade',
                'url': new_url,
                'reason': 'Read the Docs now requires HTTPS'
            })
        
        # Python.org domain changes
        elif 'docs.python.org' in url:
            if '/2.7/' in url:
                new_url = url.replace('/2.7/', '/3/')
                suggestion['suggestions'].append({
                    'type': 'version_update',
                    'url': new_url,
                    'reason': 'Python 2.7 is deprecated, consider Python 3 documentation'
                })
        
        # General HTTPS upgrade (but be cautious with legitimate domains)
        elif url.startswith('http://') and 'localhost' not in url:
            new_url = url.replace('http://', 'https://')
            if is_legitimate_domain:
                suggestion['suggestions'].append({
                    'type': 'https_upgrade',
                    'url': new_url,
                    'reason': 'HTTPS is more secure and widely supported'
                })
            else:
                # For unknown domains, suggest checking manually
                suggestion['suggestions'].append({
                    'type': 'manual_check',
                    'url': new_url,
                    'reason': 'Try HTTPS version or verify the link manually'
                })
        
        # Only add suggestions if we have constructive fixes
        if suggestion['suggestions']:
            suggestions.append(suggestion)
    
    # Handle redirects
    for result in redirect_results:
        if result['redirect_count'] > 0:
            suggestion = {
                'original_url': result['url'],
                'issue': f"Redirected {result['redirect_count']} times",
                'suggestions': [{
                    'type': 'redirect_update',
                    'url': result['final_url'],
                    'reason': f'Update to final destination to avoid {result["redirect_count"]} redirect(s)'
                }]
            }
            suggestions.append(suggestion)
    
    return suggestions

def main():
    parser = argparse.ArgumentParser(description='Check links in HTML files')
    parser.add_argument('file_path', help='Path to HTML file')
    parser.add_argument('--timeout', type=int, default=45, help='Timeout in seconds (increased default for robustness)')
    parser.add_argument('--max-redirects', type=int, default=5, help='Maximum redirects')
    parser.add_argument('--silent-codes', default='403,503', help='Silent status codes')
    parser.add_argument('--ai-suggestions', action='store_true', help='Enable AI suggestions')
    
    args = parser.parse_args()
    
    silent_codes = [int(x.strip()) for x in args.silent_codes.split(',') if x.strip()]
    
    # Extract links
    links = extract_links_from_html(args.file_path)
    if not links:
        print(json.dumps({
            'broken_results': [], 'redirect_results': [], 
            'ai_suggestions': [], 'total_links': 0
        }))
        return
    
    broken_results = []
    redirect_results = []
    
    print(f"Checking {len(links)} links in {args.file_path} (timeout: {args.timeout}s)...", file=sys.stderr)
    
    # Check each link
    for i, link_info in enumerate(links):
        url = link_info['url']
        result = check_link(url, args.timeout, args.max_redirects, silent_codes)
        result['file'] = args.file_path
        result['text'] = link_info['text']
        
        if result['broken'] and not result['silent']:
            broken_results.append(result)
        elif result['redirected']:
            redirect_results.append(result)
        
        # Add small delay to be respectful to servers
        if i < len(links) - 1:
            time.sleep(0.2)  # Slightly increased delay to be more respectful
    
    # Generate AI suggestions
    ai_suggestions = []
    if args.ai_suggestions:
        ai_suggestions = generate_ai_suggestions(broken_results, redirect_results)
    
    # Output results
    print(json.dumps({
        'broken_results': broken_results,
        'redirect_results': redirect_results, 
        'ai_suggestions': ai_suggestions,
        'total_links': len(links)
    }))

if __name__ == "__main__":
    main()