import pygame
import sys
import os
import json
import math
from pathlib import Path

pygame.init()

# ============================================================
# NEON RHYTHM
# ============================================================

WIDTH = 1100
HEIGHT = 720
FPS = 120

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("NEON RHYTHM")

clock = pygame.time.Clock()

# ============================================================
# COLORS
# ============================================================

BLACK = (5, 5, 12)
BG = (10, 10, 20)
WHITE = (245, 245, 255)
GRAY = (130, 130, 155)

CYAN = (60, 220, 255)
GREEN = (80, 255, 150)
PINK = (255, 70, 200)
YELLOW = (255, 220, 60)
RED = (255, 70, 90)
PURPLE = (170, 100, 255)

LANE_COLORS = [
    CYAN,
    GREEN,
    PINK,
    YELLOW
]

# ============================================================
# FONTS
# ============================================================

font_tiny = pygame.font.SysFont(
    "arial", 17, bold=True
)

font_small = pygame.font.SysFont(
    "arial", 23, bold=True
)

font_medium = pygame.font.SysFont(
    "arial", 31, bold=True
)

font_big = pygame.font.SysFont(
    "arial", 48, bold=True
)

font_huge = pygame.font.SysFont(
    "arial", 68, bold=True
)

# ============================================================
# CONTROLS
# ============================================================

KEYS = [
    pygame.K_LEFT,
    pygame.K_DOWN,
    pygame.K_UP,
    pygame.K_RIGHT
]

ARROWS = [
    "←",
    "↓",
    "↑",
    "→"
]

# ============================================================
# LANES
# ============================================================

LANES = 4

LANE_WIDTH = 90
LANE_GAP = 12

TOTAL_LANE_WIDTH = (
    LANES * LANE_WIDTH
    + (LANES - 1) * LANE_GAP
)

LANE_START_X = (
    WIDTH - TOTAL_LANE_WIDTH
) // 2

RECEPTOR_Y = 535
NOTE_SIZE = 68

# ============================================================
# TIMING
# ============================================================

NOTE_SPEED = 0.43

PERFECT_WINDOW = 40
GREAT_WINDOW = 80
GOOD_WINDOW = 125
BAD_WINDOW = 180

# ============================================================
# DIFFICULTIES
# ============================================================

DIFFICULTIES = [
    {
        "name": "EASY",
        "color": GREEN
    },
    {
        "name": "NORMAL",
        "color": YELLOW
    },
    {
        "name": "HARD",
        "color": RED
    }
]

selected_difficulty = 1

# ============================================================
# MOD LOADING
# ============================================================

MODS_FOLDER = "mods"
CHARTS_FOLDER = "charts"

BUILTIN_CHART_FILES = [
    "neon_pulse.json",
    "digital_duel.json",
    "final_voltage.json"
]


def load_json_file(path):

    try:

        with open(
            path,
            "r",
            encoding="utf-8"
        ) as file:

            return json.load(file)

    except (
        OSError,
        json.JSONDecodeError
    ) as error:

        print(
            f"[NEON RHYTHM] "
            f"Could not load {path}: {error}"
        )

        return None


def load_mods():

    mods = []

    if not os.path.exists(
        MODS_FOLDER
    ):

        os.makedirs(
            MODS_FOLDER
        )

    for mod_folder in os.listdir(
        MODS_FOLDER
    ):

        mod_path = os.path.join(
            MODS_FOLDER,
            mod_folder
        )

        if not os.path.isdir(
            mod_path
        ):

            continue

        mod_json = os.path.join(
            mod_path,
            "mod.json"
        )

        if not os.path.exists(
            mod_json
        ):

            continue

        mod_data = load_json_file(
            mod_json
        )

        if mod_data is None:

            continue

        mod = {
            "folder": mod_folder,
            "path": mod_path,
            "name": mod_data.get(
                "name",
                mod_folder
            ),
            "author": mod_data.get(
                "author",
                "Unknown"
            ),
            "description": mod_data.get(
                "description",
                ""
            ),
            "version": mod_data.get(
                "version",
                "1.0"
            ),
            "songs": []
        }

        songs_folder = os.path.join(
            mod_path,
            "songs"
        )

        if os.path.exists(
            songs_folder
        ):

            for filename in os.listdir(
                songs_folder
            ):

                if not filename.endswith(
                    ".json"
                ):

                    continue

                song_path = os.path.join(
                    songs_folder,
                    filename
                )

                song_data = load_json_file(
                    song_path
                )

                if song_data is None:

                    continue

                song_data["_mod"] = (
                    mod_folder
                )

                song_data["_path"] = (
                    song_path
                )

                mod["songs"].append(
                    song_data
                )

        mods.append(mod)

    return mods


