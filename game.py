from random import choice
from math import sqrt

def direction_to_offset(direction: int) -> tuple[int, int]:
    """Converts a direction into the x and y changes it causes
    
    Args:
        direction: in int representing a direction
    
    Returns:
        A tuple of the x y offset caused by the direction"""
    direction = abs(direction) % 4 # clamp the range
    x = [1, 0, -1, 0]
    y = [0, 1, 0, -1]
    return x[direction], y[direction]

def distance(p1: 'Position', p2: 'Position') -> float:
    """Calculates the distance between two positions
    
    Args:
        p1: the first position
        p2: the second position
    
    Returns:
        The distance between the two positions"""
    # unpack
    x1, y1 = p1
    x2, y2 = p2

    # pythagorean theorem
    dx = x1 - x2
    dy = y1 - y2

    return sqrt((dx ** 2) + (dy ** 2))

class Position(tuple):
    """A class that holds a position
    
    Attributes:
        x: the x coordinate
        y: the y coordinate"""
    def __new__(cls, x: int, y: int):
        """Create a new instance.
        
        Args:
            x: the x coordinate
            y: the y coordinate"""
        return super().__new__(cls, (x, y))
    
    @property
    def x(self) -> int:
        return self[0]
    
    @property
    def y(self) -> int:
        return self[1]

class Snake:
    """A snake on the board
    
    Attributes:
        positions: a list of all positions occupied by the snake
        length: the length of the snake
        diretion: the direction the snake is heading"""
    def __init__(self, head_pos: Position, length: int, direction: int):
        """Initialize an instance
        
        Args:
            head_pos: the location of the snake's head
            length: how long to make the snake
            direction: the snake's direction of travel"""
        self.positions = [head_pos]
        self.length = length
        self.direction = direction

    def head_position(self) -> Position:
        """Returns the position of the snake's head
        
        Returns:
            the position of the snake's head"""
        return self.positions[-1]

    def step(self) -> None:
        """Move forward"""
        # figure out where the next bit goes
        dx, dy = direction_to_offset(self.direction)
        head_position = self.head_position()
        next_position = Position(head_position.x + dx, head_position.y + dy)
        
        # advance the snake
        self.positions.append(next_position)
        if len(self.positions) > self.length: self.positions.pop(0)

class Apple:
    """An apple on the board
    
    Attributes:
        position: the apple's position"""
    def __init__(self, position: Position) -> None:
        """Initilize an instance
        
        Args:
            position: the position of the apple"""
        self.position = position

