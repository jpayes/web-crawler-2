#!/usr/bin/env python3
"""
Diagnostic tool to identify which pages are generating trap URLs.
This will help us understand the source of repeated trap links.
"""

import sys
import os
from urllib.parse import urlparse, urljoin
from lxml import html, etree
import requests
import re

# Add the parent directory to the path so we can import scraper
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scraper import check_for_traps, extract_links_from_tree

def analyze_page_for_traps(url, max_traps_to_show=5):
    """Analyze a single page to see what trap URLs it generates."""
    print(f"\n=== ANALYZING: {url} ===")
    
    try:
        # Fetch the page (using a simple request for testing)
        headers = {'User-Agent': 'Mozilla/5.0 (compatible; TrapAnalyzer/1.0)'}
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code != 200:
            print(f"❌ Failed to fetch (status {response.status_code})")
            return
        
        # Parse HTML and extract links
        try:
            tree = html.fromstring(response.content)
        except:
            print("❌ Failed to parse HTML")
            return
            
        # Extract all links from this page
        all_links = extract_links_from_tree(tree, url)
        
        # Check which ones are traps
        trap_urls = []
        valid_urls = []
        
        for link in all_links[:50]:  # Limit to first 50 links to avoid spam
            try:
                parsed = urlparse(link)
                if check_for_traps(link, parsed):
                    valid_urls.append(link)
                else:
                    trap_urls.append(link)
            except:
                pass
        
        print(f"📊 Found {len(all_links)} total links")
        print(f"✅ Valid links: {len(valid_urls)}")
        print(f"🚫 Trap links: {len(trap_urls)}")
        
        if trap_urls:
            print(f"\n🚫 TRAP URLS (showing first {max_traps_to_show}):")
            for trap_url in trap_urls[:max_traps_to_show]:
                print(f"  - {trap_url}")
            
            if len(trap_urls) > max_traps_to_show:
                print(f"  ... and {len(trap_urls) - max_traps_to_show} more")
        
        return {
            'url': url,
            'total_links': len(all_links),
            'trap_count': len(trap_urls),
            'trap_urls': trap_urls[:max_traps_to_show]
        }
        
    except Exception as e:
        print(f"❌ Error analyzing {url}: {e}")
        return None

def main():
    """Analyze common UCI pages that might be generating trap links."""
    
    # Common UCI pages that are likely sources of trap links
    test_pages = [
        "https://www.stat.uci.edu",
        "https://www.stat.uci.edu/seminar-series",
        "https://ics.uci.edu",
        "https://ics.uci.edu/events",
        "https://cs.uci.edu",
        "https://www.informatics.uci.edu"
    ]
    
    print("🔍 TRAP URL SOURCE ANALYSIS")
    print("=" * 50)
    
    results = []
    for page in test_pages:
        result = analyze_page_for_traps(page)
        if result:
            results.append(result)
    
    print("\n" + "=" * 50)
    print("📋 SUMMARY - Pages generating the most traps:")
    
    # Sort by trap count
    results.sort(key=lambda x: x['trap_count'], reverse=True)
    
    for result in results:
        if result['trap_count'] > 0:
            print(f"🚫 {result['url']}: {result['trap_count']} trap links")
            for trap in result['trap_urls']:
                print(f"    - {trap}")

if __name__ == '__main__':
    main()