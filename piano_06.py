import pygame
import pygame.midi
import mido
import numpy as np
import random
import os

# Inicializando o pygame e o pygame.midi
pygame.init()
pygame.midi.init()

# Definindo a largura e a altura da janela
WIDTH, HEIGHT = 800, 600  # Ajuste a largura para acomodar mais teclas se necessário
font_size = 36

# Piano setup
whitekey_height = 100
whitekey_width = 30
whitekey_separation = 2
blackkey_height = 60
blackkey_width = 20
keys_y = HEIGHT - whitekey_height
endline_y_coord = HEIGHT - whitekey_height
lowest_note = "A1"
highest_note = "D5"


# Notes setup
note_color = np.array([255, 100, 50])  # Cor da nota
note_darken = np.array([-40, -40, -40]) # Grau do escurecimento para teclas pretas
note_fall_speed = 100  # Velocidade de queda das notas [px/s]
press_time_tolerance = 0.2 # Tolerância em segundos
press_distance_tolerance = note_fall_speed * press_time_tolerance

###########################
win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Piano Hero")
font_name = pygame.font.get_default_font()
font = pygame.font.Font(font_name, font_size)

# Funções de conversão de nota
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

# Classe Note
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
        self.gone = False
    
    def calculate_color(self, color):
        if self.note_type == "black":
            return np.clip(color + note_darken, 0, 255)
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
        if self.y_coord - self.height >= endline_y_coord:
            self.gone = True
    
    def draw(self, window):
        rect_x_coord = self.x_coord - self.width / 2
        rect_y_coord = self.y_coord - self.height
        note_rect = pygame.Rect(rect_x_coord, rect_y_coord, self.width, self.height)
        pygame.draw.rect(window, tuple(self.color.astype(int)), note_rect)

# Classe Particle
class Particle:
    def __init__(self, x, y, color, life, direction):
        self.x = x
        self.y = y
        self.color = color
        self.life = life
        self.direction = direction
        self.velocity = [random.uniform(-1, 1) for _ in range(2)]

    def update(self):
        self.x += self.velocity[0] * self.direction
        self.y += self.velocity[1] * self.direction
        self.life -= 1

    def draw(self, surface):
        if self.life > 0:
            pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), 3)

# Classe EffectManager
class EffectManager:
    def __init__(self):
        self.effects = []

    def add_particles(self, x, y, color, count=10):
        for _ in range(count):
            direction = random.choice([-1, 1])
            self.effects.append(Particle(x, y, color, 100, direction))

    def update(self):
        for effect in self.effects[:]:
            effect.update()
            if effect.life <= 0:
                self.effects.remove(effect)

    def draw(self, surface):
        for effect in self.effects:
            effect.draw(surface)

