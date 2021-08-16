import html5lib

# ----------------------------- #

BINMAY_URL = 'https://binusmaya.binus.ac.id'
HTML_PARSER = 'html5lib'

class ErrorCodes:
    UNKNOWN = -1
    SCRAPE_FAIL = 0
    INCORRECT_VALUES = 1

# ----------------------------- #

if __name__ == '__main__':
    html5lib.__version__