import requests
from bs4 import BeautifulSoup
from flask import Flask, render_template, Response, request
from urllib.parse import urljoin, urlparse, urlunparse
import time
import json

app = Flask(__name__)

def get_html_links(url, visited, base_domain):
    links = set()
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status() #check for HTTP Errors 404, 500
        content = BeautifulSoup(response.text, 'html.parser')

        excluded_domains = {"facebook.com", "twitter.com", "youtube.com", "instagram.com", "linkedin.com", "tiktok.com"}
        excluded_start_links = ('#', 'tel:', 'mailto:', 'javascript:')
        excluded_file_extensions = ('.jpg', '.jpeg', '.png', '.gif', '.webp', '.pdf', '.zip', '.css', '.js', '.mp4', '.mp3')

        for a_tag in content.find_all('a', href=True):
            href = a_tag['href'].strip()
            # skip unnecessary links
            if href.startswith(excluded_start_links) or href.lower().endswith(excluded_file_extensions) or any(domain in href for domain in excluded_domains):
                continue

            link = urljoin(url, href) # convert relative links to absolut
            parsed_link = urlparse(link)

            if parsed_link.scheme in ['http', 'https'] and parsed_link.netloc == base_domain and link not in visited:
                links.add(link)

    except requests.RequestException as e:
        print(f"Error fetching {url}: {e}")

    return links


def get_xml_links(xml_path):
    links = set()
    try:
        with open(xml_path, 'r', encoding='utf-8') as file:
            content = BeautifulSoup(file, 'xml')

        for loc in content.find_all('loc'):
            links.add(loc.text.strip())

    except Exception as e:
        print(f"Error reading XML file {xml_path}: {e}")

    return links

def check_link_status(url):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

        response = requests.head(url, headers=headers, timeout=10, allow_redirects=True)
        return response.status_code
    except requests.exceptions.HTTPError as e:
        # Handle 4xx/5xx errors specifically if needed, else return status code
        return e.response.status_code
    except requests.exceptions.Timeout:
        return "Error: Timeout"
    except requests.exceptions.RequestException as e:
        # Handle other errors like connection refused, DNS errors etc.
        return f"Error: {type(e).__name__}"  # return generic error type
    except Exception as e:
        # Catch any other unexpected errors during the check
        return f"Error: Unexpected ({type(e).__name__})"

def stream_links(start_url, max_depth=3, delay=1):
    processed_or_queued = set()
    queue = [(start_url, 0)] # (URL, depth)

    parsed_start_url = urlparse(start_url)
    base_domain = parsed_start_url.netloc # get base domain

    if not base_domain:
        error_data = json.dumps({'url': start_url, 'status': 'Error: Invalid start URL'})
        yield f"event: error\ndata: {error_data}\n\n"
        return

    print(f"Starting stream crawl & status check at: {start_url}, Domain: {base_domain}, Max Depth: {max_depth}")
    # Check and yield the starting URL
    start_status = check_link_status(start_url)
    start_data = json.dumps({'url': start_url, 'status': start_status})
    processed_or_queued.add(start_url)
    yield f"data: {start_data}\n\n"

    while queue:
        url, depth = queue.pop(0)

        new_links = get_html_links(url, processed_or_queued, base_domain)

        # if url.endswith('.xml'):
        #     new_links = get_xml_links(url)
        # else:
        #     new_links = get_html_links(url, processed_or_queued, base_domain)

        # Add new links to queue
        if depth < max_depth:
            for link in new_links:
                if link not in processed_or_queued:
                    processed_or_queued.add(link) # Mark as found
                    link_status = check_link_status(link)
                    link_data = json.dumps({'url': link, 'status': link_status})
                    yield f"data: {link_data}\n\n" #SSE format
                    # Only add to queue if it's likely an HTML page (or unknown) and status is OK-ish
                    if isinstance(link_status, int) and link_status < 400:
                        queue.append((link, depth+1))
                    elif isinstance(link_status, str) and "Error" in link_status:
                        print(f"Skipping queue for link with error: {link}")
                    time.sleep(0.05) # Small delay after yield to allow SSE processing buffer

        time.sleep(delay) # Delay to avoid overwhelming server
    end_data = json.dumps({'status': 'finished', 'count': len(processed_or_queued)})
    yield f"event: end\ndata: {end_data}.\n\n"


# Flask routes
@app.route('/favicon.ico')
def favicon():
    return '', 204

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/stream')
def display_links():
    # Get URL from request query parameter
    start_url = request.args.get('url')

    # Basic validation
    if not start_url:
        error_data = json.dumps({'url': '', 'status': 'Error: No URL provided.'})
        return Response("event: error\ndata: {\"status\": \"Error: No URL provided.\"}\n\n", mimetype='text/event-stream')
    
    # Ensure scheme(https)
    parsed = urlparse(start_url)
    if not parsed.scheme:
        # Assume https if no scheme provided
        start_url = urlunparse(('https', parsed.netloc, parsed.path, parsed.params, parsed.query, parsed.fragment))
        print(f"Prepended https scheme: {start_url}")

    return Response(stream_links(start_url, max_depth=3, delay=0.3), mimetype='text/event-stream')

if __name__ == '__main__':
    app.run(debug=True, threaded=True) # Use threaded=True for better handling of background stream
