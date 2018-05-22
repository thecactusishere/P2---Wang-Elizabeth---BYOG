import pygame
import sys
import os
import time
import random

#Parameters
win_w = 60 * 16
win_h = 50 * 16

ship_w = 15
ship_h = 15

fps = 60
#Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
DARKGREEN = (0, 100, 0)
PINK = (250, 128, 14)
SAND = (244,164,96)
BROWN = (165,42,42)
YELLOW = (204,204,0)
LEMON = (255, 244, 79)


class TextRectException:
    def __init__(self, message=None):
        self.message = message

    def __str__(self):
        return self.message


def render_textrect(string, font, rect, text_color, background_color, justification=0):
    """Returns a surface containing the passed text string, reformatted
    to fit within the given rect, word-wrapping as necessary. The text
    will be anti-aliased.

    Takes the following arguments:

    string - the text you wish to render. \n begins a new line.
    font - a Font object
    rect - a rectstyle giving the size of the surface requested.
    text_color - a three-byte tuple of the rgb value of the
                 text color. ex (0, 0, 0) = BLACK
    background_color - a three-byte tuple of the rgb value of the surface.
    justification - 0 (default) left-justified
                    1 horizontally centered
                    2 right-justified

    Returns the following values:

    Success - a surface object with the text rendered onto it.
    Failure - raises a TextRectException if the text won't fit onto the surface.
    """

    import pygame

    final_lines = []

    requested_lines = string.splitlines()

    # Create a series of lines that will fit on the provided
    # rectangle.

    for requested_line in requested_lines:
        if font.size(requested_line)[0] > rect.width:
            words = requested_line.split(' ')
            # if any of our words are too long to fit, return.
            for word in words:
                if font.size(word)[0] >= rect.width:
                    raise TextRectException, "The word " + word + " is too long to fit in the rect passed."
            # Start a new line
            accumulated_line = ""
            for word in words:
                test_line = accumulated_line + word + " "
                # Build the line while the words fit.
                if font.size(test_line)[0] < rect.width:
                    accumulated_line = test_line
                else:
                    final_lines.append(accumulated_line)
                    accumulated_line = word + " "
            final_lines.append(accumulated_line)
        else:
            final_lines.append(requested_line)

            # Let's try to write the text out on the surface.

    surface = pygame.Surface(rect.size)
    surface.fill(background_color)

    accumulated_height = 0
    for line in final_lines:
        if accumulated_height + font.size(line)[1] >= rect.height:
            raise TextRectException, "Once word-wrapped, the text string was too tall to fit in the rect."
        if line != "":
            tempsurface = font.render(line, 1, text_color)
            if justification == 0:
                surface.blit(tempsurface, (0, accumulated_height))
            elif justification == 1:
                surface.blit(tempsurface, ((rect.width - tempsurface.get_width()) / 2, accumulated_height))
            elif justification == 2:
                surface.blit(tempsurface, (rect.width - tempsurface.get_width(), accumulated_height))
            else:
                raise TextRectException, "Invalid justification argument: " + str(justification)
        accumulated_height += font.size(line)[1]

    return surface


class Text:
    def __init__(self, size, text, color, xcor, ycor):
        self.font = pygame.font.SysFont("Times New Roman", size)
        self.image = self.font.render(text, 1, color)
        self.rect = self.image.get_rect()
        self.rect.centerx = xcor
        self.rect.centery = ycor


class Platform(pygame.sprite.Sprite):

    def __init__(self, xpos, ypos, col):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((16,16))
        self.image.convert()
        self.rect = pygame.Rect(xpos, ypos, 16, 16)
        self.set_color(col)
        self.type = col
    def set_color(self, col):
        if col == "A":
            self.image.fill(RED)
        elif col == "S":
            self.image.fill(BLUE)
        elif col == "D":
            self.image.fill(PINK)
        elif col == "B":
            self.image.fill(GREEN)
        elif col == "W":
            self.image.fill(DARKGREEN)
        elif col == "G":
            self.image.fill(SAND)
        elif col == "H":
            self.image.fill(BROWN)
        elif col == " ":
            self.image.fill(WHITE)


class Bullet(pygame.sprite.Sprite):
    def __init__(self, speed, xpos, ypos, energy, type):
        pygame.sprite.Sprite.__init__(self)
        self.height = self.width = 10
        self.speed = self.setspeed(speed)
        self.image = pygame.Surface((self.width, self.height)).convert()
        self.rect = self.image.get_rect()
        self.rect.x = xpos
        self.rect.centery = ypos
        self.image.fill(WHITE)
        self.energy = energy
        self.type = type

    def setspeed(self, counter):
        if counter < 450:
            return 10
        elif 450 <= counter < 900:
            return 15
        elif 900 <= counter < 45*30:
            return 20
        elif 45 * 30 <= counter< 60 * 30:
            return 35
        elif 1800 <= counter:
            return 50

    def update(self):
        if self.type == "L":
            self.rect.x -= self.speed
            if self.rect.x < 0:
                self.kill()
        if self.type == "R":
            self.rect.x += self.speed
            if self.rect.x > win_w:
                self.kill()
        if self.type == "T":
            self.rect.y -= self.speed
            if self.rect.x < 0:
                self.kill()
        if self.type == "B":
            self.rect.y += self.speed
            if self.rect.y > win_h:
                self.kill()


