from sense_hat import SenseHat
import random
import time

from sensegame import Joystick

# Constants
color_food = [0, 255, 0]
color_snake_head = [255, 255, 0]
color_snake_body1 = [180, 130, 0]
color_snake_body2 = [190, 30, 0]
color_barrier = [255, 0, 0]
color_background = [0, 0, 0]
loop_time_seconds = 0.2

def interpolate_color(A, B, t):
    return [int(a*(1.0 - t) + b*t) for a, b in zip(A, B)]

class Game(object):
    def __init__(self):
        # Initialize sense hat
        self.sense = SenseHat()
        self.sense.clear()

        self.food_cells = []
        self.snake_cells = [(2, 4)]
        self.barrier_cells = [(0, 0), (0, 7), (7, 0), (7, 7)]

        self.snake_direction = "UP"

        self.joystick = Joystick()
        self.joystick.register_key_press_callback(self.on_key_pressed)

    def play(self):
        self.place_food()

        while True:
            self.show()
            time.sleep(loop_time_seconds)

            self.move_snake()
            self.handle_collision()

    def on_key_pressed(self, key):
        if key in ["UP", "DOWN", "LEFT", "RIGHT"]:
            self.snake_direction = self.joystick.last_key_pressed

    def handle_collision(self):
        head_cell = self.snake_cells[-1]
        body_cells = self.snake_cells[:-1]

        # Check for barriers or self-intersection
        if head_cell in body_cells or head_cell in self.barrier_cells:
            print("Game over!")
            exit(0)

        if head_cell in self.food_cells:
            # #at the current food cell.
            # We'll do this by duplicating the tail. That means that next time we
            # move, our tail will stay at the same position.
            self.snake_cells = [self.snake_cells[0]] + self.snake_cells

            # Remove the food currently at the cell
            self.food_cells.remove(head_cell)

            # Place more food since we just ate it
            self.place_food()

    def cell_to_index(self, cell):
        x, y = cell
        return y * 8 + x

    def index_to_cell(self, index):
        return (index // 8, index % 8)

    def _get_cell_color(self, cell):
        if cell in self.food_cells:
            return color_food
        elif cell in self.snake_cells:
            if cell == self.snake_cells[-1]:
                return color_snake_head
            else:
                i = self.snake_cells.index(cell)
                return interpolate_color(color_snake_body1, color_snake_body2, i / len(self.snake_cells))
        elif cell in self.barrier_cells:
            return color_barrier
        else:
            return color_background

    def _iter_cells(self):
        for y in range(8):
            for x in range(8):
                yield (x, y)

    def show(self):
        pixels = [self._get_cell_color(c) for c in self._iter_cells()]
        self.sense.set_pixels(pixels)

    def move_snake(self):
        # Remove tail
        x, y = self.snake_cells[-1]
        self.snake_cells = self.snake_cells[1:]

        next = None
        if self.snake_direction == "UP":
            next = self.normalize(x, y-1)
        elif self.snake_direction == "DOWN":
            next = self.normalize(x, y+1)
        elif self.snake_direction == "LEFT":
            next = self.normalize(x-1, y)
        elif self.snake_direction == "RIGHT":
            next = self.normalize(x+1, y)

        self.snake_cells.append(next)

    def normalize(self, x, y):
        return (x + 8) % 8, (y + 8) % 8

    def is_cell_free(self, cell):
        return cell not in self.food_cells and cell not in self.snake_cells and cell not in self.barrier_cells

    def place_food(self):
        c = random.choice(list(c for c in self._iter_cells() if self.is_cell_free(c)))
        self.food_cells.append(c)

Game().play()