class Board:
    """An instance of the game of snake
    
    Attributes:
        width: the width of the board.
        height: the height of the board.
        snake: the snake on the board
        apple: the apple on the board
        cycle: a hamiltionian cycle of the board. Used for automatic playing"""
    def __init__(self, width: int, height: int) -> None:
        """Initialize an instance
        
        Args:
            width: how wide to make the game.
            height: the height of the board."""
        self.width = width
        self.height = height
        self.snake = Snake(
            Position(width // 4, height // 2),
            3,
            0
        )
        self.apple = Apple(Position(3 * width // 4, height // 2))
        self.cycle = [] # self.cycle = self.create_hamiltonian_cycle()

    def create_hamiltonian_cycle(self) -> list[Position]:
        """Connects all the spaces on the board into one big ciclical path for the snake to follow.
        Those pesky size restrictions are caused by this function
        
        Returns:
            an ordered list of positions"""
        start_pos = Position(0, 0)

        cycle = [start_pos]

        right_x = self.width - 1
        top_y = self.height - 1
        left_x = 2
        bottom_y = 0
        current_pos = cycle[-1]

        while True:
            # up
            while current_pos.y < top_y:
                cycle.append(Position(current_pos.x, current_pos.y + 1))
                current_pos = cycle[-1]
            top_y -= 2

            if left_x > right_x and bottom_y > top_y:
                break

            # right
            while current_pos.x < right_x:
                cycle.append(Position(current_pos.x + 1, current_pos.y))
                current_pos = cycle[-1]
            right_x -= 2

            if left_x > right_x and bottom_y > top_y:
                break

            # down
            while current_pos.y > bottom_y:
                cycle.append(Position(current_pos.x, current_pos.y - 1))
                current_pos = cycle[-1]
            bottom_y += 2

            if left_x > right_x and bottom_y > top_y:
                break

            # left
            while current_pos.x > left_x:
                cycle.append(Position(current_pos.x - 1, current_pos.y))
                current_pos = cycle[-1]
            left_x += 2

            if left_x > right_x and bottom_y > top_y:
                print('Breaking')
                break
        
        # we start on the left, so we end on the left
        # so to draw a spiral on the right, we move 1 unit right
        cycle.append(Position(current_pos.x + 1, current_pos.y))
        current_pos = cycle[-1]
        cycle.append(Position(current_pos.x, current_pos.y - 1))
        current_pos = cycle[-1]
        cycle.append(Position(current_pos.x + 1, current_pos.y))
        current_pos = cycle[-1]
        top_y += 1
        left_x -= 1
        bottom_y -= 1
        right_x += 1
        while True:
            # up
            top_y += 2
            while current_pos.y < top_y:
                cycle.append(Position(current_pos.x, current_pos.y + 1))
                current_pos = cycle[-1]

            # left
            left_x -= 2
            while current_pos.x > left_x:
                cycle.append(Position(current_pos.x - 1, current_pos.y))
                current_pos = cycle[-1]

            # down
            bottom_y -= 2
            while current_pos.y > bottom_y and current_pos.y > 0:
                cycle.append(Position(current_pos.x, current_pos.y - 1))
                current_pos = cycle[-1]
            
            # we only break here because we're guarenteed to end up going down
            if current_pos.y == 0:
                break

            # right
            right_x += 2
            while current_pos.x < right_x:
                cycle.append(Position(current_pos.x + 1, current_pos.y))
                current_pos = cycle[-1]

        return cycle

    def turn(self, direction: int) -> None:
        """Rotates the snake in a direction.
        
        Args:
            direction: the direction to turn the snake"""
        if self.snake.direction == (direction + 2) % 4: return
        self.snake.direction = direction

    def move_apple(self) -> None:
        """Sets the apple to a new random position on the board."""
        positions = []
        for x in range(self.width):
            for y in range(self.height):
                pos = Position(x, y)
                if pos not in self.snake.positions:
                    positions.append(pos)
        if not pos: raise Exception('We\'ve won!')
        self.apple.position = choice(positions)
    
    def step(self) -> None:
        """Advances the game 1 step"""
        # update the snake
        self.snake.step()

        # bounds check
        if not (0 <= self.snake.head_position().x < self.width):
            raise Exception('Out of bounds!')
        if not (0 <= self.snake.head_position().y < self.height):
            raise Exception('Out of bounds!')
        
        # check for self collisions
        if self.snake.head_position() in self.snake.positions[:-1]:
            raise Exception('Self Collision!')
        if self.snake.head_position() == self.apple.position:
            self.snake.length += 1
            self.move_apple()

    def get_cycle_position(self) -> int:
        """Returns where in the cycle the snake is
        
        Returns:
            the index in the cycle of the position of the snake's head"""
        return self.cycle.index(self.snake.head_position())
    
    def get_next_move(self) -> int:
        """Returns the direction the snake needs to turn to follow the cycle
        
        Returns:
            the direction the snake should turn"""
        current_index = self.get_cycle_position()
        next_index = (current_index + 1) % len(self.cycle)

        current_position = self.snake.head_position()
        next_position = self.cycle[next_index]

        dx = next_position.x - current_position.x
        dy = next_position.y - current_position.y

        if dx == 1:
            direction = 0
        if dx == -1:
            direction = 2
        if dy == 1:
            direction = 1
        if dy == -1:
            direction = 3
        
        return direction
    
    def make_ai_move(self):
        """This does not work. yet."""
        apple_index = self.cycle.index(self.apple.position)
        head_index = self.cycle.index(self.snake.head_position())
        apple_pos = self.apple.position
        head_pos = self.snake.head_position()

        current_direction = self.snake.direction
        remaining_directions = [0, 1, 2, 3]
        remaining_directions.remove((current_direction + 2) % 4)

        cx, cy = head_pos

        directions = []
        for direction in remaining_directions:
            dx, dy = direction_to_offset(direction)
            directions.append(distance(Position(cx + dx, cy + dy), apple_pos))
        
        best_direction = remaining_directions[min(range(len(directions)), key=lambda x: directions[x])]

        dx, dy = direction_to_offset(best_direction)
        test_position = Position(cx + dx, cy + dy)

        # TODO implement domain/range tests
        test_index = self.cycle.index(test_position)
        if (test_index + (self.snake.length - 1) >= apple_index) and False:
            print('Snake may be too long')
            self.turn(self.get_next_move())
            return
        
        print(test_index, head_index)
        self.turn(best_direction)