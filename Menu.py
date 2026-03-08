def interface(maze: dict,
              show_progress: bool
              ) -> None:
    while True:
        print("1. Change maze colors")
        show_solution = False
        if not show_solution:
            print("2. Show maze solution path")
        else:
            print("2. Hide maze solution path")
        print("3. Regenerate a new maze")
        if show_progress:
            print("4. Activate animation")
        else:
            print("4. Deactivate animation")
        print("9. Exit")

        choice = input("\nChoice: ")

        print("\033[2J\033[H", end="")

        if choice == "1":
            while True:
                print("Do you wich to change:")
                print("- 1. Wall colors")
                print("- 2. 42 color")
                print("- 3. The both of them")
                print("- 4. Cancel")

                side_choice = input()
                print("\033[2J\033[H", end="")

                if side_choice == "1":
                    break
                elif side_choice == "2":
                    break
                elif side_choice == "3":
                    break
                elif side_choice == "4":
                    break
                else:
                    print(f"{side_choice} isn't a valid option")

        elif choice == "2":
            if show_solution:
                pass
            else:
                pass

        elif choice == "3":
            seed = input("choose a seed (leave empty if none): ")
            pass

        elif choice == "4":
            if show_progress:
                show_progress = False
            if not show_progress:
                print("choose the speed of the animation (0.2 by default, for"
                      " a smooth and fast animation) :")
                speed = int(input())
                pass

        elif choice == "9":
            break


if __name__ == "__main__":
    maze = dict()
    interface(maze, show_progress=False)
