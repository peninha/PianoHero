import pygame
import pygame.midi
import mido
import numpy as np

# Inicializando o pygame e o pygame.midi
pygame.init()
pygame.midi.init()

# Definindo a largura e a altura da janela

#Screen setup
WIDTH, HEIGHT = 254, 600

#Piano setup
whitekey_height = 100
whitekey_width = 30
whitekey_separation = 2
blackkey_height = 60
blackkey_width = 20
keys_y = HEIGHT - whitekey_height

#notes setup
#note_width = 20  # Largura da nota
note_color = np.array([200, 50, 0])  # Cor da nota
note_fall_speed = 100  # Velocidade de queda das notas [px/s]

###########################
win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Piano Hero")

def note_to_midi(note):
    note_names = {'C':0,'C#':1,'D':2,'D#':3,'E':4,'F':5,'F#':6,'G':7,'G#':8,'A':9,'A#':10,'B':11}
    octave = int(note[-1])
    note_name = note[:-1]
    return 12 * (octave + 1) + note_names[note_name]

def midi_to_note(midi):
    note_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    note_name = note_names[midi % 12]
    octave = midi // 12 - 1
    return f"{note_name}{octave}"

class Note:
    def __init__(self, note, t, time_on, time_off, strength, fall_speed=note_fall_speed, color=note_color):
        self.t0 = time_on
        self.t1 = time_off
        self.note = note
        self.note_ID = note_to_midi(self.note)
        self.note_name = self.note[:-1]
        self.octave = int(self.note[-1])
        self.note_type = self.calculate_type(self.note_name)
        self.strength = strength
        self.fall_speed = fall_speed
        self.color = self.calculate_color(color)
        self.width = self.calculate_width(self.note_type)
        self.x_coord = self.calculate_x_coord()
        self.y_coord = self.calculate_y_coord(t)
        self.duration = self.t1 - self.t0
        self.height = self.duration * self.fall_speed
    
    def calculate_color(self, color):
        if self.note_type == "black":
            darken = np.array([-30, -30, 0])
            return np.clip(color + darken, 0, 255)
        return color
    
    def calculate_type(self, note_name):
        if note_name[-1] == "#":
            return "black"
        return "white"
    
    def calculate_width(self, note_type):
        if note_type == "black":
            return blackkey_width
        return whitekey_width
    
    def calculate_x_coord(self):
        # Cálculo da posição x com base na nota
        extra = 1
        if self.note_ID - 60 > 4:
            extra += 1
        if self.note_ID - 60 > 11:
            extra += 1
        return ((self.note_ID - 60) + extra) * (whitekey_width + whitekey_separation) / 2
    
    def calculate_y_coord(self, t):
        # Calcula a posição y com base no tempo decorrido
        return self.fall_speed * (t - self.t0)
    
    def position_update(self, t):
        self.y_coord = self.calculate_y_coord(t)
    
    def remove(self, height):
        return self.y_coord > height
    
    def draw(self, window):
        rect_x_coord = self.x_coord - self.width / 2
        rect_y_coord = self.y_coord - self.height
        note_rect = pygame.Rect(rect_x_coord, rect_y_coord, self.width, self.height)  # Ajuste a escala conforme necessário
        #print(f"Drawing note at x: {rect_x_coord}, y: {rect_y_coord}, width: {self.width}, height: {self.height}")
        pygame.draw.rect(window, tuple(self.color.astype(int)), note_rect)

