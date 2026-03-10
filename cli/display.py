import sys
from pathlib import Path
from typing import Optional
from mazegen.maze_maker import BLOCK, E, N, S, W
from core.solver import solver_maze

START_TILE = "\033[92m██\033[0m"
END_TILE = "\033[91m██\033[0m"
VISITED_TILE = "\033[94m██\033[0m"


def render_maze_ascii(maze: dict,
                      grid: list[list[int]],
                      colors: dict[str, str]
                      ) -> str:
    """
    Create the maze rendered in ascii
    """
    width = int(maze["WIDTH"])
    height = int(maze["HEIGHT"])
    WALL_TILE = colors["WALL_TILE"]
    OPEN_TILE = colors["OPEN_TILE"]
    BLOCK_TILE = colors["BLOCK_TILE"]

    lines = [
        [WALL_TILE for _ in range(2 * width + 1)]
        for _ in range(2 * height + 1)
    ]

    for y in range(height):
        for x in range(width):
            cell = grid[y][x]
            rx = 2 * x + 1
            ry = 2 * y + 1
            if cell & BLOCK:
                lines[ry][rx] = BLOCK_TILE
                continue
            lines[ry][rx] = OPEN_TILE
            if cell & N:
                lines[ry - 1][rx] = OPEN_TILE
            if cell & S:
                lines[ry + 1][rx] = OPEN_TILE
            if cell & E:
                lines[ry][rx + 1] = OPEN_TILE
            if cell & W:
                lines[ry][rx - 1] = OPEN_TILE

    entry_x, entry_y = map(int, maze["ENTRY"].replace(" ", "").split(","))
    exit_x, exit_y = map(int, maze["EXIT"].replace(" ", "").split(","))
    if entry_x == width:
        entry_x = width - 1
    if entry_y == height:
        entry_y = height - 1
    if exit_x == width:
        exit_x = width - 1
    if exit_y == height:
        exit_y = height - 1
    if 0 <= entry_x < width and 0 <= entry_y < height:
        lines[2 * entry_y + 1][2 * entry_x + 1] = START_TILE
    if 0 <= exit_x < width and 0 <= exit_y < height:
        lines[2 * exit_y + 1][2 * exit_x + 1] = END_TILE

    return "\n".join("".join(row) for row in lines)


def _path_points_from_moves(
    start: tuple[int, int],
    moves: str,
) -> list[tuple[int, int]]:
    """
    Build path coordinates from a start position and a movement string.
    """
    x, y = start
    points = [start]

    for move in moves:
        if move == "N":
            y -= 1
        elif move == "S":
            y += 1
        elif move == "E":
            x += 1
        elif move == "W":
            x -= 1
        else:
            raise ValueError(f"Unknown move: {move}")
        points.append((x, y))

    return points


def render_maze_ascii_with_path(
    maze: dict,
    grid: list[list[int]],
    colors: dict[str, str],
    moves: str,
) -> str:
    """
    Render maze with a highlighted solution path.
    """
    width = int(maze["WIDTH"])
    height = int(maze["HEIGHT"])
    wall_tile = colors["WALL_TILE"]
    open_tile = colors["OPEN_TILE"]
    block_tile = colors["BLOCK_TILE"]

    lines = [
        [wall_tile for _ in range(2 * width + 1)]
        for _ in range(2 * height + 1)
    ]

    for y in range(height):
        for x in range(width):
            cell = grid[y][x]
            rx = 2 * x + 1
            ry = 2 * y + 1
            if cell & BLOCK:
                lines[ry][rx] = block_tile
                continue
            lines[ry][rx] = open_tile
            if cell & N:
                lines[ry - 1][rx] = open_tile
            if cell & S:
                lines[ry + 1][rx] = open_tile
            if cell & E:
                lines[ry][rx + 1] = open_tile
            if cell & W:
                lines[ry][rx - 1] = open_tile

    entry_x, entry_y = _normalize_point(str(maze["ENTRY"]), width, height)

    points = _path_points_from_moves((entry_x, entry_y), moves)

    for point_x, point_y in set(points):
        if 0 <= point_x < width and 0 <= point_y < height:
            lines[2 * point_y + 1][2 * point_x + 1] = VISITED_TILE

    for (x1, y1), (x2, y2) in zip(points, points[1:]):
        if not (
            0 <= x1 < width
            and 0 <= y1 < height
            and 0 <= x2 < width
            and 0 <= y2 < height
        ):
            continue
        wall_x = x1 + x2 + 1
        wall_y = y1 + y2 + 1
        lines[wall_y][wall_x] = VISITED_TILE

    exit_x, exit_y = _normalize_point(str(maze["EXIT"]), width, height)
    if 0 <= entry_x < width and 0 <= entry_y < height:
        lines[2 * entry_y + 1][2 * entry_x + 1] = START_TILE
    if 0 <= exit_x < width and 0 <= exit_y < height:
        lines[2 * exit_y + 1][2 * exit_x + 1] = END_TILE

    return "\n".join("".join(row) for row in lines)


