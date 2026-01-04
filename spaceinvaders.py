import random

import pygame
import sys
import os
import json
from os.path import abspath, dirname
from random import choice

# Auto-detect a working framebuffer video driver
drivers = ['fbcon', 'kmsdrm', 'directfb', 'svgalib']
found_driver = False
for driver in drivers:
    os.environ['SDL_VIDEODRIVER'] = driver
    try:
        pygame.display.init()
        found_driver = True
        # print(f"Using video driver: {driver}")
        break
    except pygame.error as e:
        # print(f"Driver {driver} failed: {e}")
        continue

if not found_driver:
    # print("No suitable framebuffer video driver found.")
    try:
        os.environ['SDL_VIDEODRIVER'] = ''
        pygame.display.init()
    except pygame.error as e:
        # print(f"Got error intialising: {e}")
        sys.exit(1)

# Optional: specify framebuffer device if needed
# os.environ['SDL_FBDEV'] = '/dev/fb0'

pygame.init()
SCREEN = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
info = pygame.display.Info()
width, height = info.current_w, info.current_h

# Define a function to get the correct resource path for both development and PyInstaller environments
def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = abspath(dirname(__file__))

    return os.path.join(base_path, relative_path)

BASE_PATH = abspath(dirname(__file__))
FONT_PATH = resource_path('fonts')
IMAGE_PATH = resource_path('images')
SOUND_PATH = resource_path('sounds')

# Colors (R, G, B)
WHITE = (255, 255, 255)
GREEN = (78, 255, 87)
YELLOW = (255, 209, 0)
BLUE = (80, 255, 239)
PURPLE = (203, 0, 255)
RED = (237, 28, 36)

global HighScore



FONT = os.path.join(FONT_PATH, 'space_invaders.ttf')
IMG_NAMES = ['ship', 'mystery',
             'enemy1_1', 'enemy1_2',
             'enemy2_1', 'enemy2_2',
             'enemy3_1', 'enemy3_2',
             'explosionblue', 'explosiongreen', 'explosionpurple',
             'laser', 'enemylaser']
IMAGES = {name: pygame.image.load(os.path.join(IMAGE_PATH, '{}.png'.format(name))).convert_alpha()
          for name in IMG_NAMES}

PLAYER_NAME = ['A', 'A', 'A']
CURSOR_POSITION = 0
CURSOR_LETTER = 0
ROUND = 1

BLOCKERS_POSITION = int(height*0.75)
ENEMY_DEFAULT_POSITION = int(height*0.1)  # Initial value for a new game
ENEMY_MOVE_DOWN = int(height*0.027)

#Never gonna give you up, Never gonna let you down, Never gonna tell a lie, And hurt you

try:
    controller_keys_path = resource_path('controller-keys.json')
    with open(controller_keys_path, 'r+') as file:
        button_keys = json.load(file)
except Exception as e:
    print(f"Error loading controller keys: {e}")
    # Provide default controller keys in case the file can't be loaded
    button_keys = {
        "x": 0,
        "circle": 1,
        "left_arrow": 11,
        "right_arrow": 12,
        "up_arrow": 13,
        "down_arrow": 14
    }
# 0: Left analog horizonal, 1: Left Analog Vertical, 2: Right Analog Horizontal
# 3: Right Analog Vertical 4: Left Trigger, 5: Right Trigger
analog_keys = {0: 0, 1: 0, 2: 0, 3: 0, 4: -1, 5: -1}

pygame.joystick.init()
joysticks = []
for i in range(pygame.joystick.get_count()):
    joysticks.append(pygame.joystick.Joystick(i))
for joystick in joysticks:
    joystick.init()

class Ship(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = IMAGES['ship']
        self.rect = self.image.get_rect(topleft=(int(0.1*width), int(0.9*height)))
        self.speed = 8

    def update(self, keys, buttons, *args):
        if keys[pygame.K_LEFT] and self.rect.x > int(0.1*width):
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] and self.rect.x < int(0.9*width):
            self.rect.x += self.speed
        if buttons['left_arrow'] and self.rect.x > int(0.1*width):
            self.rect.x -= self.speed
        if buttons['right_arrow'] and self.rect.x < int(0.9*width):
            self.rect.x += self.speed
        game.screen.blit(self.image, self.rect)

