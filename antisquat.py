import argparse, cv2, publicsuffix2, shutil, json, selenium, traceback
import web_utils, image_utils, text_utils, gpt, domain_utils, file_utils, metadata_utils

metadata_file_name = "metadata_results.json"

parser = argparse.ArgumentParser()

def get_domain_list(): 
    domain_list = []
    parser.add_argument('domain_list', type=str, help="List of domains to run Antisquat on")
    args = parser.parse_args()
    if args.domain_list: 
        try:
            f = open(args.domain_list, "r")
            domain_list = f.read().splitlines()
            f.close()
        except FileNotFoundError:
            print(args.domain_list + ": File not found")
            exit(-1)

    return domain_list

def get_blacklist():
    blacklist = []
    parser.add_argument("-b", "--blacklist", help = "Line separated blacklist to skip")
    args = parser.parse_args()
    if args.blacklist: 
        try:
            f = open(args.blacklist, "r")
            blacklist = f.read().splitlines()
            f.close()
        except FileNotFoundError:
            print(args.blacklist + ": File not found")
            exit(-1)

    return blacklist

def logo():
    art = """
⠀⠀⠀⠀⠀⢀⣠⡤⢶⣾⠟⢻⡟⠻⣷⡶⢤⣄⡀⠀⠀⠀⠀⠀
⠀⠀⠀⣠⡶⠋⠁⢠⡟⠁⠀⢸⡇⠀⠈⢻⡄⠈⠙⢶⣄⠀⠀⠀
⠀⢀⡾⠛⠶⢦⣤⣟⣀⣀⣀⣸⣇⣀⣀⣀⣻⣤⡴⠶⠛⢷⡀⠀
⢠⡿⠀⠀⠀⠀⣾⠃⠉⠉⠉⢹⡏⠉⠉⠉⠘⣷⠀⠀⠀⠀⢿⡄
⣾⠃⠀⠀⠀⠀⣿⠀⠀⠀⠀⢸⡇⠀⠀⠀⠀⣿⠀⠀⠀⠀⠘⣷
⠿⠶⠶⠶⠶⠾⠿⠶⠶⠶⠶⠾⠷⠶⠶⠶⠶⠿⠷⠶⠶⠶⠶⠿
    A N T I  S Q U A T
Copyright © 2023 RedHunt Labs
By Owais Shaikh (4f77616973) 
 and Umair Nehri (umair9747)
"""
    print(art)

#############################################################################################

chatgpt_requests = 3
phishtank_results_filename = "phishtank_results.json"

logo()

domain_list = get_domain_list()
blacklist = get_blacklist()

shutil.rmtree(web_utils.temp_dir_name, ignore_errors=True)

godaddy = False
if domain_utils.grab_godaddy_key(): godaddy = True

for domain in domain_list:

    phishtank_results = []
    ribbon_word_results = []
    misspelled_results = []
    homograph_results = []

    try:
        domain = domain_utils.get_domain_from_url(domain) # extract domain only if any
        domain_without_tld = domain.replace(publicsuffix2.get_tld(domain),'').replace('.','')

        print("[>] Running antisquat on: " + domain)

        # Original page
        # print(f"[>] Grabbing page content from {domain}")
        # source = web_utils.get_page(domain)
        # page_text = web_utils.get_page_text(source.code)
        # image_text = image_utils.scan_image(source.screenshot)

        # Phishtank
        print(f"[>] Checking if {domain_without_tld} was used in a phishing URL recently...")
        phishtank_urls = web_utils.get_phishtank_urls()
        phishtank_results = []
        for url in phishtank_urls: 
            if text_utils.similar_word(url, domain_without_tld): phishtank_results.append(url)

        print(f"[!] Found {len(phishtank_results)} URLs from Phishtank.")
        phishtank_results = text_utils.eliminate_from_blacklist(phishtank_results, blacklist)

        if len (phishtank_results) > 0:
            data = {
                    domain_without_tld : phishtank_results
                }

            print (json.dumps (data, indent=4))

            file_utils.append_to_json_file(phishtank_results_filename, data)

            print("""Logged these in {filename}!""".format(filename=phishtank_results_filename))

        # Ribbon list
        print("[+] Generating domains based on common ribbon patterns...")
        ribbon_word_urls = text_utils.generate_ribbon_bar_combinations(domain, text_utils.ribbon_bar_keywords)
        ribbon_word_results = text_utils.eliminate_from_blacklist(ribbon_word_urls, blacklist)
        print(f"[!] Generated {len(ribbon_word_urls)} URLs...")
        #for url in ribbon_word_results: print (f" - {url}")

        homoglyphed_words = gpt.generate_homoglyphs(domain_name_only=domain_without_tld, size=chatgpt_requests)
        common_typos = gpt.popular_typos(domain_name_only=domain_without_tld, size=chatgpt_requests)
        visual_typos = gpt.simulate_typos(domain_name_only=domain_without_tld, size=chatgpt_requests)
        popular_tlds = gpt.popular_tlds(size=chatgpt_requests)

        homoglyphed_domains = domain_utils.merge_lists (homoglyphed_words, popular_tlds)
        common_typos = domain_utils.merge_lists (common_typos, popular_tlds)
        visual_typos = domain_utils.merge_lists (visual_typos, popular_tlds)

        results = homograph_results + misspelled_results + ribbon_word_results + phishtank_results

        print(f"[!] Generated {len(results)} URLs to inspect in total...")
        print(f"[>] Beginning inspection...")

        for url in results:
            status = web_utils.is_available(url)
            if status == True:
                try:
                    result = metadata_utils.get_page_metadata(item)
                    print (json.dumps (result, indent=4))
                    file_utils.append_to_json_file(metadata_file_name, result)
                except selenium.common.exceptions.WebDriverException: pass
            else: print (f"[x] Skipping: {url}")

    except: # Invalid domain
        traceback.print_exc()
        print ("""'{domain}' is an invalid domain. Skipping...""".format(domain=url))
        print ("Invalid domain name, skipping...")