def show_maze_in_terminal(maze_ascii: str, clear_screen: bool = False) -> None:
    """
    Display one maze frame in terminal by redrawing in place.
    """
    if clear_screen:
        sys.stdout.write("\033[2J")
    sys.stdout.write("\033[H")
    sys.stdout.write(maze_ascii + "\n")
    sys.stdout.flush()


def _normalize_point(point: str, width: int, height: int) -> tuple[int, int]:
    """
    Convert point string to valid zero-based coordinates inside maze bounds.
    """
    x, y = map(int, point.replace(" ", "").split(","))
    if x == width:
        x = width - 1
    if y == height:
        y = height - 1
    return x, y


def maze_hex_dump(maze: dict, grid: list[list[int]]) -> str:
    """
    Export maze to multiline hexadecimal format.

    Each cell is encoded on one hex digit where bit=1 means a wall is present:
    - bit 0 (1): north wall
    - bit 1 (2): east wall
    - bit 2 (4): south wall
    - bit 3 (8): west wall
    """
    width = int(maze["WIDTH"])
    height = int(maze["HEIGHT"])
    solve_path = solver_maze(maze, grid)

    hex_rows: list[str] = []
    for y in range(height):
        chars: list[str] = []
        for x in range(width):
            cell = grid[y][x]
            wall_mask = 0
            if not (cell & N):
                wall_mask |= 0x1
            if not (cell & E):
                wall_mask |= 0x2
            if not (cell & S):
                wall_mask |= 0x4
            if not (cell & W):
                wall_mask |= 0x8
            chars.append(format(wall_mask, "X"))
        hex_rows.append("".join(chars))

    entry_x, entry_y = _normalize_point(str(maze["ENTRY"]), width, height)
    exit_x, exit_y = _normalize_point(str(maze["EXIT"]), width, height)

    return (
        "\n".join(hex_rows)
        + "\n\n"
        + f"{entry_x},{entry_y}\n"
        + f"{exit_x + 1},{exit_y + 1}\n"
        + f"{solve_path}\n"
    )


def write_hex_dump_file(maze: dict,
                        dump_text: str,
                        grid: list[list[int]]
                        ) -> None:
    """
    Write the hexadecimal maze export to output file.
    """
    output_path = Path(str(maze["OUTPUT_FILE"]))
    if not output_path.is_absolute():
        output_path = Path(__file__).resolve().parent / output_path
    with open(output_path, "w", encoding="utf-8") as out:
        out.write(dump_text)


def print_maze(
    maze: dict,
    grid: list[list[int]],
    colors: dict[str, str],
    seed: Optional[str] = None,
) -> None:
    """
    Show final maze in terminal and write hex dump to file.
    """
    maze_ascii = render_maze_ascii(maze, grid, colors)
    show_maze_in_terminal(maze_ascii)
    dump_text = maze_hex_dump(maze, grid)
    write_hex_dump_file(maze, dump_text, grid)


def write_path_output(maze: dict, path: str) -> None:
    output_path = Path(str(maze["OUTPUT_FILE"]))
    if not output_path.is_absolute():
        output_path = Path(__file__).resolve().parent / output_path
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(path)


def print_maze_with_path(
    maze: dict,
    grid: list[list[int]],
    colors: dict[str, str],
    moves: str,
    seed: Optional[str] = None,
) -> None:
    """
    Show final maze in terminal with highlighted solution path.
    """
    maze_ascii = render_maze_ascii_with_path(maze, grid, colors, moves)
    show_maze_in_terminal(maze_ascii)
    if seed is not None:
        print(f"SEED used: {seed}")
    dump_text = maze_hex_dump(maze, grid)
    write_hex_dump_file(maze, dump_text, grid)
