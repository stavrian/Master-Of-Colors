import pygame as pg

def draw_ui(win, textures, SCREEN_WIDTH, SCREEN_HEIGHT, current_target, found_blocks, 
            MAX_PER_CATEGORY, message, message_timer, player_lives, game_won, game_over):
    
    # Γραμματοσειρές
    font = pg.font.SysFont(None, 24)
    font2 = pg.font.SysFont(None, 40)
        
    # Τρέχον Level
    text = font.render(f"Level: {current_target}", True, (255, 255, 255))
    win.blit(text, (10, SCREEN_HEIGHT - 30))
    
    #Πόσα blocks έχουν βρεθεί
    status =  f"1:{found_blocks['1']}/{MAX_PER_CATEGORY}  2:{found_blocks['2']}/{MAX_PER_CATEGORY}  3:{found_blocks['3']}/{MAX_PER_CATEGORY}"
    status_text = font.render(status, True, (180, 180, 180))
    win.blit(status_text, (150, SCREEN_HEIGHT - 30))
    
    # Εμφάνιση μηνύματος επιτυχίας ή αποτυχίας για περιορισμένο χρόνο
    if message and pg.time.get_ticks() - message_timer < 1500:
        msg_text = font.render(message, True, (255, 255, 0))
        win.blit(msg_text, (10, SCREEN_HEIGHT - 60))
    else:
        message = ""
        
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
    
    # Μηνύματα νίκης/ήττας
    if game_over:
        game_over_msg = font2.render("Game Over - Try Again!", True, (255, 0, 0))
        win.blit(game_over_msg, (SCREEN_HEIGHT // 2 - 100, SCREEN_HEIGHT // 2 - 20))
    elif game_won:
        win_msg = font2.render("Congratulations, You are the Master of Colors", True, (125, 215, 0))
        win.blit(win_msg, (SCREEN_HEIGHT // 2 - 100, SCREEN_HEIGHT // 2 - 20))