import json
import os
import html5lib
import stdiomask

from colorama import Fore

# ----------------------------- #

USERNAME = ''
PASSWORD = ''

BINMAY_URL = 'https://binusmaya.binus.ac.id'
HTML_PARSER = 'html5lib'

# ----------------------------- #

if __name__ == '__main__':
    html5lib.__version__

# ----------------------------- #

def load_config():
    """
    Loads the config.json file
    """
    global USERNAME, PASSWORD

    config = {
        'username': '',
        'password': ''
    }

    if not os.path.exists('config.json'):
        print(f'{Fore.LIGHTRED_EX}Cannot find config.json file!{Fore.RESET}')
        print(f'Generating {Fore.LIGHTYELLOW_EX}config.json{Fore.RESET} file...')
        print()

        config['username'] = input('Your BINUS username (without \'@binus.ac.id\'): ')
        config['password'] = stdiomask.getpass('Your BINUS password: ')

        with open('config.json', 'w') as file:
            file.write(json.dumps(config, indent=4))
    else:
        with open('config.json', 'r') as file:
            content = file.read()
            config = json.loads(content)

    USERNAME = config['username']
    PASSWORD = config['password']

    print(f'{Fore.LIGHTGREEN_EX}Successfully loaded {Fore.LIGHTYELLOW_EX}config.json{Fore.LIGHTGREEN_EX}!')
    print(Fore.RESET)