class Bullet(pygame.sprite.Sprite):
    def __init__(self, xpos, ypos, direction, speed, filename, side):
        pygame.sprite.Sprite.__init__(self)
        self.image = IMAGES[filename]
        self.rect = self.image.get_rect(topleft=(xpos, ypos))
        self.speed = speed
        self.direction = direction
        self.side = side
        self.filename = filename

    def update(self, keys, *args):
        game.screen.blit(self.image, self.rect)
        self.rect.y += self.speed * self.direction
        if self.rect.y < 50 or self.rect.y > 1600:
            self.kill()

class Leaderboard():
    def __init__(self):
        self.total = 0
        self.leaderboard

    def incrementScore(self):
        self.total += 1

    def storeHighScore(self, name):
        self.leaderboard

class Enemy(pygame.sprite.Sprite):
    def __init__(self, row, column):
        pygame.sprite.Sprite.__init__(self)
        self.row = row
        self.column = column
        self.images = []
        self.load_images()
        self.index = 0
        self.image = self.images[self.index]
        self.rect = self.image.get_rect()

    def toggle_image(self):
        self.index += 1
        if self.index >= len(self.images):
            self.index = 0
        self.image = self.images[self.index]

    def update(self, *args):
        game.screen.blit(self.image, self.rect)

    def load_images(self):
        images = {0: ['1_2', '1_1'],
                  1: ['2_2', '2_1'],
                  2: ['2_2', '2_1'],
                  3: ['3_1', '3_2'],
                  4: ['3_1', '3_2'],
                  }
        img1, img2 = (IMAGES['enemy{}'.format(img_num)] for img_num in
                      images[self.row])
        self.images.append(pygame.transform.scale(img1, (40, 35)))
        self.images.append(pygame.transform.scale(img2, (40, 35)))

class EnemiesGroup(pygame.sprite.Group):
    def __init__(self, columns, rows):
        global ROUND
        pygame.sprite.Group.__init__(self)
        self.enemies = [[None] * columns for _ in range(rows)]
        self.columns = columns
        self.rows = rows
        self.leftAddMove = 0
        self.rightAddMove = 0
        self.moveTime = 85 - (10 * ROUND)
        self.direction = 1
        self.rightMoves = 60
        self.leftMoves = 60
        self.moveNumber = 0
        self.timer = pygame.time.get_ticks()
        self.bottom = game.enemyPosition + ((rows - 1) * 45) + 35
        self._aliveColumns = list(range(columns))
        self._leftAliveColumn = 0
        self._rightAliveColumn = columns - 1
        self.multiplier = 0.5 + ROUND / 2

    def update(self, current_time):
        if current_time - self.timer > self.moveTime:
            if self.direction == 1:
                max_move = self.rightMoves + self.rightAddMove
            else:
                max_move = self.leftMoves + self.leftAddMove

            if self.moveNumber >= max_move:
                self.leftMoves = 60 + self.rightAddMove
                self.rightMoves = 60 + self.leftAddMove
                self.direction *= -1
                self.moveNumber = 0
                self.bottom = 0
                for enemy in self:
                    enemy.rect.y += ENEMY_MOVE_DOWN
                    enemy.toggle_image()
                    if self.bottom < enemy.rect.y + 35:
                        self.bottom = enemy.rect.y + 35
            else:
                velocity = 15 if self.direction == 1 else -15
                for enemy in self:
                    enemy.rect.x += velocity
                    enemy.toggle_image()
                self.moveNumber += 1

            self.timer += self.moveTime

    def add_internal(self, *sprites):
        super(EnemiesGroup, self).add_internal(*sprites)
        for s in sprites:
            self.enemies[s.row][s.column] = s

    def remove_internal(self, *sprites):
        super(EnemiesGroup, self).remove_internal(*sprites)
        for s in sprites:
            self.kill(s)
        self.update_speed()

    def is_column_dead(self, column):
        return not any(self.enemies[row][column]
                       for row in range(self.rows))

    def random_bottom(self):
        col = choice(self._aliveColumns)
        col_enemies = (self.enemies[row - 1][col]
                       for row in range(self.rows, 0, -1))
        return next((en for en in col_enemies if en is not None), None)

    def update_speed(self):
        if len(self) == 1:
            self.moveTime -= 10
        elif len(self) <= 10:
            self.moveTime -= 5

    def kill(self, enemy):
        self.enemies[enemy.row][enemy.column] = None
        is_column_dead = self.is_column_dead(enemy.column)
        if is_column_dead:
            self._aliveColumns.remove(enemy.column)

        if enemy.column == self._rightAliveColumn:
            while self._rightAliveColumn > 0 and is_column_dead:
                self._rightAliveColumn -= 1
                self.rightAddMove += 5
                is_column_dead = self.is_column_dead(self._rightAliveColumn)

        elif enemy.column == self._leftAliveColumn:
            while self._leftAliveColumn < self.columns and is_column_dead:
                self._leftAliveColumn += 1
                self.leftAddMove += 5
                is_column_dead = self.is_column_dead(self._leftAliveColumn)

