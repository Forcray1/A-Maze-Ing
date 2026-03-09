import time
import secrets
from typing import Optional

from mazegen.maze_maker import MazeGenerator
from cli.display import (
    print_maze,
    print_maze_with_path,
    render_maze_ascii,
    show_maze_in_terminal,
)
from game.play_session import play_maze
from game.player import Player


class YborderError():
    pass


class XborderError():
    pass


def edit_color(colors: dict[str, str],
               to_change: str,
               maze: dict,
               grid: list[list[int]],
               seed: Optional[int] = None
               ) -> None:
    while True:
        print("\033[2J\033[H", end="")
        print_maze(maze, grid, colors)
        print(f"SEED used: {seed}")
        print("\nChoose a color:")
        print("1. White (Default)")
        print("2. Blue")
        print("3. Red")
        print("4. Green")
        print("5. Yellow")
        print("6. Grey")

        color = int(input("\nChoice: ").strip())

        if color == 1:
            pre = ""
            suf = ""
            break
        if color == 2:
            pre = "\033[34m"
            suf = "\033[0m"
            break
        if color == 3:
            pre = "\033[31m"
            suf = "\033[0m"
            break
        if color == 4:
            pre = "\033[32m"
            suf = "\033[0m"
            break
        if color == 5:
            pre = "\033[33m"
            suf = "\033[0m"
            break
        if color == 6:
            pre = "\033[90m"
            suf = "\033[0m"
            break
        else:
            print(f"\n{color} isn't a valid option")
            time.sleep(2)

    if to_change == "wall":
        colors["WALL_TILE"] = str(pre + "██" + suf)
    if to_change == "42":
        colors["BLOCK_TILE"] = str(pre + "▓▓" + suf)
    if to_change == "both":
        colors["WALL_TILE"] = str(pre + "██" + suf)
        colors["BLOCK_TILE"] = str(pre + "▓▓" + suf)


