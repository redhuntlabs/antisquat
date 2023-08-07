import nltk, re, publicsuffix2

def between(s, start, end):
    return s.split(start)[1].split(end)[0]

def eliminate_from_blacklist(url_list, blacklist):
    new_url_list = []
    if len(blacklist) == 0: return url_list

    for item in blacklist:
        for url in url_list:
            if item not in url: new_url_list.append(url)

    return new_url_list
    
def clean_text(text):
    # Tokenize the text into sentences
    sentences = nltk.sent_tokenize(text)
    # Define the parts of speech to keep
    pos_to_keep = ['NN', 'NNS', 'NNP', 'NNPS', 'JJ', 'JJR', 'JJS', 'VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ']
    # Define the stopwords to remove
    stopwords = nltk.corpus.stopwords.words('english')
    # Define the regex pattern to match non-alphanumeric characters
    pattern = re.compile(r'[^a-zA-Z0-9\s]')
    # Define the list of words to remove
    words_to_remove = ['\n'] + stopwords + ['mr', 'mrs', 'ms', 'dr', 'prof', 'etc']
    # Clean each sentence
    cleaned_sentences = []
    for sentence in sentences:
        # Tokenize the sentence into words
        words = nltk.word_tokenize(sentence)
        # Remove non-alphanumeric characters
        words = [pattern.sub('', word) for word in words]
        # Remove words that are less than 2 characters long
        words = [word for word in words if len(word) > 2]
        # Remove stopwords and other words to remove
        words = [word.lower() for word in words if word.lower() not in words_to_remove]
        # Tag the words with their parts of speech
        tagged_words = nltk.pos_tag(words)
        # Keep only the words with the desired parts of speech
        words_to_keep = [word for word, pos in tagged_words if pos in pos_to_keep]
        # Join the words back into a sentence
        cleaned_sentence = ' '.join(words_to_keep)
        cleaned_sentences.append(cleaned_sentence)
    # Join the cleaned sentences back into a block of text
    cleaned_text = ' '.join(cleaned_sentences)
    return cleaned_text

ribbon_bar_keywords = [
        "Home",
        "About",
        "Images",
        "News",
        "Shopping",
        "Products",
        "Services",
        "Solutions",
        "Pricing",
        "Features",
        "Blog",
        "Contact Us",
        "Support",
        "Help",
        "Sign In",
        "Sign Up",
        "Register",
        "Login",
        "Account",
        "Dashboard",
        "Profile",
        "Settings",
        "Notifications",
        "Orders",
        "Cart",
        "Wishlist",
        "Favorites",
        "Checkout",
        "Shipping",
        "Payment",
        "Order",
        "Privacy",
        "Policy",
        "Support",
        "Documentation",
        "API",
        "Integrations",
        "Analytics",
        "Reports",
        "Security",
        "Billing",
        "Upgrade",
        "Log Out",
        "Feedback",
        "Demo",
        "Live", 
        "Chat",
        "Careers",
        "Partners",
        "Affiliate",
        "News",
        "Events",
        "Community",
        "Mobile"
    ]

def generate_ribbon_bar_combinations(domain, keywords):
    tld = publicsuffix2.get_tld(domain)
    domain = domain.replace(tld, "").replace('.', '')

    combinations = []

    domain = domain.strip("-_")
    
    for keyword in keywords:
        keyword = keyword.strip("-_").lower().replace(" ", "")
        combinations.append(f"{keyword}-{domain}.{tld}")
        combinations.append(f"{keyword}_{domain}.{tld}")
        combinations.append(f"{domain}-{keyword}.{tld}")
        combinations.append(f"{domain}_{keyword}.{tld}")
        combinations.append(f"{domain}{keyword}.{tld}")
        combinations.append(f"{keyword}{domain}.{tld}")

    final_list = []
    for domain in combinations:
        if "https://" not in domain: final_list.append(f'https://{domain}')
        else: final_list.append(f'{domain}')

    return final_list

def similar_word(string, substring):
    threshold=2

    string = string.lower()
    substring = substring.lower()

    def levenshtein_distance(s1, s2):
        m, n = len(s1), len(s2)
        dp = [[0] * (n + 1) for _ in range(m + 1)]

        for i in range(m + 1):
            for j in range(n + 1):
                if i == 0: dp[i][j] = j
                elif j == 0: dp[i][j] = i
                elif s1[i - 1] == s2[j - 1]: dp[i][j] = dp[i - 1][j - 1]
                else: dp[i][j] = 1 + min(dp[i - 1][j], dp[i][j - 1], dp[i - 1][j - 1])
        return dp[m][n]

    for i in range(len(string) - len(substring) + 1):
        distance = levenshtein_distance(string[i:i + len(substring)], substring)
        if distance <= threshold: return True
    
    return False






