
import pygame
import random
import sys

pygame.init()

# Screen and grid settings
GRID_WIDTH, GRID_HEIGHT = 10, 20
CELL_SIZE = 30
SCREEN_WIDTH = GRID_WIDTH * CELL_SIZE
SCREEN_HEIGHT = GRID_HEIGHT * CELL_SIZE
FPS = 60

# Colors
WHITE = (255, 255, 255)
GRAY = (50, 50, 50)
GHOST_COLOR = (150, 150, 150)

TETROMINOES = {
    'I': [[1, 1, 1, 1]],
    'J': [[1, 0, 0],
          [1, 1, 1]],
    'L': [[0, 0, 1],
          [1, 1, 1]],
    'O': [[1, 1],
          [1, 1]],
    'S': [[0, 1, 1],
          [1, 1, 0]],
    'T': [[0, 1, 0],
          [1, 1, 1]],
    'Z': [[1, 1, 0],
          [0, 1, 1]],
}

COLORS = {
    'I': (0, 255, 255),
    'J': (0, 0, 255),
    'L': (255, 165, 0),
    'O': (255, 255, 0),
    'S': (0, 255, 0),
    'T': (160, 32, 240),
    'Z': (255, 0, 0)
}

class Tetromino:
    def __init__(self, shape, x, y):
        self.shape_key = shape
        self.shape = TETROMINOES[shape]
        self.color = COLORS[shape]
        self.x = x
        self.y = y

    def rotate(self):
        self.shape = [list(row) for row in zip(*self.shape[::-1])]

    def get_cells(self):
        return [(self.x + j, self.y + i) for i, row in enumerate(self.shape) for j, val in enumerate(row) if val]

def create_grid(locked):
    grid = [[None for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
    for (x, y), color in locked.items():
        if 0 <= y < GRID_HEIGHT and 0 <= x < GRID_WIDTH:
            grid[y][x] = color
    return grid

def check_valid(shape, grid):
    for x, y in shape.get_cells():
        if x < 0 or x >= GRID_WIDTH or y >= GRID_HEIGHT or (y >= 0 and grid[y][x]):
            return False
    return True

def clear_lines(grid, locked):
    lines = 0
    for y in range(GRID_HEIGHT-1, -1, -1):
        if all(grid[y]):
            lines += 1
            for x in range(GRID_WIDTH):
                del locked[(x, y)]
            for k in sorted([key for key in locked if key[1] < y], reverse=True, key=lambda k: k[1]):
                x, yy = k
                color = locked.pop(k)
                locked[(x, yy + 1)] = color
    return lines

def draw_grid(surface, grid):
    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            rect = pygame.Rect(x*CELL_SIZE, y*CELL_SIZE, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(surface, grid[y][x] if grid[y][x] else GRAY, rect)
            pygame.draw.rect(surface, WHITE, rect, 1)

def draw_piece(surface, piece, ghost=False):
    for x, y in piece.get_cells():
        if y >= 0:
            rect = pygame.Rect(x*CELL_SIZE, y*CELL_SIZE, CELL_SIZE, CELL_SIZE)
            color = GHOST_COLOR if ghost else piece.color
            pygame.draw.rect(surface, color, rect)
            pygame.draw.rect(surface, WHITE, rect, 1)

def get_ghost_piece(piece, grid):
    ghost = Tetromino(piece.shape_key, piece.x, piece.y)
    ghost.shape = [row[:] for row in piece.shape]
    while check_valid(ghost, grid):
        ghost.y += 1
    ghost.y -= 1
    return ghost

def main():
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Advanced Tetris")
    clock = pygame.time.Clock()
    
    locked = {}
    current_piece = Tetromino(random.choice(list(TETROMINOES.keys())), 3, 0)
    hold_piece = None
    can_hold = True
    next_piece = Tetromino(random.choice(list(TETROMINOES.keys())), 3, 0)
    fall_time = 0
    fall_speed = 0.5
    score = 0

    running = True
    while running:
        grid = create_grid(locked)
        fall_time += clock.get_rawtime()
        clock.tick(FPS)

        if fall_time / 1000 >= fall_speed:
            current_piece.y += 1
            if not check_valid(current_piece, grid):
                current_piece.y -= 1
                for x, y in current_piece.get_cells():
                    locked[(x, y)] = current_piece.color
                current_piece = next_piece
                next_piece = Tetromino(random.choice(list(TETROMINOES.keys())), 3, 0)
                can_hold = True
                lines_cleared = clear_lines(grid, locked)
                score += lines_cleared * 100
            fall_time = 0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    current_piece.x -= 1
                    if not check_valid(current_piece, grid):
                        current_piece.x += 1
                elif event.key == pygame.K_RIGHT:
                    current_piece.x += 1
                    if not check_valid(current_piece, grid):
                        current_piece.x -= 1
                elif event.key == pygame.K_DOWN:
                    current_piece.y += 1
                    if not check_valid(current_piece, grid):
                        current_piece.y -= 1
                elif event.key == pygame.K_UP:
                    current_piece.rotate()
                    if not check_valid(current_piece, grid):
                        for _ in range(3):
                            current_piece.rotate()
                elif event.key == pygame.K_SPACE:
                    while check_valid(current_piece, grid):
                        current_piece.y += 1
                    current_piece.y -= 1
                elif event.key == pygame.K_c and can_hold:
                    if hold_piece:
                        current_piece, hold_piece = hold_piece, current_piece
                        current_piece.x, current_piece.y = 3, 0
                    else:
                        hold_piece = current_piece
                        current_piece = next_piece
                        next_piece = Tetromino(random.choice(list(TETROMINOES.keys())), 3, 0)
                    can_hold = False

        screen.fill((0, 0, 0))
        draw_grid(screen, grid)
        draw_piece(screen, get_ghost_piece(current_piece, grid), ghost=True)
        draw_piece(screen, current_piece)
        pygame.display.set_caption(f"Advanced Tetris - Score: {score}")
        pygame.display.update()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
