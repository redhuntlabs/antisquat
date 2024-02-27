import concurrent.futures, requests, ssl, json, whois, file_utils, traceback
import text_utils, network_utils, metric
from urllib.parse import urlparse
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

class GetResponse:
    def __init__ (self, response: requests.Response, page_source: str, redirect_chain: list):
        self.response = response
        self.page_source = page_source
        self.redirect_chain = redirect_chain

def selenium_get(url: str) -> GetResponse:
    print(f"Visiting {url} in selenium")    
    chrome_options = Options()
    chrome_options.add_argument("--headless") # Ensures Chrome runs in headless mode
    chrome_options.add_argument("--disable-gpu") # Optional, for some headless environments
    chrome_options.add_argument("--window-size=1920x1080") # Optional, to specify window size
    driver = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)

    redirect_chain = [url] 

    driver.get(url)
    WebDriverWait(driver, 10).until(lambda d: d.execute_script('return document.readyState') == 'complete')
    while True:
        current_url = driver.current_url
        if redirect_chain[-1] != current_url:
            redirect_chain.append(current_url)  # Add new URL to the chain
        else:
            break  # Exit loop if no new redirect (current URL hasn't changed)
                
    
    selenium_page_source = driver.page_source
    driver.quit()
    
    return GetResponse (
        response="", 
        page_source=selenium_page_source,
        redirect_chain=redirect_chain
    )

def get(url: str) -> GetResponse:
    print(f"Visiting {url}")
    
    session = requests.Session()
    retry = Retry(connect=3, backoff_factor=0.5)
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    response = session.get(url, timeout=30, allow_redirects=True)
    redirect_chain = [resp.url for resp in response.history] + [response.url]

    #selenium_data = selenium_get(url)

    page_source = f"{response.text}"#\n\n{selenium_data.page_source}"

    return GetResponse (
        response=response, 
        page_source=page_source,
        redirect_chain=redirect_chain
    )

def requester(input_domain: str, urls: list) -> list:
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
                result["emails"] = text_utils.extract_emails(response.text)
                
                # 4. Registrar data
                result["whois_data"] = network_utils.get_domain_registrant(urlparse(input_url).netloc.split(':')[0].split('/')[0])
                
                result["purchasable"] = {"whois": False, "privately": False}
                
                if result["whois_data"]["registrar"] == None: result["purchasable"]["whois"] = True 
                else: result["purchasable"]["whois"] = False
                
                # 5. Purchasability
                result["purchasable"]["privately"] = network_utils.is_buyable_privately(input_domain, get_response.redirect_chain[-1],response.text)
                
                score = 0
                score = metric.compute_squatability_score (
                    input_domain = input_domain,
                    emails=result["emails"],
                    page_source=get_response.page_source,
                    target_domain = result["domain"],
                    redirect_chain=result["redirect_chain"],
                    status_code=result["status_code"],
                    input_domain_created_date=result["whois_data"]["created"],
                    target_domain_created_date=network_utils.get_domain_registrant(input_domain)["created"],
                )
                
                result["score"] = score
                
            except Exception as e:
                print(f"Request to {input_url} failed with exception: {e}")
                #traceback.print_exception(e)

            if result:    
                print (result)
                print (json.dumps(result, indent=4))
                results.append (result)
                file_utils.append_to_json_file("output.json", result)

    return results

