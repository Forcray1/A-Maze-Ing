import secrets
import sys
import time

from core.check_value import check_value
from mazegen.maze_maker import MazeGenerator
from cli.display import print_maze, render_maze_ascii, show_maze_in_terminal


def main() -> None:
    """
    Core logic of the project
    """
    config = sys.argv[1]
    maze = {}
    seen_keys = set()
    try:
        with open(config, "r") as config:
            for line in config:
                line = line.strip()
                key, value = line.split("=")
                if key in seen_keys:
                    print(f"ERROR: {key} is written twice")
                    return
                seen_keys.add(key)
                if value.isdigit():
                    value = int(value)
                maze[key] = value
        if not check_value(maze):
            return
    except FileNotFoundError:
        print(f"no {config} file found")
        return
    x_start, y_start = map(int, maze["ENTRY"].split(","))
    start = {"x": x_start, "y": y_start}
    x_end, y_end = map(int, maze["EXIT"].split(","))
    end = {"x": x_end, "y": y_end}
    try:
        if start["x"] < 0 or end["x"] < 0:
            raise ValueError("The X cords must be positive")
        if start["y"] < 0 or end["y"] < 0:
            raise ValueError("The Y cords must be positive")
        if start["x"] > maze["WIDTH"] or end["x"] > maze["WIDTH"]:
            raise ValueError("The X cords must be inside the maze")
        if start["y"] > maze["HEIGHT"] or end["y"] > maze["HEIGHT"]:
            raise ValueError("The Y cords must be inside the maze")
        if maze["ENTRY"] == maze["EXIT"]:
            raise ValueError("ENTRY and EXIT can't be at the same place")
    except ValueError as e:
        print(f"ERROR of configuration: {e}")
        return
    if maze["PERFECT"] == "True":
        perfect = True
    else:
        perfect = False
    if maze.get("SHOW_PROGRESS", "False") == "True":
        show_progress = True
    else:
        show_progress = False
    if maze["WIDTH"] > 7 and maze["HEIGHT"] > 5:
        print_42 = True
    else:
        print_42 = False

    if "SEED" in maze:
        seed = int(maze["SEED"])
    else:
        seed = secrets.randbits(64)

    progress_callback = None
    if show_progress:
        show_maze_in_terminal("", clear_screen=True)

        def _progress(frame_grid: list[list[int]]) -> None:
            frame_ascii = render_maze_ascii(maze, frame_grid)
            show_maze_in_terminal(frame_ascii)
            time.sleep(0.02)

        progress_callback = _progress

    generator = MazeGenerator.from_config(
        maze=maze,
        perfect=perfect,
        print_42=print_42,
        seed=seed,
        progress_callback=progress_callback,
    )
    grid = generator.generate()
    print_maze(maze, grid)
    print(f"SEED used: {seed}")


if __name__ == "__main__":
    main()
