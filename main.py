import pygame
import sys
from game import Direction, Wall, GameField, GameState, Game, Result
from random import random

heading = 'NeuWappo'
background_src = 'img/background-sand.png'
enemy_src = 'img/devil.png'
player_src = 'img/boy.png'
exit_src = 'img/exit.png'
freeze_src = 'img/freeze.png'

WHITE = (255, 255, 255)
GREY = (238, 238, 238)
BLACK = (0, 0, 0)

PLAYER = 0
ENEMY = 1
FREEZE = 2
WALL_UP = 3
WALL_RIGHT = 4
WALL_DOWN = 5
WALL_LEFT = 6
EXIT_UP = 7
EXIT_RIGHT = 8
EXIT_DOWN = 9
EXIT_LEFT = 10

font_name = 'freesansbold.ttf'
font_size = 24
center_label_text = "Run for your life!"
win_text = "You won!"
lose_text = "You lost!"
retry_text = "Retry"
fast_text = "Faster"
slow_text = "Slower"
fastest_solution_text = "Fastest solution: "
not_fount_solution_text = "Not found"
fastest_solution = ""
solution_font_size = 18
solution_y0 = 640

screen_w = 1024
screen_h = 682
field_cells_w = 6
field_cells_h = 6
cell_w0 = int((screen_w - 42) // (field_cells_w + 2))
cell_h0 = int((screen_h - 42) // (field_cells_h + 2))
cell_w = min(cell_w0, cell_h0)
cell_h = cell_w
wall_w = 4

center_x = screen_w // 2
center_y = screen_h // 2
field_x0 = int(center_x - field_cells_w * cell_w / 2)
field_y0 = int(center_y - field_cells_h * cell_h / 2)
field_w = field_cells_w * cell_w
field_h = field_cells_h * cell_h
retry_x0 = 800
retry_y0 = 30
fast_x0 = 800
fast_y0 = 90
slow_x0 = 800
slow_y0 = 150
button_w = 120
button_h = 40

pygame.init()
pygame.display.set_caption(heading)
background_img = pygame.image.load(background_src)
enemy_img = pygame.image.load(enemy_src)
enemy_scale_img = pygame.transform.scale(enemy_img, (int(0.8 * cell_w), int(0.8 * cell_h)))
pygame.display.set_icon(enemy_img)
player_img = pygame.image.load(player_src)
player_scale_img = pygame.transform.scale(player_img, (int(0.8 * cell_w), int(0.8 * cell_h)))
exit_img = pygame.image.load(exit_src)
exit_scale_img = pygame.transform.scale(exit_img, (cell_w, cell_h))
freeze_img = pygame.image.load(freeze_src)
freeze_scale_img = pygame.transform.scale(freeze_img, (int(0.9 * cell_w), int(0.9 * cell_h)))

screen = pygame.display.set_mode((screen_w, screen_h))


def update_screen(game_state: GameState, result: Result):
    screen.blit(background_img, (0, 0))
    draw_retry_button(WHITE)
    draw_fast_button(WHITE)
    draw_slow_button(WHITE)
    draw_game_field(game_state)
    draw_walking_elements(game_state)
    draw_center_label(result)
    draw_solution_label()
    pygame.display.update()


def get_test_game_field() -> GameField:
    field_size = (6, 6)
    exit_pos = (5, 2)
    exit_direction = Direction.RIGHT
    walls = [Wall(0, 0, Direction.DOWN), Wall(0, 1, Direction.RIGHT),
             Wall(0, 2, Direction.RIGHT), Wall(0, 3, Direction.RIGHT)]
    freeze_cells = []
    return GameField(field_size, exit_pos, exit_direction, walls, freeze_cells)


def get_test_game_state() -> GameState:
    player_pos = (2, 4)
    enemy_pos = (0, 2)
    return GameState(get_test_game_field(), player_pos, enemy_pos)


def launch_test_game() -> Game:
    return Game(get_test_game_state())


def draw_game_field(game_state: GameState):
    for f in game_state.field.freeze_cells:
        f_x = field_x0 + f[0] * cell_w + int(0.05 * cell_w)
        f_y = field_y0 + f[1] * cell_h + int(0.05 * cell_h)
        screen.blit(freeze_scale_img, (f_x, f_y))
    exit_img_x = field_x0 + game_state.field.exit_pos[0] * cell_w
    exit_img_y = field_y0 + game_state.field.exit_pos[1] * cell_h
    if game_state.field.exit_direction == Direction.RIGHT:
        exit_img_x += cell_w
    elif game_state.field.exit_direction == Direction.LEFT:
        exit_img_x -= cell_w
    elif game_state.field.exit_direction == Direction.UP:
        exit_img_y -= cell_h
    else:
        exit_img_y += cell_h
    screen.blit(exit_scale_img, (exit_img_x, exit_img_y))
    pygame.draw.rect(screen, BLACK, (field_x0, field_y0, field_w, field_h), 4)
    draw_retry_button(WHITE)
    for _ in range(field_cells_w - 1):
        pygame.draw.line(screen, BLACK, (field_x0 + (_ + 1) * cell_w, field_y0),
                         (field_x0 + (_ + 1) * cell_w, field_y0 + field_cells_w * cell_h))
    for _ in range(field_cells_h - 1):
        pygame.draw.line(screen, BLACK, (field_x0, field_y0 + (_ + 1) * cell_h),
                         (field_x0 + field_cells_h * cell_w, field_y0 + (_ + 1) * cell_h))
    for w in game_state.field.walls:
        w_x0 = field_x0 + w.x * cell_w
        w_y0 = field_y0 + w.y * cell_h
        w_x1 = field_x0 + w.x * cell_w + cell_w
        w_y1 = field_y0 + w.y * cell_h + cell_h
        if w.direction == Direction.LEFT:
            w_x1 = w_x0
        elif w.direction == Direction.RIGHT:
            w_x0 = w_x1
        elif w.direction == Direction.UP:
            w_y1 = w_y0
        else:
            w_y0 = w_y1
        pygame.draw.line(screen, BLACK, (w_x0, w_y0), (w_x1, w_y1), wall_w)


def draw_walking_elements(game_state: GameState):
    enemy_img_x = field_x0 + game_state.enemy_x * cell_w + int(0.1 * cell_w)
    enemy_img_y = field_y0 + game_state.enemy_y * cell_h + int(0.1 * cell_h)
    screen.blit(enemy_scale_img, (enemy_img_x, enemy_img_y))
    player_img_x = field_x0 + game_state.player_x * cell_w + int(0.1 * cell_w)
    player_img_y = field_y0 + game_state.player_y * cell_h + int(0.1 * cell_h)
    screen.blit(player_scale_img, (player_img_x, player_img_y))


def draw_center_label(result: Result):
    font_state = pygame.font.Font(font_name, font_size)
    if result == Result.UNDEFINED:
        text = center_label_text
    elif result == Result.WIN:
        text = win_text
    else:
        text = lose_text
    text_state = font_state.render(text, True, BLACK)
    text_state_rect = text_state.get_rect()
    text_state_rect.center = (screen_w // 2, retry_y0 + button_h // 2)
    screen.blit(text_state, text_state_rect)


def draw_solution_label():
    font_state = pygame.font.Font(font_name, solution_font_size)
    text = fastest_solution_text
    if fastest_solution == "":
        text += not_fount_solution_text
    else:
        text += fastest_solution
    text_state = font_state.render(text, True, BLACK)
    text_state_rect = text_state.get_rect()
    text_state_rect.center = (screen_w // 2, solution_y0)
    screen.blit(text_state, text_state_rect)


def draw_retry_button(color: tuple[int, int, int]):
    pygame.draw.rect(screen, color, (retry_x0, retry_y0, button_w, button_h), 0, 10)
    pygame.draw.rect(screen, BLACK, (retry_x0, retry_y0, button_w, button_h), 4, 10)
    font_state = pygame.font.Font(font_name, font_size)
    text_state = font_state.render(retry_text, True, BLACK)
    text_state_rect = text_state.get_rect()
    text_state_rect.center = (retry_x0 + button_w // 2, retry_y0 + button_h // 2)
    screen.blit(text_state, text_state_rect)


def draw_fast_button(color: tuple[int, int, int]):
    pygame.draw.rect(screen, color, (fast_x0, fast_y0, button_w, button_h), 0, 10)
    pygame.draw.rect(screen, BLACK, (fast_x0, fast_y0, button_w, button_h), 4, 10)
    font_state = pygame.font.Font(font_name, font_size)
    text_state = font_state.render(fast_text, True, BLACK)
    text_state_rect = text_state.get_rect()
    text_state_rect.center = (fast_x0 + button_w // 2, fast_y0 + button_h // 2)
    screen.blit(text_state, text_state_rect)


def draw_slow_button(color: tuple[int, int, int]):
    pygame.draw.rect(screen, color, (slow_x0, slow_y0, button_w, button_h), 0, 10)
    pygame.draw.rect(screen, BLACK, (slow_x0, slow_y0, button_w, button_h), 4, 10)
    font_state = pygame.font.Font(font_name, font_size)
    text_state = font_state.render(slow_text, True, BLACK)
    text_state_rect = text_state.get_rect()
    text_state_rect.center = (slow_x0 + button_w // 2, slow_y0 + button_h // 2)
    screen.blit(text_state, text_state_rect)


def is_button_clicked(mouse_pos: tuple[int, int]) -> str:
    if (retry_x0 < mouse_pos[0] < retry_x0 + button_w) and (retry_y0 < mouse_pos[1] < retry_y0 + button_h):
        return retry_text
    if (fast_x0 < mouse_pos[0] < fast_x0 + button_w) and (fast_y0 < mouse_pos[1] < fast_y0 + button_h):
        return fast_text
    if (slow_x0 < mouse_pos[0] < slow_x0 + button_w) and (slow_y0 < mouse_pos[1] < slow_y0 + button_h):
        return slow_text
    return ""


def get_initial_q_table():
    return [[random(), random(), random(), random()] for _ in range(4 * ((field_cells_w * field_cells_h) ** 2))]


def state_id(game_state: GameState):
    x = field_cells_w * game_state.player_y + game_state.player_x
    y = field_cells_w * game_state.enemy_y + game_state.enemy_x
    return field_cells_w * field_cells_h * x + y + ((field_cells_w * field_cells_h) ** 2) * game_state.freeze_time


game = launch_test_game()
update_screen(game.cur_state, game.result)
q_table = get_initial_q_table()

lr = 0.1
gamma = 0.6

time_wait = 30
fast_coeff = 2

current_route = ""

while True:
    if game.result != Result.UNDEFINED:
        if game.result == Result.WIN:
            if fastest_solution == "" or len(fastest_solution) > len(current_route):
                fastest_solution = current_route
        pygame.time.wait(time_wait)
        game.retry()
        current_route = ""
    cur_state = state_id(game.cur_state)
    q_values = q_table[cur_state]
    while game.result == Result.UNDEFINED:
        q_values = q_table[cur_state]
        ans = q_values.index(max(q_values))
        d = Direction.UP
        step = 'U'
        if ans == 1:
            d = Direction.RIGHT
            step = 'R'
        if ans == 2:
            d = Direction.DOWN
            step = 'D'
        if ans == 3:
            d = Direction.LEFT
            step = 'L'
        r = 0
        if game.move(d):
            current_route += step
            if game.cur_state.find_exit:
                r = 10
            elif game.result == Result.LOSE:
                r = -1
            else:
                r = -0.1
            new_state_id = state_id(game.cur_state)
            q_table[cur_state][ans] = (1 - lr) * q_table[cur_state][ans] + lr * (r + gamma * max(q_table[new_state_id]))
            break
        q_table[cur_state][ans] = -100500
    update_screen(game.cur_state, game.result)
    pygame.time.wait(time_wait)

    for ev in pygame.event.get():
        if ev.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if ev.type == pygame.KEYDOWN:
            if ev.key == pygame.K_UP:
                game.move(Direction.UP)
            if ev.key == pygame.K_DOWN:
                game.move(Direction.DOWN)
            if ev.key == pygame.K_LEFT:
                game.move(Direction.LEFT)
            if ev.key == pygame.K_RIGHT:
                game.move(Direction.RIGHT)
            update_screen(game.cur_state, game.result)
        if ev.type == pygame.MOUSEBUTTONDOWN:
            txt = is_button_clicked(pygame.mouse.get_pos())
            if txt == retry_text:
                draw_retry_button(GREY)
                pygame.display.update()
                pygame.time.wait(100)
                game.retry()
                update_screen(game.cur_state, game.result)
            if txt == fast_text:
                draw_fast_button(GREY)
                pygame.display.update()
                pygame.time.wait(100)
                time_wait = max(1, int(time_wait / fast_coeff))
            if txt == slow_text:
                draw_slow_button(GREY)
                pygame.display.update()
                pygame.time.wait(100)
                time_wait = int(time_wait * fast_coeff)
