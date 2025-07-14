import pygame as pg
import sys
import math
from textures import load_textures
from sound_manager import SoundManager
from UImanager import draw_ui

# Ρυθμίσεις παραθύρου και χάρτη
SCREEN_HEIGHT = 480
SCREEN_WIDTH = SCREEN_HEIGHT * 2
MAP_SIZE = 8
TILE_SIZE = int(SCREEN_HEIGHT / MAP_SIZE)
WALL = 21000

# Raycasting
FOV = math.pi / 3
HALF_FOV = FOV / 2
CASTED_RAYS = 240
STEP_ANGLE = FOV / CASTED_RAYS
MAX_DEPTH = SCREEN_HEIGHT
SCALE = (SCREEN_WIDTH / 2) / CASTED_RAYS

# Διαθέσιμοι χάρτες
MAPS = [
    [
        '########',
        '# 13##2#',
        '# 2#  1#',
        '# #  ###',
        '#    3##',
        '#21#  1#',
        '#3 ##23#',
        '########'
    ],
    [
        '########',
        '#  3#32#',
        '#2#23#1#',
        '# 1    #',
        '# ## # #',
        '#1  #3 #',
        '# 2## 1#',
        '########'
    ]
]

def run_game(win, level_index):
    import pygame as pg
    import math
    import sys

    from textures import load_textures
    from sound_manager import SoundManager
    from UImanager import draw_ui

    pg.init()
    clock = pg.time.Clock()

    # --- Αρχικοποίηση παίκτη ---
    player_x = SCREEN_WIDTH / 4
    player_y = SCREEN_HEIGHT / 2
    player_angle = math.pi
    speed = 3
    forward = True

    # --- Αρχικοποίηση πίστας ---
    MAP = [row[:] for row in MAPS[level_index % len(MAPS)]]  # deepcopy για αποφυγή mutability bug
    block_textures_map = {}
    textures = load_textures()
    sound = SoundManager()
    sound.play_background()

    # --- Αρχικοποίηση αντικειμένων παιχνιδιού ---
    category_indices = {'1': 0, '2': 0, '3': 0}
    for row in range(MAP_SIZE):
        for col in range(MAP_SIZE):
            tile = MAP[row][col]
            if tile in category_indices:
                tex_list = textures.get(tile)
                idx = category_indices[tile]
                chosen = tex_list[idx] if idx < len(tex_list) else tex_list[-1]
                block_textures_map[(row, col)] = chosen
                category_indices[tile] += 1

    # --- Καταστάσεις παιχνιδιού ---
    found_blocks = {'1': 0, '2': 0, '3': 0}
    MAX_PER_CATEGORY = 4
    current_target = 1
    player_lives = 4
    remove_block = False
    game_over = False
    game_won = False
    message = ""
    message_timer = 0
    end_time = None

    # --- Συναρτήσεις ---
    def cast_rays():
        nonlocal remove_block, current_target, message, message_timer
        nonlocal player_lives, game_over, game_won
        start_angle = player_angle - HALF_FOV

        for ray in range(CASTED_RAYS):
            for depth in range(MAX_DEPTH):
                target_x = player_x - math.sin(start_angle) * depth
                target_y = player_y + math.cos(start_angle) * depth
                row = int(target_y / TILE_SIZE)
                col = int(target_x / TILE_SIZE)
                hit_vertical = abs(math.cos(start_angle)) > abs(math.sin(start_angle))

                if 0 <= row < MAP_SIZE and 0 <= col < MAP_SIZE:
                    tile = MAP[row][col]
                    if tile != ' ':
                        corrected_depth = depth * math.cos(player_angle - start_angle)
                        wall_height = min(WALL / (corrected_depth + 0.0001), SCREEN_HEIGHT)
                        texture = block_textures_map.get((row, col), textures.get(tile))
                        if texture:
                            hit_x = target_x % TILE_SIZE if hit_vertical else target_y % TILE_SIZE
                            tex_x = int(hit_x / TILE_SIZE * texture.get_width())
                            tex_x = max(0, min(tex_x, texture.get_width() - 1))
                            column = texture.subsurface((tex_x, 0, 1, texture.get_height()))
                            column = pg.transform.scale(column, (int(SCALE), int(wall_height)))
                            win.blit(column, (
                                SCREEN_HEIGHT + ray * SCALE,
                                SCREEN_HEIGHT / 2 - wall_height / 2
                            ))

                        # Ελέγχει το κεντρικό ray
                        if ray == CASTED_RAYS // 2 and remove_block:
                            if tile == str(current_target):
                                if found_blocks[tile] < MAX_PER_CATEGORY:
                                    found_blocks[tile] += 1
                                    MAP[row] = MAP[row][:col] + ' ' + MAP[row][col+1:]
                                    block_textures_map.pop((row, col), None)
                                    message = f"Correct! {found_blocks[tile]}/{MAX_PER_CATEGORY}"
                                    sound.play_correct()
                                    if found_blocks[tile] >= MAX_PER_CATEGORY:
                                        current_target += 1
                                else:
                                    message = "Already done!"
                                message_timer = pg.time.get_ticks()
                            else:
                                player_lives -= 1
                                sound.play_wrong()
                                message = "Try Again!"
                                message_timer = pg.time.get_ticks()
                                if player_lives <= 0:
                                    game_over = True
                            remove_block = False
                        break
                if ray % 3 == 0:
                    pg.draw.line(win, (0, 255, 0), (player_x, player_y), (target_x, target_y), 1)
            start_angle += STEP_ANGLE

    def draw_map():
        for row in range(MAP_SIZE):
            for col in range(MAP_SIZE):
                tile = MAP[row][col]
                rect = (col * TILE_SIZE, row * TILE_SIZE, TILE_SIZE - 2, TILE_SIZE - 2)
                if tile in textures:
                    texture = block_textures_map.get((row, col), textures.get(tile))
                    tex_sample = pg.transform.scale(texture, (TILE_SIZE - 2, TILE_SIZE - 2))
                    win.blit(tex_sample, rect)
                else:
                    pg.draw.rect(win, (100, 100, 100), rect)
        pg.draw.circle(win, (255, 0, 0), (int(player_x), int(player_y)), 8)
        pg.draw.line(win, (0, 255, 0),
            (player_x, player_y),
            (player_x - math.sin(player_angle)*50, player_y + math.cos(player_angle)*50), 3)

    # --- Game loop ---
    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return "quit"
            if event.type == pg.KEYDOWN and event.key == pg.K_e:
                remove_block = True

        keys = pg.key.get_pressed()
        if keys[pg.K_LEFT]: player_angle -= 0.1
        if keys[pg.K_RIGHT]: player_angle += 0.1
        if keys[pg.K_UP]:
            forward = True
            player_x -= math.sin(player_angle) * speed
            player_y += math.cos(player_angle) * speed
        if keys[pg.K_DOWN]:
            forward = False
            player_x += math.sin(player_angle) * speed
            player_y -= math.cos(player_angle) * speed
        if keys[pg.K_p]: speed += 1
        if keys[pg.K_m]: speed = max(1, speed - 1)

        # Collision
        player_x = max(0, min(player_x, SCREEN_WIDTH / 2))
        player_y = max(0, min(player_y, SCREEN_HEIGHT))
        row = int(player_y / TILE_SIZE)
        col = int(player_x / TILE_SIZE)
        if 0 <= row < MAP_SIZE and 0 <= col < MAP_SIZE and MAP[row][col] != ' ':
            dx = math.sin(player_angle) * speed
            dy = -math.cos(player_angle) * speed
            if forward:
                player_x += dx
                player_y += dy
            else:
                player_x -= dx
                player_y -= dy

        # Σχεδίαση
        win.fill((0, 0, 0))
        draw_map()
        win.blit(pg.transform.scale(textures['floor'], (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)), (SCREEN_HEIGHT, SCREEN_HEIGHT // 2))
        pg.draw.rect(win, (200, 200, 200), (SCREEN_HEIGHT, -SCREEN_HEIGHT / 2, SCREEN_HEIGHT, SCREEN_HEIGHT))

        cast_rays()

        draw_ui(
            win=win,
            textures=textures,
            SCREEN_WIDTH=SCREEN_WIDTH,
            SCREEN_HEIGHT=SCREEN_HEIGHT,
            current_target=current_target,
            found_blocks=found_blocks,
            MAX_PER_CATEGORY=MAX_PER_CATEGORY,
            message=message,
            message_timer=message_timer,
            player_lives=player_lives,
            game_won=game_won,
            game_over=game_over
        )

        pg.draw.circle(win, (255, 0, 0), (SCREEN_HEIGHT + (SCREEN_WIDTH - SCREEN_HEIGHT) // 2, SCREEN_HEIGHT // 2), 4)

        if all(found_blocks[str(k)] >= MAX_PER_CATEGORY for k in range(1, 4)):
            game_won = True
        if player_lives <= 0:
            game_over = True

        if (game_won or game_over) and end_time is None:
            end_time = pg.time.get_ticks()

        if end_time is not None and pg.time.get_ticks() - end_time > 3000:
            return "won" if game_won else "lost"

        pg.display.flip()
        clock.tick(60)