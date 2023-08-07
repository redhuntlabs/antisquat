# importing webdriver from selenium
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import re, html, os, cv2, urllib, shutil, bs4, csv, time, glob, publicsuffix2
import text_utils, image_utils

temp_dir_name = ".imaging_temp"
phishtank_timeout = 3600

def get_links(source):
    urls = []
    regex = "(?:(?:https?|ftp):\/\/)?[\w/\-?=%.]+\.[\w/\-&?=%.]+"
    matches = re.findall(regex, source)

    for match in matches:
        if '?' in match:
            match = match.replace(match.split('?',1)[1], '').replace('?', '')
        if "://" in match:
            url = html.unescape(match)
            urls.append(url)

    return list(filter(None, urls))

def get_image_links(source):
    extension_list = ["jpg", "png", "bmp", "gif"]
    image_links = []
    links = get_links(source)
    for link in links:
        _, file_extension = os.path.splitext(link)
        if file_extension.replace('.', '') in extension_list:
            image_links.append(link)

    return image_links

def get_hyper_links(source):
    links = get_links(source)
    hyper_links = []
    for link in links:
        _, file_extension = os.path.splitext(link)
        if file_extension == '':
            hyper_links.append(link)
    
    return hyper_links

def get_page_text(source):
    soup = bs4.BeautifulSoup(source, 'html.parser')
    for script in soup(["script", "style"]): script.decompose() # extract and kill all script and style elements
    text = soup.get_text() # get text

    lines = (line.strip() for line in text.splitlines()) # break into lines and remove leading and trailing space on each
    chunks = (phrase.strip() for line in lines for phrase in line.split("  ")) # break multi-headlines into a line each
    text = '\n'.join(chunk for chunk in chunks if chunk) # drop blank lines

    text = text_utils.separate_fused_words(text)

    return text

class Image:
    def __init__(self, image: cv2.Mat, image_text: str, image_file_name: str):
        self.image = image
        self.image_text = image_text
        self.image_cached_file_name = image_file_name

def download_image(url):
    if not os.path.exists(temp_dir_name): os.makedirs(temp_dir_name)

    image_file_name = temp_dir_name + '/' + os.path.basename(url)

    _file = open(image_file_name, "wb")
    _file.write(urllib.request.urlopen(url).read())
    _file.close()

    image = cv2.imread(image_file_name) 
    image_text = image_utils.scan_image(image)
    
    return Image (image=image, image_text=image_text, image_file_name=image_file_name)

class Source:
    def __init__(self, screenshot: cv2.Mat, code: str, title: str):
        self.screenshot = screenshot
        self.code = code
        self.title = title

def get_page(domain):
    #screenshot_file_name = temp_dir_name + '/' + domain.replace(".", "_").split("://")[0].split("/")[0] + ".png"
    if "://" not in domain and  "http" not in domain: domain = "https://" + domain
    options = Options()
    options.add_argument('--headless')
    options.add_argument("--window-size=1280,720")
    options.add_argument('--disable-gpu')
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome (service=service, options=options)
    driver.set_page_load_timeout(15)
    driver.get(domain)
    WebDriverWait(driver, 100).until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
    html = driver.page_source
    title = driver.title
    
    #if not os.path.exists(temp_dir_name): os.makedirs(temp_dir_name)
    #driver.save_screenshot(screenshot_file_name)
    #driver.close()
    #screenshot = cv2.imread(screenshot_file_name)
    shutil.rmtree(temp_dir_name, ignore_errors=True)

    #return Source(screenshot, html, title)
    return Source(None, html, title)

def get_phishtank_urls():
    urls = []
    phishtank_url = "http://data.phishtank.com/data/online-valid.csv"
    
    filename = f".phishtank.csv"

    if not os.path.exists(filename):
        phishtank_file = open(filename, "wb")
        print(f"[+] Downloading new phishtank URLs list...")
        phishtank_file.write(urllib.request.urlopen(phishtank_url).read())
        phishtank_file.close()

    else:
        creation_time = os.path.getctime(filename)
        time_difference = time.time() - creation_time
        if time_difference >= phishtank_timeout:
            os.remove(filename)
            print(f"[+] Downloading new phistank URLs list...")
            phishtank_file = open(filename, "wb")
            phishtank_file.write(urllib.request.urlopen(phishtank_url).read())
            phishtank_file.close()

    phishtank_file = open(filename, 'r')
    data = list(csv.reader(phishtank_file, delimiter=','))
    phishtank_file.close()

    for entry in data: urls.append(entry[1])
    return urls

def is_available(url):
    success_codes = [200]
    try:
        response = urllib.request.urlopen(url, timeout=15)
        status_code = response.getcode()
        for code in success_codes:
            if str(code) in str(status_code): return True
            else: return False
    except urllib.error.URLError:
        return False
    
def change_tld(domain):
    domains = []

    tlds = [
  "com",
  "net",
  "org",
  "info",
  "in",
  "ru",
  "ir",
  "uk",
  "de",
  "ua",
  "ca",
  "tr",
  "br",
  "io",
  "it",
  "nl",
  "pl",
  "us",
  "eu",
  "be",
  "se",
  "cc",
  "ro",
  "ar",
  "ph",
  "edu",
  "si",
  "link",
  "agency",
  "im",
  "digital",
  "is",
  "cm"
]

    for tld in tlds:
        domain = publicsuffix2.get_sld(domain) # extract domain only if any
        domain_without_tld = domain.replace(publicsuffix2.get_tld(domain),'').replace('.','')
        new_permutation = domain_without_tld + '.' + tld
        domains.append(new_permutation)

    final_list = []
    for domain in domains:
        if "https://" not in domain: final_list.append(f'https://{domain}')
        else: final_list.append(f'{domain}')

    return final_list
