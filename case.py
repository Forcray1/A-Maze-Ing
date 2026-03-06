class case():
    def __init__(self,
                 north: bool,
                 south: bool,
                 east: bool,
                 west: bool,
                 direction: int,
                 posx: int,
                 posy: int,
                 size_maze_x: int,
                 size_maze_y: int
                 ):
        self.north = north
        self.south = south
        self.east = east
        self.west = west
        self.direction = direction
        self.posx = posx
        self.posy = posy
        self.size_maze_x = size_maze_x
        self.size_maze_y = size_maze_y
        if self.verif_border():
            self.border = True
        else:
            self.border = False

    def verif_border(self) -> bool:
        border = False
        if self.posx == self.size_maze_x or self.posy == self.size_maze_y:
            border = True
        return border
