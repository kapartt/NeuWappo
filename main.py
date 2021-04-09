import pygame
import sys
from game import Direction, Wall, GameField, GameState, Game, Result


heading = 'NeuWappo'
background_src = 'img/background-sand.png'
enemy_src = 'img/devil.png'
player_src = 'img/boy.png'
exit_src = 'img/exit.png'
freeze_src = 'img/freeze.png'

WHITE = (255, 255, 255)
GREY = (238, 238, 238)
BLACK = (0, 0, 0)


font_name = 'freesansbold.ttf'
font_size = 24
center_label_text = "Run for your life!"
win_text = "You won!"
lose_text = "You lost!"
retry_text = "Retry"

screen_w = 1024
screen_h = 682
cell_w = 80
cell_h = 80
wall_w = 4

center_x = screen_w // 2
center_y = screen_h // 2
field_x0 = center_x - 3 * cell_w
field_y0 = center_y - 3 * cell_h
field_w = 6 * cell_w
field_h = 6 * cell_h
retry_x0 = 800
retry_y0 = 30
retry_w = 120
retry_h = 40

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
    draw_game_field(game_state)
    draw_walking_elements(game_state)
    draw_center_label(result)
    pygame.display.update()


def get_test_game_field() -> GameField:
    field_size = (6, 6)
    exit_pos = (5, 2)
    exit_direction = Direction.RIGHT
    walls = [Wall(0, 0, Direction.DOWN), Wall(0, 1, Direction.RIGHT),
             Wall(0, 2, Direction.RIGHT), Wall(0, 3, Direction.RIGHT)]
    freeze_cells = [(0, 0), (0, 4)]
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
    for _ in range(5):
        pygame.draw.line(screen, BLACK, (field_x0 + (_ + 1) * cell_w, field_y0),
                         (field_x0 + (_ + 1) * cell_w, field_y0 + 6 * cell_h))
        pygame.draw.line(screen, BLACK, (field_x0, field_y0 + (_ + 1) * cell_h),
                         (field_x0 + 6 * cell_w, field_y0 + (_ + 1) * cell_h))
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
    text_state_rect.center = (screen_w // 2, retry_y0 + retry_h // 2)
    screen.blit(text_state, text_state_rect)


def draw_retry_button(color: tuple[int, int, int]):
    pygame.draw.rect(screen, color, (retry_x0, retry_y0, retry_w, retry_h), 0, 10)
    pygame.draw.rect(screen, BLACK, (retry_x0, retry_y0, retry_w, retry_h), 4, 10)
    font_state = pygame.font.Font(font_name, font_size)
    text_state = font_state.render(retry_text, True, BLACK)
    text_state_rect = text_state.get_rect()
    text_state_rect.center = (retry_x0 + retry_w // 2, retry_y0 + retry_h // 2)
    screen.blit(text_state, text_state_rect)


def is_button_clicked(mouse_pos: tuple[int, int]) -> bool:
    return (retry_x0 < mouse_pos[0] < retry_x0 + retry_w) and (retry_y0 < mouse_pos[1] < retry_y0 + retry_h)


game = launch_test_game()
update_screen(game.cur_state, game.result)

while True:
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
            if is_button_clicked(pygame.mouse.get_pos()):
                draw_retry_button(GREY)
                pygame.display.update()
                game.retry()
                update_screen(game.cur_state, game.result)
