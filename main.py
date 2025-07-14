import pygame as pg
from game_states import GameState
from menu import draw_menu
from game import run_game

# Αρχικοποίηση και παράθυρο
pg.init()
SCREEN_HEIGHT = 480
SCREEN_WIDTH = SCREEN_HEIGHT * 2
win = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pg.display.set_caption("Master of Colors")

state = GameState.MENU
while True:
    if state == GameState.MENU:
        selected_level = draw_menu(win)
        if selected_level is not None:
            state = GameState.IN_GAME

    elif state == GameState.IN_GAME:
        #run_game(win, selected_level)  # επιστρέφει στο MENU μετά τη νίκη/ήττα
        result = run_game(win, selected_level)
        print("Αποτέλεσμα:", result)
        state = GameState.MENU