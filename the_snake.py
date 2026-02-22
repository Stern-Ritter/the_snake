"""
Snake game implementation using Pygame.

This module contains the classic Snake game where the player controls a snake
to eat apples and grow longer. The game ends if the snake collides with itself.
"""
from random import choice, randint

import pygame

# Constants for field and grid sizes
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

# Movement directions
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# Colors
BOARD_BACKGROUND_COLOR = (0, 0, 0)

BORDER_COLOR = (93, 216, 228)

APPLE_COLOR = (255, 0, 0)

SNAKE_COLOR = (0, 255, 0)

# Game speed (frames per second)
SPEED = 5

# Initialize pygame and set up the game window
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)
pygame.display.set_caption('Snake')
clock = pygame.time.Clock()

KEYS_DIRECTIONS = {
    pygame.K_UP: (UP, DOWN),
    pygame.K_DOWN: (DOWN, UP),
    pygame.K_LEFT: (LEFT, RIGHT),
    pygame.K_RIGHT: (RIGHT, LEFT)
}


def handle_keys(game_object):
    """
    Process keyboard input to change the snake's direction.

    Args:
        game_object (Snake): The snake object whose direction will be updated.
    """
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            raise SystemExit
        if event.type == pygame.KEYDOWN and event.key in KEYS_DIRECTIONS:
            new_direction, opposite_direction = KEYS_DIRECTIONS[event.key]
            if game_object.direction != opposite_direction:
                game_object.next_direction = new_direction


class GameObject:
    """Base class for all game objects that can be drawn on the screen."""

    def __init__(self, body_color=None):
        """
        Initialize a game object with a color and a default position.

        Args:
            body_color (tuple, optional): RGB color of the object.
            Defaults to None.
        """
        self.body_color = body_color
        x_pos = SCREEN_WIDTH // 2
        y_pos = SCREEN_HEIGHT // 2
        self.position = (x_pos, y_pos)

    def draw(self):
        """Draw the object on the screen. Must be implemented by subclasses."""


class Apple(GameObject):
    """Class representing the apple that the snake eats."""

    def __init__(self, occupied_positions=[], body_color=APPLE_COLOR):
        """
        Initialize an apple with a color and a random position.

        Args:
            body_color (tuple, optional): RGB color of the apple.
            Defaults to APPLE_COLOR.
        """
        super().__init__(body_color)
        self.randomize_position(occupied_positions)

    def randomize_position(self, occupied_positions):
        """
        Place the apple at a random grid-aligned position within
        the screen.

        Args:
            occupied_positions (list of tuples): A list of (x, y)
            positions that are currently occupied (e.g., by the snake's body).

        Raises:
            Exception: If there are no free cells left on the board (i.e., when
                the number of occupied positions equals or exceeds
                the total number of grid cells).
        """
        total_cells = GRID_WIDTH * GRID_HEIGHT
        if len(occupied_positions) >= total_cells:
            raise Exception("No free cells on board")
        while True:
            x_pos = randint(0, GRID_WIDTH - 1) * GRID_SIZE
            y_pos = randint(0, GRID_HEIGHT - 1) * GRID_SIZE
            new_position = (x_pos, y_pos)
            if new_position not in occupied_positions:
                self.position = new_position
                break

    def draw(self):
        """Draw the apple as a filled rectangle with a border."""
        rect = pygame.Rect(self.position, (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(screen, self.body_color, rect)
        pygame.draw.rect(screen, BORDER_COLOR, rect, 1)


class Snake(GameObject):
    """Class representing the player-controlled snake."""

    def __init__(self, body_color=SNAKE_COLOR):
        """
        Initialize the snake with a color, starting position,
                 and default direction.

        Args:
            body_color (tuple, optional): RGB color of the snake.
            Defaults to SNAKE_COLOR.
        """
        super().__init__(body_color)
        self.length = 1
        x_pos = SCREEN_WIDTH // 2
        y_pos = SCREEN_HEIGHT // 2
        self.positions = [(x_pos, y_pos)]
        self.last = None
        self.direction = RIGHT
        self.next_direction = None

    def update_direction(self):
        """Apply the next direction if it is set."""
        if self.next_direction:
            self.direction = self.next_direction
            self.next_direction = None

    def move(self):
        """
        Move the snake one step in the current direction.
        The screen wraps around at the edges.
        """
        head_x, head_y = self.get_head_position()
        dx, dy = self.direction
        x_pos = head_x + dx * GRID_SIZE
        y_pos = head_y + dy * GRID_SIZE
        head_position = (x_pos % SCREEN_WIDTH, y_pos % SCREEN_HEIGHT)

        self.positions.insert(0, head_position)

        if len(self.positions) > self.length:
            self.last = self.positions.pop()

    def draw(self):
        """
        Draw the snake on the screen.
        The head is drawn separately to ensure it stands out,
        and the last segment is erased by drawing over it with
        the background color.
        """
        for position in self.positions[:-1]:
            rect = (pygame.Rect(position, (GRID_SIZE, GRID_SIZE)))
            pygame.draw.rect(screen, self.body_color, rect)
            pygame.draw.rect(screen, BORDER_COLOR, rect, 1)

        head_rect = pygame.Rect(self.get_head_position(),
                                (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(screen, self.body_color, head_rect)
        pygame.draw.rect(screen, BORDER_COLOR, head_rect, 1)

        if self.last:
            last_rect = pygame.Rect(self.last, (GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(screen, BOARD_BACKGROUND_COLOR, last_rect)

    def get_head_position(self):
        """Return the current position of the snake's head."""
        return self.positions[0]

    def reset(self):
        """Reset the snake to its initial state after a collision."""
        self.length = 1
        x_pos = SCREEN_WIDTH // 2
        y_pos = SCREEN_HEIGHT // 2
        self.positions = [(x_pos, y_pos)]
        self.last = None
        self.direction = choice([UP, DOWN, LEFT, RIGHT])
        self.next_direction = None


def main():
    """Main game loop."""
    pygame.init()

    snake = Snake()
    apple = Apple(snake.positions)

    while True:
        clock.tick(SPEED)

        handle_keys(snake)
        snake.update_direction()
        snake.move()

        if apple.position in snake.positions:
            snake.length += 1
            apple.randomize_position(snake.positions)
        elif snake.get_head_position() in snake.positions[1:]:
            screen.fill(BOARD_BACKGROUND_COLOR)
            snake.reset()

        apple.draw()
        snake.draw()

        pygame.display.update()


if __name__ == '__main__':
    main()
