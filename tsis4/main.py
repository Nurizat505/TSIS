import pygame
import sys
import os
import json
from db import setup_tables, record_match, fetch_leaderboard, fetch_best_score
from game import SnakeEngine, VIEW_WIDTH, VIEW_HEIGHT


MUSIC_FILE = "assets/music.mp3" 

class Interface:
    def __init__(self):
        pygame.init()
        pygame.mixer.init() 
        
        self.canvas = pygame.display.set_mode((VIEW_WIDTH, VIEW_HEIGHT))
        pygame.display.set_caption("Cyber Snake v2.0")
        
      
        self.title_font = pygame.font.SysFont("Impact", 42)
        self.ui_font = pygame.font.SysFont("Verdana", 24)
        self.small_font = pygame.font.SysFont("Verdana", 16)
        
        self.user_name = ""
        self.pref_path = "user_prefs.json"
        self.prefs = self.load_prefs()
        
        setup_tables()
        self.apply_music()

    def load_prefs(self):
        """Загрузка настроек из JSON"""
        default = {"snake_color": (0, 255, 100), "grid": True, "music": True}
        if os.path.exists(self.pref_path):
            try:
                with open(self.pref_path, "r") as f:
                    data = json.load(f)
                    data["snake_color"] = tuple(data["snake_color"])
                    if "music" not in data: data["music"] = True
                    return data
            except:
                pass
        return default

    def save_prefs(self):
        """Сохранение настроек в JSON"""
        with open(self.pref_path, "w") as f:
            json.dump(self.prefs, f)

    def apply_music(self):
        """Логика включения/выключения музыки"""
        if self.prefs.get("music") and os.path.exists(MUSIC_FILE):
            if not pygame.mixer.music.get_busy():
                try:
                    pygame.mixer.music.load(MUSIC_FILE)
                    pygame.mixer.music.set_volume(0.3)
                    pygame.mixer.music.play(-1)
                except Exception as e:
                    print(f"Ошибка загрузки музыки: {e}")
        else:
            pygame.mixer.music.stop()

    def draw_text(self, msg, y, color=(255, 255, 255), font=None):
        """Вспомогательный метод для центровки текста"""
        f = font if font else self.ui_font
        img = f.render(msg, True, color)
        self.canvas.blit(img, img.get_rect(center=(VIEW_WIDTH // 2, y)))

    def menu(self):
        """Главный цикл меню"""
        while True:
            self.canvas.fill((15, 15, 25))
            self.draw_text("SNAKE ARENA", 80, (0, 255, 150), self.title_font)
            
            # Поле ввода имени
            input_rect = pygame.Rect(VIEW_WIDTH // 2 - 110, 140, 220, 45)
            pygame.draw.rect(self.canvas, (40, 40, 65), input_rect, border_radius=8)
            pygame.draw.rect(self.canvas, (0, 255, 150), input_rect, 1, border_radius=8)
            
            name_disp = self.user_name if self.user_name else "Enter Nickname..."
            self.draw_text(name_disp, 162, (200, 200, 200), self.small_font)
            
            self.draw_text("PRESS [ENTER] TO START", 240)
            self.draw_text("[S] SETTINGS  |  [L] LEADERS", 300, (150, 150, 150), self.small_font)
            self.draw_text("EXIT WITH [ESC]", 350, (100, 100, 100), self.small_font)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return
                    if event.key == pygame.K_RETURN and self.user_name.strip():
                
                        pb = fetch_best_score(self.user_name)
                        game = SnakeEngine(self.canvas, self.prefs, self.user_name, pb)
                        res = game.start_loop()
                        
                        if res["exit"]: return
                        
                        record_match(self.user_name, res["score"], res["lvl"])
                        self.apply_music() 
                        
                    elif event.key == pygame.K_BACKSPACE:
                        self.user_name = self.user_name[:-1]
                    elif event.key == pygame.K_l:
                        self.show_leaders()
                    elif event.key == pygame.K_s:
                        self.settings_menu()
                    else:
                        if len(self.user_name) < 14 and event.unicode.isalnum():
                            self.user_name += event.unicode
            
            pygame.display.flip()

    def settings_menu(self):
        """Экран настроек"""
        active = True
        while active:
            self.canvas.fill((25, 25, 35))
            self.draw_text("CONFIGURATION", 60, (255, 255, 255), self.title_font)
            
            grid_status = "ENABLED" if self.prefs["grid"] else "DISABLED"
            music_status = "ON" if self.prefs["music"] else "OFF"
            
            self.draw_text(f"[G] GRID: {grid_status}", 140, font=self.small_font)
            self.draw_text(f"[M] MUSIC: {music_status}", 180, font=self.small_font)
            self.draw_text(f"[C] CHANGE COLOR", 230, font=self.small_font)
            

            preview_rect = pygame.Rect(VIEW_WIDTH // 2 - 40, 255, 80, 15)
            pygame.draw.rect(self.canvas, self.prefs["snake_color"], preview_rect, border_radius=5)
            
            self.draw_text("PRESS [ESC] TO SAVE & EXIT", 340, (150, 150, 150), self.small_font)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_g:
                        self.prefs["grid"] = not self.prefs["grid"]
                    if event.key == pygame.K_m:
                        self.prefs["music"] = not self.prefs["music"]
                        self.apply_music()
                    if event.key == pygame.K_c:
                        colors = [(0, 255, 120), (255, 180, 0), (220, 50, 255), (50, 150, 255), (255, 50, 50)]
                        try:
                            current_tuple = tuple(self.prefs["snake_color"])
                            idx = (colors.index(current_tuple) + 1) % len(colors)
                        except:
                            idx = 0
                        self.prefs["snake_color"] = colors[idx]
                    if event.key == pygame.K_ESCAPE:
                        self.save_prefs()
                        active = False
            pygame.display.flip()

    def show_leaders(self):
        """Экран таблицы лидеров"""
        active = True
        while active:
            self.canvas.fill((10, 10, 15))
            self.draw_text("HALL OF FAME", 50, (255, 215, 0))
            
            data = fetch_leaderboard()
            if not data:
                self.draw_text("No records yet...", 180, (100, 100, 100), self.small_font)
            else:
                for i, r in enumerate(data):
                    txt = f"{i+1}. {r[0]} | {r[1]} pts | Lv.{r[2]}"
                    self.draw_text(txt, 110 + i * 25, font=self.small_font)
            
            self.draw_text("PRESS ANY KEY TO BACK", 370, (80, 80, 80), self.small_font)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    active = False
            pygame.display.flip()

if __name__ == "__main__":
    try:
        app = Interface()
        app.menu()
    except Exception as e:
        print(f"Критическая ошибка: {e}")
    finally:
        pygame.quit()