import pygame
import sys
import os
from datetime import datetime
import tools

pygame.init()

WIDTH, HEIGHT = 1200, 800
TOOLBAR_WIDTH = 80
BOTTOMBAR_HEIGHT = 100

CANVAS_RECT = pygame.Rect(TOOLBAR_WIDTH, 0, WIDTH - TOOLBAR_WIDTH, HEIGHT - BOTTOMBAR_HEIGHT)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Paint")

canvas = pygame.Surface((CANVAS_RECT.width, CANVAS_RECT.height))
canvas.fill((255,255,255))

WHITE=(255,255,255)
BLACK=(0,0,0)

color = BLACK
tool = "pencil"

brush_sizes = [2, 5, 10]
brush_index = 1
brush_size = brush_sizes[brush_index]

drawing = False
start_pos = (0,0)
last_pos = (0,0)

typing = False
text = ""
text_pos = (0,0)
font = pygame.font.SysFont(None, 24)

BASE_DIR = os.path.dirname(__file__)

def load_icon(name):
    return pygame.transform.scale(
        pygame.image.load(os.path.join(BASE_DIR, "assets", name)).convert_alpha(),
        (35,35)
    )

def make_icon(draw_func):
    surf = pygame.Surface((40,40))
    surf.fill((240,240,240))
    draw_func(surf)
    return surf

icons = {
    "pencil": load_icon("pencil.png"),
    "eraser": load_icon("eraser.png"),
    "fill": load_icon("fill.png"),
    "line": make_icon(lambda s: pygame.draw.line(s, BLACK,(5,35),(35,5),2)),
    "rect": make_icon(lambda s: pygame.draw.rect(s, BLACK,(5,5,30,30),2)),
    "circle": make_icon(lambda s: pygame.draw.circle(s, BLACK,(20,20),15,2)),
    "square": make_icon(lambda s: pygame.draw.rect(s, BLACK,(8,8,24,24),2)),
    "r_triangle": make_icon(lambda s: pygame.draw.polygon(s, BLACK,[(5,35),(5,5),(35,35)],2)),
    "e_triangle": make_icon(lambda s: pygame.draw.polygon(s, BLACK,[(5,35),(35,35),(20,5)],2)),
    "rhombus": make_icon(lambda s: pygame.draw.polygon(s, BLACK,[(20,5),(35,20),(20,35),(5,20)],2)),
    "text": make_icon(lambda s: s.blit(font.render("T",True,BLACK),(12,5)))
}

tools_list = list(icons.keys())

tool_rects = []
for i,t in enumerate(tools_list):
    tool_rects.append((pygame.Rect(10, 10 + i*55, 60, 50), t))

colors = [
(0,0,0),(128,128,128),(192,192,192),(255,255,255),
(255,0,0),(128,0,0),(255,128,128),
(0,255,0),(0,128,0),(128,255,128),
(0,0,255),(0,0,128),(128,128,255),
(255,255,0),(128,128,0),
(255,0,255),(128,0,128),
(0,255,255),(0,128,128)
]

