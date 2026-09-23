from pathlib import Path
import subprocess
import sys


DEV_FOLDER = Path(__file__).resolve().parent


def clear_screen():
    print("\033[2J\033[H", end="")


def show_menu():
    clear_screen()

    print("=" * 40)
    print("        NEON RHYTHM DEV MODE")
    print("=" * 40)
    print()
    print("1. Chart Editor")
    print("2. Chart Viewer")
    print("3. Chart Tester")
    print("4. Exit")
    print()


def launch_tool(filename):
    tool_path = DEV_FOLDER / filename

    if not tool_path.exists():
        print()
        print(f"Error: {filename} does not exist.")
        input("Press Enter to continue...")
        return

    subprocess.run(
        [sys.executable, str(tool_path)],
        cwd=DEV_FOLDER.parent
    )


def main():
    while True:

        show_menu()

        choice = input("Select an option: ").strip()

        if choice == "1":
            launch_tool("chart_editor.py")

        elif choice == "2":
            launch_tool("chart_viewer.py")

        elif choice == "3":
            launch_tool("chart_test.py")

        elif choice == "4":
            print()
            print("Exiting Developer Mode...")
            break

        else:
            print()
            print("Invalid option.")
            input("Press Enter to continue...")


if __name__ == "__main__":
    main()
