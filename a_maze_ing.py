import secrets
import sys
import time

from core.check_value import check_value
from cli.Menu import interface


def main() -> None:
    """
    Core logic of the project
    """
    if len(sys.argv) != 2:
        print("Usage: python3 a_maze_ing.py [config file]")
        return
    keys = {
        "WIDTH",
        "HEIGHT",
        "ENTRY",
        "EXIT",
        "OUTPUT_FILE",
        "PERFECT",
        "SHOW_PROGRESS",
        "SEED"
    }
    config_file_path = sys.argv[1]
    maze: dict[str, int | str] = {}
    seen_keys = set()
    try:
        with open(config_file_path, "r") as config_file:
            for line in config_file:
                line = line.strip()
                if line.startswith("#"):
                    pass
                else:
                    try:
                        key, str_value = line.split("=")
                    except ValueError:
                        raise ValueError(line)
                    key = key.upper()
                    if key not in keys:
                        print(f"{key} is not recognised")
                    if key in seen_keys:
                        print(f"ERROR: {key} is written twice")
                        return
                    seen_keys.add(key)
                    if str_value.isdigit():
                        maze[key] = int(str_value)
                    else:
                        maze[key] = str_value
        if not check_value(maze):
            return
    except FileNotFoundError:
        print(f"no {config_file_path} file found")
        return
    except ValueError as e:
        print(f"{e} is not in the right format (KEY=VALUE)")
        return

    x_start, y_start = map(int, str(maze["ENTRY"]).split(","))
    start = {"x": x_start, "y": y_start}
    x_end, y_end = map(int, str(maze["EXIT"]).split(","))
    end = {"x": x_end, "y": y_end}
    try:
        if start["x"] < 0 or end["x"] < 0:
            raise ValueError("The X cords must be positive")
        if start["y"] < 0 or end["y"] < 0:
            raise ValueError("The Y cords must be positive")
        if start["x"] > int(maze["WIDTH"]) or end["x"] > int(maze["WIDTH"]):
            raise ValueError("The X cords must be inside the maze")
        if start["y"] > int(maze["HEIGHT"]) or end["y"] > int(maze["HEIGHT"]):
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
    if int(maze["WIDTH"]) > 7 and int(maze["HEIGHT"]) > 5:
        print_42 = True
    else:
        print("The maze is too small, so there won't be a 42 logo")
        time.sleep(3)
        print_42 = False

    if "SEED" in maze:
        seed = int(maze["SEED"])
    else:
        seed = secrets.randbits(64)

    colors = {"WALL_TILE": "██", "OPEN_TILE": "  ", "BLOCK_TILE": "▓▓"}

    interface(maze, show_progress, colors, perfect, print_42, seed)


if __name__ == "__main__":
    main()
