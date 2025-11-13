#!/usr/bin/env python3
"""
Test improved trap detection against previously trapped URLs
"""

import sys
import re
from urllib.parse import urlparse

# Import the trap detection function from scraper
sys.path.append('/home/aaalras1/web-crawler-2')
from scraper import check_for_traps

def test_trap_detection():
    """Test trap detection against URLs that previously caused traps"""
    
    # URLs that previously trapped us (from ISG, WICS, NGS)
    trap_urls = [
        # ISG date event traps
        "https://isg.ics.uci.edu/events/2019-09-19",
        "https://isg.ics.uci.edu/events/2025-01-25", 
        "https://isg.ics.uci.edu/events/2020-05-14",
        "https://isg.ics.uci.edu/events/2023-08-24",
        "https://isg.ics.uci.edu/events/2018-11-17",
        "https://isg.ics.uci.edu/events/2024-03-25",
        
        # WICS date event traps
        "https://wics.ics.uci.edu/events/2024-04-14",
        "https://wics.ics.uci.edu/events/2023-10-18", 
        "https://wics.ics.uci.edu/events/2022-10-04",
        "https://wics.ics.uci.edu/events/2023-01-19",
        "https://wics.ics.uci.edu/events/2025-03-12",
        
        # WICS social share traps
        "https://wics.ics.uci.edu/wics-spring-quarter-week-7-slalom-tour/?share=facebook",
        "https://wics.ics.uci.edu/fall-quarter-2016-first-general-meeting/?share=twitter",
        "https://wics.ics.uci.edu/fall-2022-week-1-general-meeting-paint-night-social/?share=facebook",
        "http://wics.ics.uci.edu/week-6-socal-gas-company/?share=twitter",
        "https://wics.ics.uci.edu/events/2024-11-04/?ical=1",
        
        # NGS tag page traps  
        "https://ngs.ics.uci.edu/tag/compelling-experiences",
        "https://ngs.ics.uci.edu/tag/should",
        "https://ngs.ics.uci.edu/tag/computational-storytelling",
        "https://ngs.ics.uci.edu/tag/life-lessons",
        
        # NGS pagination traps
        "https://ngs.ics.uci.edu/category/entrepreneurism/page/2",
        "https://ngs.ics.uci.edu/category/experiential-computing/page/5",
        "https://ngs.ics.uci.edu/author/ramesh/page/5", 
        "https://ngs.ics.uci.edu/tag/photos/page/2",
        "https://ngs.ics.uci.edu/blog/page/3",
    ]
    
    # URLs that should be allowed (legitimate content)
    allowed_urls = [
        # ISG legitimate pages
        "https://isg.ics.uci.edu/event/jiawei-han-distinguished-lecture",
        "https://isg.ics.uci.edu/event/amr-el-abbadi-ucsb-practical-approaches-for-private-and-scalable-information-data-management-systems",
        "https://isg.ics.uci.edu/faculty2/wail-yousef-alkowaileet",
        
        # WICS legitimate pages
        "https://wics.ics.uci.edu/spring-2024-week-10-wics-banquet", 
        "https://wics.ics.uci.edu/winter-2023-week-6-wics-x-costar-group",
        "https://wics.ics.uci.edu/winter-quarter-2017-week-1-general-meeting",
        
        # NGS legitimate pages
        "https://ngs.ics.uci.edu/real-time-search",
        "https://ngs.ics.uci.edu/abstractions-and-experiential-computing", 
        "http://ngs.ics.uci.edu/computer-vision-for-developing-countries",
        "https://ngs.ics.uci.edu/obama-era-of-responsible-optimism",
        
        # Main domain pages
        "https://www.ics.uci.edu/",
        "https://www.informatics.uci.edu/",
        "https://www.stat.uci.edu/",
    ]
    
    print("=== Testing Improved Trap Detection ===\n")
    
    # Test trap URLs (should be blocked)
    print("Testing URLs that should be BLOCKED (traps):")
    blocked_count = 0
    for url in trap_urls:
        parsed = urlparse(url)
        is_allowed = check_for_traps(url, parsed)
        status = "BLOCKED" if not is_allowed else "ALLOWED (BAD)"
        print(f"  {status}: {url}")
        if not is_allowed:
            blocked_count += 1
    
    print(f"\nTrap URLs blocked: {blocked_count}/{len(trap_urls)} ({blocked_count/len(trap_urls)*100:.1f}%)")
    
    # Test legitimate URLs (should be allowed)  
    print(f"\nTesting URLs that should be ALLOWED (legitimate):")
    allowed_count = 0
    for url in allowed_urls:
        parsed = urlparse(url)
        is_allowed = check_for_traps(url, parsed)
        status = "ALLOWED" if is_allowed else "BLOCKED (BAD)"
        print(f"  {status}: {url}")
        if is_allowed:
            allowed_count += 1
            
    print(f"\nLegitimate URLs allowed: {allowed_count}/{len(allowed_urls)} ({allowed_count/len(allowed_urls)*100:.1f}%)")
    
    # Summary
    print(f"\n=== SUMMARY ===")
    print(f"Trap detection accuracy: {blocked_count}/{len(trap_urls)} traps blocked")
    print(f"False positive rate: {len(allowed_urls)-allowed_count}/{len(allowed_urls)} legitimate URLs blocked")
    
    if blocked_count == len(trap_urls) and allowed_count == len(allowed_urls):
        print("All traps blocked, all legitimate URLs allowed")
        return True
    else:
        print("Need to improve trap detection patterns")
        return False

if __name__ == "__main__":
    test_trap_detection()