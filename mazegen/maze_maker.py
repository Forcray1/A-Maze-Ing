from __future__ import annotations

import random
from typing import Callable, Optional

N, S, E, W = 1, 2, 4, 8
BLOCK = 16
OPPOSITE = {N: S, S: N, E: W, W: E}
Direction = [(0, -1, N), (0, 1, S), (1, 0, E), (-1, 0, W)]


def _is_inside(x: int, y: int, width: int, height: int) -> bool:
    """
    Verify if the actual cell is in the maze
    """
    return 0 <= x < width and 0 <= y < height


def _build_42_mask(width: int, height: int) -> set[tuple[int, int]]:
    """
    Build a centered 42 logo.
    """
    pattern = [
        "1000111",
        "1000001",
        "1110111",
        "0010100",
        "0010111",
    ]

    offset_x = (width - 7) // 2
    offset_y = (height - 5) // 2
    cells: set[tuple[int, int]] = set()

    for row, line in enumerate(pattern):
        for col, char in enumerate(line):
            if char == "1":
                cells.add((offset_x + col, offset_y + row))
    return cells


class MazeGenerator:
    """
    Maze generator based on iterative DFS (Depth First Search).
    """

    def __init__(
        self,
        width: int,
        height: int,
        entry: tuple[int, int],
        exit_point: tuple[int, int],
        perfect: bool = True,
        print_42: bool = False,
        seed: Optional[int] = None,
        progress_callback: Optional[Callable[[list[list[int]]], None]] = None,
    ) -> None:
        self.width = int(width)
        self.height = int(height)
        self.entry = entry
        self.exit_point = exit_point
        self.perfect = perfect
        self.print_42 = print_42
        self.randomizer = random.Random(seed)
        self.progress_callback = progress_callback

    @classmethod
    def from_config(
        cls,
        maze: dict,
        perfect: bool,
        print_42: bool,
        seed: Optional[int] = None,
        progress_callback: Optional[Callable[[list[list[int]]], None]] = None,
    ) -> "MazeGenerator":
        """
        Build a MazeGenerator from the existing project configuration map.
        """
        width = int(maze["WIDTH"])
        height = int(maze["HEIGHT"])
        start_x, start_y = map(int, maze["ENTRY"].replace(" ", "").split(","))
        end_x, end_y = map(int, maze["EXIT"].replace(" ", "").split(","))
        return cls(
            width=width,
            height=height,
            entry=(start_x, start_y),
            exit_point=(end_x, end_y),
            perfect=perfect,
            print_42=print_42,
            seed=seed,
            progress_callback=progress_callback,
        )

    def _normalize_point(self, point: tuple[int, int]) -> tuple[int, int]:
        x, y = point
        if x < 0 or y < 0 or x >= self.width or y >= self.height:
            raise ValueError("point is outside maze bounds")
        return x, y

    def generate(self) -> list[list[int]]:
        """
        Generate and return a maze grid.
        """
        grid = [[0 for _ in range(self.width)] for _ in range(self.height)]
        visited = [
            [False for _ in range(self.width)]
            for _ in range(self.height)
        ]

        start_x, start_y = self._normalize_point(self.entry)
        end_x, end_y = self._normalize_point(self.exit_point)

        blocked_cells: set[tuple[int, int]] = set()
        if self.print_42 and self.width >= 7 and self.height >= 5:
            blocked_cells = _build_42_mask(self.width, self.height)
            blocked_cells.discard((start_x, start_y))
            blocked_cells.discard((end_x, end_y))
            for block_x, block_y in blocked_cells:
                visited[block_y][block_x] = True
                grid[block_y][block_x] = BLOCK

        stack: list[tuple[int, int]] = [(start_x, start_y)]
        visited[start_y][start_x] = True

        while stack:
            x, y = stack[-1]
            neighbors = []
            for dx, dy, direction in Direction:
                nx, ny = x + dx, y + dy
                if (
                    _is_inside(nx, ny, self.width, self.height)
                    and not visited[ny][nx]
                ):
                    neighbors.append((nx, ny, direction))

            if neighbors:
                nx, ny, direction = self.randomizer.choice(neighbors)
                grid[y][x] |= direction
                grid[ny][nx] |= OPPOSITE[direction]
                visited[ny][nx] = True
                stack.append((nx, ny))
                if self.progress_callback is not None:
                    self.progress_callback(grid)
            else:
                stack.pop()

        if not self.perfect:
            extra_openings = max(1, (self.width * self.height) // 12)
            for _ in range(extra_openings):
                x = self.randomizer.randrange(self.width)
                y = self.randomizer.randrange(self.height)
                if grid[y][x] == BLOCK:
                    continue
                dx, dy, direction = self.randomizer.choice(Direction)
                nx, ny = x + dx, y + dy
                if (
                    _is_inside(nx, ny, self.width, self.height)
                    and grid[ny][nx] != BLOCK
                ):
                    grid[y][x] |= direction
                    grid[ny][nx] |= OPPOSITE[direction]
                    if self.progress_callback is not None:
                        self.progress_callback(grid)

        return grid


def maze_maker(
    maze: dict,
    perfect: bool,
    print_42: bool,
    seed: Optional[int] = None,
    progress_callback: Optional[Callable[[list[list[int]]], None]] = None,
) -> list[list[int]]:
    """
    Backward-compatible wrapper kept for older callers.
    """
    return MazeGenerator.from_config(
        maze=maze,
        perfect=perfect,
        print_42=print_42,
        seed=seed,
        progress_callback=progress_callback,
    ).generate()
