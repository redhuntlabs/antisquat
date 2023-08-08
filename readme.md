# AntiSquat

<img src="./antisquat.png">

AntiSquat leverages AI techniques such as natural language processing (NLP), large language models (ChatGPT) and more to empower detection of typosquatting and phishing domains.

## How to use
- Clone the project via `git clone https://github.com/redhuntlabs/antisquat`. 
- Install all dependencies by typing `pip install -r requirements.txt`.
- Get a ChatGPT API key at https://platform.openai.com/account/api-keys
- Create a file named `.openai-key` and paste your chatgpt api key in there.
- (Optional) Visit https://developer.godaddy.com/keys and grab a GoDaddy API key. Create a file named `.godaddy-key` and paste your godaddy api key in there.
- Create a file named ‘domains.txt’. Type in a line-separated list of domains you’d like to scan.
- (Optional) Create a file named `blacklist.txt`. Type in a line-separated list of domains you’d like to ignore. Regular expressions are supported.
- Run antisquat using `python3.8 antisquat.py domains.txt`

## Examples:

Let’s say you’d like to run antisquat on "flipkart.com".

Create a file named "domains.txt", then type in `flipkart.com`. Then run `python3.8 antisquat.py domains.txt`.

AntiSquat generates several permutations of the domain, iterates through them one-by-one and tries extracting all contact information from the page.

### Test case:

A test case for amazon.com is attached. To run it without any api keys, simply run `python3.8 test.py`

![AntiSquat running on Amazon.com](demo.png)

Here, the tool appears to have captured a test phishing site for amazon.com. Similar domains that may be available for sale can be captured in this way and any contact information from the site may be extracted.

If you'd like to know more about the tool, make sure to check out our <a href="https://redhuntlabs.com/blog/antisquat-an-ai-powered-solution-to-prevent-typosquatting-and-phishing/">blog</a>.

## Acknowledgements
<ul type="disc">
<li><a href="https://www.blackhat.com/us-23/arsenal/schedule/index.html#antisquat---an-ai-powered-phishing-domain-finder-33636">Black Hat USA 2023 [Arsenal]</a></li>
</ul>

*[`To know more about our Attack Surface Management platform, check out NVADR.`](https://redhuntlabs.com/nvadr)*