LOADED_MODS = load_mods()

# ============================================================
# BUILT-IN SONGS
# ============================================================

def load_builtin_songs():
    songs = []

    for filename in BUILTIN_CHART_FILES:
        path = os.path.join(CHARTS_FOLDER, filename)
        data = load_json_file(path)

        if not data:
            print(f"Warning: Could not load built-in chart: {filename}")
            continue

        data["builtin"] = True
        data["_chart_file"] = filename
        data["_mod"] = None

        songs.append(data)

    return songs


BUILTIN_SONGS = load_builtin_songs()

# ============================================================
# SONG LIST
# ============================================================

ALL_SONGS = []

for song in BUILTIN_SONGS:

    song_copy = song.copy()

    song_copy["builtin"] = True
    song_copy["_mod"] = None

    ALL_SONGS.append(
        song_copy
    )


for mod in LOADED_MODS:

    for song in mod["songs"]:

        song_copy = song.copy()

        song_copy["builtin"] = False

        ALL_SONGS.append(
            song_copy
        )

# ============================================================
# NOTE
# ============================================================


class Note:

    def __init__(
        self,
        lane,
        hit_time
    ):

        self.lane = lane
        self.hit_time = hit_time

        self.hit = False
        self.missed = False

    def get_y(
        self,
        song_time
    ):

        return (
            RECEPTOR_Y
            - (
                self.hit_time
                - song_time
            )
            * NOTE_SPEED
        )

    def draw(
        self,
        song_time
    ):

        y = self.get_y(
            song_time
        )

        x = (
            LANE_START_X
            + self.lane
            * (
                LANE_WIDTH
                + LANE_GAP
            )
        )

        color = LANE_COLORS[
            self.lane
        ]

        rect = pygame.Rect(
            x + 8,
            int(
                y
                - NOTE_SIZE / 2
            ),
            LANE_WIDTH - 16,
            NOTE_SIZE
        )

        pygame.draw.rect(
            screen,
            color,
            rect,
            border_radius=12
        )

        pygame.draw.rect(
            screen,
            WHITE,
            rect,
            3,
            border_radius=12
        )

        arrow = font_medium.render(
            ARROWS[self.lane],
            True,
            WHITE
        )

        screen.blit(
            arrow,
            arrow.get_rect(
                center=rect.center
            )
        )

# ============================================================
# CHART CREATION
# ============================================================


def beat_to_ms(
    beat,
    bpm
):

    milliseconds_per_beat = (
        60000 / bpm
    )

    return (
        beat
        * milliseconds_per_beat
    )


def create_builtin_chart(
    song_index,
    difficulty,
    bpm
):

    chart = []

    # EASY
    if difficulty == 0:

        pattern = [
            0, 1, 2, 3,
            3, 2, 1, 0
        ]

        beat = 4

        while beat < 55:

            lane = pattern[
                int(beat - 4)
                % len(pattern)
            ]

            chart.append(
                Note(
                    lane,
                    beat_to_ms(
                        beat,
                        bpm
                    )
                )
            )

            beat += 1

    # NORMAL
    elif difficulty == 1:

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

            notes = pattern[
                int(beat - 4)
                % len(pattern)
            ]

            for lane in notes:

                chart.append(
                    Note(
                        lane,
                        beat_to_ms(
                            beat,
                            bpm
                        )
                    )
                )

            beat += 0.5

    # HARD
    else:

        beat = 4

        pattern = [
            0, 1, 2, 3,
            2, 0, 3, 1
        ]

        while beat < 55:

            lane = pattern[
                int(
                    (beat - 4) * 2
                )
                % len(pattern)
            ]

            chart.append(
                Note(
                    lane,
                    beat_to_ms(
                        beat,
                        bpm
                    )
                )
            )

            beat += 0.5

    return chart


