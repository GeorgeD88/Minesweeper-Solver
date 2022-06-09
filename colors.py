from collections import defaultdict


PURPLE = '\033[95m'
BLUE = '\033[34m'
CYAN = '\033[96m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
RED = '\033[91m'
BOLD = '\033[1m'
UNDERLINE = '\033[4m'
CIRCLE = '\033[52m'
END_COLOR = '\033[0m'

color_names = defaultdict(lambda: None, {
    '\033[95m': 'PURPLE',
    '\033[34m': 'BLUE',
    '\033[96m': 'CYAN',
    '\033[92m': 'GREEN',
    '\033[93m': 'YELLOW',
    '\033[91m': 'RED',
    '\033[1m': 'BOLD',
    '\033[4m': 'UNDERLINE',
    '\033[52m': 'CIRCLE',
    '\033[0m': 'END_COLOR'
})

COLOR_LIST = [
    '\033[95m',
    '\033[34m',
    '\033[96m',
    '\033[92m',
    '\033[93m',
    '\033[91m',
    '\033[1m',
    '\033[4m',
    '\033[52m'
]

def test_all_colors():
    """ Prints a test string in every color. """
    for c in COLOR_LIST:
        print(c + 'Hello World!' + END_COLOR)
