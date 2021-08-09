"""All Game Constants"""
FPS = 60
SCREENX, SCREENY = (360, 600)
GOAL_WIDTH = SCREENX * 0.4

AI_DIFFICULTY = 3 # Set higher for more difficulty (1-4)
PLAYER_RADIUS = (SCREENX * 3.25) // 51.25
BALL_RADIUS =  PLAYER_RADIUS - 3
MAX_PLAYER_SPEED = 0.8
MAX_BALL_SPEED = 1.6

GOAL_TEXT_DELAY = 3

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
BACKGROUND_COLOR = (0, 0xC0, 0)

PLAYER_COLORS = [RED, BLUE]

ABOUT_TEXT = """Air hockey is a game where
two players play against each other

Move your player using the mouse
Hit the ball to the opponent's
side to score a goal
First one to get 7 goals wins!\n
-----------------------------------\n
Credits:\n
Creator - Mashaal Sayeed
Font - OmenType
Images - pzUH
"""