def create_mod_chart(
    song,
    difficulty_index
):

    bpm = song.get(
        "bpm",
        120
    )

    difficulties = song.get(
        "difficulties",
        {}
    )

    difficulty_name = (
        DIFFICULTIES[
            difficulty_index
        ]["name"].title()
    )

    chart_data = difficulties.get(
        difficulty_name,
        []
    )

    chart = []

    for entry in chart_data:

        if not isinstance(
            entry,
            list
        ):

            continue

        if len(entry) < 2:

            continue

        beat = entry[0]
        lane = entry[1]

        try:

            beat = float(beat)
            lane = int(lane)

        except (
            ValueError,
            TypeError
        ):

            continue

        if lane < 0 or lane >= 4:

            continue

        chart.append(
            Note(
                lane,
                beat_to_ms(
                    beat,
                    bpm
                )
            )
        )

    return chart


def create_chart_from_data(
    chart_data,
    bpm,
    difficulty_index
):

    chart = []

    difficulty_name = (
        DIFFICULTIES[
            difficulty_index
        ]["name"].title()
    )

    notes = chart_data.get(
        difficulty_name,
        []
    )

    for entry in notes:

        if not isinstance(
            entry,
            list
        ):

            continue

        if len(entry) < 2:

            continue

        beat = entry[0]
        lane = entry[1]

        try:

            beat = float(beat)
            lane = int(lane)

        except (
            ValueError,
            TypeError
        ):

            continue

        if lane < 0 or lane >= 4:

            continue

        chart.append(
            Note(
                lane,
                beat_to_ms(
                    beat,
                    bpm
                )
            )
        )

    return chart


def create_builtin_chart(
    song,
    difficulty_index
):

    bpm = song.get(
        "bpm",
        120
    )

    difficulties = song.get(
        "difficulties",
        {}
    )

    return create_chart_from_data(
        difficulties,
        bpm,
        difficulty_index
    )


def create_mod_chart(
    song,
    difficulty_index
):

    bpm = song.get(
        "bpm",
        120
    )

    difficulties = song.get(
        "difficulties",
        {}
    )

    return create_chart_from_data(
        difficulties,
        bpm,
        difficulty_index
    )


def create_chart(
    song,
    difficulty_index
):

    if song.get(
        "builtin",
        False
    ):

        return create_builtin_chart(
            song,
            difficulty_index
        )

    return create_mod_chart(
        song,
        difficulty_index
    )

# ============================================================
# GAME VARIABLES
# ============================================================

state = "song_select"

song_selected = 0

current_song = None
notes = []

score = 0
combo = 0
max_combo = 0

hits = 0
misses = 0

health = 0.5
boss_health = 0.5

song_time = 0
song_start_time = 0

judgement = ""
judgement_color = WHITE
judgement_timer = 0

paused = False

pressed = [
    False,
    False,
    False,
    False
]

# ============================================================
# START SONG
# ============================================================


def start_song():

    global state
    global current_song
    global notes
    global score
    global combo
    global max_combo
    global hits
    global misses
    global health
    global boss_health
    global song_time
    global song_start_time
    global judgement
    global judgement_timer
    global paused

    current_song = ALL_SONGS[
        song_selected
    ]

    notes = create_chart(
        current_song,
        selected_difficulty
    )

    score = 0
    combo = 0
    max_combo = 0

    hits = 0
    misses = 0

    health = 0.5
    boss_health = 0.5

    song_time = 0

    judgement = ""
    judgement_timer = 0

    paused = False

    song_start_time = (
        pygame.time.get_ticks()
    )

    state = "playing"

# ============================================================
# BACKGROUND
# ============================================================


def draw_background():

    screen.fill(BG)

    for x in range(
        0,
        WIDTH,
        50
    ):

        pygame.draw.line(
            screen,
            (22, 22, 38),
            (x, 0),
            (x, HEIGHT)
        )

    for y in range(
        0,
        HEIGHT,
        50
    ):

        pygame.draw.line(
            screen,
            (22, 22, 38),
            (0, y),
            (WIDTH, y)
        )

    time = (
        pygame.time.get_ticks()
        / 1000
    )

    for i in range(8):

        x = (
            WIDTH / 2
            + math.sin(
                time * 0.3 + i
            ) * 500
        )

        y = (
            300
            + math.cos(
                time * 0.4 + i
            ) * 200
        )

        pygame.draw.circle(
            screen,
            (18, 18, 35),
            (
                int(x),
                int(y)
            ),
            90
        )

# ============================================================
# LANES
# ============================================================


