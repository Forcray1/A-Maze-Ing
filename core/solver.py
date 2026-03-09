from mazegen.maze_maker import BLOCK, E, N, S, W


def normalize_point(point, width, height):
    """
    Convert an ENTRY/EXIT value to valid maze coordinates.
    """
    if width <= 0:
        raise ValueError("width must be positive")
    if height <= 0:
        raise ValueError("height must be positive")

    if isinstance(point, str):
        x, y = map(int, point.replace(" ", "").split(","))
    else:
        x, y = point

    if x == width:
        x = width - 1
    if y == height:
        y = height - 1

    if x < 0 or y < 0 or x >= width or y >= height:
        raise ValueError("point is outside maze bounds")

    return x, y


def get_start_exit(maze):
    """
    Extract and normalize start/end coordinates from the maze config.
    """
    width = int(maze["WIDTH"])
    height = int(maze["HEIGHT"])
    start = normalize_point(str(maze["ENTRY"]), width, height)
    exit = normalize_point(str(maze["EXIT"]), width, height)
    return start, exit


def iter_open_neighbors(
    grid,
    x,
    y,
    width,
    height,
):
    """
    Yield reachable adjacent cells from one maze cell.
    """
    cell = grid[y][x]
    neighbors = []

    directions = (
        (N, 0, -1),
        (S, 0, 1),
        (E, 1, 0),
        (W, -1, 0),
    )

    for direction, dx, dy in directions:
        if not (cell & direction):
            continue
        nx, ny = x + dx, y + dy
        if 0 <= nx < width and 0 <= ny < height and not (grid[ny][nx] & BLOCK):
            neighbors.append((nx, ny))

    return neighbors


def reconstruct_path(
    parents,
    start,
    exit,
):
    """
    Rebuild the shortest path from BFS (Breadth-First Search) parent links.
    """
    if exit not in parents:
        raise ValueError("no path from start to exit")

    path = []
    current = exit
    while current is not None:
        path.append(current)
        current = parents[current]

    path.reverse()
    if not path or path[0] != start:
        raise ValueError("invalid parent map: start not reached")
    return path


def solver_maze(
    maze,
    grid,
):
    """
    Compute a shortest valid path from ENTRY to EXIT using BFS
     (Breadth-First Search).
    """
    height = len(grid)
    if height == 0:
        raise ValueError("grid is empty")
    width = len(grid[0])
    if width == 0:
        raise ValueError("grid is empty")

    start, exit = get_start_exit(maze)
    sx, sy = start
    ex, ey = exit

    if grid[sy][sx] & BLOCK:
        raise ValueError("ENTRY is blocked")
    if grid[ey][ex] & BLOCK:
        raise ValueError("EXIT is blocked")

    path = [start]
    head = 0
    parents = {}
    parents[start] = None

    while head < len(path):
        current = path[head]
        head += 1
        if current == exit:
            result = reconstruct_path(parents, start, exit)
            return path_to_moves(result)

        x, y = current
        for neighbor in iter_open_neighbors(grid, x, y, width, height):
            if neighbor in parents:
                continue
            parents[neighbor] = current
            path.append(neighbor)

    raise ValueError("no path exists between ENTRY and EXIT")


def path_to_moves(path: list[str]) -> str:
    """
    Convert a coordinate path into movement letters (NSEW).
    """
    if len(path) < 2:
        return ""

    moves = []
    for (x1, y1), (x2, y2) in zip(path, path[1:]):
        dx = int(x2) - int(x1)
        dy = int(y2) - int(y1)
        if dx == 0 and dy == -1:
            moves.append("N")
        elif dx == 0 and dy == 1:
            moves.append("S")
        elif dx == 1 and dy == 0:
            moves.append("E")
        elif dx == -1 and dy == 0:
            moves.append("W")
        else:
            raise ValueError("path contains non-adjacent coordinates")

    return "".join(moves)
