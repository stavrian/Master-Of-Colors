import pygame as pg

class SoundManager:
    def __init__(self):
        pg.mixer.init()
        self.background_music = 'sounds\main theme.mp3'
        self.correct_sound = pg.mixer.Sound('sounds\correctchoice.mp3')
        self.wrong_sound = pg.mixer.Sound('sounds\wrongchoice.wav')
        self.wrong_sound.set_volume(0.3)    # ✅ μειωμένη ένταση


    def play_background(self):
        pg.mixer.music.load(self.background_music)
        pg.mixer.music.set_volume(0.5)
        pg.mixer.music.play(-1)  # επανάληψη για πάντα

    def stop_background(self):
        pg.mixer.music.stop()

    def play_correct(self):
        self.correct_sound.play()

    def play_wrong(self):
        self.wrong_sound.play()