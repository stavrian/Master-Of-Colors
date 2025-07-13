import pygame as pg
import sys
import math
from textures import load_textures
from sound_manager import SoundManager

# Ρυθμίσεις παραθύρου και χάρτη
SCREEN_HEIGHT = 480
SCREEN_WIDTH = SCREEN_HEIGHT * 2
MAP_SIZE = 8
TILE_SIZE = int(SCREEN_HEIGHT / MAP_SIZE)

# Παίκτης
player_x = SCREEN_WIDTH / 4
player_y = SCREEN_HEIGHT / 2
player_angle = math.pi
speed = 3

# Raycasting
FOV = math.pi / 3
HALF_FOV = FOV / 2
CASTED_RAYS = 240
STEP_ANGLE = FOV / CASTED_RAYS
MAX_DEPTH = SCREEN_HEIGHT
SCALE = (SCREEN_WIDTH / 2) / CASTED_RAYS

# Ενέργειες
#place_block = False
remove_block = False
game_won= False
game_over = False

MAP = [
    '########',
    '# 13##2#',
    '# 2#  1#',
    '# #  ###',
    '#    3##',
    '#21#  1#',
    '#3 ##23#',
    '########'
]

# Αρχικοποίηση
pg.init()
win = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pg.display.set_caption('Master Of Colors')
clock = pg.time.Clock()

#Φόρτωση Ήχων
sound = SoundManager()
sound.play_background()

#φόρτωση τών textures από εξωτερικό αρχείο py
textures= load_textures() 

block_textures_map = {}

# Μετρητής για κάθε κατηγορία (1, 2, 3)
category_indices = {'1': 0, '2': 0, '3': 0}

for row in range(MAP_SIZE):
    for col in range(MAP_SIZE):
        tile = MAP[row][col]
        if tile in ('1', '2', '3'):
            tex_list = textures.get(tile)
            index = category_indices[tile]

            if index < len(tex_list):
                chosen_texture = tex_list[index]
                block_textures_map[(row, col)] = chosen_texture
                category_indices[tile] += 1
            else:
                # Fallback αν έχεις παραπάνω από 4 blocks με το ίδιο tile
                block_textures_map[(row, col)] = tex_list[-1]  
                
current_target = 1 #επίπεδο

#Dictionary που ταξινομεί τα blocks ανά χρώμα
found_blocks = {
    '1': 0,
    '2': 0,
    '3': 0
}
MAX_PER_CATEGORY = 4
player_lives = 4


