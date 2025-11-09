#!/usr/bin/env python3
"""
Quick test to verify the date pattern fix allows PDFs but blocks date archives
"""

import sys
import os
from urllib.parse import urlparse

# Add the parent directory to the path so we can import scraper
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scraper import check_for_traps

def test_date_pattern_fix():
    """Test that PDFs are allowed but date archives are still blocked."""
    
    print("Testing date pattern fix...\n")
    
    # URLs that should be ALLOWED (PDF files and other content)
    should_be_allowed = [
        "http://isg.ics.uci.edu/wp-content/uploads/2020/07/20-IoTExpunge_sensor_data_deletion_codaspy.pdf",
        "http://isg.ics.uci.edu/wp-content/uploads/2019/11/2019-IoT_Notary_Tech_report-1.pdf", 
        "http://isg.ics.uci.edu/wp-content/uploads/2020/07/19-Sharma_TDSC_Privacy_Secret-sharing_MapReduce.pdf",
        "https://ics.uci.edu/files/2023/05/research-paper.pdf",
        "https://cs.uci.edu/content/2022/12/announcement.html",
    ]
    
    print("✅ URLs that should be ALLOWED (PDFs and files):")
    all_allowed = True
    for url in should_be_allowed:
        parsed = urlparse(url)
        is_allowed = check_for_traps(url, parsed)
        status = "✅ ALLOWED" if is_allowed else "❌ BLOCKED (PROBLEM!)"
        print(f"  {status}: {url}")
        if not is_allowed:
            all_allowed = False
    
    print()
    
    # URLs that should still be BLOCKED (date archive pages)
    should_be_blocked = [
        "https://www.informatics.uci.edu/2020/07",
        "https://www.informatics.uci.edu/2020/07/",  # with trailing slash
        "https://www.informatics.uci.edu/2019/11",
        "https://cs.uci.edu/2023/05",
        "https://ics.uci.edu/2022/12/",
    ]
    
    print("🚫 URLs that should still be BLOCKED (date archives):")
    all_blocked = True
    for url in should_be_blocked:
        parsed = urlparse(url)
        is_allowed = check_for_traps(url, parsed)
        status = "✅ BLOCKED" if not is_allowed else "❌ ALLOWED (PROBLEM!)"
        print(f"  {status}: {url}")
        if is_allowed:
            all_blocked = False
    
    print()
    
    # Summary
    if all_allowed and all_blocked:
        print("🎉 SUCCESS: Date pattern fix working correctly!")
        print("PDFs and files are allowed, date archives are still blocked.")
    else:
        print("⚠️  WARNING: Date pattern needs more adjustment.")
    
    return all_allowed and all_blocked

if __name__ == '__main__':
    success = test_date_pattern_fix()
    sys.exit(0 if success else 1)