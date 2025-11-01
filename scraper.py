import re
from urllib.parse import urlparse, urljoin, urldefrag
from collections import Counter, defaultdict
from lxml import html

STOPWORDS = set("""
a about above after again against all am an and any are aren't as at be because been before being below
between both but by can't cannot could couldn't did didn't do does doesn't doing don't down during each few
for from further had hadn't has hasn't have haven't having he he'd he'll he's her here here's hers herself
him himself his how how's i i'd i'll i'm i've if in into is isn't it it's its itself let's me more most
mustn't my myself no nor not of off on once only or other ought our ours ourselves out over own same shan't
she she'd she'll she's should shouldn't so some such than that that's the their theirs them themselves then
there there's these they they'd they'll they're they've this those through to too under until up very was
wasn't we we'd we'll we're we've were weren't what what's when when's where where's which while who who's
whom why why's with won't would wouldn't you you'd you'll you're you've your yours yourself yourselves
""".split())

unique_pages = set()
subdomain_counts = defaultdict(int)
word_freq = Counter()
longest_page = {"url": None, "word_count": 0}

def scraper(url, resp):
    if resp and resp.status == 200 and getattr(resp, "raw_response", None):
        ctype = (resp.raw_response.headers.get("Content-Type", "") or "").lower()
        if "text/html" in ctype:
            page_url = _canonicalize(resp.url or url)
            if is_valid(page_url):
                if page_url not in unique_pages:
                    unique_pages.add(page_url)
                    host = (urlparse(page_url).hostname or "").lower()
                    if host.endswith(".uci.edu"):
                        subdomain_counts[host] += 1
                try:
                    tree = html.fromstring(resp.raw_response.content)
                    text = _extract_visible_text(tree)
                    tokens = _tokenize(text)
                    words = [t for t in tokens if t not in STOPWORDS and t.isalpha() and len(t) > 1]
                    word_freq.update(words)
                    wc = len(tokens)
                    if wc > longest_page["word_count"]:
                        longest_page["word_count"] = wc
                        longest_page["url"] = page_url
                except Exception:
                    pass

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
        allowed_domains = ["ics.uci.edu", "cs.uci.edu", "informatics.uci.edu", "stat.uci.edu"]
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
        if re.match(
            r".*\.(css|js|bmp|gif|jpe?g|ico"
            + r"|png|tiff?|mid|mp2|mp3|mp4"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1"
            + r"|thmx|mso|arff|rtf|jar|csv"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz)$", parsed.path.lower()
            (parsed.path or "").lower()
        ):
            return False
    
        path = unquote(parsed.path or "/")
        # repeated directory loop
        if re.search(r"(\/.+)\1{2,}", path):
            return False

        q = parsed.query or ""
        ql = q.lower()

        # extremely long queries or too many params
        if len(q) > 250:
            return False
        if q.count("&") + q.count(";") > 8:
            return False

        # session/tracking/calendar/pagination traps
        if re.search(r"(session|sid|phpsessid|jsessionid|aspSESSIONID|cfid|cftoken)", ql, re.I):
            return False
        if re.search(r"(utm_|fbclid=|gclid=)", ql):
            return False
        if re.search(r"(calendar|ical|year=\d{4}|month=\d{1,2})", ql):
            return False
        if re.search(r"(\bpage=\d{3,}|\boffset=\d{3,})", ql):
            return False

        return True

    except TypeError:
        print ("TypeError for ", parsed)
        return False

def _canonicalize(u: str) -> str:
    u = (u or "").strip()
    if not u:
        return u
    u, _ = urldefrag(u)
    p = urlparse(u)
    scheme = (p.scheme or "http").lower()
    host = (p.hostname or "").lower()
    netloc = host
    if p.port and not ((scheme == "http" and p.port == 80) or (scheme == "https" and p.port == 443)):
        netloc = f"{host}:{p.port}"
    path = unquote(p.path or "/")
    path = re.sub(r"/{2,}", "/", path)
    query = (p.query or "").strip()
    return f"{scheme}://{netloc}{path}" + (f"?{query}" if query else "")

def _extract_visible_text(tree) -> str:
    try:
        texts = tree.xpath('//text()[not(ancestor::script or ancestor::style or ancestor::noscript)]')
        text = " ".join(t.strip() for t in texts if t and t.strip())
        return re.sub(r"\s+", " ", text).strip()
    except Exception:
        return ""

def _tokenize(text: str):
    return re.findall(r"[A-Za-z]+", text)