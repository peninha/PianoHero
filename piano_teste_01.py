import pygame
import numpy as np

# Inicializando o pygame
pygame.init()

# Definindo a largura e a altura da janela
WIDTH, HEIGHT = 400, 300
win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Piano Test")

# Definindo a cor do fundo
background_color = (0, 0, 0)

# Configurando a fonte para o texto
font_name = pygame.font.get_default_font()
font = pygame.font.Font(font_name, 36)

# Definindo as teclas do piano e os canais
key_sounds = {
    'Z': "sounds/C.wav",
    'X': "sounds/D.wav",
    'C': "sounds/E.wav",
    'V': "sounds/F.wav",
    'B': "sounds/G.wav"
}

# Inicializar canais
pygame.mixer.set_num_channels(len(key_sounds))
channels = {key: pygame.mixer.Channel(i) for i, key in enumerate(key_sounds.keys())}

# Carregar sons de piano
sounds = {key: pygame.mixer.Sound(file) for key, file in key_sounds.items()}

def draw_text(surface, text, font, color, x, y):
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    text_rect.topleft = (x, y)
    surface.blit(text_surface, text_rect)

def play_sound_with_fade(sound, channel, fade_in_time=1):
    channel.play(sound, fade_ms=fade_in_time)

def stop_sound_with_fade(channel, fade_out_time=200):
    channel.fadeout(fade_out_time)

# Função principal
def main():
    run = True
    clock = pygame.time.Clock()

    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            elif event.type == pygame.KEYDOWN:
                key = event.unicode.upper()
                if key in sounds:
                    play_sound_with_fade(sounds[key], channels[key])
            elif event.type == pygame.KEYUP:
                key = event.unicode.upper()
                if key in sounds:
                    stop_sound_with_fade(channels[key])

        win.fill(background_color)  # Limpar a tela com fundo preto

        # Desenhar as instruções
        draw_text(win, "Press Z, X, C, V, B to play sounds", font, (255, 255, 255), 20, 20)
        draw_text(win, "Hold to sustain, release to stop", font, (255, 255, 255), 20, 60)
        
        pygame.display.update()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()