class Blocker(pygame.sprite.Sprite):
    def __init__(self, size, color, row, column):
        pygame.sprite.Sprite.__init__(self)
        self.height = size
        self.width = size
        self.color = color
        self.image = pygame.Surface((self.width, self.height))
        self.image.fill(self.color)
        self.rect = self.image.get_rect()
        self.row = row
        self.column = column

    def update(self, keys, *args):
        game.screen.blit(self.image, self.rect)

class Mystery(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = IMAGES['mystery']
        self.image = pygame.transform.scale(self.image, (75, 35))
        self.rect = self.image.get_rect(topleft=(-80, int(height*0.1)))
        self.row = 5
        self.moveTime = 25000
        self.direction = 1
        self.timer = pygame.time.get_ticks()
        self.mysteryEntered = pygame.mixer.Sound(os.path.join(SOUND_PATH, 'mysteryentered.wav'))
        self.mysteryEntered.set_volume(0.3)
        self.playSound = True

    def update(self, keys, _buttons, currentTime, *args):
        resetTimer = False
        passed = currentTime - self.timer
        if passed > self.moveTime:
            if (self.rect.x < 0 or self.rect.x > width) and self.playSound:
                self.mysteryEntered.play()
                self.playSound = False
            if self.rect.x < width + 30 and self.direction == 1:
                self.mysteryEntered.fadeout(4000)
                self.rect.x += random.randint(2, 6)
                game.screen.blit(self.image, self.rect)
            if self.rect.x > -100 and self.direction == -1:
                self.mysteryEntered.fadeout(4000)
                self.rect.x -= random.randint(2, 6)
                game.screen.blit(self.image, self.rect)

        if self.rect.x > width + 30:
            self.playSound = True
            self.direction = -1
            resetTimer = True
        if self.rect.x < -90:
            self.playSound = True
            self.direction = 1
            resetTimer = True
        if passed > self.moveTime and resetTimer:
            self.timer = currentTime

class EnemyExplosion(pygame.sprite.Sprite):
    def __init__(self, enemy, *groups):
        super(EnemyExplosion, self).__init__(*groups)
        self.image = pygame.transform.scale(self.get_image(enemy.row), (40, 35))
        self.image2 = pygame.transform.scale(self.get_image(enemy.row), (50, 45))
        self.rect = self.image.get_rect(topleft=(enemy.rect.x, enemy.rect.y))
        self.timer = pygame.time.get_ticks()

    @staticmethod
    def get_image(row):
        img_colors = ['purple', 'blue', 'blue', 'green', 'green']
        return IMAGES['explosion{}'.format(img_colors[row])]

    def update(self, current_time, *args):
        passed = current_time - self.timer
        if passed <= 100:
            game.screen.blit(self.image, self.rect)
        elif passed <= 200:
            game.screen.blit(self.image2, (self.rect.x - 6, self.rect.y - 6))
        elif 400 < passed:
            self.kill()

class MysteryExplosion(pygame.sprite.Sprite):
    def __init__(self, mystery, score, *groups):
        super(MysteryExplosion, self).__init__(*groups)
        self.text = Text(FONT, 20, str(score), WHITE,
                         mystery.rect.x + 20, mystery.rect.y + 6)
        self.timer = pygame.time.get_ticks()

    def update(self, current_time, *args):
        passed = current_time - self.timer
        if passed <= 200 or 400 < passed <= 600:
            self.text.draw(game.screen)
        elif 600 < passed:
            self.kill()

class ShipExplosion(pygame.sprite.Sprite):
    def __init__(self, ship, *groups):
        super(ShipExplosion, self).__init__(*groups)
        self.image = IMAGES['ship']
        self.rect = self.image.get_rect(topleft=(ship.rect.x, ship.rect.y))
        self.timer = pygame.time.get_ticks()

    def update(self, current_time, *args):
        passed = current_time - self.timer
        if 300 < passed <= 600:
            game.screen.blit(self.image, self.rect)
        elif 900 < passed:
            self.kill()

class Life(pygame.sprite.Sprite):
    def __init__(self, xpos, ypos):
        pygame.sprite.Sprite.__init__(self)
        self.image = IMAGES['ship']
        self.image = pygame.transform.scale(self.image, (40, 40))
        self.rect = self.image.get_rect(topleft=(xpos, ypos))

    def update(self, *args):
        game.screen.blit(self.image, self.rect)

class Text(object):
    def __init__(self, textFont, size, message, color, xpos, ypos):
        self.message = message
        self.xpos = xpos
        self.ypos = ypos
        self.font = pygame.font.Font(textFont, size)
        self.surface = self.font.render(message, True, color)
        self.rect = self.surface.get_rect(topleft=(self.xpos, ypos))

    def draw(self, surface):
        surface.blit(self.surface, self.rect)

    def move(self, position):
        self.rect = self.surface.get_rect(topleft=(position, self.ypos))
    def center(self):
        position = int((width-self.surface.get_width())/2)
        self.rect = self.surface.get_rect(topleft=(position, self.ypos))

class NameInput():
    def __init__(self, screen):
        self.screen = screen
        ###
        ### move the ref to the current player and the cursor position to a global variable that isn't reset by the main game loop.
        ###
        global PLAYER_NAME
        global CURSOR_POSITION
        self.letterOneText = Text(FONT, 50, PLAYER_NAME[0], WHITE, 625, 1410)
        self.letterTwoText = Text(FONT, 50, PLAYER_NAME[1], WHITE, 675, 1410)
        self.letterThreeText = Text(FONT, 50, PLAYER_NAME[2], WHITE, 725, 1410)

        self.letterOneText.draw(screen)
        self.letterTwoText.draw(screen)
        self.letterThreeText.draw(screen)

        if CURSOR_POSITION == 0:
            self.underline = Text(FONT, 50, '_', WHITE, 625, 1430)
            self.underline.draw(self.screen)
        if CURSOR_POSITION == 1:
            self.underline = Text(FONT, 50, '_', WHITE, 675, 1430)
            self.underline.draw(self.screen)
        if CURSOR_POSITION == 2:
            self.underline = Text(FONT, 50, '_', WHITE, 725, 1430)
            self.underline.draw(self.screen)

    def handle_input(self, button):
        global CURSOR_LETTER
        global CURSOR_POSITION
        global PLAYER_NAME
        alph = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
        if button == button_keys['right_arrow']:
            if CURSOR_POSITION < 2:
                CURSOR_POSITION += 1
            else:
                CURSOR_POSITION = 0
            CURSOR_LETTER = alph.index(PLAYER_NAME[CURSOR_POSITION])
        if button == button_keys['left_arrow']:
            if CURSOR_POSITION > 0:
                CURSOR_POSITION -= 1
            else:
                CURSOR_POSITION = 2
            CURSOR_LETTER = alph.index(PLAYER_NAME[CURSOR_POSITION])
        if button == button_keys['down_arrow']:
            if CURSOR_LETTER >= 0:
                CURSOR_LETTER -= 1
            else:
                CURSOR_LETTER = 25
            PLAYER_NAME[CURSOR_POSITION] = alph[CURSOR_LETTER]
        if button == button_keys['up_arrow']:
            if CURSOR_LETTER < 27:
                CURSOR_LETTER += 1
            else:
                CURSOR_LETTER = 0

        if CURSOR_POSITION == 0:
            self.underline.move(625)
        if CURSOR_POSITION == 1:
            self.underline.move(675)
        if CURSOR_POSITION == 2:
            self.underline.move(725)

class SpaceInvaders(object):
    def __init__(self):
        # It seems, in Linux buffersize=512 is not enough, use 4096 to prevent:
        #   ALSA lib pcm.c:7963:(snd_pcm_recover) underrun occurred
        pygame.mixer.pre_init(44100, -16, 1, 4096)
        self.clock = pygame.time.Clock()
        self.caption = pygame.display.set_caption('Space Invaders')
        self.screen = SCREEN
        bgimage = pygame.image.load(os.path.join(IMAGE_PATH, 'background.jpg'))
        bgimage1 = pygame.transform.scale(bgimage, (width, height))
        # self.background = pygame.image.load(os.path.join(IMAGE_PATH, 'background.jpg')).convert()
        self.background = bgimage1.convert()
        self.startGame = False
        self.mainScreen = True
        self.gameOver = False
        # Counter for enemy starting position (increased each new round)
        self.enemyPosition = ENEMY_DEFAULT_POSITION

        self.titleText = Text(FONT, int(height*0.1), 'Pi INVADERS', YELLOW, 380, int(height*0.3))
        self.titleText.center()
        self.titleText2 = Text(FONT, int(height*0.025), 'Collect as many points as you can while', WHITE, 260, int(height*0.45))
        self.titleText2.center()
        self.titleText3 = Text(FONT, int(height*0.025), 'avoiding the aliens\' lasers', WHITE, 380, int(height*0.49))
        self.titleText3.center()

        self.gameOverText = Text(FONT, int(height*0.1), 'Game Over', RED, 535, int(height*0.49))
        self.gameOverText.center()
        self.finalScoreText = Text(FONT, int(height*0.1), 'Points:', WHITE, 420, int(height*0.45))
        self.finalScoreText.center()
        self.nextRoundText = Text(FONT, int(height*0.1), 'Next Round', WHITE, 240, int(height*0.49))
        self.nextRoundText.center()
        self.enemy1Text = Text(FONT, int(height*0.03), '=    10 pts', GREEN, int(width*0.5), int(height*0.6))
        self.enemy2Text = Text(FONT, int(height*0.03), '=    20 pts', BLUE, int(width*0.5), int(height*0.66))
        self.enemy3Text = Text(FONT, int(height*0.03), '=    30 pts', PURPLE, int(width*0.5), int(height*0.72))
        self.enemy4Text = Text(FONT, int(height*0.03), '=    ?????', RED, int(width*0.5), int(height*0.78))

        self.scoreText = Text(FONT, int(height*0.03), 'Points:', WHITE, int(width*0.1), int(height*0.05))
        self.livesText = Text(FONT, int(height*0.03), 'Lives: ', WHITE, int(width*0.7), int(height*0.05))

        self.life1 = Life(int(width*0.8), int(height*0.05))
        self.life2 = Life(int(width*0.83), int(height*0.05))
        self.life3 = Life(int(width*0.86), int(height*0.05))
        self.livesGroup = pygame.sprite.Group(self.life1, self.life2, self.life3)

    def reset(self, score):
        global ROUND

        ROUND += 1
        self.player = Ship()
        self.playerGroup = pygame.sprite.Group(self.player)
        self.explosionsGroup = pygame.sprite.Group()
        self.bullets = pygame.sprite.Group()
        self.mysteryShip = Mystery()
        self.mysteryGroup = pygame.sprite.Group(self.mysteryShip)
        self.enemyBullets = pygame.sprite.Group()
        self.make_enemies()
        self.allSprites = pygame.sprite.Group(self.player, self.enemies,
                                       self.livesGroup, self.mysteryShip)
        self.keys = pygame.key.get_pressed()
        self.buttons = self.initButtons()
        self.timer = pygame.time.get_ticks()
        self.noteTimer = pygame.time.get_ticks()
        self.shipTimer = pygame.time.get_ticks()
        self.score = score
        self.create_audio()
        self.makeNewShip = False
        self.shipAlive = True

    def initButtons(self):
        buttons = {}
        for key in button_keys.keys():
            buttons[key] = False
        return buttons

    def make_blockers(self, number):
        blockerGroup = pygame.sprite.Group()
        for row in range(4):
            for column in range(10):
                blocker = Blocker(int(width*0.01), YELLOW, row, column)
                blocker.rect.x = int(width*0.15) + (int(width*0.2) * number) + (column * blocker.width)
                blocker.rect.y = BLOCKERS_POSITION + (row * blocker.height)
                blockerGroup.add(blocker)
        return blockerGroup

    def create_audio(self):
        self.sounds = {}
        for sound_name in ['shoot', 'shoot2', 'invaderkilled', 'mysterykilled',
                           'shipexplosion']:
            self.sounds[sound_name] = pygame.mixer.Sound(
                os.path.join(SOUND_PATH, '{}.wav'.format(sound_name)))
            self.sounds[sound_name].set_volume(0.2)

        self.musicNotes = [pygame.mixer.Sound(os.path.join(SOUND_PATH, '{}.wav'.format(i))) for i
                           in range(4)]
        for sound in self.musicNotes:
            sound.set_volume(0.5)

        self.noteIndex = 0

    def play_main_music(self, currentTime):
        if currentTime - self.noteTimer > self.enemies.moveTime:
            self.note = self.musicNotes[self.noteIndex]
            if self.noteIndex < 3:
                self.noteIndex += 1
            else:
                self.noteIndex = 0

            self.note.play()
            self.noteTimer += self.enemies.moveTime

    @staticmethod
    def should_exit(evt):
        # type: (pygame.event.EventType) -> bool
        return evt.type == pygame.QUIT or (evt.type == pygame.KEYUP and evt.key == pygame.K_ESCAPE)

    @staticmethod
    def should_reset(evt):
        # type: (pygame.event.EventType) -> bool
        if evt.type == pygame.KEYUP:
            return True
        elif evt.type == pygame.JOYBUTTONUP:
            if evt.button == button_keys['circle']:
                return True

    def check_input(self):
        self.keys = pygame.key.get_pressed()
        for e in pygame.event.get():
            if self.should_exit(e):
                sys.exit()
            if (e.type == pygame.KEYDOWN and e.key == pygame.K_SPACE) or (e.type == pygame.JOYBUTTONDOWN and e.button == button_keys['x']):
                if len(self.bullets) <= 15 and self.shipAlive:
                    if self.score < 1000:
                        bullet = Bullet(self.player.rect.x + 22,
                                        self.player.rect.y + 5, -1,
                                        15, 'laser', 'center')
                        self.bullets.add(bullet)
                        self.allSprites.add(self.bullets)
                        self.sounds['shoot'].play()
                    else:
                        leftbullet = Bullet(self.player.rect.x + 8,
                                            self.player.rect.y + 5, -1,
                                            15, 'laser', 'left')
                        rightbullet = Bullet(self.player.rect.x + 38,
                                             self.player.rect.y + 5, -1,
                                             15, 'laser', 'right')
                        self.bullets.add(leftbullet)
                        self.bullets.add(rightbullet)
                        self.allSprites.add(self.bullets)
                        self.sounds['shoot2'].play()
            else:
                if e.type == pygame.JOYBUTTONDOWN:
                    for btnKey in button_keys.keys():
                        if e.button == button_keys[btnKey]:
                            self.buttons[btnKey] = True
            if e.type == pygame.JOYAXISMOTION:
                if e.axis == 0 and int(e.value) == 1:
                    self.buttons['left_arrow'] = True
                if e.axis == 0 and int(e.value) == -1:
                    self.buttons['right_arrow'] = True
                if e.axis == 0 and int(e.value) == 0:
                    self.buttons['left_arrow'] = False
                    self.buttons['right_arrow'] = False
            if e.type == pygame.JOYBUTTONUP:
                if e.button == button_keys['x']:
                    1 + 1
                    #do nothing
                else:
                    for btnKey in button_keys.keys():
                        if e.button == button_keys[btnKey]:
                            self.buttons[btnKey] = False

    def make_enemies(self):
        enemies = EnemiesGroup(10, 5)
        for row in range(5):
            for column in range(10):
                enemy = Enemy(row, column)
                enemy.rect.x = int(width*0.1) + (column * 80)
                enemy.rect.y = self.enemyPosition + (row * 45)
                enemies.add(enemy)

        self.enemies = enemies

    def make_enemies_shoot(self):
        if (pygame.time.get_ticks() - self.timer) > 500 and self.enemies:
            enemy = self.enemies.random_bottom()
            self.enemyBullets.add(
                Bullet(enemy.rect.x + 14, enemy.rect.y + 20, 1, 5,
                       'enemylaser', 'center'))
            self.allSprites.add(self.enemyBullets)
            self.timer = pygame.time.get_ticks()

    def calculate_score(self, row):
        scores = {0: 30,
                  1: 20,
                  2: 20,
                  3: 10,
                  4: 10,
                  5: choice([50, 100, 150, 300])
                  }

        score = scores[row]
        self.score += score
        return score

    def create_main_menu(self):
        enem = int(40*(height/800))
        self.enemy1 = IMAGES['enemy3_1']
        self.enemy1 = pygame.transform.scale(self.enemy1, (enem, enem))
        self.enemy2 = IMAGES['enemy2_2']
        self.enemy2 = pygame.transform.scale(self.enemy2, (enem, enem))
        self.enemy3 = IMAGES['enemy1_2']
        self.enemy3 = pygame.transform.scale(self.enemy3, (enem, enem))
        self.enemy4 = IMAGES['mystery']
        self.enemy4 = pygame.transform.scale(self.enemy4, (2*enem, enem))
        self.screen.blit(self.enemy1, (int(width*0.44), int(height*0.6)))
        self.screen.blit(self.enemy2, (int(width*0.44), int(height*0.66)))
        self.screen.blit(self.enemy3, (int(width*0.44), int(height*0.72)))
        self.screen.blit(self.enemy4, (int(width*0.425), int(height*0.78)))
        self.startText = Text(FONT, int(height*0.03), "Press X to start the game", WHITE, 375, int(height*0.54))
        self.startText.center()
        self.startText.draw(self.screen)

    def check_collisions(self):
        pygame.sprite.groupcollide(self.bullets, self.enemyBullets, True, True)

        for enemy in pygame.sprite.groupcollide(self.enemies, self.bullets,
                                         True, True).keys():
            self.sounds['invaderkilled'].play()
            self.calculate_score(enemy.row)
            EnemyExplosion(enemy, self.explosionsGroup)
            self.gameTimer = pygame.time.get_ticks()

        for mystery in pygame.sprite.groupcollide(self.mysteryGroup, self.bullets,
                                           True, True).keys():
            mystery.mysteryEntered.stop()
            self.sounds['mysterykilled'].play()
            score = self.calculate_score(mystery.row)
            MysteryExplosion(mystery, score, self.explosionsGroup)
            newShip = Mystery()
            self.allSprites.add(newShip)
            self.mysteryGroup.add(newShip)

        for player in pygame.sprite.groupcollide(self.playerGroup, self.enemyBullets,
                                          True, True).keys():
            if self.life3.alive():
                self.life3.kill()
            elif self.life2.alive():
                self.life2.kill()
            elif self.life1.alive():
                self.life1.kill()
            else:
                self.gameOver = True
                self.startGame = False
            self.sounds['shipexplosion'].play()
            ShipExplosion(player, self.explosionsGroup)
            self.makeNewShip = True
            self.shipTimer = pygame.time.get_ticks()
            self.shipAlive = False

        if self.enemies.bottom >= int(height*0.8):
            pygame.sprite.groupcollide(self.enemies, self.playerGroup, True, True)
            if not self.player.alive() or self.enemies.bottom >= int(height*0.9):
                self.gameOver = True
                self.startGame = False

        pygame.sprite.groupcollide(self.bullets, self.allBlockers, True, True)
        pygame.sprite.groupcollide(self.enemyBullets, self.allBlockers, True, True)
        if self.enemies.bottom >= BLOCKERS_POSITION:
            pygame.sprite.groupcollide(self.enemies, self.allBlockers, False, True)

    def create_new_ship(self, createShip, currentTime):
        if createShip and (currentTime - self.shipTimer > 900):
            self.player = Ship()
            self.allSprites.add(self.player)
            self.playerGroup.add(self.player)
            self.makeNewShip = False
            self.shipAlive = True

    def create_game_over(self, currentTime):
        global ROUND
        global HighScore
        ROUND = 0
        self.screen.blit(self.background, (0, 0))
        passed = currentTime - self.timer
        if passed < 750:
            self.gameOverText.draw(self.screen)
        elif 750 < passed < 1500:
            self.screen.blit(self.background, (0, 0))
        elif 1500 < passed < 2250:
            self.gameOverText.draw(self.screen)
        elif 2250 < passed < 2750:
            self.screen.blit(self.background, (0, 0))
        elif 3000 < passed < 6750:
            self.gameOverText.draw(self.screen)
            self.finalScoreText2 = Text(FONT, 50, str(self.score), YELLOW, 450, 10)
            self.finalScoreText.draw(self.screen)
            self.finalScoreText2.draw(self.screen)
        elif passed > 7000:
            self.finalScoreText.draw(self.screen)
            self.finalScoreText2.draw(self.screen)
            if self.score > HighScore:
                HighScore = self.score
                self.finalScoreText2 = Text(FONT, 50, "New High Score :" + str(self.score), PURPLE, 450, 10)
                self.finalScoreText2.draw(self.screen)

            self.goBackText = Text(FONT, 50, "Press circle to reset the game", WHITE, 100, 450)
            self.goBackText.draw(self.screen)

        # with open(os.path.join("leaderboard.json"), 'r+') as file:
        #     leaderboard = json.load(file)

        # input = NameInput(self.screen)
        for e in pygame.event.get():
            if self.should_exit(e):
                sys.exit()
            elif self.should_reset(e) and passed > 7000:
                self.mainScreen = True
            # elif e.type == pygame.JOYBUTTONUP:
            #     input.handle_input(e.button)

    def main(self):
        global ROUND
        global HighScore
        HighScore = 0
        while True:
            if self.mainScreen:
                self.screen.blit(self.background, (0, 0))
                self.titleText.draw(self.screen)
                self.titleText2.draw(self.screen)
                self.titleText3.draw(self.screen)
                self.enemy1Text.draw(self.screen)
                self.enemy2Text.draw(self.screen)
                self.enemy3Text.draw(self.screen)
                self.enemy4Text.draw(self.screen)
                self.create_main_menu()

                for e in pygame.event.get():
                    if self.should_exit(e):
                        sys.exit()
                    if e.type == pygame.KEYUP or e.type == pygame.JOYBUTTONUP:
                        # Only create blockers on a new game, not a new round
                        self.allBlockers = pygame.sprite.Group(self.make_blockers(0),
                                                        self.make_blockers(1),
                                                        self.make_blockers(2),
                                                        self.make_blockers(3))
                        self.livesGroup.add(self.life1, self.life2, self.life3)
                        self.reset(0)
                        self.startGame = True
                        self.mainScreen = False
            elif self.startGame:
                if not self.enemies and not self.explosionsGroup:
                    currentTime = pygame.time.get_ticks()
                    if currentTime - self.gameTimer < 3000:
                        self.screen.blit(self.background, (0, 0))
                        self.scoreText2 = Text(FONT, int(height*0.03), str(self.score), YELLOW, int(width*0.25), int(height*0.05))
                        self.scoreText.draw(self.screen)
                        self.scoreText2.draw(self.screen)
                        self.nextRoundText.draw(self.screen)
                        self.livesText.draw(self.screen)
                        self.livesGroup.update()
                        self.check_input()
                    if currentTime - self.gameTimer > 3000:
                        # Move enemies closer to bottom
                        self.enemyPosition += ENEMY_MOVE_DOWN
                        self.reset(self.score)
                        self.gameTimer += 3000
                else:
                    currentTime = pygame.time.get_ticks()
                    self.play_main_music(currentTime)
                    self.screen.blit(self.background, (0, 0))
                    self.allBlockers.update(self.screen)
                    self.scoreText2 = Text(FONT, int(height*0.03), str(self.score), YELLOW, int(width*0.25), int(height*0.05))
                    self.scoreText.draw(self.screen)
                    self.scoreText2.draw(self.screen)
                    self.livesText.draw(self.screen)
                    self.check_input()
                    self.enemies.update(currentTime)
                    self.allSprites.update(self.keys, self.buttons, currentTime)
                    self.explosionsGroup.update(currentTime)
                    self.check_collisions()
                    self.create_new_ship(self.makeNewShip, currentTime)
                    self.make_enemies_shoot()
            elif self.gameOver:
                currentTime = pygame.time.get_ticks()
                # Reset enemy starting position
                self.enemyPosition = ENEMY_DEFAULT_POSITION
                self.create_game_over(currentTime)

            pygame.display.update()
            self.clock.tick(60)


if __name__ == '__main__':
    HighScore = 0
    game = SpaceInvaders()
    game.main()
