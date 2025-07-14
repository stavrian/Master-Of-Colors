import pygame as pg

def draw_menu(win):
    pg.font.init()
    clock = pg.time.Clock()
    font = pg.font.SysFont("arial", 40)
    small_font = pg.font.SysFont("arial", 30)

    # Χρώματα
    BG_COLOR = (30, 30, 30)
    BUTTON_COLOR = (70, 130, 180)
    HOVER_COLOR = (100, 160, 210)
    TEXT_COLOR = (255, 255, 255)

    # Κουμπιά (label, rect, level_index)
    buttons = [
        ("Πίστα 1", pg.Rect(150, 250, 200, 60), 0),
        ("Πίστα 2", pg.Rect(450, 250, 200, 60), 1),
    ]

    while True:
        win.fill(BG_COLOR)

        # Τίτλος
        title = font.render("Master of Colors", True, TEXT_COLOR)
        win.blit(title, (win.get_width() // 2 - title.get_width() // 2, 100))

        # Σχεδίαση κουμπιών
        mouse_pos = pg.mouse.get_pos()
        for text, rect, index in buttons:
            color = HOVER_COLOR if rect.collidepoint(mouse_pos) else BUTTON_COLOR
            pg.draw.rect(win, color, rect)
            label = small_font.render(text, True, TEXT_COLOR)
            win.blit(label, (rect.x + rect.width // 2 - label.get_width() // 2,
                             rect.y + rect.height // 2 - label.get_height() // 2))

        # Γεγονότα
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                exit()
            if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                for _, rect, index in buttons:
                    if rect.collidepoint(event.pos):
                        return index  # Επιστρέφει το index της πίστας που επιλέχθηκε

        pg.display.flip()
        clock.tick(60)