class Enemy(pygame.sprite.Sprite):
    def __init__(self, life, type, xpos, ypos, color):
        pygame.sprite.Sprite.__init__(self)
        self.energy = life
        if type == "normal":
            self.height = ship_h
            self.width = ship_w
            self.image = pygame.Surface((self.width, self.height)).convert()
            self.rect = self.image.get_rect()
            self.rect.centerx = xpos
            self.rect.centery = ypos
            self.speed = 5

        elif type == "Boss":
            self.height = 50
            self.width = 60
            self.image = pygame.Surface((self.width, self.height)).convert()
            self.rect = self.image.get_rect()
            self.image.fill(color)
            self.rect.centerx = xpos
            self.rect.centery = ypos
            self.speed = [0, 15]
            self.lifescore = Text(20, str(self.energy), BLACK, self.rect.centerx, self.rect.centery)

    def update(self, hero, bullet_group, game):
        if game.defense:
            if game.loop_counter % 60 == 0:
                bl = Bullet(10, self.rect.left, self.rect.centery, 10, "L")
                bt = Bullet(10, self.rect.centerx, self.rect.top, 10, "T")
                bb = Bullet(10, self.rect.centerx, self.rect.bottom, 10, "B")
                br = Bullet(10, self.rect.right, self.rect.centery, 10, "R")
                bullet_group.add(bl, bt, bb, br)
        if game.scenetop:
            if self.rect.bottom >= win_h or self.rect.top <= 0:
                self.speed = (self.speed[0], -self.speed[1])
            if game.loop_counter % 30 == 0:
                br = Bullet(10, self.rect.right, self.rect.centery, 1, "R")
                bullet_group.add(br)

            self.rect = self.rect.move(self.speed)



        bullet_group.update()

    def gethit(self, hero, game):
        ouch = pygame.sprite.spritecollide(self, hero, False)
        for b in ouch:
            self.energy -= b.strength // 2
            self.lifescore.image = self.lifescore.font.render(str(self.energy), 1, BLACK)

            return self.energy


class Hero(pygame.sprite.Sprite):
    def __init__(self, container):
        pygame.sprite.Sprite.__init__(self)
        self.life = 100
        self.strength = 1
        self.agility = 1
        self.defense = 1
        self.container = container
        self.height = ship_h
        self.width = ship_w
        self.side_speed = self.top_speed = 6
        self.image = pygame.Surface((self.width, self.height)).convert()
        self.rect = self.image.get_rect()
        self.rect.centerx = container.width/2
        self.rect.centery = container.height/2
        self.image.fill(BLACK)
        self.death = False
        self.trainlife = 5
        self.lifescore = Text(20, "Health:" + str(self.life), BLACK, 2 * win_w/7, container.bottom - 20)
        self.agilityscore = Text(20, "Agility:" + str(self.agility), BLACK, 3 * win_w/7, container.bottom - 20)
        self.strengthscore = Text(20, "Strength:" + str(self.strength), BLACK, 4 * win_w/7, container.bottom - 20)
        self.defensescore = Text(20, "Defense:" + str(self.defense), BLACK, 5 * win_w/7, container.bottom - 20)
        self.trainscore = Text(30, "Lives:" + str(self.trainlife), BLACK, 200, container.bottom - 20)

    def move(self):
        key = pygame.key.get_pressed()
        if key[pygame.K_RIGHT]:
            self.rect.x += self.side_speed
        if key[pygame.K_LEFT]:
            self.rect.x -= self.side_speed
        if key[pygame.K_UP]:
            self.rect.y -= self.top_speed
        if key[pygame.K_DOWN]:
            self.rect.y += self.top_speed

    def checkdeath(self):
        if self.life <= 0:
            self.death = True
        if self.death:
            pass

    def read(self, scroll_group, scroll, game):
        collisions = pygame.sprite.spritecollide(self, scroll_group, True)
        for b in collisions:
            scroll.checkread(game)

    def changescene(self, map_group, scroll_group, game):
        if game.scene1:
            collisions = pygame.sprite.spritecollide(self, map_group, False)
            for p in collisions:
                if p.type == "A":
                    game.scene1 = False
                    game.agility = True
                    map_group.empty()
                    scroll_group.empty()
                    game.build(game.agilityscene, map_group)
                    scroll_group.add(game.agilityscroll)
                    self.centerx = win_w / 4 - 5
                    self.centery = win_h / 2
                    game.loop_counter = 0
                    self.trainlife = 5
                elif p.type == "S":
                    game.scene1 = False
                    game.strength = True
                    map_group.empty()
                    scroll_group.empty()
                    scroll_group.add(game.strengthscroll)
                    game.build(game.strengthscene, map_group)
                    self.trainlife = 0
                    game.loop_counter = 0
                elif p.type == "D":
                    game.scene1 = False
                    game.defense = True
                    map_group.empty()
                    scroll_group.empty()
                    scroll_group.add(game.defensescroll)
                    game.build(game.defensescene, map_group)
                    game.loop_counter = 0
                    self.trainlife = 5
                elif p.type == " " and self.rect.top <= 0:
                    game.scene1 = False
                    game.scenetop = True
                    map_group.empty()
                    scroll_group.empty()
                    scroll_group.add(game.scenetopscroll)
                    game.build(game.screentop, map_group)
                    self.rect.y = win_h - 100
                    game.loop_counter = 0
        if game.scenetop:
            collisions = pygame.sprite.spritecollide(self, map_group, False)
            for p in collisions:
                if p.type == "G" and self.rect.bottom >= win_h - 10:
                    game.scenetop = False
                    game.scene1 = True
                    map_group.empty()
                    scroll_group.empty()
                    scroll_group.add(game.introscroll)
                    game.build(game.screen1, map_group)
                    game.loop_counter = 0
                    self.rect.y = 100

    def update(self, scroll_group, scroll, map_group, game):
        self.move()
        self.read(scroll_group, scroll, game)
        self.changescene(map_group, scroll_group, game)
        self.checkdeath()
        self.rect.clamp_ip(self.container)

    def traincheckhit(self, bullet_group):
        collisions = pygame.sprite.spritecollide(self, bullet_group, True)
        for b in collisions:
            self.trainlife -= b.energy
            self.trainscore.image = self.trainscore.font.render("Lives: " + str(self.trainlife), 1, BLACK)

    def trainsmash(self, bullet_group):
        collisions = pygame.sprite.spritecollide(self, bullet_group, False)
        for b in collisions:
            b.energy -= 1
            self.trainlife += 1
            if b.rect.left < self.rect.left <= b.rect.right:
                self.rect.x += 10
            elif b.rect.top < self.rect.bottom <= b.rect.bottom:
                self.rect.y -= 10
            elif  b.rect.bottom > self.rect.top >= b.rect.top:
                self.rect.y += 10
            elif b.rect.right > self.rect.right >= b.rect.left:
                self.rect.x -= 10
            self.trainscore.image = self.trainscore.font.render("Score: " + str(self.trainlife), 1, BLACK)
            if b.energy <= 0:
                b.kill()
            return self.trainlife

    def attack(self, bullet_group, enemy_group, game):
        ouch = pygame.sprite.spritecollide(self, bullet_group, True)
        for b in ouch:
            self.life -= b.energy
            self.lifescore.image = self.lifescore.font.render("Health: " + str(self.life), 1, BLACK)

        bang = pygame.sprite.spritecollide(self, enemy_group, False)
        for b in bang:
            b.energy -= 1
            if self.rect.top > b.rect.top and self.rect.bottom < b.rect.bottom and b.rect.left < self.rect.left <= b.rect.right:
                self.rect.x += 10
            elif self.rect.right < b.rect.right and self.rect.left > b.rect.left and 256 < self.rect.bottom <= b.rect.bottom:
                self.rect.y -= 10
                #print(str(self.rect.bottom))
                #print("Boss's Y: " + str(b.rect.top))
            elif self.rect.right < b.rect.right and self.rect.left > b.rect.left and b.rect.bottom > self.rect.top >= b.rect.top:
                self.rect.y += 10
            elif self.rect.top > b.rect.top and self.rect.bottom < b.rect.bottom and b.rect.right > self.rect.right >= b.rect.left:
                self.rect.x -= 10
            b.lifescore.image = b.lifescore.font.render(str(b.lifescore), 1, BLACK)
            if b.energy <= 0:
                b.kill()
            return b.energy