# Classe Piano
class Piano:
    def __init__(self, start_note, end_note):
        self.start_note = start_note
        self.end_note = end_note
        self.keys = self.generate_keys()
        self.key_map = self.generate_key_map()
        self.channels = {key: pygame.mixer.Channel(i) for i, key in enumerate(self.key_map.keys())}
        self.sounds = self.load_sounds()

    def get_note_x_coord(self, note):
        for key in self.keys:
            if key['note'] == note:
                return key['x_coord']
        return None

    def generate_keys(self):
        keys = []
        start_midi = note_to_midi(self.start_note)
        end_midi = note_to_midi(self.end_note)
        white_key_count = 0
        
        for midi_note in range(start_midi, end_midi + 1):
            note = midi_to_note(midi_note)
            note_type = "white" if len(note) == 2 else "black"
            color = (255, 255, 255) if note_type == "white" else (0, 0, 0)
            pressed_color = (200, 200, 200) if note_type == "white" else (50, 50, 50)
            width = whitekey_width if note_type == "white" else blackkey_width
            height = whitekey_height if note_type == "white" else blackkey_height
            x = white_key_count * (whitekey_width + whitekey_separation) if note_type == "white" else white_key_count * (whitekey_width + whitekey_separation) - (blackkey_width + whitekey_separation)/2
            
            keys.append({
                'note': note,
                'color': color,
                'pressed_color': pressed_color,
                'rect': pygame.Rect(x, keys_y, width, height),
                'pressed': False,
                'x_coord': x
            })
            
            if note_type == "white":
                white_key_count += 1
        
        return keys

    def generate_key_map(self):
        key_map = {}
        keys = "ZXCVBNM,./ASDFGHJKL;'QWERTYUIOP[]"
        for i, key in enumerate(keys):
            if i < len(self.keys):
                key_map[key] = self.keys[i]
        return key_map

    def load_sounds(self):
        sounds = {}
        for key, value in self.key_map.items():
            note = value['note']
            sound_path = f"sounds/S&S_AT2035_XY_Angle_Dn_PD_101_114_{note}.wav"
            if os.path.exists(sound_path):
                sounds[key] = pygame.mixer.Sound(sound_path)
            else:
                print(f"Sound file for {note} not found at {sound_path}")
        return sounds

    def draw(self, window):
        # Desenhar teclas brancas primeiro
        for key in self.keys:
            if len(key['note']) == 2:  # Teclas brancas têm nome de nota com 2 caracteres
                color = key['pressed_color'] if key['pressed'] else key['color']
                pygame.draw.rect(window, color, key['rect'])
        
        # Desenhar teclas pretas depois
        for key in self.keys:
            if len(key['note']) == 3:  # Teclas pretas têm nome de nota com 3 caracteres
                color = key['pressed_color'] if key['pressed'] else key['color']
                pygame.draw.rect(window, color, key['rect'])


    def press_key(self, key_char):
        if key_char in self.key_map:
            self.key_map[key_char]['pressed'] = True
            if key_char in self.sounds:
                self.channels[key_char].play(self.sounds[key_char], fade_ms=1)

    def release_key(self, key_char):
        if key_char in self.key_map:
            self.key_map[key_char]['pressed'] = False
            if key_char in self.sounds:
                self.channels[key_char].fadeout(200)
    

# Função para obter o tempo decorrido
def getTime(start_ticks):
    return (pygame.time.get_ticks() - start_ticks) / 1000

# Função para desenhar texto na tela
def draw_text(surface, text, font, color, x, y):
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    text_rect.topleft = (x, y)
    surface.blit(text_surface, text_rect)

# Instância do gerenciador de efeitos
effect_manager = EffectManager()


total_notes = note_to_midi(highest_note) - note_to_midi(lowest_note) + 1
pygame.mixer.set_num_channels(total_notes)

# Função principal
def main():
    run = True
    clock = pygame.time.Clock()
    score = 0
    
    # Carregar arquivo MIDI
    midi_file = 'midi/hung_rhap_n2.mid'
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
                        'time_off': time/1000 - 0.03,
                        'strength': note_list[msg.note]["velocity"]})
                    del note_list[msg.note]

    # Instância do piano
    piano = Piano(lowest_note, highest_note)

    start_ticks = pygame.time.get_ticks()  # Tempo inicial
    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            elif event.type == pygame.KEYDOWN:
                key = event.unicode.upper()
                if key in piano.key_map:
                    piano.press_key(key)
                    for screen_note in screen_notes:
                        if (screen_note.note == piano.key_map[key]['note']) and (abs(screen_note.y_coord - endline_y_coord) <= press_distance_tolerance):
                            score += 1
                if event.key == pygame.K_SPACE:
                    # Adicionar partículas ao pressionar a barra de espaço
                    print("espaço")
                    effect_manager.add_particles(100, 300, (255, 255, 0), 20)
                
            elif event.type == pygame.KEYUP:
                key = event.unicode.upper()
                if key in piano.key_map:
                    piano.release_key(key)

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
        for note in screen_notes[:]:  # Usando cópia da lista para evitar problemas ao remover itens
            note.position_update(getTime(start_ticks))
            if note.gone:
                screen_notes.remove(note)
                del note  # Opcional: Remove a referência explicitamente
            else:
                note.draw(win)

        # Desenhar o piano
        piano.draw(win)
        
        # Desenhar o placar na tela
        draw_text(win, f"{score}", font, (255, 255, 255), 50, 50)
        
        # Atualizar e desenhar os efeitos
        effect_manager.update()
        effect_manager.draw(win)
        
        pygame.display.update()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()
