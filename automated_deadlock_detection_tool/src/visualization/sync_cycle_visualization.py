# sync_cycle_visualization.py

import tkinter as tk
from deadlock_algo import DeadlockDetector
import matplotlib.pyplot as plt
import networkx as nx
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.patches import Rectangle
from matplotlib.lines import Line2D
import time
import threading
import os
import pygame

class SyncCycleVisualization:
    """Handles synchronized narrative and simulation visualization of the cycle detection algorithm."""
    def __init__(self, gui, window):
        self.gui = gui
        self.window = window
        self.sound_manager = gui.sound_manager
        self.detector = DeadlockDetector(self.gui.resources_held, self.gui.resources_wanted, self.gui.total_resources)
        self.rag = self.detector.build_rag()
        self.steps = []
        self.current_step = 0
        self.cycle = None
        self.narrative = []
        self.is_playing = False
        self.play_thread = None
        self.window_valid = True

        # Bind window close event
        self.window.protocol("WM_DELETE_WINDOW", self._on_window_close)

        # Run DFS with step logging
        self._run_dfs_with_steps()

        # Initialize UI
        self._setup_ui()

    def _on_window_close(self):
        """Handle window close event."""
        self.is_playing = False
        self.window_valid = False
        self.window.destroy()

    def _run_dfs_with_steps(self):
        """Modified DFS to log each step for visualization and narrative."""
        visited = set()
        recursion_stack = set()
        parent = {}
        narrative = []
        graph = self.rag
        steps = []

        def dfs(node):
            narrative.append(f"Visiting {node}... let's see where this leads!")
            steps.append({
                'node': node,
                'visited': visited.copy(),
                'recursion_stack': recursion_stack.copy(),
                'action': 'visit',
                'parent': parent.copy()
            })
            visited.add(node)
            recursion_stack.add(node)
            for neighbor in graph.get(node, []):
                narrative.append(f"From {node}, checking neighbor {neighbor}.")
                steps.append({
                    'node': node,
                    'neighbor': neighbor,
                    'visited': visited.copy(),
                    'recursion_stack': recursion_stack.copy(),
                    'action': 'check_edge',
                    'parent': parent.copy()
                })
                if neighbor not in visited:
                    narrative.append(f"{neighbor} hasn't been visited yet. Diving in!")
                    parent[neighbor] = node
                    if dfs(neighbor):
                        return True
                elif neighbor in recursion_stack:
                    narrative.append(f"Whoa! Found {neighbor} in my stack. We got a cycle!")
                    cycle = []
                    current = node
                    while current != neighbor:
                        cycle.append(current)
                        current = parent[current]
                    cycle.append(neighbor)
                    cycle.append(node)
                    self.cycle = cycle
                    steps.append({
                        'node': node,
                        'neighbor': neighbor,
                        'visited': visited.copy(),
                        'recursion_stack': recursion_stack.copy(),
                        'action': 'cycle_found',
                        'cycle': cycle,
                        'parent': parent.copy()
                    })
                    narrative.append(f"Cycle detected: {' -> '.join(cycle)}. Trouble spotted!")
                    return True
            recursion_stack.remove(node)
            narrative.append(f"Done with {node}. Backtracking...")
            steps.append({
                'node': node,
                'visited': visited.copy(),
                'recursion_stack': recursion_stack.copy(),
                'action': 'backtrack',
                'parent': parent.copy()
            })
            return False

        narrative.append("Hey there! I'm Algo, your cycle detection buddy. Got the graph, let's hunt for cycles!")
        for node in graph:
            if node.startswith("P") and node not in visited:
                narrative.append(f"Starting fresh at process {node}. Here we go!")
                if dfs(node):
                    break
        if not self.cycle:
            narrative.append("Phew! No cycles found. The system is safe... for now!")
        else:
            narrative.append("Mission complete! Found a cycle, so there's a deadlock. Time to alert the team!")

        self.steps = steps
        self.narrative = narrative

    def _setup_ui(self):
        """Sets up the UI for synchronized narrative and simulation."""
        self.canvas = tk.Canvas(self.window, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        self.gui.add_gradient(self.canvas, "#A3BFFA", "#F3F4F6", 1200, 700)

        # Bind resize event to update gradient
        def on_resize(event):
            if not self.window_valid:
                return
            new_width = self.canvas.winfo_width()
            new_height = self.canvas.winfo_height()
            self.canvas.delete("all")
            self.gui.add_gradient(self.canvas, "#A3BFFA", "#F3F4F6", new_width, new_height)
            # Re-place UI elements
            main_frame.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.95, relheight=0.85)
            control_frame.place(relx=0.5, rely=0.95, anchor="center")

        self.canvas.bind("<Configure>", on_resize)

        # Main frame to hold narrative and simulation
        main_frame = tk.Frame(self.canvas, bg="#F3F4F6")
        main_frame.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.95, relheight=0.85)

        # Left panel: Narrative
        narrative_frame = tk.Frame(main_frame, bg="#F3F4F6")
        narrative_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        narrative_title = tk.Label(narrative_frame, text="Algo's Cycle Detection Narrative",
                                   font=("Helvetica", 16, "bold"), bg="#F3F4F6", fg="#2E3A59")
        narrative_title.pack(anchor="n", pady=5)
        self.text_area = tk.Text(narrative_frame, wrap=tk.WORD, font=("Arial", 12), bg="#FFFFFF", fg="#2E3A59", height=20, width=50)
        scrollbar = tk.Scrollbar(narrative_frame, command=self.text_area.yview)
        self.text_area.config(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.text_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Right panel: Simulation
        simulation_frame = tk.Frame(main_frame, bg="#F3F4F6")
        simulation_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        simulation_title = tk.Label(simulation_frame, text="Cycle Detection Simulation",
                                    font=("Helvetica", 16, "bold"), bg="#F3F4F6", fg="#2E3A59")
        simulation_title.pack(anchor="n", pady=5)
        self.fig, self.ax = plt.subplots(figsize=(6, 5))
        self.ax.set_facecolor('#f8f9fa')
        self.ax.grid(True, linestyle='--', alpha=0.3)
        self.fig_canvas = FigureCanvasTkAgg(self.fig, master=simulation_frame)
        self.fig_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Control frame
        control_frame = tk.Frame(self.canvas, bg="#A3BFFA")
        control_frame.place(relx=0.5, rely=0.95, anchor="center")
        prev_button = tk.Button(control_frame, text="⬅️ Previous", font=("Arial", 12),
                                command=self.prev_step, bg="#FF9800", fg="white")
        prev_button.pack(side=tk.LEFT, padx=5)
        next_button = tk.Button(control_frame, text="Next ➡️", font=("Arial", 12),
                                command=self.next_step, bg="#4CAF50", fg="white")
        next_button.pack(side=tk.LEFT, padx=5)
        self.play_pause_button = tk.Button(control_frame, text="▶️ Play", font=("Arial", 12),
                                           command=self.toggle_play_pause, bg="#2196F3", fg="white")
        self.play_pause_button.pack(side=tk.LEFT, padx=5)

        # Initial display
        self._update_display()

    def _update_display(self):
        """Updates both narrative and simulation for the current step."""
        self._show_narrative()
        self._draw_simulation()

    def _show_narrative(self):
        """Displays the narrative text up to the current step."""
        if not self.window_valid or not self.text_area.winfo_exists():
            return
        try:
            self.text_area.delete(1.0, tk.END)
            for i, line in enumerate(self.narrative[:self.current_step + 1]):
                self.text_area.insert(tk.END, f"{line}\n\n")
            self.text_area.see(tk.END)
        except tk.TclError as e:
            print(f"Tkinter error in _show_narrative: {e}")
            self.is_playing = False
            self.window_valid = False
            return
        if self.sound_manager.sound_enabled:
            try:
                script_dir = os.path.dirname(os.path.abspath(__file__))
                pop_sound_path = os.path.join(script_dir, "..", "..", "assets", "pop.wav")
                pop_sound = pygame.mixer.Sound(pop_sound_path)
                pop_sound.play()
            except FileNotFoundError:
                print(f"Error: 'assets/pop.wav' not found at {pop_sound_path}.")
            except Exception as e:
                print(f"Error playing pop sound: {e}")
        if self.current_step == len(self.narrative) - 1:
            if self.cycle:
                self.sound_manager.play_deadlock_sound()
            else:
                self.sound_manager.play_safe_sound()

    def _draw_simulation(self):
        """Draws the current step of the simulation."""
        if self.current_step >= len(self.steps):
            return

        step = self.steps[self.current_step]
        node = step['node']
        visited = step['visited']
        recursion_stack = step['recursion_stack']
        action = step['action']
        parent = step['parent']
        neighbor = step.get('neighbor')
        cycle = step.get('cycle')

        # Clear previous plot
        self.ax.clear()
        self.ax.set_facecolor('#f8f9fa')
        self.ax.grid(True, linestyle='--', alpha=0.3)
        self.ax.set_title(f"Step {self.current_step + 1}: {action.capitalize()}", fontsize=12)

        # Create graph
        G = nx.DiGraph()
        for n in self.rag:
            G.add_node(n)
            for m in self.rag[n]:
                G.add_edge(n, m)

        # Node types
        processes = [n for n in G.nodes if n.startswith("P")]
        resources = [n for n in G.nodes if n.startswith("R")]
        pos = nx.bipartite_layout(G, processes, align='horizontal', scale=2.0)

        # Node colors
        node_colors = []
        for n in G.nodes:
            if n == node:
                node_colors.append('#ff9999')  # Current node
            elif n in recursion_stack:
                node_colors.append('#ffd700')  # In recursion stack
            elif n in visited:
                node_colors.append('#90ee90')  # Visited
            else:
                node_colors.append('#add8e6')  # Unvisited

        # Draw nodes
        nx.draw_networkx_nodes(G, pos, nodelist=processes, node_shape='o',
                               node_color=[node_colors[list(G.nodes).index(n)] for n in processes],
                               node_size=600, edgecolors='black', ax=self.ax)
        for r in resources:
            x, y = pos[r]
            color = node_colors[list(G.nodes).index(r)]
            rect = Rectangle((x - 0.08, y - 0.08), 0.16, 0.16, facecolor=color, edgecolor='black', linewidth=0.5)
            self.ax.add_patch(rect)
            self.ax.plot(x, y, 'ko', markersize=5)

        # Draw edges
        allocation_edges = [(u, v) for u, v in G.edges if u.startswith("R") and v.startswith("P")]
        request_edges = [(u, v) for u, v in G.edges if u.startswith("P") and v.startswith("R")]
        highlight_edge = [(node, neighbor)] if action == 'check_edge' and neighbor else []
        cycle_edges = [(cycle[i], cycle[i + 1]) for i in range(len(cycle) - 1)] if cycle else []

        nx.draw_networkx_edges(G, pos, edgelist=[e for e in allocation_edges if e not in highlight_edge and e not in cycle_edges],
                               edge_color='black', width=1.2, arrows=True, arrowstyle='-|>', arrowsize=10, ax=self.ax)
        nx.draw_networkx_edges(G, pos, edgelist=[e for e in request_edges if e not in highlight_edge and e not in cycle_edges],
                               edge_color='black', width=1.2, arrows=True, arrowstyle='->', arrowsize=10, ax=self.ax)
        if highlight_edge:
            edge_color = 'blue' if neighbor not in recursion_stack else 'red'
            arrowstyle = '-|>' if node.startswith("R") else '->'
            nx.draw_networkx_edges(G, pos, edgelist=highlight_edge, edge_color=edge_color, width=2.0,
                                   arrows=True, arrowstyle=arrowstyle, arrowsize=15, ax=self.ax)
        if cycle_edges:
            nx.draw_networkx_edges(G, pos, edgelist=[e for e in cycle_edges if e in allocation_edges],
                                   edge_color='red', width=2.0, arrows=True, arrowstyle='-|>', arrowsize=15, ax=self.ax)
            nx.draw_networkx_edges(G, pos, edgelist=[e for e in cycle_edges if e in request_edges],
                                   edge_color='red', width=2.0, arrows=True, arrowstyle='->', arrowsize=15, ax=self.ax)

        # Edge labels
        for edge in allocation_edges:
            u, v = edge
            x1, y1 = pos[u]
            x2, y2 = pos[v]
            mid_x, mid_y = (x1 + x2) / 2, (y1 + y2) / 2
            color = 'red' if edge in cycle_edges else ('blue' if edge in highlight_edge else 'black')
            self.ax.text(mid_x - 0.05, mid_y, "H", fontsize=8, color=color, ha='right', va='center')
        for edge in request_edges:
            u, v = edge
            x1, y1 = pos[u]
            x2, y2 = pos[v]
            mid_x, mid_y = (x1 + x2) / 2, (y1 + y2) / 2
            color = 'red' if edge in cycle_edges else ('blue' if edge in highlight_edge else 'black')
            self.ax.text(mid_x + 0.05, mid_y, "R", fontsize=8, color=color, ha='left', va='center')

        # Node labels
        label_pos = pos.copy()
        for n in label_pos:
            x, y = label_pos[n]
            label_pos[n] = (x - 0.15 if n.startswith("P") else x + 0.15, y)
        nx.draw_networkx_labels(G, label_pos, font_size=10, font_weight='bold', ax=self.ax)

        # Legend
        legend_elements = [
            Line2D([0], [0], marker='o', color='w', label='Process', markerfacecolor='#add8e6', markersize=10),
            Line2D([0], [0], marker='s', color='w', label='Resource', markerfacecolor='#add8e6', markersize=10),
            Line2D([0], [0], color='black', lw=1.2, label='Held (H)/Request (R)'),
            Line2D([0], [0], marker='o', color='w', label='Current Node', markerfacecolor='#ff9999', markersize=10),
            Line2D([0], [0], marker='o', color='w', label='In Stack', markerfacecolor='#ffd700', markersize=10),
            Line2D([0], [0], marker='o', color='w', label='Visited', markerfacecolor='#90ee90', markersize=10)
        ]
        if highlight_edge:
            legend_elements.append(Line2D([0], [0], color='blue', lw=2.0, label='Checking Edge'))
        if cycle_edges:
            legend_elements.append(Line2D([0], [0], color='red', lw=2.0, label='Cycle Edge'))

        self.ax.legend(handles=legend_elements, loc='lower center', bbox_to_anchor=(0.5, -0.3), fontsize=9,
                       ncol=4, frameon=True, edgecolor='black', framealpha=1)

        self.ax.axis('off')
        self.fig.subplots_adjust(bottom=0.25)
        self.fig.tight_layout()
        self.fig_canvas.draw()

    def prev_step(self):
        """Shows the previous step in the visualization."""
        if self.current_step > 0:
            self.current_step -= 1
            self._update_display()

    def next_step(self):
        """Shows the next step in the visualization."""
        if self.current_step < len(self.steps) - 1 and self.window_valid:
            self.current_step += 1
            self._update_display()

    def toggle_play_pause(self):
        """Toggles between play and pause for automatic progression."""
        if self.is_playing:
            self.is_playing = False
            if self.window_valid and self.play_pause_button.winfo_exists():
                self.play_pause_button.config(text="▶️ Play")
            self.play_thread = None
        else:
            if not self.window_valid:
                return
            self.is_playing = True
            if self.play_pause_button.winfo_exists():
                self.play_pause_button.config(text="⏸️ Pause")
            self.play_thread = threading.Thread(target=self._auto_play, daemon=True)
            self.play_thread.start()

    def _auto_play(self):
        """Automatically advances the visualization with a 3-second gap."""
        while self.is_playing and self.current_step < len(self.steps) - 1 and self.window_valid:
            self.window.after(0, self.next_step)
            time.sleep(3)
        if self.current_step >= len(self.steps) - 1 or not self.window_valid:
            self.is_playing = False
            if self.window_valid and self.play_pause_button.winfo_exists():
                self.window.after(0, lambda: self.play_pause_button.config(text="▶️ Play"))