import json
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
CHARTS_FOLDER = BASE_DIR / "charts"


def clear_screen():
    print("\033[2J\033[H", end="")


def load_chart(path):
    try:
        with path.open("r", encoding="utf-8") as file:
            return json.load(file)

    except FileNotFoundError:
        print("Error: Chart file not found.")
        return None

    except json.JSONDecodeError as error:
        print(f"Error: Invalid JSON: {error}")
        return None


def save_chart(path, chart):
    try:
        with path.open("w", encoding="utf-8") as file:
            json.dump(
                chart,
                file,
                indent=4
            )

        return True

    except OSError as error:
        print(f"Error saving chart: {error}")
        return False


def choose_chart():
    files = sorted(
        CHARTS_FOLDER.glob("*.json")
    )

    if not files:
        print("No charts found.")
        input("Press Enter to continue...")
        return None

    print("Available charts:")
    print()

    for index, path in enumerate(
        files,
        start=1
    ):
        print(
            f"{index}. {path.stem}"
        )

    print()

    choice = input(
        "Select a chart: "
    ).strip()

    try:
        index = int(choice) - 1

        return files[index]

    except (
        ValueError,
        IndexError
    ):
        print()
        print("Invalid selection.")
        input("Press Enter to continue...")

        return None


def choose_difficulty(chart):
    difficulties = [
        "Easy",
        "Normal",
        "Hard"
    ]

    print("Difficulties:")
    print()

    for index, difficulty in enumerate(
        difficulties,
        start=1
    ):
        notes = chart.get(
            "difficulties",
            {}
        ).get(
            difficulty,
            []
        )

        print(
            f"{index}. {difficulty} "
            f"({len(notes)} notes)"
        )

    print()

    choice = input(
        "Select a difficulty: "
    ).strip()

    try:
        index = int(choice) - 1

        return difficulties[index]

    except (
        ValueError,
        IndexError
    ):
        print()
        print("Invalid selection.")
        input("Press Enter to continue...")

        return None


def list_notes(notes):
    print()
    print(
        f"{'ID':<6}"
        f"{'Beat':<12}"
        f"Lane"
    )
    print("-" * 30)

    for index, note in enumerate(
        notes
    ):
        if not isinstance(
            note,
            list
        ):
            continue

        if len(note) < 2:
            continue

        beat = note[0]
        lane = note[1]

        print(
            f"{index:<6}"
            f"{beat:<12}"
            f"{lane}"
        )

    print()
    print(
        f"Total notes: {len(notes)}"
    )


def add_note(notes):
    print()
    print("Add Note")
    print("-" * 30)

    beat_input = input(
        "Beat: "
    ).strip()

    lane_input = input(
        "Lane (0-3): "
    ).strip()

    try:
        beat = float(
            beat_input
        )

        lane = int(
            lane_input
        )

    except ValueError:
        print()
        print(
            "Invalid number."
        )
        input(
            "Press Enter to continue..."
        )
        return

    if lane < 0 or lane > 3:
        print()
        print(
            "Lane must be between 0 and 3."
        )
        input(
            "Press Enter to continue..."
        )
        return

    notes.append([
        beat,
        lane
    ])

    notes.sort(
        key=lambda note: note[0]
    )

    print()
    print(
        f"Added note at beat "
        f"{beat}, lane {lane}."
    )

    input(
        "Press Enter to continue..."
    )


def delete_note(notes):
    if not notes:
        print()
        print("There are no notes to delete.")
        input(
            "Press Enter to continue..."
        )
        return

    list_notes(notes)

    note_input = input(
        "Note ID to delete: "
    ).strip()

    try:
        index = int(
            note_input
        )

        notes.pop(index)

    except (
        ValueError,
        IndexError
    ):
        print()
        print("Invalid note ID.")
        input(
            "Press Enter to continue..."
        )
        return

    print()
    print(
        f"Deleted note {index}."
    )

    input(
        "Press Enter to continue..."
    )


def edit_note(notes):
    if not notes:
        print()
        print("There are no notes to edit.")
        input(
            "Press Enter to continue..."
        )
        return

    list_notes(notes)

    note_input = input(
        "Note ID to edit: "
    ).strip()

    try:
        index = int(
            note_input
        )

        note = notes[index]

    except (
        ValueError,
        IndexError
    ):
        print()
        print("Invalid note ID.")
        input(
            "Press Enter to continue..."
        )
        return

    print()
    print(
        f"Current beat: {note[0]}"
    )
    print(
        f"Current lane: {note[1]}"
    )
    print()

    beat_input = input(
        "New beat: "
    ).strip()

    lane_input = input(
        "New lane (0-3): "
    ).strip()

    try:
        beat = float(
            beat_input
        )

        lane = int(
            lane_input
        )

    except ValueError:
        print()
        print("Invalid number.")
        input(
            "Press Enter to continue..."
        )
        return

    if lane < 0 or lane > 3:
        print()
        print(
            "Lane must be between 0 and 3."
        )
        input(
            "Press Enter to continue..."
        )
        return

    note[0] = beat
    note[1] = lane

    notes.sort(
        key=lambda note: note[0]
    )

    print()
    print("Note updated.")

    input(
        "Press Enter to continue..."
    )


def editor_loop(chart, chart_path, difficulty):
    difficulties = chart.setdefault(
        "difficulties",
        {}
    )

    notes = difficulties.setdefault(
        difficulty,
        []
    )

    modified = False

    while True:
        clear_screen()

        print("=" * 50)
        print("             CHART EDITOR")
        print("=" * 50)
        print()

        print(
            f"Chart:      "
            f"{chart.get('name', 'Unknown')}"
        )

        print(
            f"Difficulty: {difficulty}"
        )

        print(
            f"Notes:      {len(notes)}"
        )

        if modified:
            print(
                "Status:     UNSAVED CHANGES"
            )
        else:
            print(
                "Status:     Saved"
            )

        print()
        print("-" * 50)
        print()

        print("1. List notes")
        print("2. Add note")
        print("3. Edit note")
        print("4. Delete note")
        print("5. Save")
        print("6. Back")
        print()

        choice = input(
            "Select an option: "
        ).strip()

        if choice == "1":
            clear_screen()

            list_notes(notes)

            input(
                "\nPress Enter to continue..."
            )

        elif choice == "2":
            add_note(notes)
            modified = True

        elif choice == "3":
            edit_note(notes)
            modified = True

        elif choice == "4":
            delete_note(notes)
            modified = True

        elif choice == "5":
            if save_chart(
                chart_path,
                chart
            ):
                print()
                print(
                    "Chart saved successfully."
                )
                modified = False

            input(
                "Press Enter to continue..."
            )

        elif choice == "6":

            if modified:
                print()
                print(
                    "You have unsaved changes."
                )

                confirm = input(
                    "Exit without saving? "
                    "(y/n): "
                ).strip().lower()

                if confirm != "y":
                    continue

            return

        else:
            print()
            print("Invalid option.")
            input(
                "Press Enter to continue..."
            )


def main():
    while True:
        clear_screen()

        print("=" * 50)
        print("             CHART EDITOR")
        print("=" * 50)
        print()

        chart_path = choose_chart()

        if chart_path is None:
            return

        chart = load_chart(
            chart_path
        )

        if chart is None:
            input(
                "Press Enter to continue..."
            )
            continue

        clear_screen()

        difficulty = choose_difficulty(
            chart
        )

        if difficulty is None:
            continue

        editor_loop(
            chart,
            chart_path,
            difficulty
        )

        return


if __name__ == "__main__":
    main()
