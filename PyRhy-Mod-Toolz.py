import pygame
import json
import os
import math
import tkinter as tk
from tkinter import filedialog

pygame.init()

# ============================================================
# CONFIG
# ============================================================

WIDTH = 1200
HEIGHT = 750
FPS = 120

SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("PyRhy Mod Tools - Chart Editor")

CLOCK = pygame.time.Clock()

# ============================================================
# COLORS
# ============================================================

BLACK = (10, 10, 15)
DARK = (20, 20, 30)
DARKER = (14, 14, 22)
WHITE = (240, 240, 245)
GRAY = (140, 140, 150)
LIGHT_GRAY = (190, 190, 200)

CYAN = (0, 220, 255)
GREEN = (70, 255, 130)
YELLOW = (255, 220, 60)
RED = (255, 80, 100)
PURPLE = (190, 100, 255)
PINK = (255, 100, 190)

LANE_COLORS = [
    CYAN,
    GREEN,
    YELLOW,
    RED
]

# ============================================================
# FONTS
# ============================================================

FONT_BIG = pygame.font.SysFont("arial", 32, bold=True)
FONT_MEDIUM = pygame.font.SysFont("arial", 22, bold=True)
FONT_SMALL = pygame.font.SysFont("arial", 17)
FONT_TINY = pygame.font.SysFont("arial", 14)

# ============================================================
# EDITOR SETTINGS
# ============================================================

DIFFICULTIES = ["Easy", "Normal", "Hard"]

current_difficulty = "Normal"

bpm = 120

song_name = "New Song"
artist_name = "UnknownDotOrg"

chart_data = {
    "Easy": [],
    "Normal": [],
    "Hard": []
}

current_file = None

# Beat displayed at the top of the editor.
scroll_beat = 0.0

# How many beats are visible vertically.
VISIBLE_BEATS = 16

# Beat snapping.
SNAP_VALUES = [
    1.0,
    0.5,
    0.25,
    0.125
]

snap_index = 1
snap_value = SNAP_VALUES[snap_index]

# Selected note.
selected_note = None

# Current tool.
tool = "place"

# ============================================================
# UI AREAS
# ============================================================

TOP_BAR_HEIGHT = 80
BOTTOM_BAR_HEIGHT = 70

EDITOR_X = 70
EDITOR_Y = TOP_BAR_HEIGHT
EDITOR_WIDTH = 800
EDITOR_HEIGHT = HEIGHT - TOP_BAR_HEIGHT - BOTTOM_BAR_HEIGHT

LANE_WIDTH = EDITOR_WIDTH // 4

TIMELINE_X = EDITOR_X + EDITOR_WIDTH + 20
TIMELINE_WIDTH = WIDTH - TIMELINE_X - 20

# ============================================================
# TEXT INPUT
# ============================================================

text_input_active = None
text_input_value = ""

# ============================================================
# HELPERS
# ============================================================


def draw_text(text, font, color, x, y, center=False):
    surface = font.render(str(text), True, color)

    if center:
        rect = surface.get_rect(center=(x, y))
    else:
        rect = surface.get_rect(topleft=(x, y))

    SCREEN.blit(surface, rect)


def clamp(value, minimum, maximum):
    return max(minimum, min(maximum, value))


def snap_beat(beat):
    return round(beat / snap_value) * snap_value


def beat_to_y(beat):
    relative = beat - scroll_beat

    return EDITOR_Y + (
        relative / VISIBLE_BEATS
    ) * EDITOR_HEIGHT


def y_to_beat(y):
    relative = (y - EDITOR_Y) / EDITOR_HEIGHT

    return scroll_beat + relative * VISIBLE_BEATS


def lane_to_x(lane):
    return EDITOR_X + lane * LANE_WIDTH + LANE_WIDTH // 2


def mouse_to_lane(x):
    if x < EDITOR_X or x >= EDITOR_X + EDITOR_WIDTH:
        return None

    lane = int((x - EDITOR_X) / LANE_WIDTH)

    if 0 <= lane <= 3:
        return lane

    return None


def format_beat(beat):
    if beat == int(beat):
        return str(int(beat))

    return f"{beat:.3f}".rstrip("0").rstrip(".")


