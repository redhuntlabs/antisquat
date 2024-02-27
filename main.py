import argparse, json, publicsuffix2, sys
import multithreaded_requester, file_utils#, gpt

parser = argparse.ArgumentParser()
parser.add_argument('domain', type=str, help="Domain to run Antisquat on")
args = parser.parse_args()


print ("Generating domains...")
#gpt_domains = gpt.all_prompts(args.domain)
gpt_domains = ['FlipkartDeals.com']#['fliipkart.com', 'fliipcarat.com', 'flippkart.com', 'flipcart.com', 'fliptkart.com', 'flipkatt.com', 'flilkart.com', 'fliikart.com', 'flippkert.com', 'flippkard.com', 'flippkar.com', 'fflipkart.com', 'flipkarrt.com', 'flpkart.com', 'flpkard.com', 'flipcar.com', 'flpkarrt.com', 'flpkat.com', 'flikart.com', 'flpkatt.com', 'flipkert.com', 'flipcat.com', 'flipkrt.com', 'flipkadt.com', 'flpkartt.com', 'lflipkart.com', 'flipkat.com', 'fiipkart.com', 'fdlipkart.com', 'flpkartt.com', 'flkart.com', 'flipkert.com', 'flipkatr.com', 'flipkrtt.com', 'flipkkart.com', 'flipart.com', 'flipcartt.com', 'flipkar.com', 'flippkatt.com', 'flpikart.com', 'flipklart.com', 'flippkarrt.com', 'flpkcart.com', 'flipkatt.com', 'filpkart.com', 'flppkart.com', 'flpikatt.com', 'flipkrt.com', 'fliipkart.com', 'flilpkart.com', 'flippkrt.com', 'flpikcart.com', 'flippkatty.com', 'flipkart-shopping.com', 'flipkart-deals.com', 'flipkart-offers.net', 'flipkart-discounts.co', 'flipkart-sale.biz', 'flipkart-online.org', 'flipkart-store.info', 'flipkart-shop.biz', 'flipkart-bargains.net', 'flipkart-ecommerce.co', 'flipkartshopping.com', 'flipkartdeals.com', 'flipkartoffers.net', 'flipkartdiscounts.co', 'flipkartsale.biz', 'flipkartonline.org', 'flipkartstore.info', 'flipkartshop.biz', 'flipkartbargains.net', 'flipkartecommerce.co', 'flipkart.store', 'flipkart.deals', 'flipkart.shop', 'flipkart.sale', 'flipkart.online', 'flipkart.biz', 'flipkart.info', 'flipkart.xyz', 'flipkart.site', 'flipkart.club']

print (gpt_domains)

initial_site = multithreaded_requester.requester ([args.domain])
output = multithreaded_requester.requester (gpt_domains)

output = initial_site + output

for entry in output:
    print (json.dumps(entry, indent=4))
    file_utils.append_to_json_file("output.json", entry)