def draw_lanes():

    for lane in range(4):

        x = (
            LANE_START_X
            + lane
            * (
                LANE_WIDTH
                + LANE_GAP
            )
        )

        pygame.draw.rect(
            screen,
            (15, 15, 28),
            (
                x,
                0,
                LANE_WIDTH,
                HEIGHT
            )
        )

        pygame.draw.rect(
            screen,
            (40, 40, 58),
            (
                x,
                0,
                LANE_WIDTH,
                HEIGHT
            ),
            2
        )

        receptor = pygame.Rect(
            x + 8,
            RECEPTOR_Y - 34,
            LANE_WIDTH - 16,
            68
        )

        color = LANE_COLORS[
            lane
        ]

        if pressed[lane]:

            pygame.draw.rect(
                screen,
                color,
                receptor,
                border_radius=12
            )

            text_color = BLACK

        else:

            pygame.draw.rect(
                screen,
                (25, 25, 40),
                receptor,
                border_radius=12
            )

            pygame.draw.rect(
                screen,
                color,
                receptor,
                3,
                border_radius=12
            )

            text_color = color

        arrow = font_medium.render(
            ARROWS[lane],
            True,
            text_color
        )

        screen.blit(
            arrow,
            arrow.get_rect(
                center=receptor.center
            )
        )

# ============================================================
# CHARACTERS
# ============================================================


def draw_player():

    x = 180
    y = 285

    pygame.draw.rect(
        screen,
        CYAN,
        (
            x - 40,
            y + 55,
            80,
            105
        ),
        border_radius=18
    )

    pygame.draw.circle(
        screen,
        (245, 220, 200),
        (x, y),
        60
    )

    pygame.draw.polygon(
        screen,
        PURPLE,
        [
            (x - 60, y - 20),
            (x - 30, y - 80),
            (x, y - 50),
            (x + 35, y - 85),
            (x + 65, y - 15)
        ]
    )

    pygame.draw.circle(
        screen,
        BLACK,
        (x - 22, y),
        7
    )

    pygame.draw.circle(
        screen,
        BLACK,
        (x + 22, y),
        7
    )

    pygame.draw.arc(
        screen,
        BLACK,
        (
            x - 25,
            y + 5,
            50,
            30
        ),
        0,
        math.pi,
        4
    )


def draw_boss():

    x = WIDTH - 180
    y = 285

    if combo >= 50:

        expression = "panic"

    elif combo >= 25:

        expression = "angry"

    elif combo >= 10:

        expression = "nervous"

    else:

        expression = "normal"

    pygame.draw.rect(
        screen,
        PINK,
        (
            x - 42,
            y + 55,
            84,
            105
        ),
        border_radius=18
    )

    pygame.draw.circle(
        screen,
        (210, 170, 230),
        (x, y),
        62
    )

    pygame.draw.polygon(
        screen,
        RED,
        [
            (x - 60, y - 20),
            (x - 35, y - 82),
            (x, y - 50),
            (x + 35, y - 82),
            (x + 60, y - 20)
        ]
    )

    if expression == "panic":

        pygame.draw.circle(
            screen,
            WHITE,
            (x - 22, y),
            13
        )

        pygame.draw.circle(
            screen,
            WHITE,
            (x + 22, y),
            13
        )

        pygame.draw.circle(
            screen,
            BLACK,
            (x - 22, y),
            5
        )

        pygame.draw.circle(
            screen,
            BLACK,
            (x + 22, y),
            5
        )

        pygame.draw.ellipse(
            screen,
            BLACK,
            (
                x - 20,
                y + 15,
                40,
                45
            )
        )

    elif expression == "angry":

        pygame.draw.line(
            screen,
            BLACK,
            (x - 35, y - 15),
            (x - 10, y - 5),
            6
        )

        pygame.draw.line(
            screen,
            BLACK,
            (x + 10, y - 5),
            (x + 35, y - 15),
            6
        )

        pygame.draw.circle(
            screen,
            RED,
            (x - 22, y),
            7
        )

        pygame.draw.circle(
            screen,
            RED,
            (x + 22, y),
            7
        )

    else:

        pygame.draw.circle(
            screen,
            BLACK,
            (x - 22, y),
            7
        )

        pygame.draw.circle(
            screen,
            BLACK,
            (x + 22, y),
            7
        )

        pygame.draw.arc(
            screen,
            BLACK,
            (
                x - 25,
                y + 5,
                50,
                30
            ),
            math.pi,
            math.pi * 2,
            4
        )

# ============================================================
# HEALTH
# ============================================================


