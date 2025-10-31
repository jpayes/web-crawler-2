import re
from urllib.parse import urlparse, urljoin, urldefrag
from lxml import html
from bs4 import BeautifulSoup

# GLOBAL VAR for minimum words for a website to be useful
MIN_WORDS = 100
# common stop words provided in write-up
stopwords = {
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and",
    "any", "are", "aren't", "as", "at", "be", "because", "been", "before", "being",
    "below", "between", "both", "but", "by", "can't", "cannot", "could", "couldn't",
    "did", "didn't", "do", "does", "doesn't", "doing", "don't", "down", "during",
    "each", "few", "for", "from", "further", "had", "hadn't", "has", "hasn't",
    "have", "haven't", "having", "he", "he'd", "he'll", "he's", "her", "here",
    "here's", "hers", "herself", "him", "himself", "his", "how", "how's", "i",
    "i'd", "i'll", "i'm", "i've", "if", "in", "into", "is", "isn't", "it", "it's",
    "its", "itself", "let's", "me", "more", "most", "mustn't", "my", "myself", "no",
    "nor", "not", "of", "off", "on", "once", "only", "or", "other", "ought", "our",
    "ours", "ourselves", "out", "over", "own", "same", "shan't", "she", "she'd",
    "she'll", "she's", "should", "shouldn't", "so", "some", "such", "than", "that",
    "that's", "the", "their", "theirs", "them", "themselves", "then", "there",
    "there's", "these", "they", "they'd", "they'll", "they're", "they've", "this",
    "those", "through", "to", "too", "under", "until", "up", "very", "was",
    "wasn't", "we", "we'd", "we'll", "we're", "we've", "were", "weren't", "what",
    "what's", "when", "when's", "where", "where's", "which", "while", "who",
    "who's", "whom", "why", "why's", "with", "won't", "would", "wouldn't", "you",
    "you'd", "you'll", "you're", "you've", "your", "yours", "yourself", "yourselves",
}

analytics = {
    # set of the unique pages found
    "unique_pages": set(),
    # the url to the page with most words
    "longest_page_url": None,
    # the count of words in the longest page
    "longest_page_word_count": 0,
    # dictionary for the words parsed and their count
    "word_frequencies": {},
    # dictionary for the subdomains and their count
    "subdomain_counts": {}
}

def scraper(url, resp):
    links = extract_next_links(url, resp)
    # will be a list containing all the valid links after extraction
    valid_links = [link for link in links if is_valid(link)]
    # checks if the response is valid and if there is any valid content to parse
    if (resp.status == 200) and (resp.raw_response) and (resp.raw_response.content):
        # this will separate the url from the fragment(fragment not needed)
        # this is just a double check possibly redundent if URL is still clean from extraction
        clean_url, fragment = urldefrag(resp.url if resp.url else url)
        # checks if url is in set of unique pages, if not then add it
        if clean_url not in analytics["unique_pages"]:
            analytics["unique_pages"].add(clean_url)
            try:
                # using beautiful soup library (prof mentioned in lecture) to parse HTML
                soup = BeautifulSoup(resp.raw_response.content, "lxml")
                # removes unneccesary tags before text analysis
                # so only useful text will be taken for the parsing
                for useless in soup(["script", "style", "noscript"]): 
                    useless.extract()
                
                # this will get the text
                text = soup.get_text(separator = " ", strip = True)
                # THIS IS THE "TOKENIZER", MAY NEED TO CHANGE 
                # BUT FOR NOW ONLY ALPHABET CHARS ALLOWED
                words = re.findall(r"[A-Za-z]+", text.lower())
                
                word_count = len(words)
                # will skip pages with minimal content
                if word_count < MIN_WORDS: # REVIEW BC IDK IF ITS TOO LOW OR HIGH 
                    return valid_links
                # this loop updates the table for word frequencies
                for word in words:
                    # excludes any stopwords from the set
                    if word not in stopwords:
                        analytics["word_frequencies"][word] = (analytics["word_frequencies"].get(word, 0) + 1)
                
                # Will update the longest page analytics
                if len(words) > analytics["longest_page_word_count"]:
                    analytics["longest_page_url"]= clean_url
                    analytics["longest_page_word_count"] = word_count
                
                #TODO
                # IMPLEMENT THE SUBDOMAIN TRACKER FOR ANALYTICS
                # SUBDOMAINS ALLOWED ARE "UCI.EDU" I THINK?
                
            except Exception as e:
                print(f"Error for {clean_url}: {e}")
    return valid_links

def extract_next_links(url, resp):
    # Implementation required.
    # url: the URL that was used to get the page
    # resp.url: the actual url of the page
    # resp.status: the status code returned by the server. 200 is OK, you got the page. Other numbers mean that there was some kind of problem.
    # resp.error: when status is not 200, you can check the error here, if needed.
    # resp.raw_response: this is where the page actually is. More specifically, the raw_response has two parts:
    #         resp.raw_response.url: the url, again
    #         resp.raw_response.content: the content of the page!
    # Return a list with the hyperlinks (as strings) scrapped from resp.raw_response.content
    
    new_urls = []

    if resp.status != 200:
        return new_urls

    if resp.raw_response is None or resp.raw_response.content is None:
        return new_urls
    
    try:
        # Parse HTML content with lxml using BeautifulSoup
        soup = BeautifulSoup(resp.raw_response.content, "lxml")
        raw_links = [a["href"] for a in soup.find_all("a", href=True)]
    
        base_url = resp.url if resp.url else url

        for link in raw_links:
            if link:
                # Convert relative URLs to absolute URLs
                absolute_url = urljoin(base_url, link)
                
                # Remove fragment (everything after #) - proper way
                absolute_url, _ = urldefrag(absolute_url)
                
                if absolute_url:
                    new_urls.append(absolute_url)
    
    except Exception as e:
        print(f"Error parsing HTML for {url}: {e}")
        return []
    
    # Remove duplicates while preserving order
    seen = set()
    unique_links = []
    for url in new_urls:
        if url not in seen:
            seen.add(url)
            unique_links.append(url)

    return unique_links

def is_valid(url):
    # Decide whether to crawl this url or not. 
    # If you decide to crawl it, return True; otherwise return False.
    # There are already some conditions that return False.
    try:
        parsed = urlparse(url)
        if parsed.scheme not in set(["http", "https"]):
            return False
        
        # Check if URL is in allowed UCI domains - CRITICAL REQUIREMENT
        allowed_domains = [
            "ics.uci.edu",
            "cs.uci.edu",
            "informatics.uci.edu",
            "stat.uci.edu"
        ]
        
        netloc = parsed.netloc.lower()
        
        # Check if netloc exactly matches or is a subdomain of allowed domains
        is_valid_domain = False
        for domain in allowed_domains:
            if netloc == domain or netloc.endswith('.' + domain):
                is_valid_domain = True
                break
        
        if not is_valid_domain:
            return False
        
        # Check for unwanted file extensions
        return not re.match(
            r".*\.(css|js|bmp|gif|jpe?g|ico"
            + r"|png|tiff?|mid|mp2|mp3|mp4"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1"
            + r"|thmx|mso|arff|rtf|jar|csv"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz)$", parsed.path.lower())

    except TypeError:
        print ("TypeError for ", parsed)
        return False
