from enum import Enum, IntEnum


class Direction(IntEnum):
    UP = 1
    RIGHT = 2
    DOWN = 3
    LEFT = 4


class Result(Enum):
    WIN = 1
    LOSE = 2
    UNDEFINED = 3


class Wall:
    def __init__(self, x: int, y: int, direction: Direction):
        self.x = x
        self.y = y
        self.direction = direction

    def __int__(self):
        return 10000 * self.x + 100 * self.y + self.direction


class GameField:
    def __init__(self, field_size: tuple[int, int], exit_pos: tuple[int, int],
                 exit_direction: Direction, walls: list[Wall], freeze_cells: list[tuple[int, int]]):
        self.field_size = field_size
        self.exit_pos = exit_pos
        self.exit_direction = exit_direction
        self.walls = walls
        self.freeze_cells = freeze_cells
        self.wall_set = set()
        for w in walls:
            self.wall_set.add(int(w))
            w_x = w.x
            w_y = w.y
            w_d = Direction.UP
            if w.direction == Direction.UP:
                w_x -= 1
                w_d = Direction.DOWN
            elif w.direction == Direction.DOWN:
                w_x += 1
            elif w.direction == Direction.LEFT:
                w_y -= 1
                w_d = Direction.RIGHT
            else:
                w_y += 1
                w_d = Direction.LEFT
            self.wall_set.add(int(Wall(w_x, w_y, w_d)))


class GameState:
    def __init__(self, field: GameField, player_pos: tuple[int, int], enemy_pos: tuple[int, int]):
        self.field = field
        self.player_x = player_pos[0]
        self.player_y = player_pos[1]
        self.enemy_x = enemy_pos[0]
        self.enemy_y = enemy_pos[1]
        self.find_exit = False

    def can_player_move(self, direction: Direction):
        if self.find_exit:
            return False
        w_x0 = self.player_x
        w_y0 = self.player_y
        w_d0 = direction

        ex_x = self.field.exit_pos[0]
        ex_y = self.field.exit_pos[1]
        ex_d = self.field.exit_direction

        if w_x0 == ex_x and w_y0 == ex_y and w_d0 == ex_d:
            return True

        w_x1 = self.player_x
        w_y1 = self.player_y
        if direction == Direction.UP:
            if self.player_y == 0:
                return False
            w_y1 = w_y0 - 1
            w_d1 = Direction.DOWN
        elif direction == Direction.DOWN:
            if self.player_y == self.field.field_size[1] - 1:
                return False
            w_y1 = w_y0 + 1
            w_d1 = Direction.UP
        elif direction == Direction.LEFT:
            if self.player_x == 0:
                return False
            w_x1 = w_x0 - 1
            w_d1 = Direction.RIGHT
        else:
            if self.player_x == self.field.field_size[0] - 1:
                return False
            w_x1 = w_x0 + 1
            w_d1 = Direction.LEFT
        s = self.field.wall_set
        return not ((int(Wall(w_x0, w_y0, w_d0)) in s) or (int(Wall(w_x1, w_y1, w_d1)) in s))

    def move(self, direction: Direction) -> bool:
        if not self.can_player_move(direction):
            return False
        w_x0 = self.player_x
        w_y0 = self.player_y
        w_d0 = direction

        ex_x = self.field.exit_pos[0]
        ex_y = self.field.exit_pos[1]
        ex_d = self.field.exit_direction

        if w_x0 == ex_x and w_y0 == ex_y and w_d0 == ex_d:
            self.find_exit = True

        if direction == Direction.UP:
            self.player_y -= 1
        elif direction == Direction.DOWN:
            self.player_y += 1
        elif direction == Direction.LEFT:
            self.player_x -= 1
        else:
            self.player_x += 1
        return True
