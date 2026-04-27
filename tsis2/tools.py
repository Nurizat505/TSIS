import pygame
from collections import deque

WHITE=(255,255,255)

def draw_pencil(canvas,color,p1,p2,size):
    pygame.draw.line(canvas,color,p1,p2,size)

def draw_eraser(canvas,p1,p2,size):
    pygame.draw.line(canvas,WHITE,p1,p2,size)

def draw_line(canvas,color,p1,p2,size):
    pygame.draw.line(canvas,color,p1,p2,size)

def draw_rect(canvas,color,rect,size):
    pygame.draw.rect(canvas,color,rect,size)

def draw_square(canvas,color,p1,p2,size):
    x1,y1=p1
    x2,y2=p2
    side=max(abs(x2-x1),abs(y2-y1))
    pygame.draw.rect(canvas,color,pygame.Rect(x1,y1,side,side),size)

def draw_circle(canvas,color,p1,p2,size):
    x1,y1=p1
    x2,y2=p2
    r=int(((x2-x1)**2+(y2-y1)**2)**0.5)
    pygame.draw.circle(canvas,color,p1,r,size)

def draw_r_triangle(canvas,color,p1,p2,size):
    x1,y1=p1
    x2,y2=p2
    pygame.draw.polygon(canvas,color,[(x1,y2),(x1,y1),(x2,y2)],size)

def draw_e_triangle(canvas,color,p1,p2,size):
    x1,y1=p1
    x2,y2=p2
    mx=(x1+x2)//2
    pygame.draw.polygon(canvas,color,[(x1,y2),(x2,y2),(mx,y1)],size)

def draw_rhombus(canvas,color,p1,p2,size):
    x1,y1=p1
    x2,y2=p2
    mx=(x1+x2)//2
    my=(y1+y2)//2
    pygame.draw.polygon(canvas,color,[(mx,y1),(x2,my),(mx,y2),(x1,my)],size)

def flood_fill(canvas,x,y,color):
    target=canvas.get_at((x,y))
    if target==color:
        return
    q=deque()
    q.append((x,y))
    w,h=canvas.get_size()
    while q:
        cx,cy=q.popleft()
        if cx<0 or cy<0 or cx>=w or cy>=h:
            continue
        if canvas.get_at((cx,cy))!=target:
            continue
        canvas.set_at((cx,cy),color)
        q.append((cx+1,cy))
        q.append((cx-1,cy))
        q.append((cx,cy+1))
        q.append((cx,cy-1))