def interface(maze: dict,
              show_progress: bool,
              colors: dict[str, str],
              perfect: bool,
              print_42: bool,
              seed: Optional[int] = None,
              ) -> None:
    """
    Handle the interactive user pannel, and all of the display
    """
    speed = 2
    color_changed = 0
    show_solution = False
    solution_path = ""
    pause_animation_once = False
    solver_maze = __import__(
        "core.solver",
        fromlist=["solver_maze"],
    ).solver_maze
    while True:
        print("\033[2J\033[H", end="")
        progress_callback = None
        if pause_animation_once:
            pause_animation_once = False
        elif color_changed == 0:
            if show_progress:
                show_maze_in_terminal("", clear_screen=True)

                def _progress(frame_grid: list[list[int]]) -> None:
                    frame_ascii = render_maze_ascii(maze, frame_grid, colors)
                    show_maze_in_terminal(frame_ascii)
                    time.sleep(float(speed / 100))

                progress_callback = _progress

        generator = MazeGenerator.from_config(
            maze=maze,
            perfect=perfect,
            print_42=print_42,
            seed=seed,
            progress_callback=progress_callback,
        )
        grid = generator.generate()
        if show_solution:
            try:
                solution_path = solver_maze(maze, grid)
                print_maze_with_path(
                    maze,
                    grid,
                    colors,
                    solution_path,
                    str(seed) if seed is not None else None
                )
            except ValueError:
                print_maze(maze, grid, colors)
                print(f"SEED used: {seed}")
                print("\nNo solution path found for this maze")
        else:
            print_maze(maze, grid, colors)
            print(f"SEED used: {seed}")
        print("\n=== A-Maze-ing ===")
        print("1. Change maze colors")
        if not show_solution:
            print("2. Show maze solution path")
        else:
            print("2. Hide maze solution path")
        print("3. Regenerate a new maze")
        if not show_progress:
            print("4. Activate animation")
        else:
            print("4. Deactivate animation")
        print("5. Change maze dimensions")
        print("6. Play this maze")
        print("9. Exit")

        choice = input("\nChoice: ").strip()

        print("\033[2J\033[H", end="")

        if choice == "1":
            while True:
                print("\033[2J\033[H", end="")
                print_maze(maze, grid, colors)
                print(f"SEED used: {seed}")

                print("\nDo you wich to change:")
                print("- 1. Wall colors")
                print("- 2. 42 color")
                print("- 3. The both of them")
                print("- 4. Cancel")

                side_choice = input("\nChoice: ").strip()
                print("\033[2J\033[H", end="")

                print_maze(maze, grid, colors)
                print(f"SEED used: {seed}")
                if side_choice == "1":
                    edit_color(colors, "wall", maze, grid, seed)
                    color_changed = 1
                    break
                elif side_choice == "2":
                    edit_color(colors, "42", maze, grid, seed)
                    color_changed = 1
                    break
                elif side_choice == "3":
                    edit_color(colors, "both", maze, grid, seed)
                    color_changed = 1
                    break
                elif side_choice == "4":
                    break
                else:
                    print(f"\n{side_choice} isn't a valid option")
                    time.sleep(2)

        elif choice == "2":
            if show_solution:
                show_solution = False
            else:
                show_solution = True

        elif choice == "3":
            print_maze(maze, grid, colors)
            print(f"SEED used: {seed}")

            color_changed = 0
            seed_input = input("\nchoose a seed (leave empty if none, 'same' "
                               "for the same seed): ")
            if seed_input.strip() == "same":
                seed = seed
            elif seed_input != "":
                try:
                    seed = int(seed_input)
                except ValueError:
                    print(f"{seed_input} isn't a valid seed")
                    time.sleep(2)
                    continue
            else:
                seed = secrets.randbits(64)

        elif choice == "4":
            color_changed = 0
            if show_progress:
                show_progress = False
            elif not show_progress:
                print_maze(maze, grid, colors)
                print(f"SEED used: {seed}")
                print("\nchoose the speed of the animation (2 by default, for"
                      " a smooth and fast animation, and the lower the "
                      "faster) :")
                try:
                    if speed == "":
                        raise ValueError
                    if speed < 0:
                        raise ValueError
                    speed = float(input("\nChoice: ").strip())
                except ValueError:
                    print(f"{speed}: isn't a valid speed")
                show_progress = True

        elif choice == "5":
            print_maze(maze, grid, colors)
            print(f"SEED used: {seed}")

            new_width_input = input("\nEnter Width: ").strip()
            new_height_input = input("\nEnter Height: ").strip()

            try:
                if int(new_width_input) < 1:
                    raise ValueError
                new_width = int(new_width_input)
            except ValueError:
                print(f"{new_width_input} isn't a valid input "
                      "(enter a positive int)")
                time.sleep(2)
                continue

            try:
                if int(new_height_input) < 1:
                    raise ValueError
                new_height = int(new_height_input)
            except ValueError:
                print(f"{new_height_input} isn't a valid input "
                      "(enter a positive int)")
                time.sleep(2)
                continue

            x_start, y_start = map(int, str(maze["ENTRY"]).split(","))
            x_end, y_end = map(int, str(maze["EXIT"]).split(","))
            x_error = (
                x_start < 0
                or x_end < 0
                or x_start > new_width
                or x_end > new_width
            )
            y_error = (
                y_start < 0
                or y_end < 0
                or y_start > new_height
                or y_end > new_height
            )

            while True:
                edit_points = input(
                    "Modify ENTRY and EXIT as x,y? (y/n): "
                ).strip().lower()
                if edit_points in ("y", "n"):
                    break
                print("Please enter y or n")
                time.sleep(1)

            if edit_points == "y" or x_error or y_error:
                while True:
                    if x_error or y_error:
                        print("\nENTRY/EXIT coordinates are outside the new"
                              " dimensions.")
                    entry_input = input("New ENTRY (x,y): ").strip()
                    exit_input = input("New EXIT (x,y): ").strip()
                    try:
                        entry_parts = entry_input.replace(" ", "").split(",")
                        exit_parts = exit_input.replace(" ", "").split(",")
                        if len(entry_parts) != 2 or len(exit_parts) != 2:
                            raise ValueError
                        x_start, y_start = int(entry_parts[0]), int(
                            entry_parts[1]
                        )
                        x_end, y_end = int(exit_parts[0]), int(exit_parts[1])
                    except ValueError:
                        print("Coordinates must be entered as x,y with"
                              " integers")
                        time.sleep(2)
                        continue
                    if x_start < 0 or x_end < 0 or y_start < 0 or y_end < 0:
                        print("Coordinates must be positive")
                        time.sleep(2)
                        continue
                    if x_start > new_width or x_end > new_width:
                        print(f"X coordinates must be inside the new "
                              f"width ({new_width})")
                        time.sleep(2)
                        continue
                    if y_start > new_height or y_end > new_height:
                        print(f"Y coordinates must be inside the new "
                              f"height ({new_height})")
                        time.sleep(2)
                        continue
                    x_error = False
                    y_error = False
                    break

            if x_start < 0 or x_end < 0:
                print("ERROR of configuration: The X cords must be positive")
                time.sleep(2)
                continue
            if y_start < 0 or y_end < 0:
                print("ERROR of configuration: The Y cords must be positive")
                time.sleep(2)
                continue
            if x_start > new_width or x_end > new_width:
                print("ERROR of configuration: The X cords must be inside"
                      " the maze")
                time.sleep(2)
                continue
            if y_start > new_height or y_end > new_height:
                print("ERROR of configuration: The Y cords must be inside"
                      " the maze")
                time.sleep(2)
                continue
            if x_start == x_end and y_start == y_end:
                print("ERROR of configuration: ENTRY and EXIT can't be at"
                      " the same place")
                time.sleep(2)
                continue

            maze["WIDTH"] = new_width
            maze["HEIGHT"] = new_height
            maze["ENTRY"] = f"{x_start},{y_start}"
            maze["EXIT"] = f"{x_end},{y_end}"

            if int(maze["WIDTH"]) > 7 and int(maze["HEIGHT"]) > 5:
                print_42 = True
            else:
                print_42 = False

        elif choice == "6":
            play_maze(
                maze,
                grid,
                colors,
                Player,
                seed,
            )

        elif choice == "9":
            break

        else:
            pause_animation_once = True
            print_maze(maze, grid, colors)
            print(f"SEED used: {seed}")
            print(f"\n{choice} isn't a valid option")
            time.sleep(2)
