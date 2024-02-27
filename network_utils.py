import argparse, json, os, whois, requests, re, publicsuffix2, ssl, socket, datetime
from urllib.parse import urlparse
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization

godaddy_key_file_name = ".godaddy-key"

def get_certificate_details(url, port=443):
    hostname = urlparse(url).netloc.split(':')[0].split('/')[0]
    context = ssl.create_default_context()
    
    with socket.create_connection((hostname, port)) as sock:
        with context.wrap_socket(sock, server_hostname=hostname) as sslsock:
            certificate = sslsock.getpeercert()
            certificate_der = sslsock.getpeercert(binary_form=True)
            
            # Convert the DER format certificate to an X.509 certificate object
            certificatex509 = x509.load_der_x509_certificate(certificate_der, default_backend())
            public_key = certificatex509.public_key()
            public_key_pem = public_key.public_bytes(encoding=serialization.Encoding.PEM, format=serialization.PublicFormat.SubjectPublicKeyInfo)
            certificate["publicKey"] = public_key_pem.decode()
    
    return certificate

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

#goDaddyCreds = grab_godaddy_key()
    
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

def is_buyable_privately (input_domain, url, page_source):
    sale_sentence = [
        "This domain is for sale",
        "Interested in purchasing this domain",
        "Domain available",
        "may be for sale",
        "This domain is for sale",
        "inquire about this domain",
        "Secure this domain",
        "Make an offer"
    ]
    
    if "domain" in url and "domain" not in input_domain: return True 
    
    for sentence in sale_sentence:
        if sentence.lower() in page_source.lower(): return True 
    
    return False

def get_domain_from_url(url):
    try:
        domain_regex = r'''^(?:https?:\/\/)?([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})(?:\/.*)?$'''
        subdomain = re.findall(domain_regex, url)[0]
        return publicsuffix2.get_sld(subdomain)
    except:
        return Exception("""'{domain}' is not a valid domain. Expected format: 'sld.tld'""".format(domain=url))
import whois

def get_domain_registrant(domain):
    try:
        domain_info = whois.whois(domain)
        
        updated_date = ""
        try:
            if len(domain_info.updated_date) > 1: updated_date = str(domain_info.updated_date[0])
            else: updated_date = str(domain_info.updated_date)
        except: updated_date = str(domain_info.updated_date)
        
        creation_date = ""
        try:
            if len(domain_info.creation_date) > 1: creation_date = str(domain_info.creation_date[0])
            else: creation_date = str(domain_info.creation_date)
        except: creation_date = str(domain_info.creation_date)
            
        return {
            "organization": domain_info.organization, 
            "registrar": domain_info.registrar,
            "created": creation_date,
            "updated": updated_date
        }
        
    except Exception as e:
        #print (f"Error fetching WHOIS information: {e}")
        return {}
