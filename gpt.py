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
        print("OpenAI key not found. Please paste a valid OpenAI key in a file named '{}'".format(openai_key_file_name))
        exit(-1)


def ask_chatgpt(query):
    api_key = grab_openai_key()
    
    openai.api_key = api_key
    response = openai.Completion.create (
        model="text-davinci-003",
        prompt=query,
        temperature=0.5,
        max_tokens=2500,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
        stop=None,
    )

    return response

def prepare_output(chatgpt_response):
    return chatgpt_response["choices"][0]["text"]

def simulate_typos(domain_name_only, size):
    if size < 3: size = 3 # ChatGPT fails if the value is less than 3
    prompt = """You are a near-sighted old-aged laptop user. You want to type  the word "{domain}". What are at least {size} potential ways you could misspell it? Put them all in a JSON Array.""".format(domain=domain_name_only, size=size)
    results = json.loads(prepare_output(ask_chatgpt(prompt)))
    return results

def generate_homoglyphs(domain_name_only, size):
    if size < 3: size = 3 # ChatGPT fails if the value is less than 3
    prompt = """Generate {size} unique and realistic homoglyphed-words that look identical to the word  "{domain}". Put them all in a JSON Array.""".format(domain=domain_name_only, size=size)
    results = json.loads(prepare_output(ask_chatgpt(prompt)))
    return results

def popular_typos(domain_name_only, size):
    if size < 3: size = 3 # ChatGPT fails if the value is less than 3
    prompt = """What are the most common misspellings of "{domain}" that you have found on the internet so far?  Give me at least {size}. Put them all in a JSON Array.""".format(domain=domain_name_only, size=size)
    results = json.loads(prepare_output(ask_chatgpt(prompt)))
    return results

def popular_tlds(size):
    if size < 3: size = 3 # ChatGPT fails if the value is less than 3
    prompt = """What are the {size} most popular TLDs and ccTLDs you have come across on hosting sites? Put them all in a JSON Array.""".format(size=size)
    results = json.loads(prepare_output(ask_chatgpt(prompt)))
    return results
