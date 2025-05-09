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
    def __init__(self, gui, window, mode, narrative_depth="basic"):
        self.gui = gui
        self.window = window
        self.mode = mode
        self.narrative_depth = narrative_depth  # "basic" or "verbose"
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
        self.tic_channel = None

        # Load narrative templates
        script_dir = os.path.dirname(os.path.abspath(__file__))
        try:
            with open(os.path.join(script_dir, 'narrative.json'), 'r', encoding='utf-8') as f:
                self.narrative_templates = json.load(f)
        except FileNotFoundError:
            print("Error: narrative.json not found. Using fallback narrative.")
            self.narrative_templates = {
                'intro': {'basic': ["Fallback: Starting cycle detection..."], 'verbose': ["Fallback: Starting cycle detection with details..."]},
                'start': {'basic': ["Visiting {node}..."], 'verbose': ["Detailed visit to {node}..."]},
                'visit': {'basic': ["Visiting {node}..."], 'verbose': ["Detailed visit to {node}..."]},
                'check_edge': {'basic': ["Checking edge from {node} to {neighbor}..."], 'verbose': ["Detailed edge check from {node} to {neighbor}..."]},
                'dive': {'basic': ["Diving to {neighbor}..."], 'verbose': ["Detailed dive to {neighbor}..."]},
                'cycle_found': {'basic': ["Cycle found: {cycle}!"], 'verbose': ["Detailed cycle found: {cycle}!"]},
                'backtrack': {'basic': ["Backtracking from {node}..."], 'verbose': ["Detailed backtrack from {node}..."]},
                'no_cycle': {'basic': ["No cycles found!"], 'verbose': ["Detailed: No cycles found!"]},
                'cycle_detected': {'basic': ["Deadlock at {cycle}!"], 'verbose': ["Detailed deadlock at {cycle}!"]}
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
        if self.tic_channel:
            self.tic_channel.stop()
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
            held = [r for p, rs in self.gui.resources_held.items() for r in rs if p == node]
            wanted = self.gui.resources_wanted.get(node, [])
            context = f"clutching {', '.join(held) or 'nothing'}" if held else ""
            context += f" and eyeing {', '.join(wanted) or 'nothing'}" if wanted else ""
            narrative.append(random.choice(self.narrative_templates['visit'][self.narrative_depth]).format(
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
                edge_type = "hoarding" if node.startswith("R") else "begging for"
                narrative.append(random.choice(self.narrative_templates['check_edge'][self.narrative_depth]).format(
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
                    narrative.append(random.choice(self.narrative_templates['dive'][self.narrative_depth]).format(
                        neighbor=neighbor, node=node))
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
                    cycle_str = " -> ".join(cycle)
                    narrative.append(random.choice(self.narrative_templates['cycle_found'][self.narrative_depth]).format(
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
            narrative.append(random.choice(self.narrative_templates['backtrack'][self.narrative_depth]).format(node=node))
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
                narrative.append(random.choice(self.narrative_templates['start'][self.narrative_depth]).format(node=node))
                if dfs(node):
                    break
        if not self.cycle:
            narrative.append(random.choice(self.narrative_templates['no_cycle'][self.narrative_depth]))
        else:
            narrative.append(random.choice(self.narrative_templates['cycle_detected'][self.narrative_depth]).format(
                cycle=" -> ".join(self.cycle)))

        self.steps = steps
        self.narrative = narrative

    def _build_intro(self):
        """Builds an introductory narrative summarizing the graph."""
        num_processes = sum(1 for n in self.rag if n.startswith("P"))
        num_resources = sum(1 for n in self.rag if n.startswith("R"))
        allocations = []
        for p, rs in self.gui.resources_held.items():
            if rs:
                allocations.append(f"{p} holds {', '.join(rs)}")
        requests = []
        for p, rs in self.gui.resources_wanted.items():
            if rs:
                requests.append(f"{p} wants {', '.join(rs)}")
        intro = random.choice(self.narrative_templates['intro'][self.narrative_depth]).format(
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
                narrative_frame.place(relx=0.5, rely=0.35, anchor="center", relwidth=0.9, relheight=0.35)
                data_frame.place(relx=0.5, rely=0.75, anchor="center", relwidth=0.9, relheight=0.35)
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
            title_label = tk.Label(self.canvas, text="Detective Algo's Deadlock Quest",
                                   font=("Helvetica", 20, "bold"), bg="#A3BFFA", fg="#2E3A59")
            title_label.place(relx=0.5, rely=0.05, anchor="center")
            
            # Narrative frame
            narrative_frame = tk.Frame(self.canvas, bg="#F3F4F6")
            narrative_frame.place(relx=0.5, rely=0.35, anchor="center", relwidth=0.9, relheight=0.35)
            self.text_area = tk.Text(narrative_frame, wrap=tk.WORD, font=("Arial", 12), bg="#F3F4F6", fg="#2E3A59")
            scrollbar = tk.Scrollbar(narrative_frame, command=self.text_area.yview)
            self.text_area.config(yscrollcommand=scrollbar.set)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            self.text_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            
            # Data frame for real-time data
            data_frame = tk.Frame(self.canvas, bg="#E6F0FA")
            data_frame.place(relx=0.5, rely=0.75, anchor="center", relwidth=0.9, relheight=0.35)
            self.data_area = tk.Text(data_frame, wrap=tk.WORD, font=("Arial", 10), bg="#E6F0FA", fg="#2E3A59")
            data_scrollbar = tk.Scrollbar(data_frame, command=self.data_area.yview)
            self.data_area.config(yscrollcommand=data_scrollbar.set)
            data_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            self.data_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            
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
            depth_button = tk.Button(control_frame, text="Toggle Verbose", font=("Arial", 12),
                                     command=self.toggle_narrative_depth, bg="#9C27B0", fg="white")
            depth_button.pack(side=tk.LEFT, padx=5)
            self._show_narrative()

    def _draw_step(self):
        """Draws the current step of the simulation with highlighted current node and informative heading."""
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

        # Set informative title based on action
        if action == 'visit':
            title = f"Step {self.current_step + 1}: Visiting Node {node}, Adding to Stack and Exploring Connections"
        elif action == 'check_edge':
            edge_type = "Holds" if node.startswith("R") else "Requests"
            title = f"Step {self.current_step + 1}: Checking Edge {node} {edge_type} {neighbor}, Following Dependency"
        elif action == 'cycle_found':
            cycle_str = " -> ".join(cycle)
            title = f"Step {self.current_step + 1}: Cycle Detected at {neighbor}: {cycle_str}, Deadlock Found"
        elif action == 'backtrack':
            title = f"Step {self.current_step + 1}: Backtracking from {node}, No Cycle Found, Removing from Stack"
        else:
            title = f"Step {self.current_step + 1}: {action.capitalize()}"
        self.ax.set_title(title, fontsize=12, pad=10)

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
                node_colors.append('#ff3333')  # Bright red for current node
            elif n in recursion_stack:
                node_colors.append('#ffd700')
            elif n in visited:
                node_colors.append('#90ee90')
            else:
                node_colors.append('#add8e6')

        # Highlight current node with larger, more prominent effect
        if node in pos:
            x, y = pos[node]
            if node.startswith("P"):
                # Larger circle with border for processes
                highlight = Circle((x, y), 0.18, facecolor='#ff3333', edgecolor='black', linewidth=2, alpha=0.7, zorder=0)
                self.ax.add_patch(highlight)
            else:
                # Larger rectangle with border for resources
                highlight = Rectangle((x - 0.15, y - 0.15), 0.3, 0.3, facecolor='#ff3333', edgecolor='black', linewidth=2, alpha=0.7, zorder=0)
                self.ax.add_patch(highlight)

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

        # Label edges
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

        # Draw node labels
        label_pos = pos.copy()
        for n in label_pos:
            x, y = label_pos[n]
            label_pos[n] = (x - 0.15 if n.startswith("P") else x + 0.15, y)
        nx.draw_networkx_labels(G, label_pos, font_size=10, font_weight='bold', ax=self.ax)

        # Add legend
        legend_elements = [
            Line2D([0], [0], marker='o', color='w', label='Process', markerfacecolor='#add8e6', markersize=10),
            Line2D([0], [0], marker='s', color='w', label='Resource', markerfacecolor='#add8e6', markersize=10),
            Line2D([0], [0], color='black', lw=1.2, label='Held (H)/Request (R)'),
            Line2D([0], [0], marker='o', color='w', label='Current Node', markerfacecolor='#ff3333', markersize=10),
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
        """Plays the simulation automatically with tic.wav looping and end sound."""
        def play():
            if self.sound_manager.sound_enabled:
                try:
                    script_dir = os.path.dirname(os.path.abspath(__file__))
                    tic_sound_path = os.path.join(script_dir, "..", "..", "assets", "tic.wav")
                    tic_sound = pygame.mixer.Sound(tic_sound_path)
                    self.tic_channel = pygame.mixer.Channel(0)
                    self.tic_channel.play(tic_sound, loops=-1)
                except FileNotFoundError:
                    print(f"Error: 'assets/tic.wav' not found at {tic_sound_path}.")
                except Exception as e:
                    print(f"Error playing tic sound: {e}")

            while self.current_step < len(self.steps) - 1 and self.window_valid:
                self.current_step += 1
                self._draw_step()
                self.fig_canvas.get_tk_widget().update()
                time.sleep(1)

            if self.window_valid and self.sound_manager.sound_enabled:
                if self.tic_channel:
                    self.tic_channel.stop()
                try:
                    if self.cycle:
                        self.sound_manager.play_deadlock_sound()
                    else:
                        self.sound_manager.play_safe_sound()
                except Exception as e:
                    print(f"Error playing end sound: {e}")

        if not self.is_playing:
            self.is_playing = True
            self.play_thread = threading.Thread(target=play, daemon=True)
            self.play_thread.start()

    def _show_narrative(self):
        """Displays the narrative text and real-time data up to the current step."""
        if not self.window_valid or not self.text_area.winfo_exists() or not self.data_area.winfo_exists():
            return
        try:
            # Update narrative text
            self.text_area.delete(1.0, tk.END)
            self.text_area.tag_configure("progress", foreground="#4CAF50")
            self.text_area.tag_configure("action", foreground="#2196F3")
            self.text_area.tag_configure("error", foreground="#FF0000")
            self.text_area.tag_configure("success", foreground="#4CAF50")
            self.text_area.tag_configure("tip", foreground="#9C27B0", font=("Arial", 12, "italic"))
            self.text_area.insert(tk.END, f"Step {self.current_step + 1} of {len(self.narrative)}\n\n", "progress")
            for i, line in enumerate(self.narrative[:self.current_step + 1]):
                if "Tip:" in line or "Did you know?" in line:
                    self.text_area.insert(tk.END, f"{line}\n\n", "tip")
                elif any(keyword in line for keyword in ["Deadlock", "Cycle detected", "Trouble", "Alert"]):
                    self.text_area.insert(tk.END, f"{line}\n\n", "error")
                elif any(keyword in line for keyword in ["Success", "No cycles", "Mission accomplished", "Case solved"]):
                    self.text_area.insert(tk.END, f"{line}\n\n", "success")
                else:
                    self.text_area.insert(tk.END, f"{line}\n\n", "action")
            self.text_area.see(tk.END)

            # Update data display
            self.data_area.delete(1.0, tk.END)
            self.data_area.tag_configure("header", font=("Arial", 10, "bold"))
            self.data_area.tag_configure("data", font=("Arial", 10))
            
            # Current Allocations
            self.data_area.insert(tk.END, "Current Allocations:\n", "header")
            allocations = [f"{p}: {', '.join(rs) or 'none'}" for p, rs in self.gui.resources_held.items()]
            self.data_area.insert(tk.END, "\n".join(allocations) + "\n\n", "data")
            
            # Current Requests
            self.data_area.insert(tk.END, "Current Requests:\n", "header")
            requests = [f"{p}: {', '.join(rs) or 'none'}" for p, rs in self.gui.resources_wanted.items()]
            self.data_area.insert(tk.END, "\n".join(requests) + "\n\n", "data")
            
            # Algorithm State
            self.data_area.insert(tk.END, "Algorithm State:\n", "header")
            if self.current_step < len(self.steps):
                step = self.steps[self.current_step]
                action = step['action']
                node = step['node']
                visited = step['visited']
                recursion_stack = step['recursion_stack']
                parent = step['parent']
                neighbor = step.get('neighbor')
                cycle = step.get('cycle')
                
                data_lines = [f"Action: {action.capitalize()}"]
                data_lines.append(f"Current Node: {node}")
                if neighbor:
                    data_lines.append(f"Neighbor: {neighbor}")
                data_lines.append(f"Visited Nodes: {', '.join(visited) or 'none'}")
                data_lines.append(f"Recursion Stack: {', '.join(recursion_stack) or 'none'}")
                if cycle:
                    data_lines.append(f"Cycle Detected: {' -> '.join(cycle)}")
                else:
                    data_lines.append("Cycle Detected: None")
                
                # RAG Edges
                edges = []
                for u in self.rag:
                    for v in self.rag[u]:
                        edge_type = "Holds" if u.startswith("R") else "Requests"
                        edges.append(f"{u} {edge_type} {v}")
                data_lines.append(f"RAG Edges: {', '.join(edges) or 'none'}")
                
                self.data_area.insert(tk.END, "\n".join(data_lines) + "\n", "data")
            else:
                self.data_area.insert(tk.END, "No algorithm state available.\n", "data")
            self.data_area.see(tk.END)
            
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

    def toggle_narrative_depth(self):
        """Toggles between basic and verbose narrative modes."""
        self.narrative_depth = "verbose" if self.narrative_depth == "basic" else "basic"
        # Rebuild narrative with new depth
        self.current_step = 0
        self.narrative = []
        self._build_intro()
        self._run_dfs_with_steps()
        self._show_narrative()

    def _auto_play_narrative(self):
        """Automatically advances the narrative with a 3-second gap."""
        while self.is_playing and self.current_step < len(self.narrative) - 1 and self.window_valid:
            self.window.after(0, self.next_narrative)
            time.sleep(3)
        if self.current_step >= len(self.narrative) - 1 or not self.window_valid:
            self.is_playing = False
            if self.window_valid and self.play_pause_button.winfo_exists():
                self.window.after(0, lambda: self.play_pause_button.config(text="▶️ Play"))