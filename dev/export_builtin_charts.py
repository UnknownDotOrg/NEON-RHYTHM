import json
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
CHARTS_DIR = BASE_DIR / "charts"


def beat_to_ms(beat, bpm):
    return beat * (60000 / bpm)


def generate_chart(difficulty):
    notes = []

    if difficulty == "Easy":
        pattern = [0, 1, 2, 3, 3, 2, 1, 0]
        beat = 4

        while beat < 55:
            lane = pattern[int((beat - 4) % len(pattern))]
            notes.append([beat, lane])
            beat += 1

    elif difficulty == "Normal":
        pattern = [
            [0],
            [2],
            [1],
            [3],
            [0, 2],
            [1, 3],
            [0, 3],
            [1, 2]
        ]

        beat = 4

        while beat < 55:
            lanes = pattern[int(((beat - 4) * 2) % len(pattern))]

            for lane in lanes:
                notes.append([beat, lane])

            beat += 0.5

    elif difficulty == "Hard":
        pattern = [0, 1, 2, 3, 2, 0, 3, 1]
        beat = 4

        while beat < 55:
            lane = pattern[int(((beat - 4) * 2) % len(pattern))]
            notes.append([beat, lane])
            beat += 0.5

    return notes


songs = [
    {
        "filename": "neon_pulse.json",
        "name": "Neon Pulse",
        "bpm": 120
    },
    {
        "filename": "digital_duel.json",
        "name": "Digital Duel",
        "bpm": 135
    },
    {
        "filename": "final_voltage.json",
        "name": "Final Voltage",
        "bpm": 150
    }
]


CHARTS_DIR.mkdir(parents=True, exist_ok=True)

for song in songs:
    chart = {
        "name": song["name"],
        "artist": "NEON RHYTHM",
        "bpm": song["bpm"],
        "length": 30000,
        "difficulties": {
            "Easy": generate_chart("Easy"),
            "Normal": generate_chart("Normal"),
            "Hard": generate_chart("Hard")
        }
    }

    output_path = CHARTS_DIR / song["filename"]

    with output_path.open("w", encoding="utf-8") as file:
        json.dump(chart, file, indent=4)

    print(f"Created: {output_path}")
