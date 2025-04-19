import matplotlib.pyplot as plt
import networkx as nx
from matplotlib.patches import Rectangle
from matplotlib.lines import Line2D
import numpy as np
import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from tkinter import Scrollbar, Text

def compute_safe_sequence(processes, resources_held, resources_wanted, total_resources):
    """
    Computes a safe execution sequence using a simplified Banker's Algorithm.
    
    Args:
        processes (list): List of process names (e.g., ['P1', 'P2', ...]).
        resources_held (dict): Mapping of processes to held resources.
        resources_wanted (dict): Mapping of processes to requested resources.
        total_resources (int): Total number of resources in the system.
    
    Returns:
        list: A safe execution sequence, or None if no safe sequence exists.
    """
    held_resources = set()
    for proc in resources_held:
        held_resources.update(resources_held[proc])
    
    all_resources = {f"R{i+1}" for i in range(total_resources)}
    available = all_resources - held_resources
    finish = {proc: False for proc in processes}
    safe_sequence = []

    while len(safe_sequence) < len(processes):
        found = False
        for proc in processes:
            if not finish[proc]:
                can_run = True
                for res in resources_wanted[proc]:
                    if res not in available and res not in resources_held[proc]:
                        can_run = False
                        break
                if can_run:
                    safe_sequence.append(proc)
                    available.update(resources_held[proc])
                    finish[proc] = True
                    found = True
                    break
        if not found:
            return None
    return safe_sequence

def build_wait_for_graph(resources_held, resources_wanted):
    """
    Builds the Wait-For Graph (WFG) from the RAG.
    
    Args:
        resources_held (dict): Mapping of processes to held resources.
        resources_wanted (dict): Mapping of processes to requested resources.
    
    Returns:
        dict: Adjacency list representing the WFG.
    """
    wfg = {proc: [] for proc in resources_held}
    for p1 in resources_wanted:
        for res in resources_wanted[p1]:
            for p2 in resources_held:
                if res in resources_held[p2] and p1 != p2:
                    wfg[p1].append(p2)
    return wfg

def convert_deadlock_cycle_to_wfg(deadlock_cycle, resources_held, resources_wanted):
    """
    Converts a deadlock cycle from the RAG to a WFG cycle (processes only).
    
    Args:
        deadlock_cycle (list): The deadlock cycle from the RAG.
        resources_held (dict): Mapping of processes to held resources.
        resources_wanted (dict): Mapping of processes to requested resources.
    
    Returns:
        list: A deadlock cycle containing only process nodes.
    """
    if not deadlock_cycle:
        return None
    
    process_cycle = [node for node in deadlock_cycle if node.startswith("P")]
    wfg_cycle = []
    for i in range(len(process_cycle)):
        p1 = process_cycle[i]
        p2 = process_cycle[(i + 1) % len(process_cycle)]
        for res in resources_wanted[p1]:
            if res in resources_held[p2]:
                if p1 not in wfg_cycle:
                    wfg_cycle.append(p1)
                break
    
    if wfg_cycle:
        wfg_cycle.append(wfg_cycle[0])
    
    return wfg_cycle if len(wfg_cycle) > 1 else None

def get_deadlock_details(deadlock_cycle, resources_held, resources_wanted):
    """
    Generates a detailed description of the deadlock cycle.
    
    Args:
        deadlock_cycle (list): The deadlock cycle from the RAG.
        resources_held (dict): Mapping of processes to held resources.
        resources_wanted (dict): Mapping of processes to requested resources.
    
    Returns:
        list: A list of strings describing each step in the deadlock cycle.
    """
    if not deadlock_cycle:
        return []
    
    details = []
    process_cycle = [node for node in deadlock_cycle if node.startswith("P")]
    for i in range(len(process_cycle)):
        p1 = process_cycle[i]
        p2 = process_cycle[(i + 1) % len(process_cycle)]
        for res in resources_wanted[p1]:
            if res in resources_held[p2]:
                detail = f"{p1} holds {resources_held[p1]} and requests {res}, which is held by {p2}"
                details.append(detail)
                break
    return details

