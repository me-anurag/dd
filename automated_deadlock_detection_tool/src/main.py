import tkinter as tk
import os
import argparse
from gui import DeadlockDetectionGUI
from sound_manager import SoundManager

def main():
    """Entry point for the Deadlock Detection Tool."""
    parser = argparse.ArgumentParser(description="Deadlock Detection Tool")
    parser.add_argument("--radar-sound", default="assets/radar_ping.wav", help="Path to radar sound")
    parser.add_argument("--click-sound", default="assets/click.wav", help="Path to click sound")
    parser.add_argument("--chime-sound", default="assets/chime.wav", help="Path to chime sound")
    parser.add_argument("--suspense-sound", default="assets/suspense_hum.wav", help="Path to suspense sound")
    parser.add_argument("--deadlock-sound", default="assets/deadlock_alarm.wav", help="Path to deadlock sound")
    parser.add_argument("--safe-sound", default="assets/safe_chime.wav", help="Path to safe state sound")
    parser.add_argument("--rewind-sound", default="assets/rewind_whoosh.wav", help="Path to rewind sound")
    parser.add_argument("--pop-sound", default="assets/pop.wav", help="Path to pop sound")
    args = parser.parse_args()

    base_dir = os.path.dirname(os.path.abspath(__file__))
    radar_sound_path = os.path.join(base_dir, "..", args.radar_sound)
    click_sound_path = os.path.join(base_dir, "..", args.click_sound)
    chime_sound_path = os.path.join(base_dir, "..", args.chime_sound)
    suspense_sound_path = os.path.join(base_dir, "..", args.suspense_sound)
    deadlock_sound_path = os.path.join(base_dir, "..", args.deadlock_sound)
    safe_sound_path = os.path.join(base_dir, "..", args.safe_sound)
    rewind_sound_path = os.path.join(base_dir, "..", args.rewind_sound)
    pop_sound_path = os.path.join(base_dir, "..", args.pop_sound)

    # Print paths for debugging
    print(f"Base directory: {base_dir}")
    print(f"Radar sound path: {radar_sound_path}")
    print(f"Click sound path: {click_sound_path}")
    print(f"Chime sound path: {chime_sound_path}")
    print(f"Suspense sound path: {suspense_sound_path}")
    print(f"Deadlock sound path: {deadlock_sound_path}")
    print(f"Safe sound path: {safe_sound_path}")
    print(f"Rewind sound path: {rewind_sound_path}")
    print(f"Pop sound path: {pop_sound_path}")

    # Verify files exist
    for path in [radar_sound_path, click_sound_path, chime_sound_path, suspense_sound_path, 
                 deadlock_sound_path, safe_sound_path, rewind_sound_path, pop_sound_path]:
        if not os.path.exists(path):
            print(f"Warning: File not found at {path}")

    sound_manager = SoundManager(radar_sound_path, click_sound_path, chime_sound_path, suspense_sound_path, 
                                deadlock_sound_path, safe_sound_path, rewind_sound_path, pop_sound_path)

    main_window = tk.Tk()
    app = DeadlockDetectionGUI(main_window, sound_manager)
    main_window.mainloop()

if __name__ == "__main__":
    main()