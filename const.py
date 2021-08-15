import json
import html5lib

with open('config.json', 'r') as file:
    content = file.read()
    config = json.loads(content)

# ----------------------------- #

USERNAME = config['username']
PASSWORD = config['password']

BINMAY_URL = 'https://binusmaya.binus.ac.id'
HTML_PARSER = 'html5lib'

# ----------------------------- #

if __name__ == '__main__':
    html5lib.__version__