color_rects = []
for i,c in enumerate(colors):
    color_rects.append((pygame.Rect(TOOLBAR_WIDTH + 10 + (i%12)*40, HEIGHT - 90 + (i//12)*40, 30,30), c))

size_rects = [
    (pygame.Rect(500, HEIGHT - 70, 60, 30), 2),
    (pygame.Rect(570, HEIGHT - 70, 60, 30), 5),
    (pygame.Rect(640, HEIGHT - 70, 60, 30), 10)
]

while True:
    screen.fill((200,200,200))

    pygame.draw.rect(screen,(180,180,180),(0,0,TOOLBAR_WIDTH,HEIGHT))
    pygame.draw.rect(screen,(200,200,200),(0,HEIGHT-BOTTOMBAR_HEIGHT,WIDTH,BOTTOMBAR_HEIGHT))

    screen.blit(canvas,(CANVAS_RECT.x,CANVAS_RECT.y))
    pygame.draw.rect(screen,BLACK,CANVAS_RECT,2)

    for rect,c in color_rects:
        pygame.draw.rect(screen,c,rect)

    for rect,t in tool_rects:
        pygame.draw.rect(screen,WHITE,rect)
        screen.blit(icons[t], icons[t].get_rect(center=rect.center))
        if t == tool:
            pygame.draw.rect(screen,(255,215,0),rect,3)

    for rect,size in size_rects:
        pygame.draw.rect(screen,(255,255,255),rect)
        txt = font.render(str(size),True,BLACK)
        screen.blit(txt, txt.get_rect(center=rect.center))
        if size == brush_size:
            pygame.draw.rect(screen,(255,215,0),rect,2)

    mx,my = pygame.mouse.get_pos()

    if tool == "pencil":
        pygame.draw.circle(screen, BLACK, (mx,my), brush_size, 1)

    if drawing and tool == "line":
        pygame.draw.line(screen,color,
        (start_pos[0]+CANVAS_RECT.x,start_pos[1]+CANVAS_RECT.y),
        (mx,my),brush_size)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_s and pygame.key.get_mods() & pygame.KMOD_CTRL:
                pygame.image.save(canvas, datetime.now().strftime("img_%H%M%S.png"))

            if typing:
                if event.key == pygame.K_RETURN:
                    canvas.blit(font.render(text,True,color),text_pos)
                    typing = False
                    text = ""
                elif event.key == pygame.K_ESCAPE:
                    typing = False
                    text = ""
                elif event.key == pygame.K_BACKSPACE:
                    text = text[:-1]
                else:
                    text += event.unicode

        if event.type == pygame.MOUSEBUTTONDOWN:
            mx,my = event.pos

            for rect,c in color_rects:
                if rect.collidepoint(mx,my):
                    color = c

            for rect,size in size_rects:
                if rect.collidepoint(mx,my):
                    brush_size = size

            for rect,t in tool_rects:
                if rect.collidepoint(mx,my):
                    tool = t

            if CANVAS_RECT.collidepoint(mx,my):
                x = mx - CANVAS_RECT.x
                y = my - CANVAS_RECT.y

                if tool == "fill":
                    tools.flood_fill(canvas,x,y,color)
                elif tool == "text":
                    typing = True
                    text_pos = (x,y)
                    text = ""
                else:
                    drawing = True
                    start_pos = (x,y)
                    last_pos = (x,y)

        if event.type == pygame.MOUSEBUTTONUP:
            if drawing:
                mx,my = event.pos
                x = mx - CANVAS_RECT.x
                y = my - CANVAS_RECT.y

                rect = pygame.Rect(min(start_pos[0],x),min(start_pos[1],y),
                                   abs(x-start_pos[0]),abs(y-start_pos[1]))

                if tool == "line":
                    tools.draw_line(canvas,color,start_pos,(x,y),brush_size)
                if tool == "rect":
                    tools.draw_rect(canvas,color,rect,brush_size)
                if tool == "square":
                    tools.draw_square(canvas,color,start_pos,(x,y),brush_size)
                if tool == "circle":
                    tools.draw_circle(canvas,color,start_pos,(x,y),brush_size)
                if tool == "r_triangle":
                    tools.draw_r_triangle(canvas,color,start_pos,(x,y),brush_size)
                if tool == "e_triangle":
                    tools.draw_e_triangle(canvas,color,start_pos,(x,y),brush_size)
                if tool == "rhombus":
                    tools.draw_rhombus(canvas,color,start_pos,(x,y),brush_size)

            drawing = False

        if event.type == pygame.MOUSEMOTION and drawing:
            mx,my = event.pos
            x = mx - CANVAS_RECT.x
            y = my - CANVAS_RECT.y

            if tool == "pencil":
                tools.draw_pencil(canvas,color,last_pos,(x,y),brush_size)
                last_pos = (x,y)

            if tool == "eraser":
                tools.draw_eraser(canvas,last_pos,(x,y),brush_size)
                last_pos = (x,y)

    pygame.display.update()