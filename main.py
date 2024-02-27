import argparse, json, publicsuffix2, sys
import multithreaded_requester, gpt

parser = argparse.ArgumentParser()
parser.add_argument('domain', type=str, help="Domain to run Antisquat on")
args = parser.parse_args()


print ("Generating domains...")
gpt_domains = gpt.all_prompts(args.domain)

output = multithreaded_requester.requester (args.domain, gpt_domains)
    