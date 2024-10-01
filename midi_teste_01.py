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

#print(midi_data.tracks)
#print(falling_notes)