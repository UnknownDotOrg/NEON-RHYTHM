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
    files = sorted(CHARTS_FOLDER.glob("*.json"))

    if not files:
        print("No charts found.")
        input("Press Enter to continue...")
        return None

    print("Available charts:")
    print()

    for index, path in enumerate(files, start=1):
        print(f"{index}. {path.stem}")

    print()
    choice = input("Select a chart: ").strip()

    try:
        index = int(choice) - 1
        return files[index]

    except (ValueError, IndexError):
        print()
        print("Invalid selection.")
        input("Press Enter to continue...")
        return None


def show_chart(path):
    chart = load_chart(path)

    if chart is None:
        input("Press Enter to continue...")
        return

    clear_screen()

    print("=" * 50)
    print("             CHART VIEWER")
    print("=" * 50)
    print()

    print(f"Name:   {chart.get('name', 'Unknown')}")
    print(f"Artist: {chart.get('artist', 'Unknown')}")
    print(f"BPM:    {chart.get('bpm', 120)}")
    print(f"Length: {chart.get('length', 30000)} ms")
    print()

    difficulties = chart.get("difficulties", {})

    for difficulty_name, notes in difficulties.items():
        print(f"{difficulty_name}: {len(notes)} notes")

    print()
    print("-" * 50)
    print()

    for difficulty_name, notes in difficulties.items():

        print(f"[{difficulty_name}]")
        print()

        for number, note in enumerate(notes, start=1):

            if not isinstance(note, list) or len(note) < 2:
                continue

            beat = note[0]
            lane = note[1]

            print(
                f"{number:04d}  "
                f"Beat: {beat:<6} "
                f"Lane: {lane}"
            )

        print()


def main():
    while True:

        clear_screen()

        print("=" * 50)
        print("             CHART VIEWER")
        print("=" * 50)
        print()

        chart_path = choose_chart()

        if chart_path is None:
            return

        show_chart(chart_path)

        print()
        choice = input(
            "Press Enter to return, or type 'q' to quit: "
        ).strip().lower()

        if choice == "q":
            return


if __name__ == "__main__":
    main()
