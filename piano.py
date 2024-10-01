import pygame
import pygame.midi
import mido

# Inicializando o pygame e o pygame.midi
pygame.init()
pygame.midi.init()

# Definindo a largura e a altura da janela
WIDTH, HEIGHT = 254, 600
whitekey_height = 100
whitekey_width = 30
whitekey_separation = 2
blackkey_height = 60
blackkey_width = 20
keys_y = HEIGHT - whitekey_height
win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Piano Hero")

# Carregar sons de piano (substitua pelos caminhos corretos dos arquivos de som)
sounds = {
    'A': pygame.mixer.Sound("sounds/C.wav"),
    'W': pygame.mixer.Sound("sounds/C#.wav"),
    'S': pygame.mixer.Sound("sounds/D.wav"),
    'E': pygame.mixer.Sound("sounds/D#.wav"),
    'D': pygame.mixer.Sound("sounds/E.wav"),
    'F': pygame.mixer.Sound("sounds/F.wav"),
    'T': pygame.mixer.Sound("sounds/F#.wav"),
    'G': pygame.mixer.Sound("sounds/G.wav"),
    'Y': pygame.mixer.Sound("sounds/G#.wav"),
    'H': pygame.mixer.Sound("sounds/A.wav"),
    'U': pygame.mixer.Sound("sounds/A#.wav"),
    'J': pygame.mixer.Sound("sounds/B.wav"),
    'K': pygame.mixer.Sound("sounds/C2.wav")
}

# Definindo as teclas do piano e as cores
keys = [
    {'note': 'C', 'key': 'A', 'color': (255, 255, 255), 'pressed_color': (200, 200, 200), 'rect': pygame.Rect(0 * (whitekey_width + whitekey_separation), keys_y, whitekey_width, whitekey_height), 'pressed': False},
    {'note': 'D', 'key': 'S', 'color': (255, 255, 255), 'pressed_color': (200, 200, 200), 'rect': pygame.Rect(1 * (whitekey_width + whitekey_separation), keys_y, whitekey_width, whitekey_height), 'pressed': False},
    {'note': 'E', 'key': 'D', 'color': (255, 255, 255), 'pressed_color': (200, 200, 200), 'rect': pygame.Rect(2 * (whitekey_width + whitekey_separation), keys_y, whitekey_width, whitekey_height), 'pressed': False},
    {'note': 'F', 'key': 'F', 'color': (255, 255, 255), 'pressed_color': (200, 200, 200), 'rect': pygame.Rect(3 * (whitekey_width + whitekey_separation), keys_y, whitekey_width, whitekey_height), 'pressed': False},
    {'note': 'G', 'key': 'G', 'color': (255, 255, 255), 'pressed_color': (200, 200, 200), 'rect': pygame.Rect(4 * (whitekey_width + whitekey_separation), keys_y, whitekey_width, whitekey_height), 'pressed': False},
    {'note': 'A', 'key': 'H', 'color': (255, 255, 255), 'pressed_color': (200, 200, 200), 'rect': pygame.Rect(5 * (whitekey_width + whitekey_separation), keys_y, whitekey_width, whitekey_height), 'pressed': False},
    {'note': 'B', 'key': 'J', 'color': (255, 255, 255), 'pressed_color': (200, 200, 200), 'rect': pygame.Rect(6 * (whitekey_width + whitekey_separation), keys_y, whitekey_width, whitekey_height), 'pressed': False},
    {'note': 'C2', 'key': 'K', 'color': (255, 255, 255), 'pressed_color': (200, 200, 200), 'rect': pygame.Rect(7 * (whitekey_width + whitekey_separation), keys_y, whitekey_width, whitekey_height), 'pressed': False},
    {'note': 'C#', 'key': 'W', 'color': (0, 0, 0), 'pressed_color': (50, 50, 50), 'rect': pygame.Rect(1 * (whitekey_width + whitekey_separation) - (blackkey_width + whitekey_separation)/2, keys_y, blackkey_width, blackkey_height), 'pressed': False},
    {'note': 'D#', 'key': 'E', 'color': (0, 0, 0), 'pressed_color': (50, 50, 50), 'rect': pygame.Rect(2 * (whitekey_width + whitekey_separation) - (blackkey_width + whitekey_separation)/2, keys_y, blackkey_width, blackkey_height), 'pressed': False},
    {'note': 'F#', 'key': 'T', 'color': (0, 0, 0), 'pressed_color': (50, 50, 50), 'rect': pygame.Rect(4 * (whitekey_width + whitekey_separation) - (blackkey_width + whitekey_separation)/2, keys_y, blackkey_width, blackkey_height), 'pressed': False},
    {'note': 'G#', 'key': 'Y', 'color': (0, 0, 0), 'pressed_color': (50, 50, 50), 'rect': pygame.Rect(5 * (whitekey_width + whitekey_separation) - (blackkey_width + whitekey_separation)/2, keys_y, blackkey_width, blackkey_height), 'pressed': False},
    {'note': 'A#', 'key': 'U', 'color': (0, 0, 0), 'pressed_color': (50, 50, 50), 'rect': pygame.Rect(6 * (whitekey_width + whitekey_separation) - (blackkey_width + whitekey_separation)/2, keys_y, blackkey_width, blackkey_height), 'pressed': False},
]

# Carregar arquivo MIDI
midi_file = 'midi/example_02.mid'
midi_data = mido.MidiFile(midi_file)

# Lista para armazenar as notas em queda
falling_notes = []

# Converter as notas MIDI para o formato adequado
for track in midi_data.tracks:
    time = 0
    note_on_times = {}
    for msg in track:
        time += msg.time
        if msg.type == 'note_on' and msg.velocity > 0:
            note_on_times[msg.note] = time
        elif msg.type == 'note_off' or (msg.type == 'note_on' and msg.velocity == 0):
            if msg.note in note_on_times:
                note = msg.note
                start_time = note_on_times[note]
                duration = time - start_time
                # Mapeamento da nota MIDI para o índice da tecla
                key_index = note % 12  # Supondo que você tenha as notas de 0 a 11
                if 0 <= key_index < len(keys):
                    falling_notes.append({'key_index': key_index, 'start_time': start_time, 'duration': duration, 'y': 0})
                del note_on_times[note]

print(midi_data.tracks)
print(falling_notes)

# Função principal
def main():
    run = True
    clock = pygame.time.Clock()
    falling_speed = 1  # Velocidade de queda das notas

    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            elif event.type == pygame.KEYDOWN:
                for key in keys:
                    if event.unicode.upper() == key['key']:
                        sounds[key['key']].play()
                        key['pressed'] = True
            elif event.type == pygame.KEYUP:
                for key in keys:
                    if event.unicode.upper() == key['key']:
                        key['pressed'] = False

        win.fill((0, 0, 0))  # Limpar a tela com fundo preto

        # Desenhar as teclas do piano
        for key in keys:
            color = key['pressed_color'] if key['pressed'] else key['color']
            pygame.draw.rect(win, color, key['rect'])

        # Atualizar e desenhar as notas em queda
        for note in falling_notes:
            note_rect = pygame.Rect(keys[note['key_index']]['rect'].x, note['y'], keys[note['key_index']]['rect'].width, note['duration'] / 10)  # Ajuste a escala conforme necessário
            pygame.draw.rect(win, (0, 255, 0), note_rect)
            note['y'] += falling_speed
            if note['y'] > HEIGHT:
                falling_notes.remove(note)

        pygame.display.update()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()
