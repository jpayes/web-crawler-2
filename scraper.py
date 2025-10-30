import re
from urllib.parse import urlparse, urljoin
from lxml import html

def scraper(url, resp):
    links = extract_next_links(url, resp)
    return [link for link in links if is_valid(link)]

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
        # Parse HTML content with lxml
        tree = html.fromstring(resp.raw_response.content)
        
        raw_links = tree.xpath('//a/@href')

        base_url = resp.url if resp.url else url

        for link in raw_links:
            if link:
                # Convert relative URLs to absolute URLs
                absolute_url = urljoin(base_url, link)
                
                if '#' in absolute_url:
                    absolute_url = absolute_url.split('#')[0]
                
                if absolute_url:
                    new_urls.append(absolute_url)
    
    except Exception as e:
        print(f"Error parsing HTML for {url}: {e}")
        return []

    return new_urls

def is_valid(url):
    # Decide whether to crawl this url or not. 
    # If you decide to crawl it, return True; otherwise return False.
    # There are already some conditions that return False.
    try:
        parsed = urlparse(url)
        if parsed.scheme not in set(["http", "https"]):
            return False
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
        raise
