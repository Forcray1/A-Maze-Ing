def check_value(config: dict) -> bool:
    """
    Verify the values contained in the config
    """
    i = 0
    keys = {"WIDTH": 0,
            "HEIGHT": 0,
            "ENTRY": 0,
            "EXIT": 0,
            "OUTPUT_FILE": 0,
            "PERFECT": 0,
            "SEED": 0,
            "SHOW_PROGRESS": 0
            }
    try:
        for key in config:
            key_found = False
            for verif in keys:
                if key == verif and keys[verif] == 0:
                    key_found = True
                    keys[verif] = 1
                    break
                elif keys[verif] == 1 and key == verif:
                    raise TypeError(f"{key} is written twice")
                else:
                    key_found = False
            if not key_found:
                raise ValueError(f"{key} isn't a valid setting")
    except ValueError as e:
        print(f"ERROR: {e}")
        return False
    except TypeError as e:
        print(f"ERROR: {e}")
        return False
    for key in config:
        i += 1
    if i not in (6, 7, 8):
        print("ERROR: Wrong amount of arguments in config, it should contain"
              " at least: WIDTH, HEIGHT, ENTRY, EXIT, OUTPUT_FILE, PERFECT")
        return False
    try:
        width = int(config["WIDTH"])
        if width <= 0:
            raise ValueError("WIDTH")
        height = int(config["HEIGHT"])
        if height <= 0:
            raise ValueError("HEIGHT")
        entry = str(config["ENTRY"]).replace(" ", "").split(",")
        if (
            len(entry) != 2
            or not entry[0].isdigit()
            or not entry[1].isdigit()
        ):
            raise ValueError("ENTRY")
        entry_x = int(entry[0])
        entry_y = int(entry[1])
        exit_cord = str(config["EXIT"]).replace(" ", "").split(",")
        if (
            len(exit_cord) != 2
            or not exit_cord[0].isdigit()
            or not exit_cord[1].isdigit()
        ):
            raise ValueError("EXIT")
        exit_x = int(exit_cord[0])
        exit_y = int(exit_cord[1])
        if entry_x >= width or entry_y >= height:
            raise ValueError("ENTRY")
        if exit_x >= width or exit_y >= height:
            raise ValueError("EXIT")
        if (entry_x, entry_y) == (exit_x, exit_y):
            raise ValueError("ENTRY/EXIT")
        if str(config["OUTPUT_FILE"]):
            pass
        else:
            raise ValueError("OUTPUT_FILE")
        if config["PERFECT"] == "True" or config["PERFECT"] == "False":
            pass
        else:
            raise ValueError("PERFECT")
        if "SEED" in config:
            int(config["SEED"])
        if "SHOW_PROGRESS" in config:
            if (
                config["SHOW_PROGRESS"] == "True"
                or config["SHOW_PROGRESS"] == "False"
            ):
                pass
            else:
                raise ValueError("SHOW_PROGRESS")
    except ValueError as e:
        print(f"{e} doesn't have the good type of value")
        return False
    forbidden = """:/\\¢™$®,[]}{()!;"'*?<>|àâéèêëîïôöùûü"""
    output_file = str(config["OUTPUT_FILE"])
    valid_chars = all(c not in output_file for c in forbidden)
    if output_file.endswith(".txt") and valid_chars:
        pass
    else:
        print(f"{output_file} isn't a valid output file")
        return False
    try:
        with open(output_file, "r", encoding="utf-8"):
            pass
        with open(output_file, "w", encoding="utf-8"):
            pass
    except PermissionError:
        print(f"{output_file} cannot be accessed correctly")
        return False
    except FileNotFoundError:
        pass
    return True
