from urllib.parse import urlparse
import network_utils
from datetime import datetime, timedelta
import traceback

def check_url_shorteners(redirect_chain):
    score = 0
    
    # List of common URL shorteners
    url_shorteners = [
        "bitly.com",
        "bit.ly",
        "tinyurl.com",
        "ow.ly",
        "rebrandly.com",
        "t2m.io",
        "blink.com",
        "shorte.st",
        "is.gd",
        "clickmeter.com",
        "choto.xyz",
        "yourls.org",
        "buff.ly",
        "polrproject.org",
        "hyperlink.co",
        "tiny.cc",
        "linklyhq.com",
        "snip.ly",
        "shorturl.at",
        "bit.do",
        "clkim.com",
        "capsulink.com",
        "goo.gl"
    ]
    
    try:
        for service in url_shorteners:
            for url in redirect_chain:
                if service in url:
                    score += 1
    
        score = score / len(redirect_chain)
    
    except IndexError: pass
    
    return score

def check_number_of_redirects(input_domain, target_domain, redirect_chain):
    score = 0
    try:
        for url in redirect_chain:
            domain = network_utils.get_domain_from_url(url)
            if input_domain.lower() in domain or target_domain.lower() in domain:
                redirect_chain.remove(url)

        for url in redirect_chain:
            if input_domain.lower() not in url.lower():
                score += 1
    except IndexError: pass
    
    if len (redirect_chain) >= 1: score += 1 # too many redirects
    return score
    
def get_age(date_string):
    current_datetime = datetime.now()
    given_datetime = datetime.strptime(date_string, "%Y-%m-%d %H:%M:%S")
    age = current_datetime - given_datetime
    return age.days
    
def check_email_in_source(emails, domain):
    score = 0
    try:
        for email in emails:
            if domain.lower() not in email.lower(): score += 1
        score = score/len(emails)
    except:
        pass
        
    return score

def check_domain_registration_age (input_date_string, target_date_string):
    # Domains with a short history or recently changed ownership could be flagged for further review.
    score = 0
    
    try:
        input_age = get_age(input_date_string)
        target_age = get_age(target_date_string)
        if (target_age < input_age): score += 0.5
        if (input_age - target_age) <= 730: score += 0.5 
    
    except: pass
        
    return score

def compute_squatability_score(target_domain, input_domain, status_code, page_source, redirect_chain, emails, input_domain_created_date, target_domain_created_date):

    score = 0
    
    shortener_score = check_url_shorteners(redirect_chain)
    
    email_score = check_email_in_source(emails, input_domain)
    
    redirect_score = check_number_of_redirects(input_domain, target_domain, redirect_chain)
    
    status_score = 0
    if status_code in [301, 302, 404, 503] and redirect_score == 1: status_score = 1
    
    age_score = check_domain_registration_age(input_domain_created_date, target_domain_created_date)
    
    sale_score = 0
    if network_utils.is_buyable_privately(input_domain, redirect_chain[-1], page_source): sale_score = 1
    
    """
    print (f"Shortener score: {shortener_score}")
    print (f"Status score: {status_score}")
    print (f"Email score: {email_score}")
    print (f"Redirect score: {redirect_score}")
    print (f"Age score: {age_score}")
    print (f"Sale score: {sale_score}")
    """
    
    score = (shortener_score*1.5 + status_score*1.25 + email_score + redirect_score*1.5 + age_score*1.25 + sale_score*1.5) / 6
    
    return score