def detect_deadlock_cycles(rag):
    """
    Detects all cycles in the Resource Allocation Graph (RAG) using networkx.
    
    Args:
        rag (dict): The Resource Allocation Graph as an adjacency list.
    
    Returns:
        list: A list of lists, each containing nodes forming a deadlock cycle.
    """
    G = nx.DiGraph()
    for node in rag:
        G.add_node(node)
        for neighbor in rag[node]:
            G.add_edge(node, neighbor)
    
    cycles = list(nx.simple_cycles(G))
    valid_cycles = []
    for cycle in cycles[:5]:
        has_process = any(node.startswith("P") for node in cycle)
        has_resource = any(node.startswith("R") for node in cycle)
        if has_process and has_resource:
            cycle.append(cycle[0])
            valid_cycles.append(cycle)
    
    return valid_cycles if valid_cycles else []

def visualize_rag(rag, resources_held, resources_wanted, deadlock_cycle=None, total_resources=None, root=None):
    """
    Visualizes the Resource Allocation Graph (RAG) and Wait-For Graph (WFG) side by side.
    
    Args:
        rag (dict): The Resource Allocation Graph as an adjacency list.
        resources_held (dict): Mapping of processes to held resources.
        resources_wanted (dict): Mapping of processes to requested resources.
        deadlock_cycle (list, optional): List of nodes forming a deadlock cycle in the RAG.
        total_resources (int, optional): Total number of resources in the system.
        root (tk.Tk, optional): Tkinter root window for embedding the plot.
    """
    # Infer total_resources if not provided
    if total_resources is None:
        all_res = set()
        for res_list in resources_held.values():
            all_res.update(res_list)
        for res_list in resources_wanted.values():
            all_res.update(res_list)
        total_resources = max([int(r[1:]) for r in all_res]) if all_res else 0

    # Debug output
    print(f"RAG: {rag}")
    print(f"Resources Held: {resources_held}")
    print(f"Resources Wanted: {resources_wanted}")
    print(f"Provided Deadlock Cycle: {deadlock_cycle}")
    print(f"Total Resources: {total_resources}")

    # Create RAG
    G_rag = nx.DiGraph()
    for node in rag:
        G_rag.add_node(node)
        for neighbor in rag[node]:
            G_rag.add_edge(node, neighbor)

    # Build WFG
    wfg = build_wait_for_graph(resources_held, resources_wanted)
    G_wfg = nx.DiGraph()
    for node in wfg:
        G_wfg.add_node(node)
        for neighbor in wfg[node]:
            G_wfg.add_edge(node, neighbor)

    # Combine provided deadlock cycle with detected cycles
    detected_cycles = detect_deadlock_cycles(rag)
    if deadlock_cycle:
        # Ensure provided cycle is included, avoiding duplicates
        provided_cycle = deadlock_cycle if deadlock_cycle[-1] == deadlock_cycle[0] else deadlock_cycle + [deadlock_cycle[0]]
        provided_set = set(tuple(provided_cycle))
        detected_sets = [set(tuple(cycle)) for cycle in detected_cycles]
        if provided_set not in detected_sets:
            detected_cycles.append(provided_cycle)
        deadlock_cycles = detected_cycles
    else:
        deadlock_cycles = detected_cycles

    print(f"Detected Deadlock Cycles: {deadlock_cycles}")

    # Convert RAG deadlock cycles to WFG cycles
    wfg_deadlock_cycles = []
    all_deadlock_details = []
    for i, cycle in enumerate(deadlock_cycles):
        wfg_cycle = convert_deadlock_cycle_to_wfg(cycle, resources_held, resources_wanted)
        if wfg_cycle:
            wfg_deadlock_cycles.append((f"Cycle {i+1}", wfg_cycle))
            details = get_deadlock_details(cycle, resources_held, resources_wanted)
            all_deadlock_details.append((f"Cycle {i+1}", details))

    # Define node types for RAG
    processes = [n for n in G_rag.nodes if n.startswith("P")]
    resources = [n for n in G_rag.nodes if n.startswith("R")]

    # Create figure with two subplots
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 8), gridspec_kw={'wspace': 0.4})

    # Set background and grid
    ax1.set_facecolor('#f8f9fa')
    ax2.set_facecolor('#f8f9fa')
    ax1.grid(True, linestyle='--', alpha=0.3, zorder=0)
    ax2.grid(True, linestyle='--', alpha=0.3, zorder=0)

    # --- RAG (Left Subplot) ---
    pos_rag = nx.bipartite_layout(G_rag, processes, align='horizontal', scale=3.0, center=(0, 0))

    # Draw nodes
    deadlock_nodes = set()
    for cycle in deadlock_cycles:
        deadlock_nodes.update(cycle)
    nx.draw_networkx_nodes(G_rag, pos_rag, nodelist=[n for n in processes if n not in deadlock_nodes], 
                           node_shape='o', node_color='#add8e6', node_size=500, 
                           edgecolors='black', linewidths=0.5, ax=ax1)
    nx.draw_networkx_nodes(G_rag, pos_rag, nodelist=[n for n in processes if n in deadlock_nodes], 
                           node_shape='o', node_color='#ff9999', node_size=500, 
                           edgecolors='black', linewidths=0.5, ax=ax1)
    nx.draw_networkx_nodes(G_rag, pos_rag, nodelist=[n for n in resources if n not in deadlock_nodes], 
                           node_shape='s', node_color='#90ee90', node_size=300, 
                           edgecolors='black', linewidths=0.5, ax=ax1)
    nx.draw_networkx_nodes(G_rag, pos_rag, nodelist=[n for n in resources if n in deadlock_nodes], 
                           node_shape='s', node_color='#ffcc99', node_size=300, 
                           edgecolors='black', linewidths=0.5, ax=ax1)

    # Draw resource nodes with rectangles
    for resource in resources:
        x, y = pos_rag[resource]
        rect = Rectangle((x - 0.07, y - 0.07), 0.14, 0.14, 
                         facecolor='#90ee90' if resource not in deadlock_nodes else '#ffcc99', 
                         edgecolor='black', linewidth=0.5, zorder=1)
        ax1.add_patch(rect)
        ax1.plot(x, y, 'ko', markersize=4, zorder=2)

    # Draw edges for RAG
    allocation_edges = [(u, v) for u, v in G_rag.edges if u.startswith("R") and v.startswith("P")]
    request_edges = [(u, v) for u, v in G_rag.edges if u.startswith("P") and v.startswith("R")]

    # Highlight deadlock edges
    deadlock_edges_rag = []
    for cycle in deadlock_cycles:
        for i in range(len(cycle) - 1):
            u, v = cycle[i], cycle[i + 1]
            if (u, v) in G_rag.edges:
                deadlock_edges_rag.append((u, v))
    non_deadlock_allocation = [(u, v) for u, v in allocation_edges if (u, v) not in deadlock_edges_rag]
    non_deadlock_request = [(u, v) for u, v in request_edges if (u, v) not in deadlock_edges_rag]
    nx.draw_networkx_edges(G_rag, pos_rag, edgelist=non_deadlock_allocation, edge_color='black', 
                           width=1.0, arrows=True, arrowstyle='-|>', arrowsize=20, ax=ax1)
    nx.draw_networkx_edges(G_rag, pos_rag, edgelist=non_deadlock_request, edge_color='black', 
                           width=1.0, arrows=True, arrowstyle='->', arrowsize=20, ax=ax1)
    nx.draw_networkx_edges(G_rag, pos_rag, edgelist=[e for e in deadlock_edges_rag if e in allocation_edges], 
                           edge_color='red', width=1.2, arrows=True, arrowstyle='-|>', arrowsize=25, ax=ax1)
    nx.draw_networkx_edges(G_rag, pos_rag, edgelist=[e for e in deadlock_edges_rag if e in request_edges], 
                           edge_color='red', width=1.2, arrows=True, arrowstyle='->', arrowsize=25, ax=ax1)

    # Add edge labels
    for edge in allocation_edges:
        u, v = edge
        x1, y1 = pos_rag[u]
        x2, y2 = pos_rag[v]
        mid_x, mid_y = (x1 + x2) / 2, (y1 + y2) / 2
        label_x, label_y = mid_x - 0.05, mid_y
        label_color = 'red' if (u, v) in deadlock_edges_rag else 'black'
        ax1.text(label_x, label_y, "H", fontsize=8, color=label_color, ha='right', va='center')

    for edge in request_edges:
        u, v = edge
        x1, y1 = pos_rag[u]
        x2, y2 = pos_rag[v]
        mid_x, mid_y = (x1 + x2) / 2, (y1 + y2) / 2
        label_x, label_y = mid_x + 0.05, mid_y
        label_color = 'red' if (u, v) in deadlock_edges_rag else 'black'
        ax1.text(label_x, label_y, "R", fontsize=8, color=label_color, ha='left', va='center')

    # Draw node labels with adjusted offset (just outside symbols)
    label_pos_rag = pos_rag.copy()
    for node in label_pos_rag:
        x, y = label_pos_rag[node]
        if node.startswith("P"):
            label_pos_rag[node] = (x - 0.15, y)  # Outside circle (radius ~0.1 + 0.05)
        else:
            label_pos_rag[node] = (x + 0.15, y)  # Outside rectangle (half-width 0.07 + 0.08)
    nx.draw_networkx_labels(G_rag, label_pos_rag, font_size=9, font_weight='bold', 
                            horizontalalignment='right' if node.startswith("P") else 'left', ax=ax1)

    # Set axis limits to prevent truncation
    x_coords = [pos_rag[node][0] for node in pos_rag]
    y_coords = [pos_rag[node][1] for node in pos_rag]
    x_min, x_max = min(x_coords), max(x_coords)
    y_min, y_max = min(y_coords), max(y_coords)
    ax1.set_xlim(x_min - 0.5, x_max + 0.5)
    ax1.set_ylim(y_min - 0.5, y_max + 0.5)

    ax1.set_title("Resource Allocation Graph", fontsize=12, pad=10, fontweight='bold')
    ax1.axis('off')

    # --- WFG (Right Subplot) ---
    pos_wfg = nx.circular_layout(G_wfg, scale=2.5)

    # Draw nodes
    wfg_deadlock_nodes = set()
    for _, cycle in wfg_deadlock_cycles:
        wfg_deadlock_nodes.update(cycle)
    nx.draw_networkx_nodes(G_wfg, pos_wfg, nodelist=[n for n in G_wfg.nodes if n not in wfg_deadlock_nodes], 
                           node_shape='o', node_color='#add8e6', node_size=500, 
                           edgecolors='black', linewidths=0.5, ax=ax2)
    nx.draw_networkx_nodes(G_wfg, pos_wfg, nodelist=[n for n in wfg_deadlock_nodes], 
                           node_shape='o', node_color='#ff9999', node_size=500, 
                           edgecolors='black', linewidths=0.5, ax=ax2)

    # Draw edges
    deadlock_edges = []
    for _, cycle in wfg_deadlock_cycles:
        deadlock_edges.extend([(cycle[i], cycle[i + 1]) for i in range(len(cycle) - 1)])
    non_deadlock_edges = [(u, v) for u, v in G_wfg.edges if (u, v) not in deadlock_edges]
    nx.draw_networkx_edges(G_wfg, pos_wfg, edgelist=non_deadlock_edges, edge_color='black', 
                           width=1.0, arrows=True, arrowstyle='->', arrowsize=20, 
                           connectionstyle='arc3,rad=0.1', ax=ax2)
    nx.draw_networkx_edges(G_wfg, pos_wfg, edgelist=deadlock_edges, edge_color='red', 
                           width=1.2, arrows=True, arrowstyle='->', arrowsize=25, 
                           connectionstyle='arc3,rad=0.1', ax=ax2)

    # Add edge labels
    for edge in G_wfg.edges:
        u, v = edge
        x1, y1 = pos_wfg[u]
        x2, y2 = pos_wfg[v]
        mid_x, mid_y = (x1 + x2) / 2, (y1 + y2) / 2
        dx, dy = x2 - x1, y2 - y1
        length = np.sqrt(dx**2 + dy**2)
        if length > 0:
            dx, dy = dx / length, dy / length
        offset_x, offset_y = -dy * 0.05, dx * 0.05
        label_x, label_y = mid_x + offset_x, mid_y + offset_y
        label_color = 'red' if edge in deadlock_edges else 'black'
        ax2.text(label_x, label_y, "W", fontsize=8, color=label_color, ha='center', va='center')

    # Draw node labels with adjusted offset (just outside circle)
    label_pos_wfg = pos_wfg.copy()
    for node in label_pos_wfg:
        x, y = label_pos_wfg[node]
        angle = np.arctan2(y, x)
        offset = 0.15  # Outside circle (radius ~0.1 + 0.05)
        label_pos_wfg[node] = (x + offset * np.cos(angle), y + offset * np.sin(angle))
    nx.draw_networkx_labels(G_wfg, label_pos_wfg, font_size=9, font_weight='bold', 
                            horizontalalignment='center', ax=ax2)

    # Set axis limits to prevent truncation
    x_coords = [pos_wfg[node][0] for node in pos_wfg]
    y_coords = [pos_wfg[node][1] for node in pos_wfg]
    x_min, x_max = min(x_coords), max(x_coords)
    y_min, y_max = min(y_coords), max(y_coords)
    # Add extra margin to accommodate labels
    ax2.set_xlim(x_min - 0.7, x_max + 0.7)
    ax2.set_ylim(y_min - 0.7, y_max + 0.7)

    ax2.set_title("Wait-For Graph", fontsize=12, pad=10, fontweight='bold')
    ax2.axis('off')

    # Legend in bottom-left corner
    legend_elements = [
        Line2D([0], [0], marker='o', color='w', label='Process', markerfacecolor='#add8e6', markersize=8),
        Line2D([0], [0], marker='o', color='w', label='Process (Deadlock)', markerfacecolor='#ff9999', markersize=8),
        Line2D([0], [0], marker='s', color='w', label='Resource', markerfacecolor='#90ee90', markersize=8),
        Line2D([0], [0], color='black', lw=1.0, label='Held (H)'),
        Line2D([0], [0], color='black', lw=1.0, linestyle='solid', label='Request (R)/Wait-For (W)'),
    ]
    if wfg_deadlock_cycles:
        legend_elements.append(Line2D([0], [0], color='red', lw=1.2, label='Deadlock Cycle'))
    fig.legend(handles=legend_elements, loc='lower left', bbox_to_anchor=(0.05, 0.05), 
               fontsize=8, title="Legend", title_fontsize=10, frameon=True, 
               edgecolor='black', framealpha=1, ncol=1)

    # Compute safe sequence
    processes = list(resources_held.keys())
    safe_sequence = compute_safe_sequence(processes, resources_held, resources_wanted, total_resources)

    # Prepare scrollable text for deadlock cycles
    cycle_text_content = ""
    if wfg_deadlock_cycles:
        involved_processes = set()
        for _, cycle in wfg_deadlock_cycles:
            involved_processes.update([node for node in cycle if node.startswith("P")])
        involved_processes = sorted(involved_processes)
        if involved_processes:
            cycle_text_content += f"Processes Involved: {', '.join(involved_processes)}\n\n"
        for i, (cycle_name, cycle) in enumerate(wfg_deadlock_cycles):
            cycle_text_content += f"{cycle_name}: {' -> '.join(cycle)}\n"
            details = all_deadlock_details[i][1]
            for detail in details:
                cycle_text_content += f"  {detail}\n"
            cycle_text_content += "\n"

    # Create Tkinter window for scrollable text if needed
    if root and cycle_text_content:
        canvas = FigureCanvasTkAgg(fig, master=root)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        # Create scrollable text area
        text_frame = tk.Frame(root)
        text_frame.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=1)
        text_canvas = tk.Canvas(text_frame, height=100)
        scrollbar = Scrollbar(text_frame, orient=tk.VERTICAL, command=text_canvas.yview)
        scrollable_frame = tk.Frame(text_canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: text_canvas.configure(scrollregion=text_canvas.bbox("all"))
        )

        text_canvas.create_window((0, 0), window=scrollable_frame, anchor="ne")
        text_canvas.configure(yscrollcommand=scrollbar.set)

        text_widget = Text(scrollable_frame, wrap=tk.WORD, width=50, height=10, font=("Arial", 9))
        text_widget.insert(tk.END, cycle_text_content)
        text_widget.config(state=tk.DISABLED)
        text_widget.pack(side=tk.RIGHT, anchor="se", padx=5, pady=5)

        text_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Display "No Safe Sequence Found" for deadlock case
        plt.figtext(0.5, 0.18, "No Safe Sequence Found", ha="center", fontsize=9, color='orange', weight='bold', 
                    bbox=dict(facecolor='white', edgecolor='orange', boxstyle='round,pad=0.3'))
    else:
        # Handle no-deadlock case or fallback rendering
        if not wfg_deadlock_cycles:
            text = "No Deadlock"
            if safe_sequence:
                text += "\nSafe Sequence Found: " + " -> ".join(safe_sequence)
            plt.figtext(0.5, 0.18, text, ha="center", fontsize=9, color='green', weight='bold', 
                        bbox=dict(facecolor='white', edgecolor='green', boxstyle='round,pad=0.3'))
        elif not root:
            # Fallback to figtext for deadlock case without Tkinter
            plt.figtext(0.5, 0.18, "No Safe Sequence Found", ha="center", fontsize=9, color='orange', weight='bold', 
                        bbox=dict(facecolor='white', edgecolor='orange', boxstyle='round,pad=0.3'))
            y_position = 0.18
            involved_processes = set()
            for _, cycle in wfg_deadlock_cycles:
                involved_processes.update([node for node in cycle if node.startswith("P")])
            involved_processes = sorted(involved_processes)
            if involved_processes:
                plt.figtext(0.95, y_position, f"Processes Involved: {', '.join(involved_processes)}", 
                            ha="right", fontsize=9, color='red', weight='bold', 
                            bbox=dict(facecolor='white', edgecolor='red', boxstyle='round,pad=0.3'))
                y_position -= 0.04
            for i, (cycle_name, cycle) in enumerate(wfg_deadlock_cycles):
                plt.figtext(0.95, y_position, f"{cycle_name}: {' -> '.join(cycle)}", 
                            ha="right", fontsize=9, color='red', weight='bold', 
                            bbox=dict(facecolor='white', edgecolor='red', boxstyle='round,pad=0.3'))
                y_position -= 0.04
                details = all_deadlock_details[i][1]
                for detail in details:
                    plt.figtext(0.95, y_position, detail, ha="right", fontsize=8, color='red', 
                                wrap=True, bbox=dict(facecolor='white', edgecolor='red', boxstyle='round,pad=0.3'))
                    y_position -= 0.04

    # Adjust layout to accommodate legend and text
    plt.subplots_adjust(left=0.05, right=0.95, top=0.85, bottom=0.35, wspace=0.4)

    if not root:
        plt.show()

