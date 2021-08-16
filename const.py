import html5lib

# ----------------------------- #

BINMAY_URL = 'https://binusmaya.binus.ac.id'
HTML_PARSER = 'html5lib'

class LoginError(Exception):

    UNKNOWN = -1
    SCRAPE_FAIL = 0
    INCORRECT_CREDENTIALS = 1

    def __init__(self, code: int) -> None:
        super().__init__()
        self.code = code

# ----------------------------- #

if __name__ == '__main__':
    html5lib.__version__