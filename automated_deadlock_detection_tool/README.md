# Deadlock Detection Tool

Hi there! This is my Deadlock Detection Tool project, built as part of my operating systems coursework. I wanted to create an interactive GUI application to detect deadlocks in systems with both single-instance and multi-instance resources. Here's how I built it, step by step, along with the features I added along the way.

## Project Overview

This tool helps visualize and detect deadlocks in a system using a Resource Allocation Graph (RAG) for single-instance resources. It has a Tkinter-based GUI where you can drag and drop processes and resources to simulate allocations and requests, and then check if a deadlock occurs. I also added sound effects to make it more interactive! Right now, the single-instance detection is fully working, and I'm planning to add multi-instance detection next.

## Project Structure

I organized the project into a modular structure to keep things clean:

- **src/**: Contains all the source code.
  - `main.py`: The entry point to run the application.
  - `gui.py`: Handles the Tkinter GUI and user interactions.
  - `deadlock_algo.py`: Implements the RAG-based deadlock detection algorithm.
  - `sound_manager.py`: Manages sound effects for allocation and request actions.
  - `__init__.py`: Makes the `src/` directory a package.
- **assets/**: Stores sound files (though currently, they're in the root directory).
- **tests/**: For future unit tests (not implemented yet).
- **venv/**: My virtual environment.
- **requirements.txt**: Lists the dependencies (like Pygame for sound).

## How I Built It: Step-by-Step Journey

I started with a basic idea and gradually added features to make the tool more functional and user-friendly. Here’s how I did it, line by line:

- I began by creating a simple Tkinter GUI with a main window that has two buttons: "Single-Instance Detection" and "Multi-Instance Detection".
- Added a gradient background to the main window to make it look nicer, along with a fade-in title animation for a cool effect.
- Included a rotating gear emoji animation on startup to give the app a loading feel.
- Added a dark mode toggle checkbox so users can switch between light and dark themes.
- Created the single-instance detection window where users can input the number of processes and resources (e.g., 2 processes, 2 resources).
- Set up a drag-and-drop interface in the single-instance window with three sections: a left canvas for allocations, a center canvas for dragging, and a right canvas for requests.
- Represented processes with a robot emoji (🤖) and resources with a computer emoji (🖥️) to make it visually clear.
- Implemented the allocation phase: users can drag resources to processes to allocate them (e.g., drag R1 to P1).
- Added validation to prevent a resource from being allocated to multiple processes (since this is single-instance).
- Added a "Finish Allocation" button to move to the request phase.
- Implemented the request phase: users can now drag processes to resources to request them (e.g., drag P1 to R2).
- Added a tooltip feature: hovering over a process or resource shows its current state (e.g., "P1: Holds [R1], Requests [R2]").
- Added an "Undo" button to revert the last allocation or request action, making the tool more user-friendly.
- Added a "Reset" button to clear everything and start over.
- Added sound effects for allocation and request actions using Pygame—I used `allocate_sound.wav` for allocations and `request_sound.wav` for requests.
- Added a sound mode toggle: a "Sound On/Off" checkbox in the main window lets users enable or disable sound effects.
- Implemented the RAG-based deadlock detection algorithm in `deadlock_algo.py` using a Depth-First Search (DFS) to detect cycles in the Resource Allocation Graph.
- Added a "Detect Deadlock" button in the single-instance window to run the deadlock detection algorithm and show the result in a messagebox (e.g., "A deadlock has been detected in the system!").
- Modularized the code into separate files (`gui.py`, `deadlock_algo.py`, `sound_manager.py`) to keep things organized and maintainable.
- Added error handling for sound loading: if the sound files are missing, the app continues without sounds and prints a message to the console.

## Features

- **Interactive GUI**: Built with Tkinter, featuring drag-and-drop for allocating and requesting resources.
- **Single-Instance Deadlock Detection**: Uses RAG to detect deadlocks by finding cycles in the graph.
- **Sound Effects**: Plays sounds for allocation and request actions, with a toggle to enable/disable them.
- **Dark Mode**: Switch between light and dark themes for better usability.
- **Undo and Reset**: Easily undo the last action or reset the entire simulation.
- **Tooltips**: Hover over processes or resources to see their current state.
- **Error Handling**: Prevents invalid allocations/requests and handles missing sound files gracefully.

