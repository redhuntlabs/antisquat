import argparse, json, publicsuffix2, time, os
from openai import OpenAI

def ask_chatgpt(system_prompt, user_query):
    
    
    client = OpenAI(
        api_key=os.environ.get("OPENAI_API_KEY"),
    )
    
    prompts = [{"role": "system", "content": system_prompt}]
    
    prompts.append ({"role": "user", "content": user_query})
    
    chat = client.chat.completions.create ( 
        #model="gpt-4-0125-preview",
        model="gpt-3.5-turbo",
        messages=prompts 
    ) 
    
    reply = chat.choices[0].message.content 
    prompts.append (
        {
            "role": "assistant", 
            "content": reply
        }
    ) 
    
    if "```json" in reply: reply = reply.replace("```json", "").replace("```", "")
    
    return reply

##############
#Prompts

class SystemPrompts:
    misspelled_domains = """You are a pentester's assistant. Your job is to help pentesters generate misspelled domain names from a given domain. For example, amazon.com can be misspelled in ways such as: "amazom.com", "amazzon.com", "amazoon.com", "amazonn.com", "amozon.com", "amazo.com", "amaazon.com", "amazona.com" and so on.

# Constraints
1. Give as many misspelled domains as you can.
2. Attempt to mimic the misspelling as if it was mistyped by a human.
3. Always put the TLD in output. Make sure it is a valid TLD.
4. Restrict your output in JSON Array format."""

    combosquat = """You are a pentester's assistant. Your job is to help pentesters generate site-specific domain name permutations based on your knowledge of a site. For example, amazon.com is a shopping site, so permutations of this domain may include "amazon-shopping.com", "amazon-sale.com" and so on. If it is a banking site, such as "federalbank.co.in", permutations may include "federalbank-online.co.in", "federalbank-account.com" and so on.

# Constraints
1. Give as many site-relevant domain names as possible.
2. Attempt to mimic what an attacker might do to mislead a victim.
3. Always put the TLD in output. Make sure it is a valid TLD.
4. Restrict your output in JSON Array format."""

    tld_squatting = """You are a pentester's assistant. Your job is to help pentesters generate domain name permutations based on TLDs that don't actually belong to a company, and may be used to mislead users. For example, amazon.com is a shopping site, so permutations of this domain may include "amazon.online", "amazon.info" and so on.

# Constraints
1. Give as many site-relevant domain names as possible.
2. Attempt to mimic what an attacker might do to mislead a victim.
3. Always put the TLD in output. Make sure it is a valid TLD.
4. Restrict your output in JSON Array format."""


system_prompts = SystemPrompts()

def all_prompts (domain):
    domains = []
    misspelled_domains = ask_chatgpt(system_prompts.misspelled_domains, domain)
    domains += json.loads(misspelled_domains)
    print (f"Generated {len(json.loads(misspelled_domains))} misspelled domains")
    print ("Sleeping for 20s to prevent rate limiting")
    time.sleep(20)
    
    combosquat = ask_chatgpt(system_prompts.combosquat, domain)
    domains += json.loads(combosquat)
    print (f"Generated {len(json.loads(combosquat))} combination domains")
    print ("Sleeping for 20s to prevent rate limiting")
    time.sleep(20)
    
    combosquat_dehyphenated = [s.replace('-', '') for s in json.loads(combosquat)]
    domains += combosquat_dehyphenated
    
    tld_squatting = ask_chatgpt(system_prompts.tld_squatting, domain)
    domains += json.loads(tld_squatting)
    print (f"Generated {len(json.loads(tld_squatting))} combination domains")

    return domains

