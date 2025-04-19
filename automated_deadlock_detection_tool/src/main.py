import tkinter as tk
import os
import argparse
from gui import DeadlockDetectionGUI
from sound_manager import SoundManager

def main():
    """Entry point for the Deadlock Detection Tool."""
    parser = argparse.ArgumentParser(description="Deadlock Detection Tool")
    parser.add_argument("--allocate-sound", default="assets/allocate_sound.wav", help="Path to allocate sound")
    parser.add_argument("--request-sound", default="assets/request_sound.wav", help="Path to request sound")
    parser.add_argument("--deadlock-sound", default="assets/deadlock_sound.wav", help="Path to deadlock sound")
    parser.add_argument("--safe-sound", default="assets/safe_sound.wav", help="Path to safe state sound")
    args = parser.parse_args()

    base_dir = os.path.dirname(os.path.abspath(__file__))
    allocate_sound_path = os.path.join(base_dir, "..", args.allocate_sound)
    request_sound_path = os.path.join(base_dir, "..", args.request_sound)
    deadlock_sound_path = os.path.join(base_dir, "..", args.deadlock_sound)
    safe_sound_path = os.path.join(base_dir, "..", args.safe_sound)

    # Print paths for debugging
    print(f"Base directory: {base_dir}")
    print(f"Allocate sound path: {allocate_sound_path}")
    print(f"Request sound path: {request_sound_path}")
    print(f"Deadlock sound path: {deadlock_sound_path}")
    print(f"Safe sound path: {safe_sound_path}")

    # Verify files exist
    for path in [allocate_sound_path, request_sound_path, deadlock_sound_path, safe_sound_path]:
        if not os.path.exists(path):
            print(f"Warning: File not found at {path}")

    sound_manager = SoundManager(allocate_sound_path, request_sound_path, deadlock_sound_path, safe_sound_path)

    main_window = tk.Tk()
    app = DeadlockDetectionGUI(main_window, sound_manager)
    main_window.mainloop()

if __name__ == "__main__":
    main()