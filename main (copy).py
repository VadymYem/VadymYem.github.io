import pygame
import random
import math
import sys
import time

# Налаштування
WIDTH, HEIGHT = 1200, 800
FPS = 30           # нижче навантаження
MAX_FRAMES = 300

SKY_TOP = (10, 15, 50)
SKY_BOTTOM = (30, 40, 80)
WATER_COLOR = (20, 60, 100)
CITY_COLORS = [(0, 150, 200), (0, 200, 150), (100, 200, 255), (50, 180, 220)]
DRONE_COLORS = [(255, 200, 0), (0, 255, 200), (255, 100, 200), (100, 255, 255)]
ENERGY_COLOR = (0, 255, 150)
WINDOW_ON = (255, 255, 200)
WINDOW_OFF = (40, 60, 80)

# Ініціалізація
pygame.init()
try:
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
except Exception:
    # Безпечний режим: створити surface якщо display не доступний
    screen = pygame.Surface((WIDTH, HEIGHT))
pygame.display.set_caption("Місто Майбутнього - Україна 2150")
clock = pygame.time.Clock()

# Підготовлені ресурси, щоб не створювати кожен кадр
gradient_surf = pygame.Surface((WIDTH, HEIGHT))
def create_gradient():
    for y in range(HEIGHT):
        progress = y / HEIGHT
        r = int(SKY_TOP[0] + (SKY_BOTTOM[0] - SKY_TOP[0]) * progress)
        g = int(SKY_TOP[1] + (SKY_BOTTOM[1] - SKY_TOP[1]) * progress)
        b = int(SKY_TOP[2] + (SKY_BOTTOM[2] - SKY_TOP[2]) * progress)
        pygame.draw.line(gradient_surf, (r, g, b), (0, y), (WIDTH, y))
create_gradient()

# Загальні поверхні для розумного малювання
trails_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
particles_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)

# Шрифти створюємо один раз
FONT_TITLE = pygame.font.Font(None, 48)
FONT_SUB = pygame.font.Font(None, 24)

