import pygame
import os
import time
import random
import threading

get = lambda x: pygame.image.load(os.path.join(os.path.dirname(__file__), x))
get_scaled = lambda file, x, y: pygame.transform.scale(pygame.image.load(os.path.join(os.path.dirname(__file__), file)), (x, y))
def timer(t):
    global current_condition, player, angle, pipes, uni_vel
    conditions = ["up", "mid", "down"]
    x = 0
    while True:
        time.sleep(t)
        current_condition = conditions[x]
        x += 1
        if x == 2:
            x = 0

once = True
def add_pipe(m):
    global once, score
    a, b = random.randint(0, 14),random.randint(0, 14)
    h = a*b
    if not once:
        pipes.append(Pipe(160*m, -h-100, True))
        pipes.append(Pipe(160*m, 400-h, False))
        once = True
        score +=1
        pygame.mixer.Sound.play(sounds["point"])
    elif once:
        once = False

def score_checker():
    global score, uni_vel

    score_mod = list(str(score))
    #24x36
    if len(score_mod) ==1:
        img = get(f"sprites\\{score_mod[0]}.png")
        screen.blit(img, (WIDTH/2-10, 50))
    elif len(score_mod) == 2:
        for i,score_ in enumerate(score_mod):
            img = get(f"sprites\\{score_}.png")
            screen.blit(img, (WIDTH/2-20+24*i, 50))
    else:
        for i,score_ in enumerate(score_mod):
            img = get(f"sprites\\{score_}.png")
            screen.blit(img, (WIDTH/2-40+24*i, 50))

    if score %50 == 0 and score != 0:
        uni_vel += 0.01



pygame.init()
pygame.mixer.init()

HEIGHT = 700
WIDTH = 400
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Flappy Bird')
pygame.display.set_icon(get("favicon.ico"))
clock = pygame.time.Clock()
running = True
bg = [get_scaled("sprites\\background-day.png", WIDTH, HEIGHT-150), get_scaled("sprites\\background-night.png", WIDTH, HEIGHT-150)]
base = get_scaled("sprites\\base.png", WIDTH, 150)
bgs = get_scaled("sprites\\message.png", WIDTH-100, HEIGHT-200)
pygame.mixer.music.set_volume(1)
uni_vel = 1
start = True
angle = 0
current_condition = "up"
score = 0
colors = ["red", "blue", "yellow"]
color = "red"

sounds = {
    "swoosh": pygame.mixer.Sound(os.path.join(os.path.dirname(__file__), "audio\\swoosh.wav")),
    "die": pygame.mixer.Sound(os.path.join(os.path.dirname(__file__), "audio\\die.wav")) ,
    "hit": pygame.mixer.Sound(os.path.join(os.path.dirname(__file__), "audio\\hit.wav")),
    "point": pygame.mixer.Sound(os.path.join(os.path.dirname(__file__), "audio\\point.wav")), 
    "wing": pygame.mixer.Sound(os.path.join(os.path.dirname(__file__), "audio\\wing.wav"))
}

class Player:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.vel = -5
        self.color = color
    def create(self, condition, angle):
        self.sprite = get(f"sprites\\{self.color}bird-{condition}flap.png")
        self.sprite = pygame.transform.rotate(self.sprite, -angle)
        self.rect = self.sprite.get_rect()
        self.rect.topleft = (self.x,self.y)    
        screen.blit(self.sprite, self.rect)

pipe_color = ["green", "red"]
pipe_color = random.choice(pipe_color)
class Pipe:
    def __init__(self, x, y, flip):
        self.x = x
        self.check = True
        self.y = y
        self.flip = flip
    def create(self):
        global pipe_color
        self.sprite = get(f"sprites\\pipe-{pipe_color}.png")
        if self.flip:
            self.sprite = pygame.transform.rotate(self.sprite, 180)
        self.rect = self.sprite.get_rect()
        self.rect.topleft = (self.x, self.y)
        screen.blit(self.sprite, self.rect)

pipes = []
player = Player(50, HEIGHT/2, color)

thread = (threading.Thread(target=lambda: timer(0.3)))

for m in range(1, 4):
    a, b = random.randint(0, 13),random.randint(0, 13) 
    pipes.append(Pipe(160*m, -a*b-100, True))
    pipes.append(Pipe(160*m, 400-a*b, False))

thread.start()

counter = 1
i=0
while running:
    if score %(50*counter) == 0 and score != 0:
        if i == 0:
            i = 1
        else:
            i = 0
        counter += 1
    #menu
    while start:
        screen.blit(bg[i], (0,0))
        screen.blit(base, (0, HEIGHT-150))
        screen.blit(bgs, (50, 10))
        pressed = pygame.key.get_pressed()
        if pressed[pygame.K_SPACE]:
            color = random.choice(colors)
            player = Player(50, HEIGHT/2, color)
            start = False
            score = 0
        for event in pygame.event.get():
            if(event.type == pygame.QUIT):
                quit()
        clock.tick(60)
        pygame.display.update()
    #menu end

    screen.blit(bg[i], (0,0))
    for pipe in pipes:
        pipe.create()
        pipe.x -= uni_vel
        if pipe.rect.x <=50 and pipe.check:
            add_pipe(3.5)
            pipe.check = False
        if pipe.x <= -52:
            pipes.remove(pipe)
    
    player.create(current_condition, angle)
    screen.blit(base, (0, HEIGHT-150))

    player.vel += 0.5
    angle += 1
    score_checker()
    ##
    if player.y <= HEIGHT-150:
        player.y += player.vel
    ###

    for pipe in pipes:
        try:
            if player.rect.colliderect(pipe.rect) or player.y >= HEIGHT-150:
                player.y = HEIGHT/2
                pygame.mixer.Sound.play(sounds["hit"])
                uni_vel = 0
                d = True
                #gameover
                pygame.mixer.Sound.play(sounds["die"])
                while d:
                    screen.blit(get("sprites\\gameover.png"), (100, 100))
                    x = pygame.key.get_pressed()
                    if x[pygame.K_SPACE]:
                        d = False
                        start = True
                        uni_vel = 1
                        time.sleep(0.3)
                    for event in pygame.event.get():
                        if(event.type == pygame.QUIT):
                            running = False
                            quit()
                    
                    clock.tick(60)
                    pygame.display.update()
                pipes = []
                for m in range(1, 4):
                    a, b = random.randint(0, 14),random.randint(0, 14) 
                    pipes.append(Pipe(160*m, -a*b-100, True))
                    pipes.append(Pipe(160*m, 400-a*b, False))
        except AttributeError:
            uni_vel = 1
            #gameover end

    pressed = pygame.key.get_pressed()
    if pressed[pygame.K_SPACE]:
        pygame.mixer.Sound.play(sounds["wing"])
        player.vel = -4
        angle = player.vel

    for event in pygame.event.get():
        if(event.type == pygame.QUIT):
            quit()
    
    clock.tick(60)
    pygame.display.update()
thread.join()
