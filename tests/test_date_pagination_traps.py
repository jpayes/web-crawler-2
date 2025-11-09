#!/usr/bin/env python3
"""
Test cases for date archive and pagination trap detection in the web crawler.
These tests ensure the crawler won't get stuck in infinite loops on date-based
archives and news pagination patterns.
"""

import unittest
import sys
import os
from urllib.parse import urlparse

# Add the parent directory to the path so we can import scraper
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scraper import check_for_traps


class TestDatePaginationTraps(unittest.TestCase):
    """Test cases for date archive and pagination trap detection."""
    
    def setUp(self):
        """Set up test fixtures."""
        pass
    
    def test_date_archive_traps_yyyy_mm_format(self):
        """Test that YYYY/MM date archive URLs are blocked."""
        date_archive_urls = [
            "https://www.informatics.uci.edu/2014/07",
            "https://www.informatics.uci.edu/2015/01",
            "https://www.informatics.uci.edu/2016/12",
            "https://www.informatics.uci.edu/2020/03",
            "https://www.informatics.uci.edu/2023/09",
            "https://cs.uci.edu/2019/05",
            "https://ics.uci.edu/2021/11"
        ]
        
        for url in date_archive_urls:
            with self.subTest(url=url):
                parsed = urlparse(url)
                result = check_for_traps(url, parsed)
                self.assertFalse(result, f"Date archive URL should be blocked: {url}")
    
    def test_date_archive_with_pagination_blocked(self):
        """Test that date archive URLs with pagination are blocked."""
        date_pagination_urls = [
            "https://www.informatics.uci.edu/2016/10/page/2",
            "https://www.informatics.uci.edu/2017/02/page/2",
            "https://www.informatics.uci.edu/2018/03/page/2",
            "https://www.informatics.uci.edu/2020/07/page/2",
            "https://www.informatics.uci.edu/2021/03/page/2"
        ]
        
        for url in date_pagination_urls:
            with self.subTest(url=url):
                parsed = urlparse(url)
                result = check_for_traps(url, parsed)
                self.assertFalse(result, f"Date archive with pagination should be blocked: {url}")
    
    def test_news_pagination_traps(self):
        """Test that news pagination URLs are blocked."""
        news_pagination_urls = [
            "https://www.informatics.uci.edu/very-top-footer-menu-items/news/page/2",
            "https://www.informatics.uci.edu/very-top-footer-menu-items/news/page/10",
            "https://www.informatics.uci.edu/very-top-footer-menu-items/news/page/53",
            "https://www.informatics.uci.edu/very-top-footer-menu-items/news"
        ]
        
        for url in news_pagination_urls:
            with self.subTest(url=url):
                parsed = urlparse(url)
                result = check_for_traps(url, parsed)
                self.assertFalse(result, f"News pagination URL should be blocked: {url}")
    
    def test_general_pagination_limits(self):
        """Test that general pagination is limited to page 5."""
        high_pagination_urls = [
            "https://ics.uci.edu/news/page/6",
            "https://ics.uci.edu/blog/page/10",
            "https://ics.uci.edu/events/page/15",
            "https://cs.uci.edu/articles/page/20"
        ]
        
        for url in high_pagination_urls:
            with self.subTest(url=url):
                parsed = urlparse(url)
                result = check_for_traps(url, parsed)
                self.assertFalse(result, f"High pagination URL should be blocked: {url}")
    
    def test_allowed_low_pagination(self):
        """Test that low pagination (1-5) is allowed."""
        allowed_pagination_urls = [
            "https://ics.uci.edu/news/page/1",
            "https://ics.uci.edu/blog/page/2",
            "https://ics.uci.edu/events/page/3",
            "https://cs.uci.edu/articles/page/4",
            "https://informatics.uci.edu/research/page/5"
        ]
        
        for url in allowed_pagination_urls:
            with self.subTest(url=url):
                parsed = urlparse(url)
                result = check_for_traps(url, parsed)
                self.assertTrue(result, f"Low pagination URL should be allowed: {url}")
    
    def test_query_parameter_pagination_limits(self):
        """Test that query parameter pagination is limited to 15."""
        high_query_pagination_urls = [
            "https://ics.uci.edu/search?page=16",
            "https://ics.uci.edu/results?page=20",
            "https://ics.uci.edu/list?start=50",
            "https://ics.uci.edu/archive?offset=100"
        ]
        
        for url in high_query_pagination_urls:
            with self.subTest(url=url):
                parsed = urlparse(url)
                result = check_for_traps(url, parsed)
                self.assertFalse(result, f"High query pagination URL should be blocked: {url}")
    
    def test_allowed_query_parameter_pagination(self):
        """Test that low query parameter pagination (1-15) is allowed."""
        allowed_query_pagination_urls = [
            "https://ics.uci.edu/search?page=1",
            "https://ics.uci.edu/results?page=10",
            "https://ics.uci.edu/list?start=5",
            "https://ics.uci.edu/archive?offset=8"
        ]
        
        for url in allowed_query_pagination_urls:
            with self.subTest(url=url):
                parsed = urlparse(url)
                result = check_for_traps(url, parsed)
                self.assertTrue(result, f"Low query pagination URL should be allowed: {url}")
    
    def test_year_month_dash_format_blocked(self):
        """Test that YYYY-MM format dates are blocked."""
        year_month_dash_urls = [
            "https://stat.uci.edu/seminar/2023-09/details",
            "https://ics.uci.edu/events/2024-01",
            "https://cs.uci.edu/archive/2022-12/papers"
        ]
        
        for url in year_month_dash_urls:
            with self.subTest(url=url):
                parsed = urlparse(url)
                result = check_for_traps(url, parsed)
                self.assertFalse(result, f"YYYY-MM format URL should be blocked: {url}")
    
    def test_calendar_related_traps(self):
        """Test that calendar-related URLs are blocked."""
        calendar_urls = [
            "https://ics.uci.edu/calendar/month",
            "https://cs.uci.edu/events/tribe-events",
            "https://informatics.uci.edu/eventdisplay?date=2023-01-01",
            "https://stat.uci.edu/calendar/tribe-bar-date=2023-01"
        ]
        
        for url in calendar_urls:
            with self.subTest(url=url):
                parsed = urlparse(url)
                result = check_for_traps(url, parsed)
                self.assertFalse(result, f"Calendar-related URL should be blocked: {url}")
    
    def test_valid_urls_not_blocked(self):
        """Test that valid URLs are not blocked by date/pagination traps."""
        valid_urls = [
            "https://ics.uci.edu/",
            "https://cs.uci.edu/about",
            "https://informatics.uci.edu/faculty",
            "https://stat.uci.edu/research",
            "https://www.ics.uci.edu/~faculty/contact",
            "https://student-council.ics.uci.edu/events",  # events without pagination
            "https://www.informatics.uci.edu/news",  # news without pagination
            "https://ics.uci.edu/2023/annual-report"  # not YYYY/MM format
        ]
        
        for url in valid_urls:
            with self.subTest(url=url):
                parsed = urlparse(url)
                result = check_for_traps(url, parsed)
                self.assertTrue(result, f"Valid URL should not be blocked: {url}")
    
    def test_edge_cases(self):
        """Test edge cases for date and pagination detection."""
        edge_case_urls = [
            # These should be blocked
            ("https://ics.uci.edu/2024/01/", False, "YYYY/MM with trailing slash"),
            ("https://ics.uci.edu/archive/2023/12", False, "YYYY/MM in path"),
            ("https://ics.uci.edu/page/5", True, "Page 5 (boundary case - allowed)"),
            ("https://ics.uci.edu/page/6", False, "Page 6 (should be blocked)"),
            
            # These should be allowed
            ("https://ics.uci.edu/course/cs2024", True, "Course code, not date"),
            ("https://ics.uci.edu/year2023/summary", True, "Year in text, not date path"),
            ("https://ics.uci.edu/project/page5", True, "Page in text, not pagination"),
        ]
        
        for url, expected, description in edge_case_urls:
            with self.subTest(url=url, desc=description):
                parsed = urlparse(url)
                result = check_for_traps(url, parsed)
                self.assertEqual(result, expected, f"{description}: {url}")


if __name__ == '__main__':
    # Run the tests
    unittest.main(verbosity=2)