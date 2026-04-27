import pygame, sys, random, time, os
from racer import Player, Enemy, Collectible, get_asset
from persistence import *

pygame.init()
pygame.mixer.init()
WIDTH, HEIGHT = 400, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

RED, WHITE, BLACK, YELLOW = (255,0,0), (255,255,255), (0,0,0), (255,255,0)


settings = load_json('settings.json', {"sound": True, "color": "Player.png", "diff": 1})


try:
    crash_sound = pygame.mixer.Sound(get_asset("crash.wav"))
    if settings['sound']:
        pygame.mixer.music.load(get_asset("crazy_frog.mp3"))
        pygame.mixer.music.play(-1)
except Exception as e:
    print(f"Звуки не найдены: {e}")

def draw_text(text, size, y, color=WHITE, x=WIDTH//2):
    font = pygame.font.SysFont("Verdana", size, bold=True)
    surf = font.render(str(text), True, color)
    rect = surf.get_rect(center=(x, y))
    screen.blit(surf, rect)

def button(text, y):
    mx, my = pygame.mouse.get_pos()
    rect = pygame.Rect(WIDTH//2 - 100, y - 25, 200, 50)
    on_hover = rect.collidepoint(mx, my)
    draw_text(text, 35, y, YELLOW if on_hover else WHITE)
    return on_hover and pygame.mouse.get_pressed()[0]

def input_name_screen():
    name = ""
    while True:
        screen.fill(BLACK)
        draw_text("ENTER NAME:", 30, 200)
        draw_text(name, 40, 300, YELLOW)
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and name != "": return name
                elif event.key == pygame.K_BACKSPACE: name = name[:-1]
                else: 
                    if len(name) < 10: name += event.unicode
        pygame.display.update()

def game_run(username):
    road = pygame.transform.scale(pygame.image.load(get_asset("road.png")), (WIDTH, HEIGHT))
    road_y = 0
    player = Player(settings['color'])
    enemies = pygame.sprite.Group(Enemy(5 + settings['diff']))
    items = pygame.sprite.Group()
    all_sprites = pygame.sprite.Group(player, *enemies)
    
    score, coins, dist = 0, 0, 0
    speed = 5 + settings['diff']
    
    while True:
        road_y += speed
        if road_y >= HEIGHT: road_y = 0
        screen.blit(road, (0, road_y))
        screen.blit(road, (0, road_y - HEIGHT))

        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
        
        if random.randint(1, 60) == 1:
            itype = random.choice(['coinn', 'oil', 'shield', 'boost', 'heal'])
            new_item = Collectible(itype, speed)
            items.add(new_item); all_sprites.add(new_item)

        player.move()
        enemies.update()
        items.update()
        dist += speed / 20
        
        if pygame.sprite.spritecollide(player, enemies, False):
            if player.shield:
                player.shield = False
                for e in enemies: e.rect.y = -200
            else:
                if settings['sound']: crash_sound.play()
                screen.fill(RED)
                draw_text("CRASH!", 60, HEIGHT//2)
                pygame.display.update()
                time.sleep(3)
                final_score = int(score + dist)
                update_leaderboard(username, final_score, dist)
                return final_score, int(dist), coins

        hits = pygame.sprite.spritecollide(player, items, True)
        for h in hits:
            if h.type == 'coinn': coins += 1; score += 50
            if h.type == 'oil': speed = max(4, speed - 2)
            if h.type == 'shield': player.shield = True
            if h.type == 'boost': speed += 3
            if h.type == 'heal': score += 100

        for s in all_sprites: screen.blit(s.image, s.rect)
        if player.shield: pygame.draw.rect(screen, (0,255,255), player.rect, 3)
        
        draw_text(f"Score: {int(score+dist)}", 20, 30, WHITE, 80)
        pygame.display.update()
        clock.tick(60)

def main_menu():
    while True:
        screen.fill(BLACK)
        draw_text("RACER 2026", 50, 100, YELLOW)
        
        if button("PLAY", 250):
            user = input_name_screen()
            s, d, c = game_run(user)
            while True:
                screen.fill(BLACK)
                draw_text("GAME OVER", 40, 100, RED)
                draw_text(f"SCORE: {s}", 30, 200)
                draw_text(f"DIST: {d}m", 30, 250)
                if button("RETRY", 400): break
                if button("MENU", 480): return main_menu()
                for e in pygame.event.get(): 
                    if e.type == pygame.QUIT: pygame.quit(); sys.exit()
                pygame.display.update()

        if button("LEADERBOARD", 330):
            while True:
                screen.fill(BLACK)
                draw_text("TOP 10", 40, 50, YELLOW)
                data = load_json('leaderboard.json', [])
                for idx, e in enumerate(data):
                    draw_text(f"{idx+1}. {e['name']} - {e['score']}", 20, 120 + idx*35)
                if button("BACK", 530): break
                for e in pygame.event.get(): 
                    if e.type == pygame.QUIT: pygame.quit(); sys.exit()
                pygame.display.update()

        if button("QUIT", 410): pygame.quit(); sys.exit()
        
        for e in pygame.event.get(): 
            if e.type == pygame.QUIT: pygame.quit(); sys.exit()
        pygame.display.update()

if __name__ == "__main__":
    main_menu()