def find_note_at(mouse_x, mouse_y):
    lane = mouse_to_lane(mouse_x)

    if lane is None:
        return None

    for note in chart_data[current_difficulty]:
        beat = note[0]
        note_lane = note[1]

        if note_lane != lane:
            continue

        y = beat_to_y(beat)

        if abs(y - mouse_y) <= 24:
            return note

    return None


def sort_notes():
    chart_data[current_difficulty].sort(
        key=lambda note: (note[0], note[1])
    )


def remove_note(note):
    if note in chart_data[current_difficulty]:
        chart_data[current_difficulty].remove(note)


# ============================================================
# FILE OPERATIONS
# ============================================================


def make_chart_json():
    return {
        "name": song_name,
        "artist": artist_name,
        "bpm": bpm,
        "difficulties": {
            "Easy": chart_data["Easy"],
            "Normal": chart_data["Normal"],
            "Hard": chart_data["Hard"]
        }
    }


def save_chart(path):
    data = make_chart_json()

    try:
        with open(path, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4)

        return True

    except Exception as error:
        print("Could not save chart:")
        print(error)

        return False


def save():
    global current_file

    if current_file is None:
        save_as()
        return

    if save_chart(current_file):
        print(f"Saved chart to: {current_file}")


def save_as():
    global current_file

    root = tk.Tk()
    root.withdraw()

    path = filedialog.asksaveasfilename(
        title="Save NEON RHYTHM Chart",
        defaultextension=".json",
        filetypes=[
            ("NEON RHYTHM Chart", "*.json"),
            ("JSON files", "*.json"),
            ("All files", "*.*")
        ]
    )

    root.destroy()

    if path:
        current_file = path

        if save_chart(path):
            print(f"Saved chart to: {path}")


def load_chart(path):
    global song_name
    global artist_name
    global bpm
    global chart_data
    global current_file

    try:
        with open(path, "r", encoding="utf-8") as file:
            data = json.load(file)

        song_name = data.get("name", "New Song")
        artist_name = data.get("artist", "UnknownDotOrg")
        bpm = data.get("bpm", 120)

        difficulties = data.get("difficulties", {})

        chart_data = {
            "Easy": difficulties.get("Easy", []),
            "Normal": difficulties.get("Normal", []),
            "Hard": difficulties.get("Hard", [])
        }

        current_file = path

        print(f"Loaded chart: {path}")

    except Exception as error:
        print("Could not load chart:")
        print(error)


def open_chart():
    root = tk.Tk()
    root.withdraw()

    path = filedialog.askopenfilename(
        title="Open NEON RHYTHM Chart",
        filetypes=[
            ("NEON RHYTHM Chart", "*.json"),
            ("JSON files", "*.json"),
            ("All files", "*.*")
        ]
    )

    root.destroy()

    if path:
        load_chart(path)


# ============================================================
# NEW CHART
# ============================================================


def new_chart():
    global song_name
    global artist_name
    global bpm
    global chart_data
    global current_file
    global scroll_beat

    song_name = "New Song"
    artist_name = "UnknownDotOrg"
    bpm = 120

    chart_data = {
        "Easy": [],
        "Normal": [],
        "Hard": []
    }

    current_file = None
    scroll_beat = 0.0

    print("Created new chart.")


# ============================================================
# DRAW TOP BAR
# ============================================================


def draw_top_bar():
    pygame.draw.rect(
        SCREEN,
        DARK,
        (0, 0, WIDTH, TOP_BAR_HEIGHT)
    )

    pygame.draw.line(
        SCREEN,
        CYAN,
        (0, TOP_BAR_HEIGHT - 1),
        (WIDTH, TOP_BAR_HEIGHT - 1),
        2
    )

    draw_text(
        "PYRHY MOD TOOLZ",
        FONT_BIG,
        CYAN,
        20,
        12
    )

    draw_text(
        "Chart Editor",
        FONT_SMALL,
        LIGHT_GRAY,
        22,
        49
    )

    # Song info
    draw_text(
        song_name,
        FONT_MEDIUM,
        WHITE,
        300,
        13
    )

    draw_text(
        f"Artist: {artist_name}",
        FONT_SMALL,
        GRAY,
        300,
        45
    )

    draw_text(
        f"BPM: {bpm}",
        FONT_SMALL,
        YELLOW,
        570,
        45
    )

    # Difficulty buttons
    button_x = 720

    for difficulty in DIFFICULTIES:
        width = 95

        if difficulty == current_difficulty:
            color = LANE_COLORS[
                DIFFICULTIES.index(difficulty) + 1
            ]

            pygame.draw.rect(
                SCREEN,
                color,
                (button_x, 20, width, 38),
                border_radius=6
            )

            draw_text(
                difficulty,
                FONT_SMALL,
                BLACK,
                button_x + width // 2,
                39,
                center=True
            )

        else:
            pygame.draw.rect(
                SCREEN,
                DARKER,
                (button_x, 20, width, 38),
                border_radius=6
            )

            pygame.draw.rect(
                SCREEN,
                GRAY,
                (button_x, 20, width, 38),
                1,
                border_radius=6
            )

            draw_text(
                difficulty,
                FONT_SMALL,
                WHITE,
                button_x + width // 2,
                39,
                center=True
            )

        button_x += width + 8


