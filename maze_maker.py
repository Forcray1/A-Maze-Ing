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
    Build a centered 42 mask with size 7x5.
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


def maze_maker(
    maze: dict,
    perfect: bool,
    print_42: bool,
    seed: Optional[int] = None,
    progress_callback: Optional[Callable[[list[list[int]]], None]] = None,
) -> list[list[int]]:
    """
    generate the maze with a DFS (Depth First Search) algorithm
    """
    width = int(maze["WIDTH"])
    height = int(maze["HEIGHT"])
    randomizer = random.Random(seed)

    grid = [[0 for _ in range(width)] for _ in range(height)]
    visited = [[False for _ in range(width)] for _ in range(height)]

    start_x, start_y = map(int, maze["ENTRY"].replace(" ", "").split(","))
    end_x, end_y = map(int, maze["EXIT"].replace(" ", "").split(","))
    if start_x == width:
        start_x = width - 1
    if start_y == height:
        start_y = height - 1
    if not _is_inside(start_x, start_y, width, height):
        start_x, start_y = 0, 0
    if not _is_inside(end_x, end_y, width, height):
        end_x, end_y = width, height

    blocked_cells: set[tuple[int, int]] = set()
    if print_42 and width >= 7 and height >= 5:
        blocked_cells = _build_42_mask(width, height)
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
            if _is_inside(nx, ny, width, height) and not visited[ny][nx]:
                neighbors.append((nx, ny, direction))

        if neighbors:
            nx, ny, direction = randomizer.choice(neighbors)
            grid[y][x] |= direction
            grid[ny][nx] |= OPPOSITE[direction]
            visited[ny][nx] = True
            stack.append((nx, ny))
            if progress_callback is not None:
                progress_callback(grid)
        else:
            stack.pop()

    if not perfect:
        extra_openings = max(1, (width * height) // 12)
        for _ in range(extra_openings):
            x = randomizer.randrange(width)
            y = randomizer.randrange(height)
            if grid[y][x] == BLOCK:
                continue
            dx, dy, direction = randomizer.choice(Direction)
            nx, ny = x + dx, y + dy
            if _is_inside(nx, ny, width, height) and grid[ny][nx] != BLOCK:
                grid[y][x] |= direction
                grid[ny][nx] |= OPPOSITE[direction]
                if progress_callback is not None:
                    progress_callback(grid)

    return grid