class Scroll(pygame.sprite.Sprite):
    def __init__(self, xpos, ypos, text):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((10, 10))
        self.image.convert()
        self.image.fill(YELLOW)
        self.rect = pygame.Rect(xpos, ypos, 10, 10)
        self.readrect = pygame.Rect (0, 0, win_w - 20, win_h - 20)
        self.text = render_textrect(text, pygame.font.Font(None, 22), self.readrect, BLACK, YELLOW, 1)
        self.mouseclick = Text(22, "Click to Continue", BLACK, win_w - 64, win_h - 20)

    def checkread(self, game):
        game.screen.fill(YELLOW)
        game.screen.blit(self.text, self.readrect)
        pygame.display.flip()
        time.sleep(1)


class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Journey of a Hero")
        self.screen = pygame.display.set_mode((win_w, win_h))
        self.clock = pygame.time.Clock()
        self.loop_counter = 0
        self.intro = self.play = self.outro = True
        self.scene1 = True
        self.agility = self.strength = self.defense = self.shop = self.scenetop = False
        # Create Scrolls
        self.introscroll = Scroll(win_w / 2, win_h / 2 - 80,
                             "There was once a land of magic, where all the mythical creatures lived. "
                             "\n Of all the creatures, the dragons were the most powerful. "
                             "\n They have the ablility to control the elements of the works, "
                             "and as such they became the rulers of the land."
                             "\n For many years, the dragons ruled in peace and harmony, "
                             "and the creatures were blessed. "
                             "\n Then, a cruel demon came to the world, and slaugthered the dragons, "
                             "hoping to control the land himself. "
                             "\n As the dragons lay dying, they each crafted a single gemstone from their blood,"
                             "and threw them to the wind, scattering them all around the world. "
                             "\n However, since the deaths of the dragons, "
                             "there was none to harness the power of the elements, "
                             "and the whole land was thrown into chaos."
                             "\n To restore harmony to this land, "
                             "you must gather the 8 lost Gemstones of the Elemental Dragons, and defeat the demon!")

        self.agilityscroll = Scroll(win_w / 4, 80,
                               "Here is where you can increase your agility. "
                               "\n Dodge the incoming bullets!")

        self.strengthscroll = Scroll(3 * win_w / 4, 80,
                                "Here is where you can increase your strength. "
                                "\n The boxes have differing density, "
                                "\n Smash the boxes!")

        self.defensescroll = Scroll(win_w / 4, win_h - 80, "Here is where you can increase your defense. "
                                                           "\n Hit the boss!")

        self.scenetopscroll = Scroll(win_w/2, win_h - 20, "This is the Ruby dragon, the weakest of them all. \n Beat him to get the ruby dragon!")

    def blink(self, image, rect):
        if pygame.time.get_ticks() % 1000 < 500:
            self.screen.blit(image, rect)

    def build(self, level, group):
        x = y = 0
        for row in level:
            for col in row:
                p = Platform(x, y, col)
                group.add(p)
                x += 16
            y += 16
            x = 0


