import json, re, bs4
import network_utils, web_utils, publicsuffix2
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

def get_page_text(source):
    soup = bs4.BeautifulSoup(source, 'html.parser')
    for script in soup(["script", "style"]): script.decompose() # extract and kill all script and style elements
    text = soup.get_text() # get text

    lines = (line.strip() for line in text.splitlines()) # break into lines and remove leading and trailing space on each
    chunks = (phrase.strip() for line in lines for phrase in line.split("  ")) # break multi-headlines into a line each
    text = '\n'.join(chunk for chunk in chunks if chunk) # drop blank lines

    return text
    
def get_page_metadata(url):
    redirect_chain = [url]
    current_url = url
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument("--window-size=1280,720")
    options.add_argument('--disable-gpu')
    service = Service(ChromeDriverManager(version='114.0.5735.90').install())
    driver = webdriver.Chrome (service=service, options=options)

    # 1. Get redirection path
        
    while True:
        driver.get(current_url)
        current_url = driver.current_url
        if current_url in redirect_chain:
            break
        redirect_chain.append(current_url)

    # 1a. Read all text on last page
    source = driver.page_source
    page_text = driver.title + get_page_text(driver.page_source)
    driver.quit()

    # 2. Get emails on page
    email_regex = r'''([a-zA-Z0-9+._-]+@[a-zA-Z0-9._-]+\.[a-zA-Z0-9_-]+)'''
    emails = list(set(re.findall (email_regex, page_text)))

    # 3. Get phone numbers on page
    phone_regex = r'''(?:\+?\d[-() \d]*){8,12}'''
    phone_numbers = list(set(re.findall (phone_regex, page_text)))

    # 4. Get urls on page
    urls = web_utils.get_links(source)

    # 5. Purchasable?
    whois = network_utils.is_buyable_whois(url)
    godaddy = network_utils.is_buyable_godaddy(url)
    private = network_utils.is_buyable_privately(page_text)

    redirects_to_target = False
    try:
        if network_utils.get_domain_from_url(url) in network_utils.get_domain_from_url(redirect_chain[-1]): redirects_to_target = True
    except: pass

    results = {
        "target" : url,
        "redirect_chain" : redirect_chain,
        "redirects_to_target" : redirects_to_target,
        "emails" : emails,
        "phone_numbers" : phone_numbers,
        "urls" : urls,
        "available_whois" : whois,
        "available_godaddy" : godaddy,
        "available_privately" : private,
    }

    return results