# ============================================================
# DRAW EDITOR
# ============================================================


def draw_editor():
    # Background
    pygame.draw.rect(
        SCREEN,
        BLACK,
        (
            EDITOR_X,
            EDITOR_Y,
            EDITOR_WIDTH,
            EDITOR_HEIGHT
        )
    )

    # Lanes
    for lane in range(4):
        x = EDITOR_X + lane * LANE_WIDTH

        pygame.draw.rect(
            SCREEN,
            DARKER if lane % 2 == 0 else DARK,
            (
                x,
                EDITOR_Y,
                LANE_WIDTH,
                EDITOR_HEIGHT
            )
        )

        pygame.draw.line(
            SCREEN,
            (45, 45, 55),
            (x, EDITOR_Y),
            (x, EDITOR_Y + EDITOR_HEIGHT),
            1
        )

        draw_text(
            ["←", "↓", "↑", "→"][lane],
            FONT_MEDIUM,
            LANE_COLORS[lane],
            x + LANE_WIDTH // 2,
            EDITOR_Y + 25,
            center=True
        )

    # Last lane border
    pygame.draw.line(
        SCREEN,
        (45, 45, 55),
        (
            EDITOR_X + EDITOR_WIDTH,
            EDITOR_Y
        ),
        (
            EDITOR_X + EDITOR_WIDTH,
            EDITOR_Y + EDITOR_HEIGHT
        ),
        1
    )

    # Beat lines
    first_beat = math.floor(scroll_beat)

    last_beat = math.ceil(
        scroll_beat + VISIBLE_BEATS
    )

    for beat_number in range(first_beat, last_beat + 1):
        y = beat_to_y(beat_number)

        if y < EDITOR_Y or y > EDITOR_Y + EDITOR_HEIGHT:
            continue

        if beat_number % 4 == 0:
            line_color = (90, 90, 105)
            width = 2
        else:
            line_color = (40, 40, 50)
            width = 1

        pygame.draw.line(
            SCREEN,
            line_color,
            (EDITOR_X, y),
            (EDITOR_X + EDITOR_WIDTH, y),
            width
        )

        draw_text(
            str(beat_number),
            FONT_TINY,
            GRAY,
            EDITOR_X - 55,
            y - 7
        )

    # Snapped grid lines
    if snap_value < 1:
        beat = math.floor(scroll_beat / snap_value) * snap_value

        while beat <= scroll_beat + VISIBLE_BEATS:
            y = beat_to_y(beat)

            if (
                y >= EDITOR_Y
                and y <= EDITOR_Y + EDITOR_HEIGHT
            ):
                pygame.draw.line(
                    SCREEN,
                    (30, 30, 38),
                    (EDITOR_X, y),
                    (
                        EDITOR_X + EDITOR_WIDTH,
                        y
                    ),
                    1
                )

            beat += snap_value

    # Notes
    for note in chart_data[current_difficulty]:
        beat = note[0]
        lane = note[1]

        y = beat_to_y(beat)

        if (
            y < EDITOR_Y - 40
            or y > EDITOR_Y + EDITOR_HEIGHT + 40
        ):
            continue

        x = lane_to_x(lane)

        color = LANE_COLORS[lane]

        radius = 25

        pygame.draw.circle(
            SCREEN,
            color,
            (x, int(y)),
            radius
        )

        pygame.draw.circle(
            SCREEN,
            WHITE,
            (x, int(y)),
            radius,
            2
        )

        # Selected note
        if note is selected_note:
            pygame.draw.circle(
                SCREEN,
                WHITE,
                (x, int(y)),
                radius + 6,
                3
            )

        arrow = ["←", "↓", "↑", "→"][lane]

        draw_text(
            arrow,
            FONT_MEDIUM,
            BLACK,
            x,
            int(y),
            center=True
        )

    # Editor border
    pygame.draw.rect(
        SCREEN,
        LIGHT_GRAY,
        (
            EDITOR_X,
            EDITOR_Y,
            EDITOR_WIDTH,
            EDITOR_HEIGHT
        ),
        2
    )


