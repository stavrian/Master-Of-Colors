import pygame as pg
import os

TILE_SIZE = 256

def load_image(filename):
    """Φόρτωση και μετατροπή εικόνας (με alpha)"""
    path = os.path.join('block_images', filename)
    image = pg.image.load(path).convert_alpha()  # χρησιμοποιούμε convert_alpha για να κρατήσει τη διαφάνεια
    return pg.transform.scale(image, (TILE_SIZE, TILE_SIZE))  # προσαρμογή μεγέθους

def load_small_image(filename, size=(32, 32)):
    """Για εικόνες όπως καρδιές – μικρότερες"""
    path = os.path.join('block_images', filename)
    image = pg.image.load(path).convert_alpha()
    return pg.transform.scale(image, size)

# Λεξικό με υφές
def load_textures():
    textures = {
        'floor': load_image('0_floor.jpg'),
        '#': load_image('0_brick.jpg'),
        '1': [  # Yellow category
            load_image('1_sunflower.png'),
            load_image('1_bee.png'),
            load_image('1_cheese.png'),
            load_image('1_lemon.png')
        ],
        '2': [  # Red category
            load_image('2_redsunset.png'),
            load_image('2_strawberry.png'),
            load_image('2_watermelon.png'),
            load_image('2_ladybug.png')
        ],
        '3': [  # Blue category
            load_image('3_blueorchid.png'),
            load_image('3_butterfly.png'),
            load_image('3_jellyfish.png'),
            load_image('3_sea.png')
        ],
        'life': load_small_image('life.png')  #  Προστέθηκε η εικόνα ζωής
    }
    return textures