def cast_rays():
    global place_block, remove_block, current_target, message, message_timer
    start_angle = player_angle - HALF_FOV

    for ray in range(CASTED_RAYS):
        last_row, last_col = None, None

        for depth in range(MAX_DEPTH):
            target_x = player_x - math.sin(start_angle) * depth
            target_y = player_y + math.cos(start_angle) * depth

            row = int(target_y / TILE_SIZE)
            col = int(target_x / TILE_SIZE)
            
            hit_vertical = abs(math.cos(start_angle)) > abs(math.sin(start_angle))

            if 0 <= row < MAP_SIZE and 0 <= col < MAP_SIZE:
                tile = MAP[row][col]

                if tile == ' ':
                    last_row, last_col = row, col  # αποθήκευση τελευταίου κενού

                if tile != ' ':
                    # Σχεδίαση 2D
                    pg.draw.rect(win, (0, 255, 0), (col*TILE_SIZE, row*TILE_SIZE, TILE_SIZE-2, TILE_SIZE-2))

                    # 3D προβολή
                    corrected_depth = depth * math.cos(player_angle - start_angle)
                    wall_height = min(21000 / (corrected_depth + 0.0001), SCREEN_HEIGHT)
                    
                    shade = 255 / (1 + corrected_depth * corrected_depth * 0.001)
                    color = (shade, shade, shade) if tile == "#" else (180, 180, 180)
                    
                    # Επιλογή texture αν υπάρχει
                    texture = block_textures_map.get((row, col), textures.get(tile))


                    if texture:
                        # Υπολογισμός "x συντεταγμένης" της πρόσκρουσης στο texture
                        if hit_vertical:
                            hit_x = target_x % TILE_SIZE
                        else:
                            hit_x = target_y % TILE_SIZE
                        tex_x = int(hit_x / TILE_SIZE * texture.get_width())
                        tex_x = max(0, min(tex_x, texture.get_width() - 1))  # clamp

                        # Κομμάτι από την υφή που θέλουμε να προβάλουμε
                        column = texture.subsurface((tex_x, 0, 1, texture.get_height()))
                        column = pg.transform.scale(column, (int(SCALE), int(wall_height)))

                        # Προβολή στη 3D οθόνη
                        win.blit(column, (
                            SCREEN_HEIGHT + ray * SCALE,
                            SCREEN_HEIGHT / 2 - wall_height / 2
                        ))
                    else: # Αν δεν υπάρχει υφή, σχεδίασε με απλό χρώμα
                        pg.draw.rect(win, color, (
                            SCREEN_HEIGHT + ray * SCALE,
                            SCREEN_HEIGHT / 2 - wall_height / 2,
                            SCALE,
                            wall_height
                    ))

                    
                    if ray == CASTED_RAYS // 2: # διόρθωση ώστε να στοχεύει με βάση την κεντρική ακτίνα
                        if remove_block and tile == str(current_target):
                            if found_blocks[tile] < MAX_PER_CATEGORY:
                                found_blocks[tile] += 1
                                MAP[row] = MAP[row][:col] + ' ' + MAP[row][col+1:]
                                if (row, col) in block_textures_map:
                                    del block_textures_map[(row, col)]
                                message = f"Correct! {found_blocks[tile]}/{MAX_PER_CATEGORY}"
                                message_timer = pg.time.get_ticks()
                                sound.play_correct()
                                remove_block = False

                                if found_blocks[tile] >= MAX_PER_CATEGORY:
                                    current_target += 1
                            else:
                                message = " Try Again!"
                                message_timer = pg.time.get_ticks()
                                remove_block = False  # αγνόησε το λάθος κλικ 
                        else:
                            if remove_block:
                                message = " Try Again!"
                                message_timer = pg.time.get_ticks()
                                sound.play_wrong()
                                remove_block = False
                                global player_lives, game_won  # <-- προσθήκη
                                player_lives -= 1
                                if player_lives <= 0:
                                    game_over = True
                                
                        '''                 
                        if remove_block and tile.isdigit():
                            MAP[row] = MAP[row][:col] + ' ' + MAP[row][col+1:]
                            remove_block = False

                        
                        # Τοποθέτηση block στο προηγούμενο κενό tile
                        if place_block and last_row is not None and last_col is not None:
                            if MAP[last_row][last_col] == ' ':
                                MAP[last_row] = MAP[last_row][:last_col] + '1' + MAP[last_row][last_col+1:]
                                place_block = False
                        '''
                    break # ΟΠΟΙΑΔΗΠΟΤΕ ακτίνα βλέπει εμπόδιο, σταματά εκεί

                        
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
                texture_sample = pg.transform.scale(texture, (TILE_SIZE - 2, TILE_SIZE - 2))
                win.blit(texture_sample, rect)
            else:
                pg.draw.rect(win, (100, 100, 100), rect)

    # Παίκτης και δείκτης κατεύθυνσης
    pg.draw.circle(win, (255, 0, 0), (int(player_x), int(player_y)), 8)
    pg.draw.line(win, (0, 255, 0), 
        (player_x, player_y), 
        (player_x - math.sin(player_angle)*50, player_y + math.cos(player_angle)*50), 3)

forward = True
message = ""  # Μήνυμα που εμφανίζεται στον χρήστη
message_timer = 0 

