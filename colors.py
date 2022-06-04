PURPLE = '\033[95m'
BLUE = '\033[94m'
CYAN = '\033[96m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
RED = '\033[91m'
BOLD = '\033[1m'
UNDERLINE = '\033[4m'
END_COLOR = '\033[0m'

COLOR_LIST = [
    '\033[95m',
    '\033[94m',
    '\033[96m',
    '\033[92m',
    '\033[93m',
    '\033[91m',
    '\033[1m',
    '\033[4m'
]

def test_all_colors():
    """ Prints a test string in every color. """
    for c in COLOR_LIST:
        print(c + 'Hello World!' + END_COLOR)
