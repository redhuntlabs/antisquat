import argparse, openai, json, publicsuffix2

openai_key_file_name = ".openai-key"

def grab_openai_key():
    try:
        key_file = open(openai_key_file_name, "r")
        key = key_file.read().strip().replace("\n","").replace("\t","").replace("\r","")
        key_file.close()
        if len(key) < 51: 
            raise Exception()
        
        return key

    except:
        raise Exception("OpenAI key not found. Please paste a valid OpenAI key in a file named '{}'".format(openai_key_file_name))
    

def ask_chatgpt(system_prompt, user_query):
    prompts = [{"role": "system", "content": system_prompt}]
    
    prompts.append ({"role": "user", "content": user_query})
    
    chat = openai.ChatCompletion.create ( 
        #model="gpt-4-0125-preview",
        model="gpt-3.5-turbo-0125",
        messages=prompts 
    ) 
    
    reply = chat.choices[0].message.content 
    prompts.append (
        {
            "role": "assistant", 
            "content": reply
        }
    ) 
    return reply

openai.api_key = grab_openai_key()

##############
#Prompts

class SystemPrompts:
    misspelled_domains = """You are a pentester's assistant. Your job is to help pentesters generate misspelled domain names from a given domain. For example, amazon.com can be misspelled in ways such as: "amazn.com", "amazzon.com", "amazoon.com", "amazonn.com", "aamzon.com", "amazo.com", "amaazon.com", "amazona.com", "amazno.com", "amazonnn.com", "amazn.com", "amaozn.com", "amazone.com", "amazoon.com", "amazom.com" and so on.

# Constraints
1. Give as many misspelled domains as you can.
2. Attempt to mimic the misspelling as if it was mistyped by a human.
3. Always put the TLD in output. Make sure it is a valid TLD.
4. Restrict your output in JSON format such as {"<user input>":["<array of generated domains>"]}"""

system_prompts = SystemPrompts()

test = json.loads(ask_chatgpt(system_prompts.misspelled_domains, "zomato.com"))
