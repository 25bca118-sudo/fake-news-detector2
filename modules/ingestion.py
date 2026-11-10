import urllib.parse
import requests
from bs4 import BeautifulSoup
from modules.security import is_safe_url

USER_AGENT = "Mozilla/5.0 (compatible; TruthLensAI/1.0)"

def extract_article_from_url(url: str) -> dict:
    """Safely extracts article title, metadata, author, publication date, and text."""
    safe, msg = is_safe_url(url)
    if not safe:
        return {'success': False, 'error': f"Security Alert: {msg}", 'data': None}

    parsed = urllib.parse.urlparse(url)
    domain = parsed.hostname.lower() if parsed.hostname else ""
    if domain.startswith("www."):
        domain = domain[4:]

    headers = {'User-Agent': USER_AGENT, 'Accept': 'text/html,application/xhtml+xml'}
    try:
        response = requests.get(url, headers=headers, timeout=10, allow_redirects=True)
        response.raise_for_status()
    except requests.exceptions.Timeout:
        return {'success': False, 'error': "The request timed out while attempting to reach the server.", 'data': None}
    except requests.exceptions.SSLError:
        return {'success': False, 'error': "SSL Certificate verification failed on destination server.", 'data': None}
    except requests.exceptions.RequestException as exc:
        return {'success': False, 'error': f"Failed to retrieve URL: {exc}", 'data': None}

    soup = BeautifulSoup(response.content, 'html.parser')
    for element in soup(['script', 'style', 'nav', 'header', 'footer', 'aside', 'noscript', 'form']):
        element.decompose()

    title = ""
    og_title = soup.find('meta', property='og:title') or soup.find('meta', attrs={'name': 'twitter:title'})
    if og_title and og_title.get('content'):
        title = og_title['content'].strip()
    elif soup.find('h1'):
        title = soup.find('h1').get_text().strip()
    elif soup.title:
        title = soup.title.get_text().strip()

    pub_date = ""
    time_tag = soup.find('time') or soup.find('meta', property='article:published_time') or soup.find('meta', attrs={'name': 'pubdate'})
    if time_tag:
        pub_date = time_tag.get('datetime') or time_tag.get('content') or time_tag.get_text().strip()

    author = ""
    author_tag = soup.find('meta', attrs={'name': 'author'}) or soup.find('meta', property='article:author')
    if author_tag and author_tag.get('content'):
        author = author_tag['content'].strip()

    article_elem = soup.find('article') or soup.find('main') or soup
    paragraphs = [p.get_text().strip() for p in article_elem.find_all('p') if len(p.get_text().split()) > 4]
    full_text = " ".join(paragraphs).strip()
    if len(full_text) < 40 and not title:
        return {'success': False, 'error': "Could not extract sufficient text. Please paste the article text manually.", 'data': None}

    return {'success': True, 'error': None, 'data': {
        'url': url, 'domain': domain, 'title': title or "Untitled News Article",
        'author': author or "Staff Reporter / Unknown", 'publication_date': pub_date or "Not specified",
        'content': full_text, 'word_count': len(full_text.split()),
        'extracted_paragraphs_count': len(paragraphs)
    }}