# ============================================================
# DRAW SIDE PANEL
# ============================================================


def draw_side_panel():
    pygame.draw.rect(
        SCREEN,
        DARK,
        (
            TIMELINE_X,
            EDITOR_Y,
            TIMELINE_WIDTH,
            EDITOR_HEIGHT
        )
    )

    draw_text(
        "CHART INFO",
        FONT_MEDIUM,
        CYAN,
        TIMELINE_X + 15,
        EDITOR_Y + 15
    )

    y = EDITOR_Y + 60

    draw_text(
        f"Difficulty: {current_difficulty}",
        FONT_SMALL,
        WHITE,
        TIMELINE_X + 15,
        y
    )

    y += 30

    draw_text(
        f"Notes: {len(chart_data[current_difficulty])}",
        FONT_SMALL,
        WHITE,
        TIMELINE_X + 15,
        y
    )

    y += 30

    draw_text(
        f"Snap: 1/{int(1 / snap_value)}",
        FONT_SMALL,
        YELLOW,
        TIMELINE_X + 15,
        y
    )

    y += 45

    draw_text(
        "CONTROLS",
        FONT_MEDIUM,
        PINK,
        TIMELINE_X + 15,
        y
    )

    controls = [
        ("Left click", "Place/select"),
        ("Right click", "Delete"),
        ("Mouse wheel", "Scroll"),
        ("S", "Save"),
        ("O", "Open"),
        ("N", "New chart"),
        ("1 / 2 / 3", "Difficulty"),
        ("G", "Change snap"),
        ("Escape", "Quit")
    ]

    y += 40

    for key, description in controls:
        draw_text(
            key,
            FONT_TINY,
            CYAN,
            TIMELINE_X + 15,
            y
        )

        draw_text(
            description,
            FONT_TINY,
            LIGHT_GRAY,
            TIMELINE_X + 95,
            y
        )

        y += 24

    # Current beat
    pygame.draw.line(
        SCREEN,
        CYAN,
        (
            TIMELINE_X + 10,
            EDITOR_Y + EDITOR_HEIGHT - 90
        ),
        (
            TIMELINE_X + TIMELINE_WIDTH - 10,
            EDITOR_Y + EDITOR_HEIGHT - 90
        ),
        1
    )

    draw_text(
        f"View: {format_beat(scroll_beat)}",
        FONT_SMALL,
        CYAN,
        TIMELINE_X + 15,
        EDITOR_Y + EDITOR_HEIGHT - 75
    )


# ============================================================
# DRAW BOTTOM BAR
# ============================================================


def draw_bottom_bar():
    y = HEIGHT - BOTTOM_BAR_HEIGHT

    pygame.draw.rect(
        SCREEN,
        DARK,
        (0, y, WIDTH, BOTTOM_BAR_HEIGHT)
    )

    pygame.draw.line(
        SCREEN,
        CYAN,
        (0, y),
        (WIDTH, y),
        2
    )

    draw_text(
        "LMB: place/select    RMB: delete    Wheel: scroll",
        FONT_SMALL,
        LIGHT_GRAY,
        20,
        y + 12
    )

    draw_text(
        f"Current beat: {format_beat(scroll_beat)}",
        FONT_SMALL,
        CYAN,
        20,
        y + 40
    )

    draw_text(
        f"Snap: 1/{int(1 / snap_value)}",
        FONT_SMALL,
        YELLOW,
        250,
        y + 40
    )

    if current_file:
        filename = os.path.basename(current_file)

        draw_text(
            filename,
            FONT_SMALL,
            GREEN,
            WIDTH - 300,
            y + 15
        )

    else:
        draw_text(
            "UNSAVED",
            FONT_SMALL,
            RED,
            WIDTH - 120,
            y + 15
        )


# ============================================================
# ADD / DELETE NOTES
# ============================================================


