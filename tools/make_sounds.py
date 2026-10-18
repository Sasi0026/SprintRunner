"""
Generates the alarm chimes in assets/sounds/ (original sounds, no licensing issues).

    python tools/make_sounds.py

Each note is a marimba-like tone: a sine fundamental plus two quickly fading
overtones, with a soft attack and an exponential fade.
"""
import math
import os
import struct
import wave

RATE = 44100
OUT_DIR = os.path.join(os.path.dirname(__file__), '..', 'assets', 'sounds')

# Note frequencies (Hz)
G5, C6, D6, E6, G6, C7 = 783.99, 1046.50, 1174.66, 1318.51, 1567.98, 2093.00


def tone(freq, t):
    """Marimba-like note at time t seconds after it was struck."""
    if t < 0:
        return 0.0
    attack = min(1.0, t / 0.004)
    return attack * (
        1.00 * math.exp(-3.2 * t) * math.sin(2 * math.pi * freq * t)
        + 0.30 * math.exp(-11 * t) * math.sin(2 * math.pi * freq * 4 * t)
        + 0.08 * math.exp(-28 * t) * math.sin(2 * math.pi * freq * 9.2 * t)
    )


def render(notes, length):
    """notes: list of (start_seconds, frequency, volume)."""
    samples = []
    total = int(RATE * length)
    fade = int(RATE * 0.08)
    for i in range(total):
        t = i / RATE
        value = sum(volume * tone(freq, t - start) for start, freq, volume in notes)
        if i > total - fade:  # avoid a click at the very end
            value *= (total - i) / fade
        samples.append(value)
    peak = max(abs(s) for s in samples) or 1
    gain = 0.7 / peak  # about -3 dB
    return [s * gain for s in samples]


def save(name, samples):
    os.makedirs(OUT_DIR, exist_ok=True)
    with wave.open(os.path.join(OUT_DIR, name), 'wb') as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(RATE)
        f.writeframes(b''.join(struct.pack('<h', int(s * 32767)) for s in samples))


SOUNDS = {
    # Sprint finished, break starts: bright rising three-note chime
    'sprint_done.wav': ([(0.00, C6, 0.9), (0.13, E6, 0.85), (0.26, G6, 1.0)], 1.6),
    # Break over, back to focus: two calm notes
    'break_done.wav': ([(0.00, G5, 0.9), (0.16, D6, 1.0)], 1.2),
    # Whole session finished: arpeggio that resolves on a chord
    'session_done.wav': ([(0.00, C6, 0.8), (0.12, E6, 0.8), (0.24, G6, 0.85), (0.36, C7, 0.9),
                          (0.62, C6, 0.6), (0.62, E6, 0.6), (0.62, G6, 0.6), (0.62, C7, 0.7)], 2.6),
}

if __name__ == '__main__':
    for filename, (notes, length) in SOUNDS.items():
        save(filename, render(notes, length))
        print('wrote', filename)