def draw_health():

    pygame.draw.rect(
        screen,
        (40, 40, 55),
        (
            70,
            45,
            350,
            25
        ),
        border_radius=12
    )

    pygame.draw.rect(
        screen,
        GREEN,
        (
            70,
            45,
            int(
                350 * health
            ),
            25
        ),
        border_radius=12
    )

    pygame.draw.rect(
        screen,
        (40, 40, 55),
        (
            WIDTH - 420,
            45,
            350,
            25
        ),
        border_radius=12
    )

    pygame.draw.rect(
        screen,
        RED,
        (
            WIDTH - 420,
            45,
            int(
                350 * boss_health
            ),
            25
        ),
        border_radius=12
    )

    screen.blit(
        font_tiny.render(
            "YOU",
            True,
            WHITE
        ),
        (70, 22)
    )

    screen.blit(
        font_tiny.render(
            "BOSS",
            True,
            WHITE
        ),
        (
            WIDTH - 420,
            22
        )
    )

# ============================================================
# SONG SELECT
# ============================================================


def draw_song_select():

    draw_background()

    title = font_huge.render(
        "SONG SELECT",
        True,
        WHITE
    )

    screen.blit(
        title,
        title.get_rect(
            center=(
                WIDTH // 2,
                90
            )
        )
    )

    for i, song in enumerate(
        ALL_SONGS
    ):

        y = 175 + i * 65

        if i == song_selected:

            color = CYAN

            pygame.draw.rect(
                screen,
                color,
                (
                    220,
                    y - 5,
                    660,
                    55
                ),
                border_radius=10
            )

            text_color = BLACK

        else:

            color = WHITE

            text_color = WHITE

        name = song.get(
            "name",
            "Unnamed Song"
        )

        if not song.get(
            "builtin",
            False
        ):

            name = "[MOD] " + name

        text = font_medium.render(
            name,
            True,
            text_color
        )

        screen.blit(
            text,
            (
                250,
                y
            )
        )

    hint = font_small.render(
        "↑ / ↓ Select    ENTER Continue",
        True,
        GRAY
    )

    screen.blit(
        hint,
        hint.get_rect(
            center=(
                WIDTH // 2,
                650
            )
        )
    )

# ============================================================
# DIFFICULTY SELECT
# ============================================================


def draw_difficulty_select():

    draw_background()

    song = ALL_SONGS[
        song_selected
    ]

    title = font_big.render(
        song.get(
            "name",
            "Song"
        ),
        True,
        WHITE
    )

    screen.blit(
        title,
        title.get_rect(
            center=(
                WIDTH // 2,
                100
            )
        )
    )

    artist = font_small.render(
        song.get(
            "artist",
            "Unknown"
        ),
        True,
        GRAY
    )

    screen.blit(
        artist,
        artist.get_rect(
            center=(
                WIDTH // 2,
                145
            )
        )
    )

    for i, difficulty in enumerate(
        DIFFICULTIES
    ):

        y = 230 + i * 100

        rect = pygame.Rect(
            WIDTH // 2 - 180,
            y,
            360,
            70
        )

        color = difficulty[
            "color"
        ]

        if i == selected_difficulty:

            pygame.draw.rect(
                screen,
                color,
                rect,
                border_radius=15
            )

            text_color = BLACK

        else:

            pygame.draw.rect(
                screen,
                (25, 25, 40),
                rect,
                border_radius=15
            )

            pygame.draw.rect(
                screen,
                color,
                rect,
                3,
                border_radius=15
            )

            text_color = color

        text = font_medium.render(
            difficulty["name"],
            True,
            text_color
        )

        screen.blit(
            text,
            text.get_rect(
                center=rect.center
            )
        )

    hint = font_small.render(
        "↑ / ↓ Select    ENTER Play    ESC Back",
        True,
        GRAY
    )

    screen.blit(
        hint,
        hint.get_rect(
            center=(
                WIDTH // 2,
                650
            )
        )
    )

# ============================================================
# GAME UI
# ============================================================


