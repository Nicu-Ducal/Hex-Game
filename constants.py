# General data
INF = float('inf')

# GUI Information
WIDTH, HEIGHT = 1280, 720
BUTTON_WIDTH, BUTTON_HEIGHT = 90, 35
TEXT_BOX_WIDTH, TEXT_BOX_HEIGHT = 100, 35

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 102, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
ORANGE = (255, 128, 0)
PINK = (255, 0, 127)
LIGHT_GRAY = (224, 224, 224)
DARK_GRAY = (192, 192, 192)
DARKER_GRAY = (96, 96, 96)
INITIAL_TO_COLOR = {'R': RED, 'G': GREEN,
                    'B': BLUE, 'Y': YELLOW, 'O': ORANGE, 'P': PINK}


# Game related data
INITIAL_RADIUS = 80
INITIAL_CENTER = (WIDTH, HEIGHT)
DEPTHS = {"Incepator": 1, "Mediu": 2, "Avansat": 3}
GAME_MODE = {0: "pvp", 1: "pvc", 2: "pvc", 3: "cvc"}