def getTime(start_ticks):
    return (pygame.time.get_ticks() - start_ticks) / 1000

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
    {'note': 'C4', 'key': 'A', 'color': (255, 255, 255), 'pressed_color': (200, 200, 200), 'rect': pygame.Rect(0 * (whitekey_width + whitekey_separation), keys_y, whitekey_width, whitekey_height), 'pressed': False},
    {'note': 'D4', 'key': 'S', 'color': (255, 255, 255), 'pressed_color': (200, 200, 200), 'rect': pygame.Rect(1 * (whitekey_width + whitekey_separation), keys_y, whitekey_width, whitekey_height), 'pressed': False},
    {'note': 'E4', 'key': 'D', 'color': (255, 255, 255), 'pressed_color': (200, 200, 200), 'rect': pygame.Rect(2 * (whitekey_width + whitekey_separation), keys_y, whitekey_width, whitekey_height), 'pressed': False},
    {'note': 'F4', 'key': 'F', 'color': (255, 255, 255), 'pressed_color': (200, 200, 200), 'rect': pygame.Rect(3 * (whitekey_width + whitekey_separation), keys_y, whitekey_width, whitekey_height), 'pressed': False},
    {'note': 'G4', 'key': 'G', 'color': (255, 255, 255), 'pressed_color': (200, 200, 200), 'rect': pygame.Rect(4 * (whitekey_width + whitekey_separation), keys_y, whitekey_width, whitekey_height), 'pressed': False},
    {'note': 'A4', 'key': 'H', 'color': (255, 255, 255), 'pressed_color': (200, 200, 200), 'rect': pygame.Rect(5 * (whitekey_width + whitekey_separation), keys_y, whitekey_width, whitekey_height), 'pressed': False},
    {'note': 'B4', 'key': 'J', 'color': (255, 255, 255), 'pressed_color': (200, 200, 200), 'rect': pygame.Rect(6 * (whitekey_width + whitekey_separation), keys_y, whitekey_width, whitekey_height), 'pressed': False},
    {'note': 'C5', 'key': 'K', 'color': (255, 255, 255), 'pressed_color': (200, 200, 200), 'rect': pygame.Rect(7 * (whitekey_width + whitekey_separation), keys_y, whitekey_width, whitekey_height), 'pressed': False},
    {'note': 'C#4', 'key': 'W', 'color': (0, 0, 0), 'pressed_color': (50, 50, 50), 'rect': pygame.Rect(1 * (whitekey_width + whitekey_separation) - (blackkey_width + whitekey_separation)/2, keys_y, blackkey_width, blackkey_height), 'pressed': False},
    {'note': 'D#4', 'key': 'E', 'color': (0, 0, 0), 'pressed_color': (50, 50, 50), 'rect': pygame.Rect(2 * (whitekey_width + whitekey_separation) - (blackkey_width + whitekey_separation)/2, keys_y, blackkey_width, blackkey_height), 'pressed': False},
    {'note': 'F#4', 'key': 'T', 'color': (0, 0, 0), 'pressed_color': (50, 50, 50), 'rect': pygame.Rect(4 * (whitekey_width + whitekey_separation) - (blackkey_width + whitekey_separation)/2, keys_y, blackkey_width, blackkey_height), 'pressed': False},
    {'note': 'G#4', 'key': 'Y', 'color': (0, 0, 0), 'pressed_color': (50, 50, 50), 'rect': pygame.Rect(5 * (whitekey_width + whitekey_separation) - (blackkey_width + whitekey_separation)/2, keys_y, blackkey_width, blackkey_height), 'pressed': False},
    {'note': 'A#4', 'key': 'U', 'color': (0, 0, 0), 'pressed_color': (50, 50, 50), 'rect': pygame.Rect(6 * (whitekey_width + whitekey_separation) - (blackkey_width + whitekey_separation)/2, keys_y, blackkey_width, blackkey_height), 'pressed': False},
]

# Função principal
def main():
    run = True
    clock = pygame.time.Clock()
    
    # Carregar arquivo MIDI
    midi_file = 'midi/asa_branca.mid'
    midi_data = mido.MidiFile(midi_file)

    # Lista para armazenar as notas em queda
    future_notes = []
    screen_notes = []

    # Converter as notas MIDI para o formato adequado
    for track in midi_data.tracks:
        time = 0
        note_list = {}
        for msg in track:
            time += msg.time
            if msg.type == 'note_on':
                note_list[msg.note] = {"time_on": time, "velocity": msg.velocity}
            elif msg.type == 'note_off':
                if msg.note in note_list:
                    future_notes.append({
                        'note': midi_to_note(msg.note),
                        'time_on': note_list[msg.note]["time_on"]/1000,
                        'time_off': time/1000 - 0.02,
                        'strength': note_list[msg.note]["velocity"]})
                    del note_list[msg.note]

    #print(midi_data.tracks)
    print(future_notes)
    """
    future_notes = [
        {'note': 'C4', 'time_on': 0.3, 'time_off': 1, 'strength': 100},
        {'note': 'C#4', 'time_on': 0.5, 'time_off': 1.5, 'strength': 100},
        {'note': 'D4', 'time_on': 1, 'time_off': 2, 'strength': 100},
        {'note': 'D#4', 'time_on': 1.5, 'time_off': 2.5, 'strength': 100},
        {'note': 'E4', 'time_on': 2, 'time_off': 3, 'strength': 100},
        {'note': 'F4', 'time_on': 2.5, 'time_off': 3.5, 'strength': 100},
        {'note': 'F#4', 'time_on': 3, 'time_off': 4, 'strength': 100},
        {'note': 'G4', 'time_on': 3.5, 'time_off': 4.5, 'strength': 100},
        {'note': 'G#4', 'time_on': 4, 'time_off': 5, 'strength': 100},
        {'note': 'A4', 'time_on': 4.5, 'time_off': 5.5, 'strength': 100},
        {'note': 'A#4', 'time_on': 5, 'time_off': 6, 'strength': 100},
        {'note': 'B4', 'time_on': 5.5, 'time_off': 6.5, 'strength': 100},
        {'note': 'C5', 'time_on': 6, 'time_off': 7, 'strength': 100},
    ]
    print(future_notes)
    """
    start_ticks = pygame.time.get_ticks()  # Tempo inicial
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

        while future_notes:
            new_note = future_notes[0]  # Verifica o primeiro elemento
            if getTime(start_ticks) < new_note['time_on']:
                break  # Pára de desenhar as notas que ainda estão no futuro
            else:
                note = Note(
                    note=new_note['note'],
                    t=getTime(start_ticks),
                    time_on=new_note['time_on'],
                    time_off=new_note['time_off'],
                    strength=new_note['strength']
                )
                screen_notes.append(note)
                future_notes.pop(0)  # Remove o primeiro elemento da lista

        # Atualizar e desenhar as notas em queda
        for screen_note in screen_notes:
            screen_note.position_update(getTime(start_ticks))
            screen_note.draw(win)

        # Desenhar as teclas do piano
        for key in keys:
            color = key['pressed_color'] if key['pressed'] else key['color']
            pygame.draw.rect(win, color, key['rect'])

        pygame.display.update()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()