def draw_game_ui():

    score_text = font_small.render(
        f"SCORE {score:,}",
        True,
        WHITE
    )

    screen.blit(
        score_text,
        (
            20,
            100
        )
    )

    if combo > 0:

        combo_text = font_huge.render(
            str(combo),
            True,
            WHITE
        )

        screen.blit(
            combo_text,
            combo_text.get_rect(
                center=(
                    WIDTH // 2,
                    100
                )
            )
        )

        screen.blit(
            font_tiny.render(
                "COMBO",
                True,
                GRAY
            ),
            (
                WIDTH // 2 - 25,
                140
            )
        )

    if judgement_timer > 0:

        text = font_big.render(
            judgement,
            True,
            judgement_color
        )

        screen.blit(
            text,
            text.get_rect(
                center=(
                    WIDTH // 2,
                    425
                )
            )
        )

    total = hits + misses

    if total > 0:

        accuracy = (
            hits / total
        ) * 100

    else:

        accuracy = 100

    accuracy_text = font_tiny.render(
        f"Accuracy: {accuracy:.1f}%",
        True,
        GRAY
    )

    screen.blit(
        accuracy_text,
        (
            WIDTH - 180,
            105
        )
    )

# ============================================================
# JUDGEMENT
# ============================================================


def show_judgement(
    text,
    color
):

    global judgement
    global judgement_color
    global judgement_timer

    judgement = text
    judgement_color = color
    judgement_timer = 650

# ============================================================
# HIT NOTE
# ============================================================


def hit_note(lane):

    global score
    global combo
    global max_combo
    global hits
    global health
    global boss_health

    possible = []

    for note in notes:

        if note.hit or note.missed:

            continue

        if note.lane != lane:

            continue

        difference = abs(
            note.hit_time
            - song_time
        )

        if difference <= BAD_WINDOW:

            possible.append(
                (
                    difference,
                    note
                )
            )

    if not possible:

        combo = 0

        health -= 0.04

        show_judgement(
            "MISS",
            RED
        )

        return

    difference, note = min(
        possible,
        key=lambda item: item[0]
    )

    note.hit = True

    hits += 1

    if difference <= PERFECT_WINDOW:

        score += 1000
        combo += 1

        health += 0.025
        boss_health -= 0.025

        show_judgement(
            "PERFECT!",
            YELLOW
        )

    elif difference <= GREAT_WINDOW:

        score += 700
        combo += 1

        health += 0.015
        boss_health -= 0.018

        show_judgement(
            "GREAT",
            CYAN
        )

    elif difference <= GOOD_WINDOW:

        score += 400
        combo += 1

        health += 0.005
        boss_health -= 0.01

        show_judgement(
            "GOOD",
            GREEN
        )

    else:

        score += 100
        combo += 1

        health -= 0.005
        boss_health -= 0.004

        show_judgement(
            "BAD",
            (255, 150, 100)
        )

    max_combo = max(
        max_combo,
        combo
    )

    health = max(
        0,
        min(
            1,
            health
        )
    )

    boss_health = max(
        0,
        min(
            1,
            boss_health
        )
    )

# ============================================================
# MISS CHECK
# ============================================================


def check_misses():

    global combo
    global misses
    global health

    for note in notes:

        if note.hit or note.missed:

            continue

        if (
            song_time
            - note.hit_time
            > BAD_WINDOW
        ):

            note.missed = True

            combo = 0
            misses += 1

            health -= 0.08

            show_judgement(
                "MISS",
                RED
            )

# ============================================================
# RESULTS
# ============================================================


def get_rank():

    total = hits + misses

    if total == 0:

        return "F"

    accuracy = (
        hits / total
    ) * 100

    if accuracy >= 98:
        return "S"

    if accuracy >= 93:
        return "A"

    if accuracy >= 85:
        return "B"

    if accuracy >= 70:
        return "C"

    return "D"


def draw_results():

    draw_background()

    title = font_big.render(
        "RESULTS",
        True,
        WHITE
    )

    screen.blit(
        title,
        title.get_rect(
            center=(
                WIDTH // 2,
                100
            )
        )
    )

    rank = font_huge.render(
        get_rank(),
        True,
        YELLOW
    )

    screen.blit(
        rank,
        rank.get_rect(
            center=(
                WIDTH // 2,
                200
            )
        )
    )

    total = hits + misses

    if total > 0:

        accuracy = (
            hits / total
        ) * 100

    else:

        accuracy = 0

    stats = [
        f"Score: {score:,}",
        f"Max Combo: {max_combo}",
        f"Accuracy: {accuracy:.1f}%",
        f"Hits: {hits}",
        f"Misses: {misses}"
    ]

    for i, text in enumerate(
        stats
    ):

        rendered = font_medium.render(
            text,
            True,
            WHITE
        )

        screen.blit(
            rendered,
            rendered.get_rect(
                center=(
                    WIDTH // 2,
                    300 + i * 45
                )
            )
        )

    hint = font_small.render(
        "ENTER Play Again    ESC Song Select",
        True,
        GRAY
    )

    screen.blit(
        hint,
        hint.get_rect(
            center=(
                WIDTH // 2,
                600
            )
        )
    )

