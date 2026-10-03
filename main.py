# Pocket Kingdom
# A playable city-builder prototype in Python/Pygame

import math
import pygame

pygame.init()

# Config
GRID_W = 16
GRID_H = 12
CELL = 32
SIDE_PANEL = 220
SCREEN_W = GRID_W * CELL + SIDE_PANEL
SCREEN_H = GRID_H * CELL + 40

FPS = 30

BUILDINGS = {
    "house": {
        "label": "Casa",
        "cost": {"wood": 12, "stone": 8},
        "color": (233, 203, 109),
        "desc": "+2 população",
        "pop": 2,
    },
    "farm": {
        "label": "Fazenda",
        "cost": {"wood": 15, "stone": 6},
        "color": (120, 190, 110),
        "desc": "+5 comida",
        "food": 5,
    },
    "lumber": {
        "label": "Serra",
        "cost": {"wood": 10, "stone": 10},
        "color": (110, 130, 80),
        "desc": "+4 madeira",
        "wood": 4,
    },
    "quarry": {
        "label": "Pedreira",
        "cost": {"wood": 12, "stone": 8},
        "color": (160, 160, 170),
        "desc": "+4 pedra",
        "stone": 4,
    },
    "market": {
        "label": "Mercado",
        "cost": {"wood": 18, "stone": 12, "gold": 10},
        "color": (200, 150, 80),
        "desc": "+5 ouro",
        "gold": 5,
    },
    "castle": {
        "label": "Castelo",
        "cost": {"wood": 25, "stone": 30, "gold": 20},
        "color": (120, 120, 180),
        "desc": "Vitória",
        "victory": True,
    },
}

RESOURCE_LABELS = {
    "wood": "Madeira",
    "stone": "Pedra",
    "food": "Comida",
    "gold": "Ouro",
}


