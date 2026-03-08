import time
import secrets
from typing import Optional

from mazegen.maze_maker import MazeGenerator
from cli.display import print_maze, render_maze_ascii, show_maze_in_terminal


def edit_color(colors: dict[str: str],
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
              colors: dict[str: str],
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
    pause_animation_once = False
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
        print_maze(maze, grid, colors)
        print(f"SEED used: {seed}")

        print("\n1. Change maze colors")
        if not show_solution:
            print("2. Show maze solution path")
        else:
            print("2. Hide maze solution path")
        print("3. Regenerate a new maze")
        if not show_progress:
            print("4. Activate animation")
        else:
            print("4. Deactivate animation")
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
                pass
            else:
                pass

        elif choice == "3":
            print_maze(maze, grid, colors)
            print(f"SEED used: {seed}")

            color_changed = 0
            seed_input = input("\nchoose a seed (leave empty if none): ")
            if seed_input != "":
                seed = seed_input
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
                    speed = float(input("\nChoice: ").strip())
                except ValueError:
                    print(f"{speed}: isn't a valid speed")
                show_progress = True

        elif choice == "9":
            break

        else:
            pause_animation_once = True
            print_maze(maze, grid, colors)
            print(f"SEED used: {seed}")
            print(f"\n{choice} isn't a valid option")
            time.sleep(2)
