from mazegen.maze_maker import N, S, E, W


_DIRECTION = {
    "\x1b[A": (0, -1),
    "\x1b[B": (0, 1),
    "\x1b[C": (1, 0),
    "\x1b[D": (-1, 0),
}


class Player:
    """
    Represent the player position and movement rules.
    """

    def __init__(
        self,
        grid: list[list[int]],
        width: int,
        height: int,
        start: tuple[int, int],
        exit_point: tuple[int, int],
    ) -> None:
        self.grid = grid
        self.width = width
        self.height = height
        self.x, self.y = start
        self.exit_x, self.exit_y = exit_point

        self.steps: int = 0
        self.path: list[tuple[int, int]] = [start]
        self.won: bool = False

    def can_move(self, direction: str) -> bool:
        """
        Return True if there is an open path in the given direction.
        """
        cell = self.grid[self.y][self.x]
        if direction == "\x1b[A":
            return bool(cell & N)
        if direction == "\x1b[B":
            return bool(cell & S)
        if direction == "\x1b[C":
            return bool(cell & E)
        if direction == "\x1b[D":
            return bool(cell & W)
        return False

    def get_position(self) -> tuple[int, int]:
        """
        Return current player coordinates.
        """
        return self.x, self.y

    def move(self, direction: str) -> bool:
        """
        Move the player if the requested direction is valid and open.
        """
        if direction not in _DIRECTION:
            return False

        if not self.can_move(direction):
            return False

        dx, dy = _DIRECTION[direction]
        self.x += dx
        self.y += dy
        self.steps += 1
        self.path.append((self.x, self.y))
        self.won = (self.x, self.y) == (self.exit_x, self.exit_y)
        return True