# Класи
class FloatingCity:
    def __init__(self, x, y, width, height, color):
        self.x = int(x)
        self.base_y = int(y)
        self.y = self.base_y
        self.width = int(width)
        self.height = int(height)
        self.color = color
        self.float_offset = random.uniform(0, math.pi * 2)
        self.float_speed = random.uniform(0.02, 0.04)
        # Вікна як відносні координати (без створення rect кожен кадр)
        self.windows = []
        window_rows = max(1, self.height // 25)
        window_cols = max(1, self.width // 20)
        for row in range(window_rows):
            for col in range(window_cols):
                if random.random() > 0.3:
                    rx = col * 20 + 5
                    ry = row * 25 + 5
                    self.windows.append([rx, ry, random.random() > 0.4, random.randint(0, 120)])
    def update(self, t):
        self.y = self.base_y + math.sin(t * self.float_speed + self.float_offset) * 8
        for w in self.windows:
            w[3] -= 1
            if w[3] <= 0:
                w[2] = random.random() > 0.3
                w[3] = random.randint(60, 180)
    def draw(self, surf):
        # тінь
        shadow = pygame.Surface((self.width + 20, 16), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow, (0,0,0,60), shadow.get_rect())
        surf.blit(shadow, (self.x - 10, int(self.y + self.height)))
        # корпус
        pygame.draw.rect(surf, self.color, (self.x, int(self.y), self.width, self.height))
        # дах
        roof_pts = [(self.x, int(self.y)), (self.x + self.width//2, int(self.y) - 20), (self.x + self.width, int(self.y))]
        roof_color = (min(255, self.color[0]+30), min(255, self.color[1]+30), min(255, self.color[2]+30))
        pygame.draw.polygon(surf, roof_color, roof_pts)
        # енергетична антена
        cx = self.x + self.width // 2
        pygame.draw.line(surf, ENERGY_COLOR, (cx, int(self.y)-20), (cx, int(self.y)-50), 3)
        pygame.draw.circle(surf, ENERGY_COLOR, (cx, int(self.y)-50), 6)
        # вікна (прямокутники)
        for w in self.windows:
            rect = (self.x + w[0], int(self.y) + w[1], 12, 15)
            pygame.draw.rect(surf, WINDOW_ON if w[2] else WINDOW_OFF, rect)

class Drone:
    def __init__(self, idx):
        self.x = random.uniform(0, WIDTH)
        self.y = random.uniform(100, HEIGHT - 200)
        self.speed_x = random.uniform(-1.8, 1.8)
        self.speed_y = random.uniform(-0.8, 0.8)
        self.color = random.choice(DRONE_COLORS)
        self.size = random.randint(7, 13)
        self.trail = []
        self.light_intensity = random.randint(30, 120)
        self.light_dir = 1
        # кешований glow surface
        gsize = self.size * 4
        self.glow = pygame.Surface((gsize, gsize), pygame.SRCALPHA)
        gc = (*self.color, 120)
        pygame.draw.circle(self.glow, gc, (gsize//2, gsize//2), gsize//2)
    def update(self):
        self.x += self.speed_x
        self.y += self.speed_y
        if self.x < -20 or self.x > WIDTH + 20:
            self.speed_x *= -1
        if self.y < 50 or self.y > HEIGHT - 150:
            self.speed_y *= -1
        self.trail.append((int(self.x), int(self.y)))
        if len(self.trail) > 12:
            self.trail.pop(0)
        self.light_intensity += self.light_dir * 6
        if self.light_intensity >= 150 or self.light_intensity <= 20:
            self.light_dir *= -1
    def draw(self, surf, trails_surface):
        # Траєкторія на спільній поверхні trails_surface
        if len(self.trail) > 1:
            points = self.trail
            for i in range(1, len(points)):
                a = int((i / len(points)) * 180)
                color = (*self.color, a)
                pygame.draw.line(trails_surface, color, points[i-1], points[i], 2)
        # Глоу та тіло
        gs = self.glow
        surf.blit(gs, (int(self.x - gs.get_width()/2), int(self.y - gs.get_height()/2)), special_flags=pygame.BLEND_ADD)
        pygame.draw.circle(surf, self.color, (int(self.x), int(self.y)), self.size)
        pygame.draw.circle(surf, (255,255,255), (int(self.x), int(self.y)), self.size, 1)
        # ротори (прості лінії)
        tick = pygame.time.get_ticks() * 0.003
        for ang in (0, math.pi/2, math.pi, 3*math.pi/2):
            rad = ang + tick
            end_x = int(self.x + math.cos(rad) * (self.size + 6))
            end_y = int(self.y + math.sin(rad) * (self.size + 6))
            pygame.draw.line(surf, (200,200,200), (int(self.x), int(self.y)), (end_x, end_y), 2)

class EnergyOrb:
    def __init__(self, x, y):
        self.x = int(x); self.y = int(y)
        self.radius = random.randint(12, 26)
        self.pulse = random.uniform(0, math.pi*2)
        self.particles = []
    def update(self):
        self.pulse = (self.pulse + 0.12) % (math.pi*2)
        if random.random() > 0.7:
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(0.6, 2.0)
            self.particles.append([self.x, self.y, math.cos(angle)*speed, math.sin(angle)*speed, random.randint(30, 70)])
        for p in self.particles[:]:
            p[0] += p[2]; p[1] += p[3]; p[4] -= 1
            if p[4] <= 0:
                self.particles.remove(p)
    def draw(self, surf, particles_surface):
        # частинки малюємо на particles_surface
        for p in self.particles:
            alpha = int((p[4]/70) * 200)
            pygame.draw.circle(particles_surface, (*ENERGY_COLOR, alpha), (int(p[0]), int(p[1])), 3)
        current_r = self.radius + math.sin(self.pulse) * 4
        # зовнішні глоу
        for i in range(3):
            radius = int(current_r + 8 - i*4)
            alpha = max(0, 40 - i*10)
            pygame.draw.circle(particles_surface, (*ENERGY_COLOR, alpha), (self.x, self.y), radius)
        pygame.draw.circle(surf, ENERGY_COLOR, (self.x, self.y), int(current_r))
        pygame.draw.circle(surf, (255,255,255), (self.x, self.y), int(current_r), 1)

class Star:
    def __init__(self):
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(0, HEIGHT//2)
        self.base = random.randint(120, 230)
        self.speed = random.uniform(0.02, 0.05)
        self.offset = random.uniform(0, math.pi*2)
        self.cur = self.base
    def update(self, t):
        tw = math.sin(t * self.speed + self.offset)
        self.cur = max(50, min(255, int(self.base + tw * 60)))
    def draw(self, surf):
        c = (self.cur, self.cur, self.cur)
        pygame.draw.circle(surf, c, (self.x, self.y), 1)

# Створення об'єктів з помірною кількістю для мобільних пристроїв
stars = [Star() for _ in range(60)]
cities = [
    FloatingCity(100, 350, 120, 180, CITY_COLORS[0]),
    FloatingCity(300, 320, 150, 220, CITY_COLORS[1]),
    FloatingCity(520, 340, 130, 200, CITY_COLORS[2]),
    FloatingCity(750, 330, 140, 190, CITY_COLORS[3]),
    FloatingCity(930, 360, 160, 210, CITY_COLORS[0]),
]
drones = [Drone(i) for i in range(12)]
energy_orbs = [EnergyOrb(150, 250), EnergyOrb(450, 230), EnergyOrb(750, 240), EnergyOrb(1000, 260)]

# Головний цикл
running = True
frame = 0
start_time = time.time()

while running and frame < MAX_FRAMES:
    t = pygame.time.get_ticks() * 0.001
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            running = False

    # Оновлення
    for s in stars: s.update(t)
    for c in cities: c.update(t)
    for d in drones: d.update()
    for o in energy_orbs: o.update()

    # Очистка екрану (копія градієнта)
    screen.blit(gradient_surf, (0,0))

    # Очистка допоміжних поверхонь
    trails_surf.fill((0,0,0,0))
    particles_surf.fill((0,0,0,0))

    # Малюємо зорі і або
    for s in stars: s.draw(screen)
    for o in energy_orbs: o.draw(screen, particles_surf)

    # Відображаємо частинки (єдиним blit'ом)
    screen.blit(particles_surf, (0,0), special_flags=pygame.BLEND_PREMULTIPLIED)

    # Міста
    for c in cities: c.draw(screen)

    # Дрони (трасування малюється на trails_surf)
    for d in drones: d.draw(screen, trails_surf)
    screen.blit(trails_surf, (0,0), special_flags=pygame.BLEND_ADD)

    # Вода
    water_y = HEIGHT - 150
    pygame.draw.rect(screen, WATER_COLOR, (0, water_y, WIDTH, 150))
    # прості хвилі, менш затратні
    wave_phase = t * 0.5
    for i in range(0, WIDTH, 40):
        y = water_y + math.sin((i * 0.04) + wave_phase) * 3
        pygame.draw.line(screen, (40,100,140), (i, y), (i+30, y), 2)
    # відблиски
    ref = pygame.Surface((WIDTH, 150), pygame.SRCALPHA)
    ref.fill((255,255,255,28))
    screen.blit(ref, (0, water_y), special_flags=pygame.BLEND_RGBA_ADD)

    # Текст
    title_text = FONT_TITLE.render("УКРАЇНА 2150 by АЛІАС", True, (0, 255, 200))
    title_shadow = FONT_TITLE.render("УКРАЇНА 2150 by АЛІАС", True, (0, 100, 100))
    screen.blit(title_shadow, (WIDTH//2 - title_text.get_width()//2 + 3, 23))
    screen.blit(title_text, (WIDTH//2 - title_text.get_width()//2, 20))
    subtitle = FONT_SUB.render("Технологічне серце Європи", True, (150,220,255))
    screen.blit(subtitle, (WIDTH//2 - subtitle.get_width()//2, 70))

    # Оновлення дисплею
    try:
        pygame.display.flip()
    except Exception:
        pass

    clock.tick(FPS)
    frame += 1
    # лог мінімальний
    if frame % 60 == 0:
        elapsed = time.time() - start_time
        print("Кадр {}/{}  FPS≈{:.1f}".format(frame, MAX_FRAMES, frame/elapsed if elapsed>0 else 0))

# Завершення
pygame.quit()
sys.exit()