# Loop παιχνιδιού
while True:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            sys.exit()
        if event.type == pg.KEYDOWN:
            #if event.key == pg.K_e:
            #    place_block = True
            if event.key == pg.K_e:
                remove_block = True

    keys = pg.key.get_pressed()
    if keys[pg.K_LEFT]:
        player_angle -= 0.1
    if keys[pg.K_RIGHT]:
        player_angle += 0.1
    if keys[pg.K_UP]:
        forward = True
        player_x -= math.sin(player_angle) * speed
        player_y += math.cos(player_angle) * speed
    if keys[pg.K_DOWN]:
        forward = False
        player_x += math.sin(player_angle) * speed
        player_y -= math.cos(player_angle) * speed
    if keys[pg.K_p]:
        speed += 1
    if keys[pg.K_m]:
        speed = max(1, speed - 1)

    # Έλεγχος ορίων και σύγκρουσης
    player_x = max(0, min(player_x, SCREEN_WIDTH / 2))
    player_y = max(0, min(player_y, SCREEN_HEIGHT))

    row = int(player_y / TILE_SIZE)
    col = int(player_x / TILE_SIZE)
    if 0 <= row < MAP_SIZE and 0 <= col < MAP_SIZE:
        #if MAP[row][col] == '#' or MAP[row][col] == 'X':
        if MAP[row][col] != ' ': 
            if forward:
                player_x += math.sin(player_angle) * speed
                player_y -= math.cos(player_angle) * speed
            else:
                player_x -= math.sin(player_angle) * speed
                player_y += math.cos(player_angle) * speed

    # Ζωγραφική
    win.fill((0, 0, 0))
    draw_map()
    
    # Πρώιμο UI
    font = pg.font.SysFont(None, 24)
    font2 = pg.font.SysFont(None, 40)
        
    text = font.render(f"Level: {current_target}", True, (255, 255, 255))
    win.blit(text, (10, SCREEN_HEIGHT - 30))
    
    status =  f"1:{found_blocks['1']}/{MAX_PER_CATEGORY}  2:{found_blocks['2']}/{MAX_PER_CATEGORY}  3:{found_blocks['3']}/{MAX_PER_CATEGORY}"
    status_text = font.render(status, True, (180, 180, 180))
    win.blit(status_text, (150, SCREEN_HEIGHT - 30))
    
    if message and pg.time.get_ticks() - message_timer < 1500:
        msg_text = font.render(message, True, (255, 255, 0))
        win.blit(msg_text, (10, SCREEN_HEIGHT - 60))
    else:
        message = ""
        

    # Πάτωμα
    floor_tex = textures['floor']
    floor_tex_scaled = pg.transform.scale(floor_tex, (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
    win.blit(floor_tex_scaled, (SCREEN_HEIGHT, SCREEN_HEIGHT // 2))
    #Ταβανι
    pg.draw.rect(win, (200, 200, 200), (SCREEN_HEIGHT, -SCREEN_HEIGHT / 2, SCREEN_HEIGHT, SCREEN_HEIGHT))

    cast_rays()
    
    # Μήνυμα καθοδήγησης ανά επίπεδο
    instruction = ""
    color = (255, 255, 255)  # default white

    if current_target == 1:
        instruction = "You must find all YELLOW items"
        color = (255, 255, 0)  # yellow
    elif current_target == 2:
        instruction = "Great, now you must find all RED items"
        color = (255, 0, 0)    # red
    elif current_target == 3:
        instruction = "And finally you must find all BLUE items"
        color = (0, 128, 255)  # blue

    if instruction:
        instruction_text = font.render(instruction, True, color)
        win.blit(instruction_text, (SCREEN_WIDTH - instruction_text.get_width() - 10, 10))
        
    # Εμφάνιση ζωών (life icons) πάνω δεξιά
    life_icon = textures['life']
    for i in range(player_lives):
        x = 10 + i * 40  # Από δεξιά προς τα αριστερά
        y = 10
        win.blit(life_icon, (x, y))
    
    # Κουκίδα στόχευσης στο κέντρο της 3D προβολής
    center_x = SCREEN_HEIGHT + (SCREEN_WIDTH - SCREEN_HEIGHT) // 2
    center_y = SCREEN_HEIGHT // 2
    pg.draw.circle(win, (255, 0, 0), (center_x, center_y), 4)
    
    # ΕΛΕΓΧΟΣ ΣΥΝΘΗΚΗΣ ΗΤΤΑΣ
    if player_lives <= 0:
        game_over = True
        game_over_msg = font2.render("Game Over - Try Again!", True, (255, 0, 0))
        win.blit(game_over_msg, (SCREEN_HEIGHT // 2 - 100, SCREEN_HEIGHT // 2 - 20))
    
    # ΕΛΕΓΧΟΣ ΣΥΝΘΗΚΗΣ ΝΙΚΗΣ
    if all(found_blocks[str(k)] >= MAX_PER_CATEGORY for k in range(1, 4)):
        game_won = True

    if game_won:
        win_msg = font2.render("Congratulations, You are the Master of Colors", True, (125, 215, 0))
        win.blit(win_msg, (SCREEN_HEIGHT // 2 - 100 , SCREEN_HEIGHT // 2 - 20))
        
    if game_over or game_won:
        pg.display.flip()
        pg.time.wait(3000)  # περίμενε 3 δευτερόλεπτα
        pg.quit()
        sys.exit()
        
    pg.display.flip()
    clock.tick(60)