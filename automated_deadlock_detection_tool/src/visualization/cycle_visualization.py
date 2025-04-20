import tkinter as tk
from deadlock_algo import DeadlockDetector
import matplotlib.pyplot as plt
import networkx as nx
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.patches import Rectangle, Circle
from matplotlib.lines import Line2D
import time
import threading
import os
import pygame
import json
import random

class CycleVisualization:
    """Handles the simulation and narrative visualization of the cycle detection algorithm."""
    def __init__(self, gui, window, mode):
        self.gui = gui
        self.window = window
        self.mode = mode
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

        # Load narrative templates
        script_dir = os.path.dirname(os.path.abspath(__file__))
        try:
            with open(os.path.join(script_dir, 'narrative.json'), 'r', encoding='utf-8') as f:  # Specify UTF-8
                self.narrative_templates = json.load(f)
        except FileNotFoundError:
            print("Error: narrative.json not found. Using fallback narrative.")
            self.narrative_templates = {
                'intro': ["Fallback: Starting cycle detection..."],
                'start': ["Visiting {node}..."],
                'visit': ["Visiting {node}..."],
                'check_edge': ["Checking edge from {node} to {neighbor}..."],
                'cycle_found': ["Cycle found: {cycle}!"],
                'backtrack': ["Backtracking from {node}..."],
                'no_cycle': ["No cycles found!"],
                'cycle_detected': ["Deadlock at {cycle}!"]
            }

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

        # Build introductory narrative
        self._build_intro()
        narrative.extend(self.narrative)

        def dfs(node):
            # Narrative for visiting a node
            held = [r for r, ps in self.gui.resources_held.items() if node in ps]
            wanted = [r for r, ps in self.gui.resources_wanted.items() if node in ps]
            context = f"clutching {', '.join(held) or 'nothing'}" if held else ""
            context += f" and eyeing {', '.join(wanted) or 'nothing'}" if wanted else ""
            narrative.append(random.choice(self.narrative_templates['visit']).format(
                node=node, context=context))
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
                # Narrative for checking an edge
                edge_type = "hoarding" if node.startswith("R") else "begging for"
                narrative.append(random.choice(self.narrative_templates['check_edge']).format(
                    node=node, neighbor=neighbor, edge_type=edge_type))
                steps.append({
                    'node': node,
                    'neighbor': neighbor,
                    'visited': visited.copy(),
                    'recursion_stack': recursion_stack.copy(),
                    'action': 'check_edge',
                    'parent': parent.copy()
                })
                if neighbor not in visited:
                    narrative.append(random.choice(self.narrative_templates['dive']).format(
                        neighbor=neighbor))
                    parent[neighbor] = node
                    if dfs(neighbor):
                        return True
                elif neighbor in recursion_stack:
                    cycle = []
                    current = node
                    while current != neighbor:
                        cycle.append(current)
                        current = parent[current]
                    cycle.append(neighbor)
                    cycle.append(node)
                    self.cycle = cycle
                    # Narrative for cycle found
                    cycle_str = " -> ".join(cycle)
                    narrative.append(random.choice(self.narrative_templates['cycle_found']).format(
                        neighbor=neighbor, cycle=cycle_str))
                    steps.append({
                        'node': node,
                        'neighbor': neighbor,
                        'visited': visited.copy(),
                        'recursion_stack': recursion_stack.copy(),
                        'action': 'cycle_found',
                        'cycle': cycle,
                        'parent': parent.copy()
                    })
                    return True
            recursion_stack.remove(node)
            # Narrative for backtracking
            narrative.append(random.choice(self.narrative_templates['backtrack']).format(node=node))
            steps.append({
                'node': node,
                'visited': visited.copy(),
                'recursion_stack': recursion_stack.copy(),
                'action': 'backtrack',
                'parent': parent.copy()
            })
            return False

        for node in graph:
            if node.startswith("P") and node not in visited:
                narrative.append(random.choice(self.narrative_templates['start']).format(node=node))
                if dfs(node):
                    break
        # Final narrative
        if not self.cycle:
            narrative.append(random.choice(self.narrative_templates['no_cycle']))
        else:
            narrative.append(random.choice(self.narrative_templates['cycle_detected']).format(
                cycle=" -> ".join(self.cycle)))

        self.steps = steps
        self.narrative = narrative

    def _build_intro(self):
        """Builds an introductory narrative summarizing the graph."""
        num_processes = sum(1 for n in self.rag if n.startswith("P"))
        num_resources = sum(1 for n in self.rag if n.startswith("R"))
        allocations = []
        for r, ps in self.gui.resources_held.items():
            if ps:
                allocations.append(f"{r} hoarded by {', '.join(ps)}")
        requests = []
        for r, ps in self.gui.resources_wanted.items():
            if ps:
                requests.append(f"{r} wanted by {', '.join(ps)}")
        intro = random.choice(self.narrative_templates['intro']).format(
            num_processes=num_processes,
            processes=", ".join([n for n in self.rag if n.startswith("P")]),
            num_resources=num_resources,
            resources=", ".join([n for n in self.rag if n.startswith("R")]),
            allocations="; ".join(allocations) or "no allocations yet",
            requests="; ".join(requests) or "no requests yet"
        )
        self.narrative = [intro]

    def _setup_ui(self):
        """Sets up the UI for simulation or narrative mode."""
        self.canvas = tk.Canvas(self.window, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        self.gui.add_gradient(self.canvas, "#A3BFFA", "#F3F4F6", 800, 600)

        def on_resize(event):
            if not self.window_valid:
                return
            new_width = self.canvas.winfo_width()
            new_height = self.canvas.winfo_height()
            self.canvas.delete("all")
            self.gui.add_gradient(self.canvas, "#A3BFFA", "#F3F4F6", new_width, new_height)
            if self.mode == "simulation":
                control_frame.place(relx=0.5, rely=0.1, anchor="center")
                self.fig_canvas.get_tk_widget().place(relx=0.5, rely=0.55, anchor="center")
            else:
                title_label.place(relx=0.5, rely=0.05, anchor="center")
                text_frame.place(relx=0.5, rely=0.55, anchor="center", relwidth=0.9, relheight=0.8)
                control_frame.place(relx=0.5, rely=0.95, anchor="center")

        self.canvas.bind("<Configure>", on_resize)

        if self.mode == "simulation":
            control_frame = tk.Frame(self.canvas, bg="#A3BFFA")
            control_frame.place(relx=0.5, rely=0.1, anchor="center")
            prev_button = tk.Button(control_frame, text="⬅️ Previous", font=("Arial", 12),
                                    command=self.prev_step, bg="#FF9800", fg="white")
            prev_button.pack(side=tk.LEFT, padx=5)
            next_button = tk.Button(control_frame, text="Next ➡️", font=("Arial", 12),
                                    command=self.next_step, bg="#4CAF50", fg="white")
            next_button.pack(side=tk.LEFT, padx=5)
            play_button = tk.Button(control_frame, text="▶️ Play", font=("Arial", 12),
                                    command=self.play_simulation, bg="#2196F3", fg="white")
            play_button.pack(side=tk.LEFT, padx=5)
            self.fig, self.ax = plt.subplots(figsize=(8, 5))
            self.ax.set_facecolor('#f8f9fa')
            self.ax.grid(True, linestyle='--', alpha=0.3)
            self.fig_canvas = FigureCanvasTkAgg(self.fig, master=self.canvas)
            self.fig_canvas.get_tk_widget().place(relx=0.5, rely=0.55, anchor="center")
            self._draw_step()
        else:
            title_label = tk.Label(self.canvas, text="Algo's Deadlock Quest",
                                   font=("Helvetica", 20, "bold"), bg="#A3BFFA", fg="#2E3A59")
            title_label.place(relx=0.5, rely=0.05, anchor="center")
            text_frame = tk.Frame(self.canvas, bg="#F3F4F6")
            text_frame.place(relx=0.5, rely=0.55, anchor="center", relwidth=0.9, relheight=0.8)
            self.text_area = tk.Text(text_frame, wrap=tk.WORD, font=("Arial", 12), bg="#F3F4F6", fg="#2E3A59")
            scrollbar = tk.Scrollbar(text_frame, command=self.text_area.yview)
            self.text_area.config(yscrollcommand=scrollbar.set)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            self.text_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            control_frame = tk.Frame(self.canvas, bg="#A3BFFA")
            control_frame.place(relx=0.5, rely=0.95, anchor="center")
            prev_button = tk.Button(control_frame, text="⬅️ Previous", font=("Arial", 12),
                                    command=self.prev_narrative, bg="#FF9800", fg="white")
            prev_button.pack(side=tk.LEFT, padx=5)
            next_button = tk.Button(control_frame, text="Next ➡️", font=("Arial", 12),
                                    command=self.next_narrative, bg="#4CAF50", fg="white")
            next_button.pack(side=tk.LEFT, padx=5)
            self.play_pause_button = tk.Button(control_frame, text="▶️ Play", font=("Arial", 12),
                                               command=self.toggle_play_pause, bg="#2196F3", fg="white")
            self.play_pause_button.pack(side=tk.LEFT, padx=5)
            self._show_narrative()

    def _draw_step(self):
        """Draws the current step of the simulation with highlighted current node."""
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
        self.ax.clear()
        self.ax.set_facecolor('#f8f9fa')
        self.ax.grid(True, linestyle='--', alpha=0.3)
        # Updated title to be more informative
        if action == 'visit':
            title = f"Step {self.current_step + 1}: Visiting Node {node}"
        elif action == 'check_edge':
            title = f"Step {self.current_step + 1}: Checking Edge {node} -> {neighbor}"
        elif action == 'cycle_found':
            cycle_str = " -> ".join(cycle)
            title = f"Step {self.current_step + 1}: Cycle Detected: {cycle_str}"
        elif action == 'backtrack':
            title = f"Step {self.current_step + 1}: Backtracking from {node}"
        else:
            title = f"Step {self.current_step + 1}: {action.capitalize()}"
        self.ax.set_title(title, fontsize=14)
        G = nx.DiGraph()
        for n in self.rag:
            G.add_node(n)
            for m in self.rag[n]:
                G.add_edge(n, m)
        processes = [n for n in G.nodes if n.startswith("P")]
        resources = [n for n in G.nodes if n.startswith("R")]
        pos = nx.bipartite_layout(G, processes, align='horizontal', scale=2.0)
        node_colors = []
        for n in G.nodes:
            if n == node:
                node_colors.append('#ff9999')
            elif n in recursion_stack:
                node_colors.append('#ffd700')
            elif n in visited:
                node_colors.append('#90ee90')
            else:
                node_colors.append('#add8e6')
        if node in pos:
            x, y = pos[node]
            if node.startswith("P"):
                highlight = Circle((x, y), 0.12, facecolor='#ff6666', edgecolor='none', alpha=0.5, zorder=0)
                self.ax.add_patch(highlight)
            else:
                highlight = Rectangle((x - 0.1, y - 0.1), 0.2, 0.2, facecolor='#ff6666', edgecolor='none', alpha=0.5, zorder=0)
                self.ax.add_patch(highlight)
        nx.draw_networkx_nodes(G, pos, nodelist=processes, node_shape='o',
                               node_color=[node_colors[list(G.nodes).index(n)] for n in processes],
                               node_size=600, edgecolors='black', ax=self.ax)
        for r in resources:
            x, y = pos[r]
            color = node_colors[list(G.nodes).index(r)]
            rect = Rectangle((x - 0.08, y - 0.08), 0.16, 0.16, facecolor=color, edgecolor='black', linewidth=0.5)
            self.ax.add_patch(rect)
            self.ax.plot(x, y, 'ko', markersize=5)
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
        label_pos = pos.copy()
        for n in label_pos:
            x, y = label_pos[n]
            label_pos[n] = (x - 0.15 if n.startswith("P") else x + 0.15, y)
        nx.draw_networkx_labels(G, label_pos, font_size=10, font_weight='bold', ax=self.ax)
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
        """Shows the previous step in the simulation."""
        if self.current_step > 0:
            self.current_step -= 1
            self._draw_step()

    def next_step(self):
        """Shows the next step in the simulation."""
        if self.current_step < len(self.steps) - 1:
            self.current_step += 1
            self._draw_step()

    def play_simulation(self):
        """Plays the simulation automatically."""
        def play():
            while self.current_step < len(self.steps) - 1 and self.window_valid:
                self.current_step += 1
                self._draw_step()
                self.fig_canvas.get_tk_widget().update()
                time.sleep(1)
        threading.Thread(target=play, daemon=True).start()

    def _show_narrative(self):
        """Displays the narrative text up to the current step with progress indicator."""
        if not self.window_valid or not self.text_area.winfo_exists():
            return
        try:
            self.text_area.delete(1.0, tk.END)
            self.text_area.insert(tk.END, f"Step {self.current_step + 1} of {len(self.narrative)}\n\n")
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

    def prev_narrative(self):
        """Shows the previous narrative step."""
        if self.current_step > 0:
            self.current_step -= 1
            self._show_narrative()

    def next_narrative(self):
        """Shows the next narrative step."""
        if self.current_step < len(self.narrative) - 1 and self.window_valid:
            self.current_step += 1
            self._show_narrative()

    def toggle_play_pause(self):
        """Toggles between play and pause for automatic narrative progression."""
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
            self.play_thread = threading.Thread(target=self._auto_play_narrative, daemon=True)
            self.play_thread.start()

    def _auto_play_narrative(self):
        """Automatically advances the narrative with a 3-second gap."""
        while self.is_playing and self.current_step < len(self.narrative) - 1 and self.window_valid:
            self.window.after(0, self.next_narrative)
            time.sleep(3)
        if self.current_step >= len(self.narrative) - 1 or not self.window_valid:
            self.is_playing = False
            if self.window_valid and self.play_pause_button.winfo_exists():
                self.window.after(0, lambda: self.play_pause_button.config(text="▶️ Play"))