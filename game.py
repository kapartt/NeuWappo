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
    def __init__(self, field: GameField, player_pos: tuple[int, int], enemy_pos: tuple[int, int], freeze_time: int = 0,
                 can_freeze: bool = True):
        self.field = field
        self.player_x = player_pos[0]
        self.player_y = player_pos[1]
        self.enemy_x = enemy_pos[0]
        self.enemy_y = enemy_pos[1]
        self.find_exit = False
        self.freeze_time = freeze_time
        self.can_freeze = can_freeze

    def can_move(self, is_player_move: bool, direction: Direction):
        if self.find_exit:
            return False

        if is_player_move:
            w_x0 = self.player_x
            w_y0 = self.player_y
        else:
            w_x0 = self.enemy_x
            w_y0 = self.enemy_y

        w_d0 = direction

        ex_x = self.field.exit_pos[0]
        ex_y = self.field.exit_pos[1]
        ex_d = self.field.exit_direction

        if w_x0 == ex_x and w_y0 == ex_y and w_d0 == ex_d:
            return True

        w_x1 = w_x0
        w_y1 = w_y0
        if direction == Direction.UP:
            if w_y0 == 0:
                return False
            w_y1 = w_y0 - 1
            w_d1 = Direction.DOWN
        elif direction == Direction.DOWN:
            if w_y0 == self.field.field_size[1] - 1:
                return False
            w_y1 = w_y0 + 1
            w_d1 = Direction.UP
        elif direction == Direction.LEFT:
            if w_x0 == 0:
                return False
            w_x1 = w_x0 - 1
            w_d1 = Direction.RIGHT
        else:
            if w_x0 == self.field.field_size[0] - 1:
                return False
            w_x1 = w_x0 + 1
            w_d1 = Direction.LEFT
        s = self.field.wall_set
        return not ((int(Wall(w_x0, w_y0, w_d0)) in s) or (int(Wall(w_x1, w_y1, w_d1)) in s))

    def move_unit(self, is_player_move: bool, direction: Direction) -> bool:
        if not self.can_move(is_player_move, direction):
            return False

        if is_player_move:
            ex_x = self.field.exit_pos[0]
            ex_y = self.field.exit_pos[1]
            ex_d = self.field.exit_direction

            if self.player_x == ex_x and self.player_y == ex_y and direction == ex_d:
                self.find_exit = True
            if direction == Direction.UP:
                self.player_y -= 1
            elif direction == Direction.DOWN:
                self.player_y += 1
            elif direction == Direction.LEFT:
                self.player_x -= 1
            else:
                self.player_x += 1
        else:
            if direction == Direction.UP:
                self.enemy_y -= 1
            elif direction == Direction.DOWN:
                self.enemy_y += 1
            elif direction == Direction.LEFT:
                self.enemy_x -= 1
            else:
                self.enemy_x += 1
        return True


class Game:
    def __init__(self, init_state: GameState):
        self.init_state = GameState(init_state.field, (init_state.player_x, init_state.player_y),
                                    (init_state.enemy_x, init_state.enemy_y), init_state.freeze_time)
        self.cur_state = GameState(init_state.field, (init_state.player_x, init_state.player_y),
                                   (init_state.enemy_x, init_state.enemy_y), init_state.freeze_time)
        self.result = Result.UNDEFINED
        if self.__check_lose():
            self.result = Result.LOSE

    def move(self, direction: Direction) -> bool:
        if self.result != Result.UNDEFINED:
            return False

        flag = self.cur_state.move_unit(True, direction)
        if not flag:
            return False

        if self.cur_state.find_exit:
            self.result = Result.WIN
            return True

        if self.__check_lose():
            self.result = Result.LOSE
            return True

        if self.cur_state.freeze_time > 0:
            enemy_moves = 0
        else:
            enemy_moves = 2

        for _ in range(enemy_moves):
            wanted_direction_x = self.cur_state.player_x - self.cur_state.enemy_x
            skip_horizontal_move = True
            if wanted_direction_x > 0 and self.cur_state.move_unit(False, Direction.RIGHT) \
                    or wanted_direction_x < 0 and self.cur_state.move_unit(False, Direction.LEFT):
                skip_horizontal_move = False
                self.cur_state.can_freeze = True
            if skip_horizontal_move:
                wanted_direction_y = self.cur_state.player_y - self.cur_state.enemy_y
                if wanted_direction_y > 0 and self.cur_state.move_unit(False, Direction.DOWN) \
                        or wanted_direction_y < 0 and self.cur_state.move_unit(False, Direction.UP):
                    self.cur_state.can_freeze = True
            if self.__check_lose():
                self.result = Result.LOSE
                return True
            if self.cur_state.can_freeze and self.__check_enemy_on_freeze():
                self.cur_state.freeze_time = 3
                return True
        if self.cur_state.freeze_time > 0:
            self.cur_state.freeze_time -= 1
            if self.cur_state.freeze_time == 0:
                self.cur_state.can_freeze = False
        return True

    def retry(self):
        self.cur_state = GameState(self.init_state.field, (self.init_state.player_x, self.init_state.player_y),
                                   (self.init_state.enemy_x, self.init_state.enemy_y), self.init_state.freeze_time)
        self.result = Result.UNDEFINED
        if self.__check_lose():
            self.result = Result.LOSE

    def __check_lose(self) -> bool:
        return self.cur_state.player_x == self.cur_state.enemy_x \
               and self.cur_state.player_y == self.cur_state.enemy_y or self.__check_player_on_freeze()

    def __check_player_on_freeze(self) -> bool:
        for f in self.cur_state.field.freeze_cells:
            if self.cur_state.player_x == f[0] and self.cur_state.player_y == f[1]:
                return True
        return False

    def __check_enemy_on_freeze(self) -> bool:
        for f in self.cur_state.field.freeze_cells:
            if self.cur_state.enemy_x == f[0] and self.cur_state.enemy_y == f[1]:
                return True
        return False