class Camera():
    def __init__(self):
        self.x_offset = 0
        self.y_offset = 0

    def apply(self, obj):
        return pygame.Rect(obj.rect.x + self.x_offset, obj.rect.y + self.y_offset, obj.rect.width, obj.rect.height)

    def update(self, ship):
        self.x_offset = -ship.rect.x + win_w / 2
        self.y_offset = -ship.rect.y + win_h / 2
        if self.x_offset <= -(ship.container.width - win_w):
            self.x_offset = -(ship.container.width - win_w)
        if self.x_offset >= 0:
            self.x_offset = 0
        if self.y_offset <= -(ship.container.height - win_h):
            self.y_offset = -(ship.container.height - win_h)
        if self.y_offset >= 0:
            self.y_offset = 0


def main():

    # Initialize variables

    game = Game()

    camera = Camera()

    scroll_group = pygame.sprite.Group()

    bullet_group = pygame.sprite.Group()

    enemy_group = pygame.sprite.Group()

    # Load maps
    game.screen1 = [
        "AAAAAAAAAAAAAAAAAAAA                    SSSSSSSSSSSSSSSSSSSS",
        "AAAAAAAAAAAAAAAAAAAA                    SSSSSSSSSSSSSSSSSSSS",
        "AAAAAAAAAAAAAAAAAAAA                    SSSSSSSSSSSSSSSSSSSS",
        "AAAAAAAAAAAAAAAAAAAA                    SSSSSSSSSSSSSSSSSSSS",
        "AAAAAAAAAAAAAAAAAAAA                    SSSSSSSSSSSSSSSSSSSS",
        "WWWWWWWWWWWWWWWWWWWW                    WWWWWWWWWWWWWWWWWWWW",
        "WWWWWWWWWWWWWWWWWWWW                    WWWWWWWWWWWWWWWWWWWW",
        "WWWWWWWWWWWWWWWWWWWW                    WWWWWWWWWWWWWWWWWWWW",
        "WWWWWWWWWWWWWWWWWWWW                    WWWWWWWWWWWWWWWWWWWW",
        "WWWWWWWWWWWWWWWWWWWW                    WWWWWWWWWWWWWWWWWWWW",
        "WWWWWWWWWWWWWWWWWWWW                    WWWWWWWWWWWWWWWWWWWW",
        "WWWWWWWWWWWWWWWWWWWW                    WWWWWWWWWWWWWWWWWWWW",
        "WWWWWWWWWWWWWWWWWWWW                    WWWWWWWWWWWWWWWWWWWW",
        "WWWWWWWWWWWWWWWWWWWW                    WWWWWWWWWWWWWWWWWWWW",
        "WWWWWWWWWWWWWWWWWWWW                    WWWWWWWWWWWWWWWWWWWW",
        "WWWWWWWWWWWWWWWWWWWW                    WWWWWWWWWWWWWWWWWWWW",
        "WWWWWWWWWWWWWWWWWWWW                    WWWWWWWWWWWWWWWWWWWW",
        "                                                            ",
        "                                                            ",
        "                                                            ",
        "                                                            ",
        "                                                            ",
        "                         HHHHHHHHHH                         ",
        "                        HHHHHHHHHHHH                        ",
        "                        HHHHHHHHHHHH                        ",
        "                        HHHHHHHHHHHH                        ",
        "                                                            ",
        "                                                            ",
        "                                                            ",
        "                                                            ",
        "                                                            ",
        "                                                            ",
        "GGGGGGGGGGGGGGGGGGGG                    GGGGGGGGGGGGGGGGGGGG",
        "GGGGGGGGGGGGGGGGGGGG                    GGGGGGGGGGGGGGGGGGGG",
        "GGGGGGGGGGGGGGGGGGGG                    GGGGGGGGGGGGGGGGGGGG",
        "GGGGGGGGGGGGGGGGGGGG                    GGGGGGGGGGGGGGGGGGGG",
        "GGGGGGGGGGGGGGGGGGGG                    GGGGGGGGGGGGGGGGGGGG",
        "GGGGGGGGGGGGGGGGGGGG                    GGGGGGGGGGGGGGGGGGGG",
        "GGGGGGGGGGGGGGGGGGGG                    GGGGGGGGGGGGGGGGGGGG",
        "GGGGGGGGGGGGGGGGGGGG                    GGGGGGGGGGGGGGGGGGGG",
        "GGGGGGGGGGGGGGGGGGGG                    GGGGGGGGGGGGGGGGGGGG",
        "GGGGGGGGGGGGGGGGGGGG                    GGGGGGGGGGGGGGGGGGGG",
        "GGGGGGGGGGGGGGGGGGGG                    GGGGGGGGGGGGGGGGGGGG",
        "GGGGGGGGGGGGGGGGGGGG                    GGGGGGGGGGGGGGGGGGGG",
        "GGGGGGGGGGGGGGGGGGGG                    GGGGGGGGGGGGGGGGGGGG",
        "DDDDDDDDDDDDDDDDDDDD                    BBBBBBBBBBBBBBBBBBBB",
        "DDDDDDDDDDDDDDDDDDDD                    BBBBBBBBBBBBBBBBBBBB",
        "DDDDDDDDDDDDDDDDDDDD                    BBBBBBBBBBBBBBBBBBBB",
        "DDDDDDDDDDDDDDDDDDDD                    BBBBBBBBBBBBBBBBBBBB",
        "DDDDDDDDDDDDDDDDDDDD                    BBBBBBBBBBBBBBBBBBBB", ]

    game.agilityscene = [
        "GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGHGGGGGGGGGGGGGG",
        "GGGGGGGGGGGGGGHGGGGGGGGGGGGGGGGGGHGGGGGGGGGGGGGGGGGGGHGGGGGG",
        "GGHGGGGGGGGGGGGGGGGGGGGGGGGGGHGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG",
        "GGGGGGGGGGGGGGHGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG",
        "GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGHGGGGGGGGGGGGGGGGGGGGGHGGGGGGG",
        "GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG",
        "GGGGGGGGHGGGGGGGGGGHGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG",
        "GGGGGGGGGGGGGGGGGGGGGHGGGGGGGGGGGGGGGGGGGGGGGGGGHGGGGGGGHGGG",
        "GGGGGGGGGGGGGHGGGGGGGGGGGGGGGGGGGHGGGGGGGGHGGGGGGGGGGGGGGGGG",
        "GGGGHGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGHGGGG",
        "WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW",
        "WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWBWWWWWW",
        "WWWWWWWWWWBWWWWWWWWWWWWWWWWWWWWWWBWWWWWWWWWWWWWWWWWWWWWWWWWW",
        "WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW",
        "WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW",
        "WWWWWWWWWWWWWWWWWWWWWBWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWBWW",
        "WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW",
        "WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW",
        "WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWBWWWWWWWWWWWWWWWWWWWWWW",
        "WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW",
        "WWWWWWWWWWWWWWWWWWWWWWWWWWWBWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW",
        "WWWWWWWWWWWWWWWBWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW",
        "WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW",
        "WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWBWWWWWWWWWW",
        "WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW",
        "WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW",
        "WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW",
        "WWWWWWWWWWWWBWWWWWWWWWWWWWWWWBWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW",
        "WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW",
        "WWWWWWWWWWWWWWWWWBWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWBWWWWWW",
        "WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW",
        "WWWWWWBWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW",
        "WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW",
        "WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWBWWWWWWWWWWWWWWWWWWWW",
        "WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW",
        "WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW",
        "WWWWWWWWBWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW",
        "WWWWWWWWWWWWWWWWWWWWWWWWWWWWWBWWWWWWWWWWWWWWWWWWBWWWWWWWWWWW",
        "WWWWWWWWWWWWWWWWWWWWWBWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW",
        "WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW",
        "GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGHGGGGGGGGGGGGGG",
        "GGGGGGGGGGGGGGHGGGGGGGGGGGGGGGGGGHGGGGGGGGGGGGGGGGGGGHGGGGGG",
        "GGHGGGGGGGGGGGGGGGGGGGGGGGGGGHGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG",
        "GGGGGGGGGGGGGGHGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG",
        "GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGHGGGGGGGGGGGGGGGGGGGGGHGGGGGGG",
        "GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG",
        "GGGGGGGGHGGGGGGGGGGHGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG",
        "GGGGGGGGGGGGGGGGGGGGGHGGGGGGGGGGGGGGGGGGGGGGGGGGHGGGGGGGHGGG",
        "GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGHGGGGGGGGHGGGGGGGGGGGGGGGGG",
        "GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGHGGGG",
    ]

    game.strengthscene = [
        "BBBBBBBBBBBBBBBBWBBBBBBBBBBBBBBBBBWBBBBBBBBBBBBBBBBBBBBBBBBB",
        "BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB",
        "BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBWBBBBBBBBBBBBB",
        "BBBBBBBWBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB",
        "BBBBBBBBBBBBBBBBBBBBBBBBBBBBWBBBBBBBBBBBBBBBBBBBBBBWBBBBBBBB",
        "BBBBBBBBBBWBBBBBBBBBBBBBBBBBBBBBBBBBBWBBBBBBBBBBBBBBBBBBBBBB",
        "BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB",
        "BBBBBBBWBBBBBBBBBBBBBBBBBBBWBBBBBBBBBBBBBBBBBBBWBBBBBBBBBBBB",
        "BBBBBBBBBBBBBBBWBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB",
        "BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBWBBBB",
        "GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG",
        "GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG",
        "GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG",
        "GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG",
        "GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG",
        "GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG",
        "GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG",
        "GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG",
        "GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG",
        "GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG",
        "GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG",
        "GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG",
        "GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG",
        "GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG",
        "GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG",
        "GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG",
        "GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG",
        "GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG",
        "GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG",
        "GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG",
        "GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG",
        "GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG",
        "GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG",
        "GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG",
        "GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG",
        "GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG",
        "GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG",
        "GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG",
        "GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG",
        "GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG",
        "BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB",
        "BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB",
        "BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB",
        "BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB",
        "BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB",
        "BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB",
        "BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB",
        "BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB",
        "BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB",
        "BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB",
    ]

    game.defensescene = [
        "SSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSS",
        "SSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSS",
        "SSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSS",
        "SSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSS",
        "SSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSS",
        "SSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSS",
        "SSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSS",
        "SSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSS",
        "SSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSS",
        "SSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSS",
        "GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG",
        "GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG",
        "GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG",
        "GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG",
        "GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG",
        "GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG",
        "GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG",
        "GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG",
        "GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG",
        "GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG",
        "GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG",
        "GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG",
        "GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG",
        "GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG",
        "GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG",
        "GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG",
        "GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG",
        "GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG",
        "GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG",
        "GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG",
        "GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG",
        "GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG",
        "GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG",
        "GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG",
        "GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG",
        "GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG",
        "GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG",
        "GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG",
        "GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG",
        "GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG",
        "HHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHH",
        "HHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHH",
        "HHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHH",
        "HHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHH",
        "HHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHH",
        "HHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHH",
        "HHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHH",
        "HHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHH",
        "HHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHH",
        "HHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHH",
    ]

    game.screentop = [
        "WWWWWWWWWWWWWWWWWWWWGGGGGGGGGGGGGGGGGGGGWWWWWWWWWWWWWWWWWWWW",
        "WWWWWWWWWWWWWWWWWWWWGGGGGGGGGGGGGGGGGGGGWWWWWWWWWWWWWWWWWWWW",
        "WWWWWWWWWWWWWWWWWWWWGGGGGGGGGGGGGGGGGGGGWWWWWWWWWWWWWWWWWWWW",
        "WWWWWWWWWWWWWWWWWWWWGGGGGGGGGGGGGGGGGGGGWWWWWWWWWWWWWWWWWWWW",
        "WWWWWWWWWWWWWWWWWWWWGGGGGGGGGGGGGGGGGGGGWWWWWWWWWWWWWWWWWWWW",
        "WWWWWWWWWWWWWWWWWWWWGGGGGGGGGGGGGGGGGGGGWWWWWWWWWWWWWWWWWWWW",
        "WWWWWWWWWWWWWWWWWWWWGGGGGGGGGGGGGGGGGGGGWWWWWWWWWWWWWWWWWWWW",
        "WWWWWWWWWWWWWWWWWWWWGGGGGGGGGGGGGGGGGGGGWWWWWWWWWWWWWWWWWWWW",
        "WWWWWWWWWWWWWWWWWWWWGGGGGGGGGGGGGGGGGGGGWWWWWWWWWWWWWWWWWWWW",
        "WWWWWWWWWWWWWWWWWWWWGGGGGGGGGGGGGGGGGGGGWWWWWWWWWWWWWWWWWWWW",
        "WWWWWWGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGWWWWW",
        "WWWWWWGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGWWWWW",
        "WWWWWWGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGWWWWW",
        "WWWWWWGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGWWWWW",
        "WWWWWWGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGWWWWW",
        "WWWWWWGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGWWWWW",
        "WWWWWWGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGWWWWW",
        "WWWWWWGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGWWWWW",
        "WWWWWWGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGWWWWW",
        "WWWWWWGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGWWWWW",
        "WWWWWWWWWWWWWWWWWWWWGGGGGGGGGGGGGGGGGGGGWWWWWWWWWWWWWWWWWWWW",
        "WWWWWWWWWWWWWWWWWWWWGGGGGGGGGGGGGGGGGGGGWWWWWWWWWWWWWWWWWWWW",
        "WWWWWWWWWWWWWWWWWWWWGGGGGGGGGGGGGGGGGGGGWWWWWWWWWWWWWWWWWWWW",
        "WWWWWWWWWWWWWWWWWWWWGGGGGGGGGGGGGGGGGGGGWWWWWWWWWWWWWWWWWWWW",
        "WWWWWWWWWWWWWWWWWWWWGGGGGGGGGGGGGGGGGGGGWWWWWWWWWWWWWWWWWWWW",
        "WWWWWWWWWWWWWWWWWWWWGGGGGGGGGGGGGGGGGGGGWWWWWWWWWWWWWWWWWWWW",
        "WWWWWWWWWWWWWWWWWWWWGGGGGGGGGGGGGGGGGGGGWWWWWWWWWWWWWWWWWWWW",
        "WWWWWWWWWWWWWWWWWWWWGGGGGGGGGGGGGGGGGGGGWWWWWWWWWWWWWWWWWWWW",
        "WWWWWWWWWWWWWWWWWWWWGGGGGGGGGGGGGGGGGGGGWWWWWWWWWWWWWWWWWWWW",
        "WWWWWWWWWWWWWWWWWWWWGGGGGGGGGGGGGGGGGGGGWWWWWWWWWWWWWWWWWWWW",
        "WWWWWWWWWWWWWWWWWWWWGGGGGGGGGGGGGGGGGGGGWWWWWWWWWWWWWWWWWWWW",
        "WWWWWWWWWWWWWWWWWWWWGGGGGGGGGGGGGGGGGGGGWWWWWWWWWWWWWWWWWWWW",
        "WWWWWWWWWWWWWWWWWWWWGGGGGGGGGGGGGGGGGGGGWWWWWWWWWWWWWWWWWWWW",
        "WWWWWWWWWWWWWWWWWWWWGGGGGGGGGGGGGGGGGGGGWWWWWWWWWWWWWWWWWWWW",
        "WWWWWWWWWWWWWWWWWWWWGGGGGGGGGGGGGGGGGGGGWWWWWWWWWWWWWWWWWWWW",
        "WWWWWWWWWWWWWWWWWWWWGGGGGGGGGGGGGGGGGGGGWWWWWWWWWWWWWWWWWWWW",
        "WWWWWWWWWWWWWWWWWWWWGGGGGGGGGGGGGGGGGGGGWWWWWWWWWWWWWWWWWWWW",
        "WWWWWWWWWWWWWWWWWWWWGGGGGGGGGGGGGGGGGGGGWWWWWWWWWWWWWWWWWWWW",
        "WWWWWWWWWWWWWWWWWWWWGGGGGGGGGGGGGGGGGGGGWWWWWWWWWWWWWWWWWWWW",
        "WWWWWWWWWWWWWWWWWWWWGGGGGGGGGGGGGGGGGGGGWWWWWWWWWWWWWWWWWWWW",
        "WWWWWWWWWWWWWWWWWWWWGGGGGGGGGGGGGGGGGGGGWWWWWWWWWWWWWWWWWWWW",
        "WWWWWWWWWWWWWWWWWWWWGGGGGGGGGGGGGGGGGGGGWWWWWWWWWWWWWWWWWWWW",
        "WWWWWWWWWWWWWWWWWWWWGGGGGGGGGGGGGGGGGGGGWWWWWWWWWWWWWWWWWWWW",
        "WWWWWWWWWWWWWWWWWWWWGGGGGGGGGGGGGGGGGGGGWWWWWWWWWWWWWWWWWWWW",
        "WWWWWWWWWWWWWWWWWWWWGGGGGGGGGGGGGGGGGGGGWWWWWWWWWWWWWWWWWWWW",
        "WWWWWWWWWWWWWWWWWWWWGGGGGGGGGGGGGGGGGGGGWWWWWWWWWWWWWWWWWWWW",
        "WWWWWWWWWWWWWWWWWWWWGGGGGGGGGGGGGGGGGGGGWWWWWWWWWWWWWWWWWWWW",
        "WWWWWWWWWWWWWWWWWWWWGGGGGGGGGGGGGGGGGGGGWWWWWWWWWWWWWWWWWWWW",
        "WWWWWWWWWWWWWWWWWWWWGGGGGGGGGGGGGGGGGGGGWWWWWWWWWWWWWWWWWWWW",
        "WWWWWWWWWWWWWWWWWWWWGGGGGGGGGGGGGGGGGGGGWWWWWWWWWWWWWWWWWWWW",
    ]
    map_group = pygame.sprite.Group()

    container = pygame.Rect(0, 0, len(game.screen1[0]) * 16, len(game.screen1) * 16)
    hero = Hero(container)

    # Create Text
    title = Text(30, "Journey of a Hero:", BLACK, win_w / 2, win_h / 2)
    title2 = Text(25, "The Stones of the Elemental Dragons", BLACK, win_w / 2, win_h / 2 + 35)
    askplay = Text(30, "Click to Start!", BLACK, win_w / 2, 3 * win_h / 4)
    agilityscreen = Text(30, "Agility", BLACK, 160, 32)
    strengthscreen = Text(30, "Strength", WHITE, container.right - 160, 32)
    defensescreen = Text(30, "Defense", BLACK, 160, container.bottom - 32)
    shopscreen = Text(30, "Shop", WHITE, container.right - 160, container.bottom - 32)



    scroll_group.add(game.introscroll)

    while game.intro:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN or pygame.key.get_pressed()[pygame.K_RETURN] != 0:
                game.intro = False
        # Blitting
        game.screen.fill(WHITE)
        game.screen.blit(title.image, title.rect)
        game.screen.blit(title2.image, title2.rect)
        game.blink(askplay.image, askplay.rect)

        pygame.display.flip()

    #Build SCENE1
    game.build(game.screen1, map_group)
    while game.play:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
        if game.scene1:

            # Updates
            hero.update(scroll_group, game.introscroll, map_group, game)
            camera.update(hero)

            #Blitting
            game.screen.fill(WHITE)
            for p in map_group:
               game.screen.blit(p.image, camera.apply(p))
            game.screen.blit(hero.image, camera.apply(hero))
            game.screen.blit(agilityscreen.image, camera.apply(agilityscreen))
            game.screen.blit(defensescreen.image, camera.apply(defensescreen))
            game.screen.blit(strengthscreen.image, camera.apply(strengthscreen))
            game.screen.blit(shopscreen.image, camera.apply(shopscreen))
            for s in scroll_group:
                game.screen.blit(s.image, camera.apply(s))
            game.screen.blit(hero.agilityscore.image, hero.agilityscore.rect)
            game.screen.blit(hero.lifescore.image, hero.lifescore.rect)
            game.screen.blit(hero.strengthscore.image, hero.strengthscore.rect)
            game.screen.blit(hero.defensescore.image, hero.defensescore.rect)

            # Sets how many frames per second
            game.loop_counter += 1
            game.clock.tick(60)
            pygame.display.flip()


        #Build AGILITYSCENE

        elif game.agility:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()
                if event.type == pygame.key.get_pressed()[pygame.K_RETURN] != 0:
                    game.agility = False
                    game.scene1 = True
                    map_group.empty()
                    game.build(game.screen1, map_group)
                    game.loop_counter = 0

            if game.loop_counter % 3 == 0:
                bullet = Bullet(game.loop_counter, len(game.agilityscene[0]) * 16, random.randrange(0, len(game.agilityscene) * 16), 1, "L")
                bullet_group.add(bullet)

            # Updates
            hero.update(scroll_group, game.agilityscroll, map_group, game)
            hero.traincheckhit(bullet_group)
            camera.update(hero)
            bullet_group.update()

            if hero.trainlife <= 0:
                score = game.loop_counter // 120
                hero.agility += score
                text = Text(30, "Congratulations, you increased your agility by " + str(score), BLACK, win_w / 2, win_h / 2)
                game.screen.fill(YELLOW)
                game.screen.blit(text.image, text.rect)
                pygame.display.flip()
                time.sleep(2)
                game.agility = False
                game.scene1 = True
                map_group.empty()
                scroll_group.empty()
                game.build(game.screen1, map_group)
                hero.centerx = win_w / 4 - 5
                hero.centery = win_h / 2
                game.loop_counter = 0
                hero.agilityscore.image = hero.agilityscore.font.render("Agility: " + str(hero.agility), 1, BLACK)

            # Blitting
            for p in map_group:
                game.screen.blit(p.image, camera.apply(p))
            game.screen.blit(hero.image, camera.apply(hero))
            for s in scroll_group:
                game.screen.blit(s.image, camera.apply(s))
            for b in bullet_group:
                game.screen.blit(b.image, camera.apply(b))
            game.screen.blit(hero.trainscore.image, hero.trainscore.rect)
            # Sets how many frames per second
            game.loop_counter +=1
            game.clock.tick(30)
            pygame.display.flip()

        elif game.strength:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()
                if event.type == pygame.key.get_pressed()[pygame.K_ESCAPE]:
                    game.strength = False
                    game.scene1 = True
                    map_group.empty()
                    game.build(game.screen1, map_group)
                    game.loop_counter = 0

            if game.loop_counter < 1800:
                if game.loop_counter % 10 == 0:
                    bullet = Bullet(game.loop_counter, random.randrange(0, len(game.agilityscene[0]) * 16), random.randrange(0, len(game.agilityscene) * 16), random.randrange(1, 10), "L")
                    bullet_group.add(bullet)

                hero.update(scroll_group, game.strengthscroll, map_group, game)
                hero.trainsmash(bullet_group)
            else:
                score = hero.trainlife // 15
                hero.strength += score
                text = Text(30, "Congratulations, you increased your strength by " + str(score), BLACK, win_w / 2,
                            win_h / 2)
                game.screen.fill(YELLOW)
                game.screen.blit(text.image, text.rect)
                pygame.display.flip()
                time.sleep(2)
                game.strength = False
                game.scene1 = True
                map_group.empty()
                bullet_group.empty()
                scroll_group.empty()
                game.build(game.screen1, map_group)
                hero.centerx = win_w / 4 - 5
                hero.centery = win_h / 2
                game.loop_counter = 0
                hero.strengthscore.image = hero.strengthscore.font.render("Strength: " + str(hero.strength), 1, BLACK)


            for p in map_group:
                game.screen.blit(p.image, camera.apply(p))
            game.screen.blit(hero.image, camera.apply(hero))
            for s in scroll_group:
                game.screen.blit(s.image, camera.apply(s))
            for b in bullet_group:
                game.screen.blit(b.image, camera.apply(b))
            game.screen.blit(hero.trainscore.image, hero.trainscore.rect)
            # Sets how many frames per second
            game.loop_counter += 1
            game.clock.tick(30)
            pygame.display.flip()

        elif game.defense:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()
                if event.type == pygame.key.get_pressed()[pygame.K_RETURN]:
                    game.defense = False
                    game.scene1 = True
                    map_group.empty()
                    game.build(game.screen1, map_group)
                    game.loop_counter = 0


            if game.loop_counter < 900:
                boss = Enemy(99999, "Boss", win_w / 2, win_h / 2, BLACK)

                enemy_group.add(boss)
                hero.update(scroll_group, game.defensescroll, map_group, game)
                hero.trainsmash(enemy_group)
                hero.traincheckhit(bullet_group)
                boss.update(hero, bullet_group, game)
            else:
                score = hero.trainlife // 20
                hero.defense += score
                text = Text(30, "Congratulations, you increased your defense by " + str(score), BLACK, win_w / 2,
                            win_h / 2)
                game.screen.fill(YELLOW)
                game.screen.blit(text.image, text.rect)
                pygame.display.flip()
                time.sleep(2)
                game.defense = False
                game.scene1 = True
                map_group.empty()
                bullet_group.empty()
                scroll_group.empty()
                game.build(game.screen1, map_group)
                hero.centerx = win_w / 4 - 5
                hero.centery = win_h / 2
                game.loop_counter = 0
                hero.defensescore.image = hero.defensescore.font.render("Defense: " + str(hero.defense), 1, BLACK)

            for p in map_group:
                game.screen.blit(p.image, camera.apply(p))
            game.screen.blit(hero.image, camera.apply(hero))
            for s in scroll_group:
                game.screen.blit(s.image, camera.apply(s))
            for b in bullet_group:
                game.screen.blit(b.image, camera.apply(b))
            game.screen.blit(hero.trainscore.image, hero.trainscore.rect)
            game.screen.blit(boss.image, camera.apply(boss))
            # Sets how many frames per second
            game.loop_counter += 1
            game.clock.tick(30)
            pygame.display.flip()

        elif game.scenetop:
            ruby = Enemy(20, "Boss", win_w / 4, win_h/3, RED)
            enemy_group.add(ruby)
            hero.update(scroll_group, game.scenetopscroll, map_group, game)
            camera.update(hero)
            ruby.update(hero, bullet_group, game)
            hero.attack(bullet_group, enemy_group, game)


            for p in map_group:
                game.screen.blit(p.image, camera.apply(p))
            game.screen.blit(hero.image, camera.apply(hero))
            for s in scroll_group:
                game.screen.blit(s.image, camera.apply(s))
            for b in bullet_group:
                game.screen.blit(b.image, camera.apply(b))
            game.screen.blit(ruby.image, camera.apply(ruby))
            game.screen.blit(ruby.lifescore.image, ruby.lifescore.rect)
            game.screen.blit(hero.agilityscore.image, hero.agilityscore.rect)
            game.screen.blit(hero.lifescore.image, hero.lifescore.rect)
            game.screen.blit(hero.strengthscore.image, hero.strengthscore.rect)
            game.screen.blit(hero.defensescore.image, hero.defensescore.rect)

            # Sets how many frames per second
            game.loop_counter += 1
            game.clock.tick(60)
            pygame.display.flip()

if __name__ == "__main__":
    main()
