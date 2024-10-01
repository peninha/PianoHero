import pygame
import random
import numpy as np

# Inicializando o pygame
pygame.init()

# Configuração da tela
WIDTH, HEIGHT = 800, 600
win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Test Effects")

# Classe Particle
class Particle:
    def __init__(self, x, y, color, life, size, velocity):
        self.x = x
        self.y = y
        self.original_color = color
        self.color = color
        self.life = life
        self.size = size
        self.velocity = velocity

    def update(self):
        self.x += self.velocity[0]
        self.y += self.velocity[1]
        self.life -= 1
        fade_factor = self.life / 100
        self.color = (
            int(self.original_color[0] * fade_factor),
            int(self.original_color[1] * fade_factor),
            int(self.original_color[2] * fade_factor)
        )

    def draw(self, surface):
        if self.life > 0:
            pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.size)

# Classe Efeitos
class Efeitos:
    def __init__(self):
        self.effects = []

    def add_faiscas_ascendentes(self, x, y, color, size, count=10):
        for _ in range(count):
            velocity = [random.uniform(-0.5, 0.5), random.uniform(-1.5, -0.5)]
            self.effects.append(Particle(x, y, color, 100, size, velocity))

    def add_explosao_de_particulas(self, x, y, color, size, count=10):
        for _ in range(count):
            velocity = [random.uniform(-1, 1), random.uniform(-1, 1)]
            self.effects.append(Particle(x, y, color, 100, size, velocity))

    def add_glow(self, x, y, color, radius):
        for angle in range(180, 361, 10):
            radian = np.radians(angle)
            velocity = [np.cos(radian) * 0.5, np.sin(radian) * 0.5]
            self.effects.append(Particle(x, y, color, 100, radius, velocity))

    def update(self):
        for effect in self.effects[:]:
            effect.update()
            if effect.life <= 0:
                self.effects.remove(effect)

    def draw(self, surface):
        for effect in self.effects:
            effect.draw(surface)

        # Desenhar o glow como uma aura circular
        for effect in self.effects:
            if isinstance(effect, Particle):
                fade_radius = effect.size
                for i in range(1, fade_radius):
                    pygame.draw.circle(
                        surface,
                        (
                            effect.color[0],
                            effect.color[1],
                            effect.color[2],
                            max(0, int(255 * (1 - i / fade_radius)))
                        ),
                        (int(effect.x), int(effect.y)),
                        i,
                        1
                    )

# Função principal
def main():
    run = True
    clock = pygame.time.Clock()
    efeitos = Efeitos()
    
    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_a:
                    efeitos.add_faiscas_ascendentes(WIDTH // 2, HEIGHT // 2, (255, 255, 0), 5, 20)
                elif event.key == pygame.K_b:
                    efeitos.add_explosao_de_particulas(WIDTH // 2, HEIGHT // 2, (255, 0, 0), 5, 20)
                elif event.key == pygame.K_c:
                    efeitos.add_glow(WIDTH // 2, HEIGHT // 2, (0, 255, 255), 1)
        
        win.fill((0, 0, 0))
        efeitos.update()
        efeitos.draw(win)
        pygame.display.update()
        clock.tick(60)
    
    pygame.quit()

if __name__ == "__main__":
    main()
