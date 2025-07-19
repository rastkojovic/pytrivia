import os
import pygame

BACKGROUND_SOUND_PATH = os.path.join("resources", "sound", "background-sound.mp3")
INCORRECT_SOUND_PATH = os.path.join("resources", "sound", "incorrect-sound.mp3")
CORRECT_SOUND_PATH = os.path.join("resources", "sound", "correct-sound.mp3")
GAMEOVER_SOUND_PATH = os.path.join("resources", "sound", "game-over-sound.mp3")
MENU_SOUND_PATH = os.path.join("resources", "sound", "menu-sound.mp3")

# Initialize mixer and create Sound objects
pygame.mixer.init()
background_sound = pygame.mixer.Sound(file=BACKGROUND_SOUND_PATH)
menu_sound = pygame.mixer.Sound(file=MENU_SOUND_PATH)
correct_sound = pygame.mixer.Sound(file=CORRECT_SOUND_PATH)
incorrect_sound = pygame.mixer.Sound(file=INCORRECT_SOUND_PATH)
game_over_sound = pygame.mixer.Sound(file=GAMEOVER_SOUND_PATH)
sound_channel1 = pygame.mixer.Channel(1)
sound_channel2 = pygame.mixer.Channel(2)