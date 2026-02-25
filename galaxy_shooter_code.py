import pygame
import random

# --- INIT ---
pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Galaxy Shooter Continuous Laser")
clock = pygame.time.Clock()

# --- COLORS ---
WHITE = (255,255,255)
RED = (255,0,0)
GREEN = (0,255,0)
BLUE = (0,0,255)
YELLOW = (255,255,0)
PURPLE = (200,0,200)
BLACK = (0,0,0)
ORANGE = (255,165,0)

# --- LOAD IMAGES ---
bg_img = pygame.image.load("background.png")
bg_img = pygame.transform.scale(bg_img,(WIDTH, HEIGHT))

player_img = pygame.image.load("player.png")
player_img = pygame.transform.scale(player_img,(50,50))

enemy_img = pygame.image.load("enemy.png")
enemy_img = pygame.transform.scale(enemy_img,(40,40))

tank_img = pygame.image.load("tank.png")
tank_img = pygame.transform.scale(tank_img,(50,50))

mother_img = pygame.image.load("mother.png")
mother_img = pygame.transform.scale(mother_img,(200,60))

bullet_img = pygame.image.load("bullet.png")
bullet_img = pygame.transform.scale(bullet_img,(5,15))

tank_bullet_img = pygame.image.load("tank_bullet.png")
tank_bullet_img = pygame.transform.scale(tank_bullet_img,(5,10))

powerup_images = {
    "health": pygame.transform.scale(pygame.image.load("power_health.png"),(20,20)),
    "shield": pygame.transform.scale(pygame.image.load("power_shield.png"),(20,20)),
    "laser": pygame.transform.scale(pygame.image.load("power_laser.png"),(20,20)),
    "speed": pygame.transform.scale(pygame.image.load("power_speed.png"),(20,20))
}

explosion_img = pygame.image.load("explosion.png")
explosion_img = pygame.transform.scale(explosion_img,(40,40))

# --- PLAYER ---
player_x = WIDTH//2
player_y = HEIGHT-80
player_speed = 6
player_health = 100
player_shield = 100
shield_recharge_rate = 0.05

# --- LASER BEAM ---
laser_active = False
laser_width = 8
laser_color = YELLOW
laser_cooldown = 0
laser_delay = 5  # small delay to control continuous firing

# --- ENEMIES ---
enemies = []
enemy_speed = 2
tanks = []
tank_bullets = []

