import argparse, openai, json, os, whois, requests, re, publicsuffix2

godaddy_key_file_name = ".godaddy-key"

def grab_godaddy_key():
    try:
        key_file = open(godaddy_key_file_name, "r")
        key = key_file.read().strip().replace("\n","").replace("\t","").replace("\r","")
        key_file.close()
        if len(key) < 60: return None
        return key

    except:
        print("Godaddy key not found. Please paste a valid Godaddy key in a file named '{}'".format(godaddy_key_file_name))
        return None

goDaddyCreds = grab_godaddy_key()
    
def is_buyable_godaddy(domain):
    url = "https://api.ote-godaddy.com/v1/domains/available"
    headers = {
        "accept": "application/json",
        "Authorization": f"sso-key {goDaddyCreds}"
    }
    params = {
        "domain": domain,
        "checkType": "FAST",
        "forTransfer": "false"
    }
    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 200:
        data = response.json()
        if data["available"] == True: return True
        else: return False

def is_buyable_whois(domain):
    try:
        w = whois.whois(domain)
        if w["registrar"] == None: return True
        else: return False
    except Exception:
        return True

def is_buyable_privately (page_source):
    sale_keywords = ["domain", "sale", "purchase", "available"]
    score = 0
    for keyword in sale_keywords:
        if keyword in page_source.lower():
            score += 1
    if score > 3: return True
    else: return False

def get_domain_from_url(url):
    try:
        domain_regex = r'''^(?:https?:\/\/)?([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})(?:\/.*)?$'''
        subdomain = re.findall(domain_regex, url)[0]
        return publicsuffix2.get_sld(subdomain)
    except:
        return Exception("""'{domain}' is not a valid domain. Expected format: 'sld.tld'""".format(domain=url))
