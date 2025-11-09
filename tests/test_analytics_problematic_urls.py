#!/usr/bin/env python3
"""
Quick test script to verify that the problematic URLs from analytics
are now properly blocked by the trap detection system.
"""

import sys
import os
from urllib.parse import urlparse

# Add the parent directory to the path so we can import scraper
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scraper import check_for_traps

def test_problematic_urls():
    """Test the specific URLs that caused issues in your analytics."""
    
    print("Testing problematic URLs from your analytics data...\n")
    
    # URLs that should be BLOCKED (caused infinite loops)
    problematic_urls = [
        # News pagination that went to page 53
        "https://www.informatics.uci.edu/very-top-footer-menu-items/news/page/2",
        "https://www.informatics.uci.edu/very-top-footer-menu-items/news/page/10",
        "https://www.informatics.uci.edu/very-top-footer-menu-items/news/page/53",
        
        # Date archives with pagination
        "https://www.informatics.uci.edu/2016/10/page/2",
        "https://www.informatics.uci.edu/2017/02/page/2",
        "https://www.informatics.uci.edu/2018/03/page/2",
        
        # Date archives (should be blocked)
        "https://www.informatics.uci.edu/2014/07",
        "https://www.informatics.uci.edu/2015/01",
        "https://www.informatics.uci.edu/2020/04",
        "https://www.informatics.uci.edu/2023/09",
    ]
    
    print("🚫 URLs that should be BLOCKED:")
    all_blocked = True
    for url in problematic_urls:
        parsed = urlparse(url)
        is_allowed = check_for_traps(url, parsed)
        status = "✅ BLOCKED" if not is_allowed else "❌ ALLOWED (PROBLEM!)"
        print(f"  {status}: {url}")
        if is_allowed:
            all_blocked = False
    
    print()
    
    # URLs that should be ALLOWED (legitimate content)
    legitimate_urls = [
        "https://www.informatics.uci.edu/",
        "https://www.informatics.uci.edu/news",  # Main news page without pagination
        "https://student-council.ics.uci.edu/contact",
        "https://student-council.ics.uci.edu/events",  # Events without pagination
        "https://ics.uci.edu/news/page/1",  # Low pagination should be OK
        "https://ics.uci.edu/blog/page/3",  # Low pagination should be OK
    ]
    
    print("✅ URLs that should be ALLOWED:")
    all_allowed = True
    for url in legitimate_urls:
        parsed = urlparse(url)
        is_allowed = check_for_traps(url, parsed)
        status = "✅ ALLOWED" if is_allowed else "❌ BLOCKED (PROBLEM!)"
        print(f"  {status}: {url}")
        if not is_allowed:
            all_allowed = False
    
    print()
    
    # Summary
    if all_blocked and all_allowed:
        print("🎉 SUCCESS: All trap detection working correctly!")
        print("Your crawler should no longer get stuck in infinite loops.")
    else:
        print("⚠️  WARNING: Some URLs are not being handled correctly.")
        print("You may need to adjust the trap detection logic.")
    
    return all_blocked and all_allowed

if __name__ == '__main__':
    success = test_problematic_urls()
    sys.exit(0 if success else 1)