if __name__ == "__main__":
    # Test case with multiple deadlock cycles
    sample_rag = {
        'P1': ['R2'], 'P2': ['R1'], 'P3': ['R2'], 'P4': ['R5'], 'P5': ['R6'], 'P6': ['R4'],
        'R1': ['P1'], 'R2': ['P2'], 'R3': ['P3'], 'R4': ['P4'], 'R5': ['P5'], 'R6': ['P6']
    }
    sample_resources_held = {
        'P1': ['R1'], 'P2': ['R2'], 'P3': ['R3'], 'P4': ['R4'], 'P5': ['R5'], 'P6': ['R6']
    }
    sample_resources_wanted = {
        'P1': ['R2'], 'P2': ['R1'], 'P3': ['R2'], 'P4': ['R5'], 'P5': ['R6'], 'P6': ['R4']
    }
    sample_deadlock_cycle = ['R1', 'P2', 'R2', 'P1', 'R1']
    root = tk.Tk()
    visualize_rag(sample_rag, sample_resources_held, sample_resources_wanted, 
                  deadlock_cycle=sample_deadlock_cycle, total_resources=6, root=root)
    root.mainloop()

    # Test case without deadlock cycles
    no_deadlock_rag = {
        'P1': [], 'P2': ['R2'], 'R1': ['P1'], 'R2': []
    }
    no_deadlock_resources_held = {'P1': ['R1'], 'P2': []}
    no_deadlock_resources_wanted = {'P1': [], 'P2': ['R2']}
    root = tk.Tk()
    visualize_rag(no_deadlock_rag, no_deadlock_resources_held, no_deadlock_resources_wanted, 
                  total_resources=2, root=root)
    root.mainloop()