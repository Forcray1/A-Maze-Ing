import time
import sys

from cli.display import show_maze_in_terminal
from mazegen.maze_maker import BLOCK, E, N, S, W
from core.solver import solver_maze


PLAYER_TILE = "^^"
START_TILE = "\033[92m██\033[0m"
END_TILE = "\033[91m██\033[0m"
VISITED_TILE = "\033[94m██\033[0m"


def check_full_path(key: str, path: str) -> bool:
    conversion = {
        "N": "\x1b[A",
        "S": "\x1b[B",
        "E": "\x1b[C",
        "W": "\x1b[D"
    }
    expected_keys = "".join(conversion[step.upper()] for step in path if step
                            in conversion)
    return key == expected_keys


def _normalize_point(point: str, width: int, height: int) -> tuple[int, int]:
    """
    Convert a point string to coordinates inside maze bounds.
    """
    x, y = map(int, point.replace(" ", "").split(","))
    if x == width:
        x = width - 1
    if y == height:
        y = height - 1
    return x, y


def _render_with_player(
    maze: dict,
    grid: list[list[int]],
    colors: dict[str, str],
    player,
) -> str:
    """
    Render the maze ,draw the player on top of it, and mark the visited cells.
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
    exit_x, exit_y = _normalize_point(str(maze["EXIT"]), width, height)

    for visited_x, visited_y in set(player.path):
        if 0 <= visited_x < width and 0 <= visited_y < height:
            lines[2 * visited_y + 1][2 * visited_x + 1] = VISITED_TILE

    for (x1, y1), (x2, y2) in zip(player.path, player.path[1:]):
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

    if 0 <= entry_x < width and 0 <= entry_y < height:
        lines[2 * entry_y + 1][2 * entry_x + 1] = START_TILE
    if 0 <= exit_x < width and 0 <= exit_y < height:
        lines[2 * exit_y + 1][2 * exit_x + 1] = END_TILE

    player_x, player_y = player.get_position()
    if 0 <= player_x < width and 0 <= player_y < height:
        lines[2 * player_y + 1][2 * player_x + 1] = PLAYER_TILE

    return "\n".join("".join(row) for row in lines)


def play_maze(
    maze: dict,
    grid: list[list[int]],
    colors: dict[str, str],
    player_class,
    seed: int | None = None,
) -> None:
    """
    Start a game session.

    Controls:
    - Arrow keys to move
    - x to quit
    """
    width = int(maze["WIDTH"])
    height = int(maze["HEIGHT"])
    start = _normalize_point(str(maze["ENTRY"]), width, height)
    exit_point = _normalize_point(str(maze["EXIT"]), width, height)

    player = player_class(grid, width, height, start, exit_point)

    perfect_path = False
    solution_path = solver_maze(maze, grid)
    while True:
        frame = _render_with_player(maze, grid, colors, player)
        info = (
            "\n\nControls: arrows to move, x to quit"
            + f"\nSteps: {player.steps}"
            + f"\nSEED used: {seed}"
        )
        show_maze_in_terminal(frame + info, clear_screen=True)

        if player.won:
            print("\n\033[92mYou reached the exit. "
                  "Press Enter to go back to menu.\033[0m")
            print("\033[96mStatistics:\033[0m\n")
            total_cells = width * height
            exploration = (len(set(player.path)) / total_cells) * 100
            path_lenght = len(solution_path)
            print(f"\033[93mYou explored {exploration:.2f}% of "
                  f"the maze\033[0m")
            print(f"\033[95mYou made it to the exit in {player.steps} move. "
                  f"The fastest you could do was : {path_lenght}\033[0m")
            if perfect_path:
                print("\n\033[91mDude get a life... "
                      "The all path seriously...\033[0m")
            elif player.steps == path_lenght:
                print("\n\033[92mWell played, that was the fastest way\033[0m")
            elif player.steps < path_lenght:
                print("\n\033[95mWell that shouldn't be possible..."
                      " How did you do it ?\033[0m")
            elif player.steps > path_lenght and exploration == 100:
                print("\n\033[94mYou explored all of this maze well"
                      " played (get a life)\033[0m")
            else:
                print("\n\033[93mNice try but not the best path "
                      "you could have had\033[0m")
            input()
            break

        key = input("\nMove (arrow key then Enter, x to quit): ")
        tryharder = check_full_path(key.strip(), solution_path)
        if tryharder:
            player.won = True
            perfect_path = True

        if key.strip() == "42":
            print("\nDude movements it ain't that hard why you"
                  " playing games ??")
            time.sleep(5)

        if key.strip() == "69":
            print("\nYou perv don't you just want to play the game ?!")
            print("You deserved this 10sec timeout, think about your action"
                  " you're a grown child...")
            time.sleep(10)

        if key.strip() == "67":
            print("\nIt is the worst meme of all time you're punished I kick"
                  " you out of here")
            time.sleep(5)
            print("\033[2J\033[H", end="")
            sys.exit(0)

        if key.strip() == "666":
            print("\nGo look up this website: slaabid.fr")
            print("And play the game for god sake it's really not that hard")
            time.sleep(5)

        if key.strip() == "125":
            print("That is the score you're gonna give us right ???")
            print("This game doesnt't deserve all of hte points ??")
            print("We spent a long time on this you know...")
            print("You should give us a star too it "
                  "looks good on our profiles")
            print("Please we can pay you you know...")
            print("A week worth of work i'll even sell my mom to "
                  "you for a star")
            time.sleep(20)

        if key.strip().lower() == "x":
            break

        if not player.move(key.strip()):
            print("\nCan't go there (there is a wall in case you"
                  " did not saw it).")
            time.sleep(1)
