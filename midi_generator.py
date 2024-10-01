from mido import Message, MidiFile, MidiTrack

# Function to convert note name to MIDI number
def note_to_midi(note):
    note_names = {'C': 0, 'C#': 1, 'D': 2, 'D#': 3, 'E': 4, 'F': 5, 'F#': 6, 'G': 7, 'G#': 8, 'A': 9, 'A#': 10, 'B': 11}
    octave = int(note[-1])
    note_name = note[:-1]
    return 12 * (octave + 1) + note_names[note_name]

# Create a new MIDI file and a new track
mid = MidiFile()
track = MidiTrack()
mid.tracks.append(track)

# Define the notes and their durations in seconds
notes = [
    ('C4', 0.5),
    ('pause', 0.1),
    ('D4', 2),
    ('pause', 0.5),
    (('C3', 'G3'), 1),
]

# Initial time in ticks
time = 0
# Ticks per beat (e.g., 480 ticks per quarter note)
ticks_per_beat = 480
# BPM (e.g., 120 beats per minute)
bpm = 120
# Seconds per beat
seconds_per_beat = 60 / bpm
# Ticks per second
ticks_per_second = ticks_per_beat / seconds_per_beat

# Add notes to the MIDI track
for note in notes:
    if note[0] == 'pause':
        time += int(note[1] * ticks_per_second)
    elif isinstance(note[0], tuple):
        for n in note[0]:
            midi_note = note_to_midi(n)
            track.append(Message('note_on', note=midi_note, velocity=64, time=time))
        time = 0
        time += int(note[1] * ticks_per_second)
        for n in note[0]:
            midi_note = note_to_midi(n)
            track.append(Message('note_off', note=midi_note, velocity=64, time=time))
        time = 0
    else:
        midi_note = note_to_midi(note[0])
        track.append(Message('note_on', note=midi_note, velocity=64, time=time))
        time = int(note[1] * ticks_per_second)
        track.append(Message('note_off', note=midi_note, velocity=64, time=time))
        time = 0

print(track)
# Save the MIDI file
mid.save('output3.mid')
