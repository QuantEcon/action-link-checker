#!/usr/bin/env python3
"""
Result formatter for link check results
"""
import json
import sys

def format_broken_results(data):
    """Format broken link results for display"""
    results = []
    for result in data['broken_results']:
        error_info = f" ({result['error']})" if result['error'] else ""
        results.append(f"❌ {result['url']} - Status: {result['status_code']}{error_info}")
        if result['text']:
            results.append(f"   Link text: {result['text']}")
    return '\n'.join(results)

def format_redirect_results(data):
    """Format redirect results for display"""
    results = []
    for result in data['redirect_results']:
        results.append(f"🔄 {result['url']} -> {result['final_url']} ({result['redirect_count']} redirects)")
    return '\n'.join(results)

def format_ai_suggestions(data):
    """Format AI suggestions for display"""
    results = []
    for suggestion in data['ai_suggestions']:
        results.append(f"🤖 {suggestion['original_url']}")
        results.append(f"   Issue: {suggestion['issue']}")
        for s in suggestion['suggestions']:
            results.append(f"   💡 {s['type']}: {s['url']}")
            results.append(f"      Reason: {s['reason']}")
    return '\n'.join(results)

def main():
    if len(sys.argv) != 2:
        print("Usage: python3 format_results.py <mode>", file=sys.stderr)
        print("Modes: broken, redirect, ai", file=sys.stderr)
        sys.exit(1)
    
    mode = sys.argv[1]
    
    try:
        data = json.load(sys.stdin)
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}", file=sys.stderr)
        sys.exit(1)
    
    if mode == "broken":
        print(format_broken_results(data))
    elif mode == "redirect":
        print(format_redirect_results(data))
    elif mode == "ai":
        print(format_ai_suggestions(data))
    else:
        print(f"Unknown mode: {mode}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()