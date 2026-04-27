import pygame
import random

VIEW_WIDTH, VIEW_HEIGHT = 600, 400
TILE = 20

class SnakeEngine:
    def __init__(self, surface, config, p_name, best_score):
        self.window = surface
        self.cfg = config
        self.p_name = p_name
        self.best = best_score
        self.timer = pygame.time.Clock()
        
        self.body = [(100, 100), (80, 100), (60, 100)]
        self.vector = (TILE, 0)
        self.total_score = 0
        self.current_lv = 1
        self.active = True
        
        self.generate_target()
        self.trap = (random.randint(0, (VIEW_WIDTH//TILE)-1)*TILE, 
                     random.randint(0, (VIEW_HEIGHT//TILE)-1)*TILE)

    def generate_target(self):
        self.target = (random.randint(0, (VIEW_WIDTH//TILE)-1)*TILE, 
                       random.randint(0, (VIEW_HEIGHT//TILE)-1)*TILE)

    def update(self):
        head_x, head_y = self.body[0]
        vx, vy = self.vector
        new_node = (head_x + vx, head_y + vy)

        if not (0 <= new_node[0] < VIEW_WIDTH and 0 <= new_node[1] < VIEW_HEIGHT) or new_node in self.body:
            self.active = False
            return

        self.body.insert(0, new_node)

        if new_node == self.target:
            self.total_score += 10
            if len(self.body) % 5 == 0: self.current_lv += 1
            self.generate_target()
        else:
            self.body.pop()

        if new_node == self.trap:
            self.active = False

    def render(self):
        self.window.fill((20, 24, 30))
        
        if self.cfg.get("grid"):
            for x in range(0, VIEW_WIDTH, TILE):
                pygame.draw.line(self.window, (40, 45, 50), (x, 0), (x, VIEW_HEIGHT))
            for y in range(0, VIEW_HEIGHT, TILE):
                pygame.draw.line(self.window, (40, 45, 50), (0, y), (VIEW_WIDTH, y))

        # Target (Circle)
        pygame.draw.circle(self.window, (255, 80, 80), (self.target[0]+10, self.target[1]+10), 8)
        # Trap
        pygame.draw.rect(self.window, (100, 0, 0), (*self.trap, TILE, TILE))

        # Snake with Eyes
        clr = self.cfg.get("snake_color", (0, 255, 100))
        for i, pos in enumerate(self.body):
            node_clr = [max(0, c - 40) for c in clr] if i == 0 else clr
            pygame.draw.rect(self.window, node_clr, (*pos, TILE-1, TILE-1), border_radius=5)
            if i == 0: # Eyes
                pygame.draw.circle(self.window, (255, 255, 255), (pos[0]+5, pos[1]+5), 2)
                pygame.draw.circle(self.window, (255, 255, 255), (pos[0]+15, pos[1]+5), 2)

    def start_loop(self):
        while self.active:
            speed = 8 + self.current_lv * 2
            self.timer.tick(speed)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT: return {"exit": True}
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP and self.vector != (0, TILE): self.vector = (0, -TILE)
                    if event.key == pygame.K_DOWN and self.vector != (0, -TILE): self.vector = (0, TILE)
                    if event.key == pygame.K_LEFT and self.vector != (TILE, 0): self.vector = (-TILE, 0)
                    if event.key == pygame.K_RIGHT and self.vector != (-TILE, 0): self.vector = (TILE, 0)

            self.update()
            self.render()
            
            
            font = pygame.font.SysFont("Arial", 18)
            info = font.render(f"Score: {self.total_score} | Best: {self.best}", True, (200, 200, 200))
            self.window.blit(info, (10, 10))
            
            pygame.display.flip()
            
        return {"exit": False, "score": self.total_score, "lvl": self.current_lv}