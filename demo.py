import pygame
from pygame.draw import line, rect
from pygame.rect import Rect
from pygame.time import Clock

import game

# define the size of the window
WINDOW_SIZE = (512 + 64, 512 + 32)

# initialize the board
board = game.Board(18, 17)

# intialize pygame
pygame.init()

pygame.display.set_caption('Snake')
window_surface = pygame.display.set_mode(WINDOW_SIZE)

background = pygame.Surface(WINDOW_SIZE)
background.fill(pygame.Color('#000000'))

font = pygame.font.Font('freesansbold.ttf', 12)

def draw_board(board: game.Board):
    """Draws the game's state to the screen
    
    Args:
        board: the board that is the game"""
    global WINDOW_SIZE
    global window_surface

    # draw the background grid
    grid_width = WINDOW_SIZE[0] / board.width
    grid_height = WINDOW_SIZE[1] / board.height

    # vertical lines
    for x in range(1, board.width):
        line(window_surface, '#444444', (x * grid_width, 0), (x * grid_width, WINDOW_SIZE[1]))

    for y in range(1, board.height):
        line(window_surface, '#444444', (0, y * grid_height), (WINDOW_SIZE[0], y * grid_height))
    
    # draw the apple
    y = (board.apple.position.y + 1) * grid_height
    y = WINDOW_SIZE[1] - y
    rect(
        window_surface, 
        '#FF0000', 
        Rect(board.apple.position.x * grid_width, y, grid_width, grid_height)
        )
    
    # draw the snake
    for position in board.snake.positions:
        y = (position.y + 1) * grid_height
        y = WINDOW_SIZE[1] - y
        rect(
            window_surface,
            '#00FF00',
            Rect(position.x * grid_width, y, grid_width, grid_height)
        )
    
    # draw the cycle:
    for p1, p2 in zip(board.cycle[:-1], board.cycle[1:]):
        x1, y1 = p1
        x2, y2 = p2
        
        # scale
        x1 *= grid_width
        x2 *= grid_width
        y1 *= grid_height
        y2 *= grid_height

        # invert y
        y1 = WINDOW_SIZE[1] - y1
        y2 = WINDOW_SIZE[1] - y2

        # shift to center
        x_shift = grid_width // 2
        y_shift = grid_height // 2

        x1 += x_shift
        x2 += x_shift
        y1 -= y_shift
        y2 -= y_shift

        line(window_surface, '#FF00FF', (x1, y1), (x2, y2))
    
    for number, position in enumerate(board.cycle):
        text = font.render(str(number), True, '#FFFFFF')
        x = position.x * grid_width
        y = (position.y + 1) * grid_height
        y = WINDOW_SIZE[1] - y
        window_surface.blit(text, (x, y))

# monitor the time
clock = Clock()

# frame counter
frame_num = 0
# input buffering
next_direction = 0

# some bools to determine what we're doing
running = True
moving = True
while running:
    # process the events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_w:
                next_direction = 1
            if event.key == pygame.K_a:
                next_direction = 2
            if event.key == pygame.K_s:
                next_direction = 3
            if event.key == pygame.K_d:
                next_direction = 0
    
    # only move once every 20 frames
    if frame_num % 20 == 0:
        board.turn(next_direction)
        if moving:
            try:
                board.step()
            except Exception as e:
                # win/loss conditions are currently just exceptions
                print(e)
                moving = False
            

    window_surface.blit(background, (0, 0))
    draw_board(board)

    pygame.display.update()
    frame_num += 1
    clock.tick(60)