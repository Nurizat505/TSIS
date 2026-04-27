import pygame

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
GREEN = (0, 200, 0)

def draw_text(screen, text, size, x, y, color=BLACK):
    font = pygame.font.SysFont("Verdana", size)
    img = font.render(text, True, color)
    screen.blit(img, (x, y))

def button(screen, msg, x, y, w, h, ic, ac, action=None):
    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()
    if x + w > mouse[0] > x and y + h > mouse[1] > y:
        pygame.draw.rect(screen, ac, (x, y, w, h))
        if click[0] == 1 and action is not None:
            return action()
    else:
        pygame.draw.rect(screen, ic, (x, y, w, h))
    
    font = pygame.font.SysFont("Verdana", 20)
    text_surf = font.render(msg, True, WHITE)
    text_rect = text_surf.get_rect(center=((x + (w / 2)), (y + (h / 2))))
    screen.blit(text_surf, text_rect)
    return None