# --- MOTHER SHIP ---
mother_active = False
mother_health = 300
mother_pos = [WIDTH//2-100,50,200,60]

# --- POWERUPS & EXPLOSIONS ---
powerups = []
explosions = []

# --- SCORE & LEVEL ---
score = 0
level = 1

# --- FONT ---
font = pygame.font.SysFont(None,30)

# --- FUNCTIONS ---
def draw_text(text,x,y,color=(255,255,255)):
    img = font.render(text,True,color)
    screen.blit(img,(x,y))

def spawn_enemy():
    x = random.randint(50, WIDTH-50)
    y = random.randint(-100, -40)
    enemies.append([x,y,enemy_img])

def spawn_tank():
    x = random.randint(50, WIDTH-50)
    y = random.randint(-100, -40)
    tanks.append([x,y,tank_img,100])

def spawn_powerup():
    x = random.randint(50, WIDTH-50)
    y = -20
    type = random.choice(["health","shield","laser","speed"])
    powerups.append([x,y,type])

def move_ai_tank(tank):
    if tank[0] < player_x:
        tank[0] += random.randint(0,2)
    elif tank[0] > player_x:
        tank[0] -= random.randint(0,2)
    tank[1] += 1

def create_explosion(x,y):
    explosions.append([x,y,40])

# --- MAIN LOOP ---
running = True
spawn_timer = 0
tank_timer = 0
powerup_timer = 0

while running:
    clock.tick(60)
    screen.blit(bg_img,(0,0))

    # --- EVENTS ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT] and player_x > 0:
        player_x -= player_speed
    if keys[pygame.K_RIGHT] and player_x < WIDTH-50:
        player_x += player_speed
    laser_active = keys[pygame.K_SPACE]

    # --- SPAWN ENEMIES / TANKS / POWERUPS ---
    spawn_timer += 1
    if spawn_timer > max(60 - level*5, 20):
        spawn_enemy()
        spawn_timer = 0

    tank_timer +=1
    if tank_timer > max(200 - level*10, 80):
        spawn_tank()
        tank_timer = 0

    powerup_timer +=1
    if powerup_timer > 600:
        spawn_powerup()
        powerup_timer = 0

    # --- DRAW PLAYER ---
    screen.blit(player_img,(player_x,player_y))

    # --- CONTINUOUS LASER ---
    if laser_active and laser_cooldown==0:
        laser_rect = pygame.Rect(player_x+player_img.get_width()//2 - laser_width//2,
                                 0, laser_width, player_y)
        laser_cooldown = laser_delay
        # Check collision with enemies
        for enemy in enemies[:]:
            enemy_rect = pygame.Rect(enemy[0],enemy[1],enemy_img.get_width(),enemy_img.get_height())
            if laser_rect.colliderect(enemy_rect):
                create_explosion(enemy[0],enemy[1])
                enemies.remove(enemy)
                score +=5
        for tank in tanks[:]:
            tank_rect = pygame.Rect(tank[0],tank[1],tank[2].get_width(),tank[2].get_height())
            if laser_rect.colliderect(tank_rect):
                tank[3]-=10
                if tank[3]<=0:
                    create_explosion(tank[0],tank[1])
                    tanks.remove(tank)
                    score+=15
        if mother_active:
            mother_rect = pygame.Rect(*mother_pos)
            if laser_rect.colliderect(mother_rect):
                mother_health -=10

    if laser_cooldown>0:
        laser_cooldown -=1

    if laser_active:
        pygame.draw.rect(screen,laser_color,(player_x+player_img.get_width()//2 - laser_width//2,0,laser_width,player_y))

    # --- MOVE ENEMIES ---
    for enemy in enemies[:]:
        enemy[1] += enemy_speed
        screen.blit(enemy_img,(enemy[0],enemy[1]))
        if enemy[1]>HEIGHT:
            enemies.remove(enemy)

    # --- MOVE TANKS ---
    for tank in tanks[:]:
        move_ai_tank(tank)
        screen.blit(tank[2],(tank[0],tank[1]))
        if random.randint(1,100)==1:
            tank_bullets.append([tank[0]+tank[2].get_width()//2, tank[1]+tank[2].get_height()])
        if tank[3]<=0:
            create_explosion(tank[0],tank[1])
            tanks.remove(tank)
            score+=15
        if tank[1]>HEIGHT:
            tanks.remove(tank)

    # --- TANK BULLETS ---
    for tb in tank_bullets[:]:
        tb[1] += 5
        screen.blit(tank_bullet_img,(tb[0],tb[1]))
        player_rect = pygame.Rect(player_x,player_y,player_img.get_width(),player_img.get_height())
        tb_rect = pygame.Rect(tb[0],tb[1],tank_bullet_img.get_width(),tank_bullet_img.get_height())
        if tb_rect.colliderect(player_rect):
            if player_shield>0:
                player_shield -=10
            else:
                player_health -=10
            tank_bullets.remove(tb)
        if tb[1]>HEIGHT:
            tank_bullets.remove(tb)

    # --- POWERUPS ---
    for pu in powerups[:]:
        pu[1]+=2
        screen.blit(powerup_images[pu[2]],(pu[0],pu[1]))
        pu_rect = pygame.Rect(pu[0],pu[1],20,20)
        player_rect = pygame.Rect(player_x,player_y,player_img.get_width(),player_img.get_height())
        if player_rect.colliderect(pu_rect):
            if pu[2]=='health':
                player_health = min(player_health+30,100)
            elif pu[2]=='shield':
                player_shield = min(player_shield+30,100)
            elif pu[2]=='laser':
                laser_width +=2
            elif pu[2]=='speed':
                player_speed +=1
            powerups.remove(pu)
        if pu[1]>HEIGHT:
            powerups.remove(pu)

    # --- SHIELD RECHARGE ---
    if player_shield<100:
        player_shield += shield_recharge_rate

    # --- MOTHER SHIP ---
    if score>=50:
        mother_active=True
    if mother_active:
        screen.blit(mother_img,(mother_pos[0],mother_pos[1]))
        draw_text(f"Mother HP: {mother_health}", WIDTH//2-60,20)
        if mother_health <=0:
            draw_text("YOU WIN!",WIDTH//2-80,HEIGHT//2)

    # --- LEVEL SYSTEM ---
    level = score//50 +1

    # --- EXPLOSIONS ---
    for exp in explosions[:]:
        exp_rect = explosion_img.get_rect(center=(exp[0]+20,exp[1]+20))
        screen.blit(explosion_img,exp_rect)
        exp[2]-=1
        if exp[2]<=0:
            explosions.remove(exp)

    # --- UI ---
    draw_text(f"Health: {int(player_health)}%",10,10)
    draw_text(f"Shield: {int(player_shield)}%",10,40)
    draw_text(f"Score: {score}",10,70)
    draw_text(f"Level: {level}",10,100)

    # --- GAME OVER ---
    if player_health<=0:
        draw_text("GAME OVER",WIDTH//2-80,HEIGHT//2)
        pygame.display.update()
        pygame.time.delay(3000)
        break

    pygame.display.update()

pygame.quit()