# ============================================================
# PAUSE
# ============================================================


def draw_pause():

    overlay = pygame.Surface(
        (
            WIDTH,
            HEIGHT
        ),
        pygame.SRCALPHA
    )

    overlay.fill(
        (0, 0, 0, 190)
    )

    screen.blit(
        overlay,
        (0, 0)
    )

    text = font_huge.render(
        "PAUSED",
        True,
        WHITE
    )

    screen.blit(
        text,
        text.get_rect(
            center=(
                WIDTH // 2,
                300
            )
        )
    )

    hint = font_small.render(
        "P = Resume",
        True,
        GRAY
    )

    screen.blit(
        hint,
        hint.get_rect(
            center=(
                WIDTH // 2,
                370
            )
        )
    )

# ============================================================
# MAIN LOOP
# ============================================================

running = True

while running:

    dt = clock.tick(FPS)

    # --------------------------------------------------------
    # EVENTS
    # --------------------------------------------------------

    for event in pygame.event.get():

        if event.type == pygame.QUIT:

            running = False

        # ====================================================
        # SONG SELECT
        # ====================================================

        elif state == "song_select":

            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_UP:

                    song_selected -= 1

                    if song_selected < 0:

                        song_selected = (
                            len(ALL_SONGS)
                            - 1
                        )

                elif event.key == pygame.K_DOWN:

                    song_selected += 1

                    if song_selected >= len(
                        ALL_SONGS
                    ):

                        song_selected = 0

                elif event.key == pygame.K_RETURN:

                    state = "difficulty"

                elif event.key == pygame.K_ESCAPE:

                    running = False

        # ====================================================
        # DIFFICULTY
        # ====================================================

        elif state == "difficulty":

            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_UP:

                    selected_difficulty -= 1

                    if selected_difficulty < 0:

                        selected_difficulty = 2

                elif event.key == pygame.K_DOWN:

                    selected_difficulty += 1

                    if selected_difficulty > 2:

                        selected_difficulty = 0

                elif event.key == pygame.K_RETURN:

                    start_song()

                elif event.key == pygame.K_ESCAPE:

                    state = "song_select"

        # ====================================================
        # PLAYING
        # ====================================================

        elif state == "playing":

            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_p:

                    paused = not paused

                elif event.key == pygame.K_ESCAPE:

                    state = "song_select"

                elif not paused:

                    for lane in range(4):

                        if event.key == KEYS[lane]:

                            pressed[lane] = True

                            hit_note(lane)

            elif event.type == pygame.KEYUP:

                for lane in range(4):

                    if event.key == KEYS[lane]:

                        pressed[lane] = False

        # ====================================================
        # RESULTS
        # ====================================================

        elif state == "results":

            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_RETURN:

                    start_song()

                elif event.key == pygame.K_ESCAPE:

                    state = "song_select"

    # --------------------------------------------------------
    # UPDATE
    # --------------------------------------------------------

    if (
        state == "playing"
        and not paused
    ):

        song_time = (
            pygame.time.get_ticks()
            - song_start_time
        )

        check_misses()

        if judgement_timer > 0:

            judgement_timer -= dt

        if health <= 0:

            state = "results"

        if boss_health <= 0:

            state = "results"

        song_length = current_song.get(
            "length",
            30000
        )

        if song_time > song_length:

            state = "results"

    # --------------------------------------------------------
    # DRAW
    # --------------------------------------------------------

    if state == "song_select":

        draw_song_select()

    elif state == "difficulty":

        draw_difficulty_select()

    elif state == "playing":

        draw_background()

        draw_health()

        draw_player()
        draw_boss()

        draw_lanes()

        for note in notes:

            if note.hit or note.missed:

                continue

            y = note.get_y(
                song_time
            )

            if (
                -100
                < y
                < HEIGHT + 100
            ):

                note.draw(
                    song_time
                )

        draw_game_ui()

        if paused:

            draw_pause()

    elif state == "results":

        draw_results()

    pygame.display.flip()


pygame.quit()
sys.exit()
