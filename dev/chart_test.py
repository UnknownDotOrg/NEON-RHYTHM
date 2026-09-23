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


def test_metadata(chart):
    errors = []
    warnings = []

    required_fields = [
        "name",
        "artist",
        "bpm",
        "length",
        "difficulties"
    ]

    for field in required_fields:
        if field not in chart:
            errors.append(
                f"Missing required field: {field}"
            )

    bpm = chart.get("bpm")

    if "bpm" in chart:
        if not isinstance(
            bpm,
            (int, float)
        ):
            errors.append(
                "BPM must be a number."
            )

        elif bpm <= 0:
            errors.append(
                "BPM must be greater than 0."
            )

    length = chart.get("length")

    if "length" in chart:
        if not isinstance(
            length,
            (int, float)
        ):
            errors.append(
                "Length must be a number."
            )

        elif length <= 0:
            errors.append(
                "Length must be greater than 0."
            )

    difficulties = chart.get(
        "difficulties"
    )

    if "difficulties" in chart:
        if not isinstance(
            difficulties,
            dict
        ):
            errors.append(
                "Difficulties must be an object."
            )

    return errors, warnings


def test_difficulty(
    difficulty_name,
    notes,
    bpm,
    length
):
    errors = []
    warnings = []

    if not isinstance(
        notes,
        list
    ):
        errors.append(
            f"{difficulty_name}: "
            "notes must be a list."
        )

        return errors, warnings

    previous_beat = None
    seen_notes = set()

    milliseconds_per_beat = (
        60000 / bpm
        if bpm > 0
        else 0
    )

    for index, note in enumerate(
        notes
    ):

        if not isinstance(
            note,
            list
        ):
            errors.append(
                f"{difficulty_name}: "
                f"Note {index} is not a list."
            )
            continue

        if len(note) < 2:
            errors.append(
                f"{difficulty_name}: "
                f"Note {index} needs "
                "beat and lane."
            )
            continue

        beat = note[0]
        lane = note[1]

        if not isinstance(
            beat,
            (int, float)
        ):
            errors.append(
                f"{difficulty_name}: "
                f"Note {index} has "
                "an invalid beat."
            )
            continue

        if beat < 0:
            errors.append(
                f"{difficulty_name}: "
                f"Note {index} has "
                f"negative beat {beat}."
            )

        if not isinstance(
            lane,
            int
        ):
            errors.append(
                f"{difficulty_name}: "
                f"Note {index} has "
                "a non-integer lane."
            )
            continue

        if lane < 0 or lane > 3:
            errors.append(
                f"{difficulty_name}: "
                f"Note {index} has "
                f"invalid lane {lane}."
            )

        if previous_beat is not None:
            if beat < previous_beat:
                warnings.append(
                    f"{difficulty_name}: "
                    f"Note {index} is out "
                    "of beat order."
                )

        previous_beat = beat

        note_key = (
            beat,
            lane
        )

        if note_key in seen_notes:
            warnings.append(
                f"{difficulty_name}: "
                f"Duplicate note at "
                f"beat {beat}, lane {lane}."
            )

        seen_notes.add(
            note_key
        )

        if milliseconds_per_beat > 0:
            note_time = (
                beat
                * milliseconds_per_beat
            )

            if note_time > length:
                warnings.append(
                    f"{difficulty_name}: "
                    f"Note {index} occurs "
                    f"after chart length."
                )

    return errors, warnings


def test_chart(chart):
    errors = []
    warnings = []

    metadata_errors, metadata_warnings = (
        test_metadata(chart)
    )

    errors.extend(
        metadata_errors
    )

    warnings.extend(
        metadata_warnings
    )

    bpm = chart.get(
        "bpm",
        120
    )

    length = chart.get(
        "length",
        30000
    )

    difficulties = chart.get(
        "difficulties",
        {}
    )

    if not isinstance(
        bpm,
        (int, float)
    ) or bpm <= 0:
        bpm = 120

    if not isinstance(
        length,
        (int, float)
    ) or length <= 0:
        length = 30000

    if not isinstance(
        difficulties,
        dict
    ):
        return errors, warnings

    for difficulty_name in [
        "Easy",
        "Normal",
        "Hard"
    ]:

        if difficulty_name not in difficulties:
            warnings.append(
                f"Missing difficulty: "
                f"{difficulty_name}"
            )
            continue

        difficulty_errors, difficulty_warnings = (
            test_difficulty(
                difficulty_name,
                difficulties[difficulty_name],
                bpm,
                length
            )
        )

        errors.extend(
            difficulty_errors
        )

        warnings.extend(
            difficulty_warnings
        )

    return errors, warnings


def show_results(
    chart_path,
    chart,
    errors,
    warnings
):
    clear_screen()

    print("=" * 60)
    print("                  CHART TESTER")
    print("=" * 60)
    print()

    print(
        f"Chart:  "
        f"{chart.get('name', 'Unknown')}"
    )

    print(
        f"File:   "
        f"{chart_path.name}"
    )

    print()

    print("-" * 60)
    print()

    if errors:
        print(
            f"RESULT: FAILED "
            f"({len(errors)} error(s))"
        )

    elif warnings:
        print(
            f"RESULT: PASSED WITH "
            f"{len(warnings)} WARNING(S)"
        )

    else:
        print(
            "RESULT: PASSED"
        )

    print()

    if errors:
        print("ERRORS")
        print("-" * 60)

        for error in errors:
            print(
                f"[ERROR] {error}"
            )

        print()

    if warnings:
        print("WARNINGS")
        print("-" * 60)

        for warning in warnings:
            print(
                f"[WARNING] {warning}"
            )

        print()

    difficulties = chart.get(
        "difficulties",
        {}
    )

    print("CHART SUMMARY")
    print("-" * 60)

    for difficulty_name in [
        "Easy",
        "Normal",
        "Hard"
    ]:

        notes = difficulties.get(
            difficulty_name,
            []
        )

        if isinstance(
            notes,
            list
        ):
            print(
                f"{difficulty_name:<10}"
                f"{len(notes)} notes"
            )

        else:
            print(
                f"{difficulty_name:<10}"
                "Invalid"
            )

    print()

    print(
        f"BPM:    "
        f"{chart.get('bpm', 'Unknown')}"
    )

    print(
        f"Length: "
        f"{chart.get('length', 'Unknown')} ms"
    )

    print()


def main():
    while True:
        clear_screen()

        print("=" * 60)
        print("                  CHART TESTER")
        print("=" * 60)
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

        errors, warnings = test_chart(
            chart
        )

        show_results(
            chart_path,
            chart,
            errors,
            warnings
        )

        print(
            "-" * 60
        )

        choice = input(
            "Press Enter to test another chart, "
            "or type 'q' to quit: "
        ).strip().lower()

        if choice == "q":
            return


if __name__ == "__main__":
    main()