def place_note(mouse_x, mouse_y):
    global selected_note

    lane = mouse_to_lane(mouse_x)

    if lane is None:
        return

    beat = snap_beat(
        y_to_beat(mouse_y)
    )

    if beat < 0:
        beat = 0

    new_note = [
        round(beat, 6),
        lane
    ]

    # Don't create duplicate notes.
    for note in chart_data[current_difficulty]:
        if (
            note[0] == new_note[0]
            and note[1] == new_note[1]
        ):
            selected_note = note
            return

    chart_data[current_difficulty].append(
        new_note
    )

    sort_notes()

    selected_note = new_note


def delete_note(mouse_x, mouse_y):
    global selected_note

    note = find_note_at(
        mouse_x,
        mouse_y
    )

    if note:
        remove_note(note)

        if selected_note is note:
            selected_note = None


# ============================================================
# HANDLE CLICK
# ============================================================


def handle_click(position, button):
    global current_difficulty
    global snap_index
    global snap_value
    global selected_note

    x, y = position

    # Difficulty buttons
    if 720 <= x <= 823 and 20 <= y <= 58:
        current_difficulty = "Easy"
        selected_note = None
        return

    if 831 <= x <= 934 and 20 <= y <= 58:
        current_difficulty = "Normal"
        selected_note = None
        return

    if 942 <= x <= 1045 and 20 <= y <= 58:
        current_difficulty = "Hard"
        selected_note = None
        return

    # Editor
    if (
        EDITOR_X <= x <= EDITOR_X + EDITOR_WIDTH
        and EDITOR_Y <= y <= EDITOR_Y + EDITOR_HEIGHT
    ):
        if button == 1:
            note = find_note_at(x, y)

            if note:
                selected_note = note
            else:
                place_note(x, y)

        elif button == 3:
            delete_note(x, y)


# ============================================================
# MOUSE WHEEL
# ============================================================


def scroll_editor(amount):
    global scroll_beat

    scroll_beat -= amount * 2

    if scroll_beat < 0:
        scroll_beat = 0


# ============================================================
# KEYBOARD
# ============================================================


def handle_key(event):
    global snap_index
    global snap_value
    global current_difficulty
    global scroll_beat
    global bpm

    if event.key == pygame.K_ESCAPE:
        return False

    if event.key == pygame.K_s:
        save()

    elif event.key == pygame.K_o:
        open_chart()

    elif event.key == pygame.K_n:
        new_chart()

    elif event.key == pygame.K_1:
        current_difficulty = "Easy"

    elif event.key == pygame.K_2:
        current_difficulty = "Normal"

    elif event.key == pygame.K_3:
        current_difficulty = "Hard"

    elif event.key == pygame.K_g:
        snap_index += 1

        if snap_index >= len(SNAP_VALUES):
            snap_index = 0

        snap_value = SNAP_VALUES[snap_index]

    elif event.key == pygame.K_PAGEUP:
        scroll_beat = max(
            0,
            scroll_beat - 8
        )

    elif event.key == pygame.K_PAGEDOWN:
        scroll_beat += 8

    elif event.key == pygame.K_UP:
        scroll_beat = max(
            0,
            scroll_beat - 1
        )

    elif event.key == pygame.K_DOWN:
        scroll_beat += 1

    elif event.key == pygame.K_DELETE:
        global selected_note

        if selected_note:
            remove_note(selected_note)
            selected_note = None

    elif event.key == pygame.K_EQUALS:
        bpm += 1

    elif event.key == pygame.K_MINUS:
        bpm = max(1, bpm - 1)

    return True


# ============================================================
# MAIN LOOP
# ============================================================


def main():
    global scroll_beat

    running = True

    while running:
        CLOCK.tick(FPS)

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button in (1, 3):
                    handle_click(
                        event.pos,
                        event.button
                    )

                elif event.button == 4:
                    scroll_editor(1)

                elif event.button == 5:
                    scroll_editor(-1)

            elif event.type == pygame.MOUSEWHEEL:
                scroll_editor(event.y)

            elif event.type == pygame.KEYDOWN:
                running = handle_key(event)

        SCREEN.fill(BLACK)

        draw_top_bar()
        draw_editor()
        draw_side_panel()
        draw_bottom_bar()

        pygame.display.flip()

    pygame.quit()


# ============================================================
# START
# ============================================================

if __name__ == "__main__":
    main()