class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
        pygame.display.set_caption("Pocket Kingdom")
        self.clock = pygame.time.Clock()

        self.font = pygame.font.SysFont("arial", 18)
        self.font_bold = pygame.font.SysFont("arial", 20, bold=True)
        self.small_font = pygame.font.SysFont("arial", 14)

        self.grid = [[None for _ in range(GRID_W)] for _ in range(GRID_H)]
        self.resources = {"wood": 90, "stone": 80, "food": 70, "gold": 60}
        self.population = 0
        self.max_population = 0
        self.day = 1
        self.tick_time = 0.0
        self.selected = "house"
        self.message = "Bem-vindo ao Pocket Kingdom!"
        self.game_over = False
        self.victory = False
        self.placed_buildings = 0

        self.ui_buttons = []
        self._build_ui_buttons()

    def _build_ui_buttons(self):
        x = GRID_W * CELL + 20
        y = 100
        for i, (key, data) in enumerate(BUILDINGS.items()):
            rect = pygame.Rect(x, y, 170, 42)
            self.ui_buttons.append({"key": key, "rect": rect})
            y += 50

    def can_afford(self, building_key):
        if building_key not in BUILDINGS:
            return False
        costs = BUILDINGS[building_key]["cost"]
        for resource, amount in costs.items():
            if self.resources.get(resource, 0) < amount:
                return False
        return True

    def pay_costs(self, building_key):
        if not self.can_afford(building_key):
            return False
        for resource, amount in BUILDINGS[building_key]["cost"].items():
            self.resources[resource] -= amount
        return True

    def place_building(self, cell_x, cell_y):
        if cell_x < 0 or cell_x >= GRID_W or cell_y < 0 or cell_y >= GRID_H:
            return
        if self.grid[cell_y][cell_x] is not None:
            self.message = "Local ocupado."
            return
        if not self.pay_costs(self.selected):
            self.message = "Recursos insuficientes."
            return

        self.grid[cell_y][cell_x] = self.selected
        self.placed_buildings += 1

        # Effects
        if self.selected == "house":
            self.max_population += 2
            self.population += 2
        elif self.selected == "farm":
            self.message = "Fazenda construída."
        elif self.selected == "market":
            self.message = "Mercado aberto."
        elif self.selected == "castle":
            self.victory = True
            self.game_over = True
            self.message = "Castelo construído! Você venceu!"
        else:
            self.message = f"{BUILDINGS[self.selected]['label']} construída."

    def remove_building(self, cell_x, cell_y):
        if cell_x < 0 or cell_x >= GRID_W or cell_y < 0 or cell_y >= GRID_H:
            return
        building = self.grid[cell_y][cell_x]
        if building is None:
            return
        self.grid[cell_y][cell_x] = None

        if building == "house":
            self.population = max(0, self.population - 2)
            self.max_population = max(0, self.max_population - 2)
        self.message = f"{BUILDINGS[building]['label']} removido."

    def simulate_tick(self):
        if self.game_over:
            return

        food_gain = 0
        wood_gain = 0
        stone_gain = 0
        gold_gain = 0

        for y in range(GRID_H):
            for x in range(GRID_W):
                b = self.grid[y][x]
                if b is None:
                    continue
                data = BUILDINGS[b]
                if "food" in data:
                    food_gain += data["food"]
                if "wood" in data:
                    wood_gain += data["wood"]
                if "stone" in data:
                    stone_gain += data["stone"]
                if "gold" in data:
                    gold_gain += data["gold"]

        self.resources["food"] += max(0, food_gain - max(0, self.population - self.max_population))
        self.resources["wood"] += wood_gain
        self.resources["stone"] += stone_gain
        self.resources["gold"] += gold_gain

        # Keep resources from going below zero
        for res in ["food", "wood", "stone", "gold"]:
            self.resources[res] = max(0, self.resources[res])

        # Ensure food doesn't vanish
        if self.resources["food"] <= 0 and self.population > 0:
            self.population = max(0, self.population - 1)
            self.message = "Há escassez de comida!"

        self.day += 1
        self.tick_time = 0.0

        if self.population >= 20 and self.resources["gold"] >= 100:
            self.message = "Seu reino está prosperando!"

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = pygame.mouse.get_pos()
            if pos[0] < GRID_W * CELL:
                cell_x = pos[0] // CELL
                cell_y = pos[1] // CELL
                if event.button == 1:
                    self.place_building(cell_x, cell_y)
                elif event.button == 3:
                    self.remove_building(cell_x, cell_y)
            else:
                for btn in self.ui_buttons:
                    if btn["rect"].collidepoint(pos):
                        self.selected = btn["key"]
                        self.message = f"Selecionado: {BUILDINGS[self.selected]['label']}"
                        break

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.game_over = True
            elif event.key == pygame.K_1:
                self.selected = "house"
            elif event.key == pygame.K_2:
                self.selected = "farm"
            elif event.key == pygame.K_3:
                self.selected = "lumber"
            elif event.key == pygame.K_4:
                self.selected = "quarry"
            elif event.key == pygame.K_5:
                self.selected = "market"
            elif event.key == pygame.K_6:
                self.selected = "castle"

    def draw_tile(self, x, y, color):
        pygame.draw.rect(self.screen, color, (x * CELL, y * CELL, CELL, CELL))
        pygame.draw.rect(self.screen, (40, 60, 40), (x * CELL, y * CELL, CELL, CELL), 1)

    def draw_building(self, x, y, key):
        color = BUILDINGS[key]["color"]
        rect = pygame.Rect(x * CELL + 6, y * CELL + 6, CELL - 12, CELL - 12)
        pygame.draw.rect(self.screen, color, rect)
        pygame.draw.rect(self.screen, (0, 0, 0), rect, 2)

    def draw_ui(self):
        sidebar_x = GRID_W * CELL
        pygame.draw.rect(self.screen, (35, 35, 45), (sidebar_x, 0, SIDE_PANEL, SCREEN_H))
        pygame.draw.rect(self.screen, (55, 55, 70), (sidebar_x, 0, SIDE_PANEL, 80))

        title = self.font_bold.render("Pocket Kingdom", True, (255, 255, 255))
        self.screen.blit(title, (sidebar_x + 18, 18))

        # Resource panel
        y = 90
        for res, label in RESOURCE_LABELS.items():
            value = self.resources.get(res, 0)
            surf = self.font.render(f"{label}: {value}", True, (255, 255, 255))
            self.screen.blit(surf, (sidebar_x + 12, y))
            y += 24

        self.screen.blit(self.font.render(f"População: {self.population}/{self.max_population}", True, (255, 255, 255)),
                         (sidebar_x + 12, y))
        y += 30
        self.screen.blit(self.font.render(f"Dia: {self.day}", True, (255, 255, 255)), (sidebar_x + 12, y))

        # Buttons
        for btn in self.ui_buttons:
            key = btn["key"]
            rect = btn["rect"]
            selected = self.selected == key
            bg = (80, 120, 90) if selected else (90, 90, 100)
            pygame.draw.rect(self.screen, bg, rect)
            pygame.draw.rect(self.screen, (200, 200, 200), rect, 2)
            label = self.font.render(BUILDINGS[key]["label"], True, (255, 255, 255))
            self.screen.blit(label, (rect.x + 8, rect.y + 10))

            cost_text = ", ".join(f"{k}:{v}" for k, v in BUILDINGS[key]["cost"].items())
            cost_surf = self.small_font.render(cost_text, True, (220, 220, 220))
            self.screen.blit(cost_surf, (rect.x + 8, rect.y + 25))

        # Selected summary
        y = 580
        pygame.draw.rect(self.screen, (70, 70, 80), (sidebar_x + 10, y, 200, 100))
        selected_data = BUILDINGS[self.selected]
        text = self.font.render(f"Selecionado: {selected_data['label']}", True, (255, 255, 255))
        self.screen.blit(text, (sidebar_x + 18, y + 10))
        desc = self.font.render(selected_data["desc"], True, (255, 255, 255))
        self.screen.blit(desc, (sidebar_x + 18, y + 38))

        # Messages
        pygame.draw.rect(self.screen, (20, 20, 30), (0, GRID_H * CELL + 2, SCREEN_W, 38))
        msg = self.font.render(self.message, True, (255, 255, 255))
        self.screen.blit(msg, (12, GRID_H * CELL + 10))

    def draw_grid(self):
        for y in range(GRID_H):
            for x in range(GRID_W):
                self.draw_tile(x, y, (90, 150, 90))
                if (x + y) % 2 == 0:
                    self.draw_tile(x, y, (78, 138, 78))
        for y in range(GRID_H):
            for x in range(GRID_W):
                if self.grid[y][x]:
                    self.draw_building(x, y, self.grid[y][x])

    def render(self):
        self.screen.fill((20, 20, 25))
        self.draw_grid()
        self.draw_ui()
        pygame.display.flip()

    def run(self):
        running = True
        while running:
            dt = self.clock.tick(FPS) / 1000.0
            self.tick_time += dt

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                else:
                    self.handle_event(event)

            if self.tick_time >= 2.0:
                self.simulate_tick()

            if self.game_over:
                if self.victory:
                    self.message = "Vitória! O reino foi conquistado!"
                else:
                    self.message = "Jogo encerrado."
                running = False

            self.render()

        pygame.quit()


def main():
    game = Game()
    game.run()


if __name__ == "__main__":
    main()
