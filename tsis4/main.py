import pygame
import sys
import os
import json
from db import setup_tables, record_match, fetch_leaderboard, fetch_best_score
from game import SnakeEngine, VIEW_WIDTH, VIEW_HEIGHT

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MUSIC_FILE = os.path.join(BASE_DIR, "assets", "music.wav")

class Interface:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        print("MIXER INIT:", pygame.mixer.get_init())
        print("MUSIC PATH:", MUSIC_FILE)

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
        default = {
            "snake_color": [0, 200, 0],
            "grid": True,
            "music": True
        }

        if os.path.exists(self.pref_path):
            try:
                with open(self.pref_path, "r") as f:
                    return json.load(f)
            except:
                pass

        return default

    def save_prefs(self):
        with open(self.pref_path, "w") as f:
            json.dump(self.prefs, f)

    def apply_music(self):
        try:
           pygame.mixer.music.stop()

           if self.prefs.get("music", True):
            pygame.mixer.music.load(MUSIC_FILE)
            pygame.mixer.music.set_volume(1.0)
            pygame.mixer.music.play(-1)
            print("MUSIC STARTED")
           else:
               print("MUSIC OFF")

        except Exception as e:
          print("MUSIC ERROR:", e)

    def draw_text(self, msg, y, color=(255, 255, 255), font=None):
        f = font if font else self.ui_font
        img = f.render(msg, True, color)
        self.canvas.blit(img, img.get_rect(center=(VIEW_WIDTH // 2, y)))

    def menu(self):
        while True:
            self.canvas.fill((15, 15, 25))
            self.draw_text("SNAKE ARENA", 80, (0, 255, 150), self.title_font)

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

                        if res["exit"]:
                            return

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
        active = True

        while active:
            self.canvas.fill((25, 25, 35))
            self.draw_text("CONFIGURATION", 60, (255, 255, 255), self.title_font)

            grid_status = "ON" if self.prefs["grid"] else "OFF"
            music_status = "ON" if self.prefs["music"] else "OFF"

            self.draw_text(f"[G] GRID: {grid_status}", 140, font=self.small_font)
            self.draw_text(f"[M] MUSIC: {music_status}", 180, font=self.small_font)
            self.draw_text("[ESC] BACK", 260, (150, 150, 150), self.small_font)

            preview = pygame.Rect(VIEW_WIDTH // 2 - 40, 300, 80, 15)
            pygame.draw.rect(self.canvas, self.prefs["snake_color"], preview)

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

                    if event.key == pygame.K_ESCAPE:
                        self.save_prefs()
                        active = False

            pygame.display.flip()

    def show_leaders(self):
        active = True

        while active:
            self.canvas.fill((10, 10, 15))
            self.draw_text("HALL OF FAME", 50, (255, 215, 0))

            data = fetch_leaderboard()

            if not data:
                self.draw_text("No records", 200, (150, 150, 150), self.small_font)
            else:
                for i, r in enumerate(data):
                    txt = f"{i+1}. {r[0]} | {r[1]} | Lv.{r[2]}"
                    self.draw_text(txt, 120 + i * 25, font=self.small_font)

            self.draw_text("PRESS ANY KEY", 360, (120, 120, 120), self.small_font)

            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    active = False

            pygame.display.flip()

if __name__ == "__main__":
    try:
        app = Interface()
        app.menu()
    finally:
        pygame.quit()