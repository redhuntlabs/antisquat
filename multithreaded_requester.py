import concurrent.futures, requests, ssl, json, whois
import text_utils, network_utils
from urllib.parse import urlparse
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from bs4 import BeautifulSoup


class GetResponse:
    def __init__ (self, response: requests.Response, redirect_chain: list):
        self.response = response
        self.redirect_chain = redirect_chain

def get(url: str) -> GetResponse:
    print(f"Visiting {url}")
    session = requests.Session()
    retry = Retry(connect=3, backoff_factor=0.5)
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    response = session.get(url, timeout=15, allow_redirects=True)
    redirect_chain = [resp.url for resp in response.history] + [response.url]
        
    return GetResponse (
        response=response, 
        redirect_chain=redirect_chain
    )

def requester(urls: list) -> list:
    results = []
    num_workers = len(urls)

    urls = [url if (url.startswith("http://") or url.startswith("https://")) else f"http://{url}" for url in urls]

    with concurrent.futures.ThreadPoolExecutor(max_workers=num_workers) as executor:
        future_to_url = {executor.submit(get, url): url for url in urls}

        for future in concurrent.futures.as_completed(future_to_url):
            input_url = future_to_url[future]
            
            result = {}
            
            try:
                get_response = future.result()
                response = get_response.response
                
                # 1. HTTP level data
                result["domain"] = urlparse(input_url).netloc.split(':')[0].split('/')[0]
                result["status_code"] = response.status_code
                result["redirect_chain"] = get_response.redirect_chain
                
                # 2. Certificate data
                #result["certificate_public_key"] = network_utils.get_certificate_details(get_response.redirect_chain[-1])["publicKey"]
                
                # 3. Webpage data
                #result["urls_in_page"] = text_utils.get_urls(input_url, response.text)
                
                # 4. Registrar data
                result["whois_data"] = network_utils.get_domain_registrant(urlparse(input_url).netloc.split(':')[0].split('/')[0])
                
                result["purchasable"] = {"whois": False, "privately": False}
                
                if result["whois_data"]["registrar"] == None: result["purchasable"]["whois"] = True 
                else: result["purchasable"]["whois"] = False
                
                # 5. Purchasability
                result["purchasable"]["privately"] = network_utils.is_buyable_privately(response.text)
                
            except Exception as e:
                #print(f"Request to {input_url} failed with exception: {e}")
                if "no address" in str(e).lower():
                    result["status_code"] = "No address associated with hostname"

            results.append (result)

    return results

