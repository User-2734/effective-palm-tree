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
        self.cycle = self.create_hamiltonian_cycle()
        self.cooldown = 0

    def create_hamiltonian_cycle(self) -> list[Position]:
        """Connects all the spaces on the board into one big ciclical path for the snake to follow.
        Those pesky size restrictions are caused by this function
        
        Returns:
            an ordered list of positions"""
        start_pos = Position(0, 0)

        # TODO randomize this more
        # TODO make this work on grids where the even and odd axes are switched
        cycle = [start_pos]

        top_y = self.height - 1
        bottom_y = 1

        right_x = self.width - 1
        shifted = False

        # allow space for a botom channel
        while cycle[0] != cycle[-1] or len(cycle) == 1:
            current_pos = cycle[-1]
            if current_pos.y == top_y and not shifted:
                shifted = True
                cycle.append(Position(current_pos.x + 1, current_pos.y))
            elif current_pos.y == bottom_y and current_pos.x != 0 and current_pos.x != right_x and not shifted:
                shifted = True
                cycle.append(Position(current_pos.x + 1, current_pos.y))
            elif current_pos.y == 0 and current_pos.x != 0:
                cycle.append(Position(current_pos.x - 1, current_pos.y))
            else:
                shifted = False
                if current_pos.x % 2 == 0:
                    cycle.append(Position(current_pos.x, current_pos.y + 1))
                else:
                    cycle.append(Position(current_pos.x, current_pos.y - 1))
        
        cycle.pop(-1)
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
        if not positions: raise Exception('You Win!')
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

    def position_to_path_index(self, position: Position) -> int:
        # TODO comment this
        return self.cycle.index(position)

    def get_path_index(self) -> int:
        """Returns where in the cycle the snake is
        
        Returns:
            the index in the cycle of the position of the snake's head"""
        return self.position_to_path_index(self.snake.head_position())
    
    def get_apple_index(self) -> int:
        """Returns where in the cycle the apple is
        
        Returns:
            the index in the cycle of the position of the apple"""
        return self.position_to_path_index(self.apple.position)
    
    def get_next_move(self) -> int:
        """Returns the direction the snake needs to turn to follow the cycle
        
        Returns:
            the direction the snake should turn"""
        current_index = self.get_path_index()
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
    
    def index_difference(self, current: int, target: int) -> int:
        difference = 0
        while current != target:
            difference += 1
            current += 1
            current %= len(self.cycle)
        return difference
    
    def make_ai_move(self):
        """This does not work. yet."""
        if self.cooldown > 0:
            self.turn(self.get_next_move())
            self.cooldown -= 1
            return
        # generate each direction we can turn
        directions = list(range(4))
        directions.remove((self.snake.direction + 2) % 4)
        
        # default scenario where we just follow the curve
        min_distance = self.index_difference(self.get_path_index() + 1, self.get_apple_index())
        best_direction = self.get_next_move()
        cooldown = 0

        cx, cy = self.snake.head_position()

        # evaluate the directions.
        for test_direction in directions:
            dx, dy = direction_to_offset(test_direction)
            test_pos = Position(cx + dx, cy + dy)
            if test_pos in self.snake.positions: continue
            try:
                test_index = self.position_to_path_index(test_pos)
            except ValueError: # out of bounds
                continue
            distance_ = self.index_difference(test_index, self.get_apple_index())
            if distance_ < min_distance:
                # TODO add in some more checks here
                # prevent taking shortcuts that compromise the path
                cooldown = self.snake.length
                min_distance = distance_
                best_direction = test_direction
        
        self.cooldown = cooldown - 1
        self.turn(best_direction)