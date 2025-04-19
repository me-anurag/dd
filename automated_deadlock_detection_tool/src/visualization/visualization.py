import matplotlib.pyplot as plt
import networkx as nx
from matplotlib.patches import Rectangle
from matplotlib.lines import Line2D
import numpy as np

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
    # Calculate currently held resources
    held_resources = set()
    for proc in resources_held:
        held_resources.update(resources_held[proc])
    
    # Initialize available resources (all resources not currently held)
    all_resources = {f"R{i+1}" for i in range(total_resources)}
    available = all_resources - held_resources
    finish = {proc: False for proc in processes}
    safe_sequence = []

    while len(safe_sequence) < len(processes):
        found = False
        for proc in processes:
            if not finish[proc]:
                # Check if all requested resources are either available or already held
                can_run = True
                for res in resources_wanted[proc]:
                    if res not in available and res not in resources_held[proc]:
                        can_run = False
                        break
                if can_run:
                    safe_sequence.append(proc)
                    available.update(resources_held[proc])  # Release held resources
                    finish[proc] = True
                    found = True
                    break  # Move to next iteration after finding one
        if not found:
            return None  # No process can run, indicating potential deadlock or unsafe state
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

def visualize_rag(rag, resources_held, resources_wanted, deadlock_cycle=None, total_resources=None):
    """
    Visualizes the Resource Allocation Graph (RAG) and Wait-For Graph (WFG) side by side.
    
    Args:
        rag (dict): The Resource Allocation Graph as an adjacency list.
        resources_held (dict): Mapping of processes to held resources.
        resources_wanted (dict): Mapping of processes to requested resources.
        deadlock_cycle (list, optional): List of nodes forming a deadlock cycle in the RAG.
        total_resources (int, optional): Total number of resources in the system.
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
    print(f"Deadlock Cycle: {deadlock_cycle}")
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

    # Convert RAG deadlock cycle to WFG deadlock cycle
    wfg_deadlock_cycle = convert_deadlock_cycle_to_wfg(deadlock_cycle, resources_held, resources_wanted)

    # Get detailed deadlock information
    deadlock_details = get_deadlock_details(deadlock_cycle, resources_held, resources_wanted)

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
    pos_rag = nx.bipartite_layout(G_rag, processes, align='horizontal', scale=2.0, center=(0, 0))

    # Draw nodes
    if deadlock_cycle:
        deadlock_nodes = set(deadlock_cycle)
        nx.draw_networkx_nodes(G_rag, pos_rag, nodelist=[n for n in processes if n not in deadlock_nodes], 
                               node_shape='o', node_color='#add8e6', node_size=600, 
                               edgecolors='black', linewidths=0.5, ax=ax1)
        nx.draw_networkx_nodes(G_rag, pos_rag, nodelist=[n for n in processes if n in deadlock_nodes], 
                               node_shape='o', node_color='#ff9999', node_size=600, 
                               edgecolors='black', linewidths=0.5, ax=ax1)
        nx.draw_networkx_nodes(G_rag, pos_rag, nodelist=[n for n in resources if n not in deadlock_nodes], 
                               node_shape='s', node_color='#90ee90', node_size=400, 
                               edgecolors='black', linewidths=0.5, ax=ax1)
        nx.draw_networkx_nodes(G_rag, pos_rag, nodelist=[n for n in resources if n in deadlock_nodes], 
                               node_shape='s', node_color='#ffcc99', node_size=400, 
                               edgecolors='black', linewidths=0.5, ax=ax1)
    else:
        nx.draw_networkx_nodes(G_rag, pos_rag, nodelist=processes, node_shape='o', 
                               node_color='#add8e6', node_size=600, 
                               edgecolors='black', linewidths=0.5, ax=ax1)
        nx.draw_networkx_nodes(G_rag, pos_rag, nodelist=resources, node_shape='s', 
                               node_color='#90ee90', node_size=400, 
                               edgecolors='black', linewidths=0.5, ax=ax1)

    # Draw resource nodes with rectangles
    for resource in resources:
        x, y = pos_rag[resource]
        rect = Rectangle((x - 0.08, y - 0.08), 0.16, 0.16, 
                         facecolor='#90ee90' if resource not in set(deadlock_cycle or []) else '#ffcc99', 
                         edgecolor='black', linewidth=0.5, zorder=1)
        ax1.add_patch(rect)
        ax1.plot(x, y, 'ko', markersize=5, zorder=2)

    # Draw edges for RAG
    allocation_edges = [(u, v) for u, v in G_rag.edges if u.startswith("R") and v.startswith("P")]
    request_edges = [(u, v) for u, v in G_rag.edges if u.startswith("P") and v.startswith("R")]

    # Highlight deadlock edges
    deadlock_edges_rag = []
    if deadlock_cycle:
        for i in range(len(deadlock_cycle) - 1):
            u, v = deadlock_cycle[i], deadlock_cycle[i + 1]
            if (u, v) in G_rag.edges:
                deadlock_edges_rag.append((u, v))
        non_deadlock_allocation = [(u, v) for u, v in allocation_edges if (u, v) not in deadlock_edges_rag]
        non_deadlock_request = [(u, v) for u, v in request_edges if (u, v) not in deadlock_edges_rag]
        nx.draw_networkx_edges(G_rag, pos_rag, edgelist=non_deadlock_allocation, edge_color='black', 
                               width=1.2, arrows=True, arrowstyle='-|>', arrowsize=10, ax=ax1)
        nx.draw_networkx_edges(G_rag, pos_rag, edgelist=non_deadlock_request, edge_color='black', 
                               width=1.2, arrows=True, arrowstyle='->', arrowsize=10, ax=ax1)
        nx.draw_networkx_edges(G_rag, pos_rag, edgelist=[e for e in deadlock_edges_rag if e in allocation_edges], 
                               edge_color='red', width=1.5, arrows=True, arrowstyle='-|>', arrowsize=10, ax=ax1)
        nx.draw_networkx_edges(G_rag, pos_rag, edgelist=[e for e in deadlock_edges_rag if e in request_edges], 
                               edge_color='red', width=1.5, arrows=True, arrowstyle='->', arrowsize=10, ax=ax1)
    else:
        nx.draw_networkx_edges(G_rag, pos_rag, edgelist=allocation_edges, edge_color='black', 
                               width=1.2, arrows=True, arrowstyle='-|>', arrowsize=10, ax=ax1)
        nx.draw_networkx_edges(G_rag, pos_rag, edgelist=request_edges, edge_color='black', 
                               width=1.2, arrows=True, arrowstyle='->', arrowsize=10, ax=ax1)

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

    # Draw node labels
    label_pos_rag = pos_rag.copy()
    for node in label_pos_rag:
        x, y = label_pos_rag[node]
        if node.startswith("P"):
            label_pos_rag[node] = (x - 0.15, y)
        else:
            label_pos_rag[node] = (x + 0.15, y)
    nx.draw_networkx_labels(G_rag, label_pos_rag, font_size=10, font_weight='bold', ax=ax1)

    ax1.set_title("Resource Allocation Graph", fontsize=14, pad=15, fontweight='bold')
    ax1.axis('off')

    # --- WFG (Right Subplot) ---
    pos_wfg = nx.circular_layout(G_wfg, scale=1.0)

    # Draw nodes
    if wfg_deadlock_cycle:
        deadlock_nodes = set(wfg_deadlock_cycle)
        nx.draw_networkx_nodes(G_wfg, pos_wfg, nodelist=[n for n in G_wfg.nodes if n not in deadlock_nodes], 
                               node_shape='o', node_color='#add8e6', node_size=600, 
                               edgecolors='black', linewidths=0.5, ax=ax2)
        nx.draw_networkx_nodes(G_wfg, pos_wfg, nodelist=[n for n in deadlock_nodes], 
                               node_shape='o', node_color='#ff9999', node_size=600, 
                               edgecolors='black', linewidths=0.5, ax=ax2)
    else:
        nx.draw_networkx_nodes(G_wfg, pos_wfg, nodelist=list(G_wfg.nodes), node_shape='o', 
                               node_color='#add8e6', node_size=600, 
                               edgecolors='black', linewidths=0.5, ax=ax2)

    # Draw edges
    deadlock_edges = []
    if wfg_deadlock_cycle:
        deadlock_edges = [(wfg_deadlock_cycle[i], wfg_deadlock_cycle[i + 1]) for i in range(len(wfg_deadlock_cycle) - 1)]
        non_deadlock_edges = [(u, v) for u, v in G_wfg.edges if (u, v) not in deadlock_edges]
        nx.draw_networkx_edges(G_wfg, pos_wfg, edgelist=non_deadlock_edges, edge_color='black', 
                               width=1.2, arrows=True, arrowstyle='->', arrowsize=10, 
                               connectionstyle='arc3,rad=0.1', ax=ax2)
        nx.draw_networkx_edges(G_wfg, pos_wfg, edgelist=deadlock_edges, edge_color='red', 
                               width=1.5, arrows=True, arrowstyle='->', arrowsize=10, 
                               connectionstyle='arc3,rad=0.1', ax=ax2)
    else:
        nx.draw_networkx_edges(G_wfg, pos_wfg, edgelist=list(G_wfg.edges), edge_color='black', 
                               width=1.2, arrows=True, arrowstyle='->', arrowsize=10, 
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

    # Draw node labels
    label_pos_wfg = pos_wfg.copy()
    for node in label_pos_wfg:
        x, y = label_pos_wfg[node]
        angle = np.arctan2(y, x)
        offset = 0.15
        label_pos_wfg[node] = (x + offset * np.cos(angle), y + offset * np.sin(angle))
    nx.draw_networkx_labels(G_wfg, label_pos_wfg, font_size=10, font_weight='bold', ax=ax2)

    ax2.set_title("Wait-For Graph", fontsize=14, pad=15, fontweight='bold')
    ax2.axis('off')

    # Legend
    legend_elements = [
        Line2D([0], [0], marker='o', color='w', label='Process', markerfacecolor='#add8e6', markersize=10),
        Line2D([0], [0], marker='s', color='w', label='Resource', markerfacecolor='#90ee90', markersize=10),
        Line2D([0], [0], color='black', lw=1.2, label='Held (H)'),
        Line2D([0], [0], color='black', lw=1.2, linestyle='solid', label='Request (R)/Wait-For (W)'),
    ]
    if wfg_deadlock_cycle:
        legend_elements.append(Line2D([0], [0], color='red', lw=1.5, label='Deadlock Cycle'))
    fig.legend(handles=legend_elements, loc='upper center', bbox_to_anchor=(0.5, 0.98), 
               fontsize=9, title="Legend", title_fontsize=11, frameon=True, 
               edgecolor='black', framealpha=1, ncol=len(legend_elements))

    # Compute and display safe sequence or deadlock info
    processes = list(resources_held.keys())
    safe_sequence = compute_safe_sequence(processes, resources_held, resources_wanted, total_resources)
    y_position = 0.12
    if safe_sequence:
        sequence_text = "Safe Execution Sequence: " + " -> ".join(safe_sequence)
        plt.figtext(0.5, y_position, sequence_text, ha="center", fontsize=10, color='green', weight='bold', 
                    bbox=dict(facecolor='white', edgecolor='green', boxstyle='round,pad=0.3'))
    else:
        plt.figtext(0.5, y_position, "No Safe Execution Sequence Found", ha="center", fontsize=10, color='orange', weight='bold', 
                    bbox=dict(facecolor='white', edgecolor='orange', boxstyle='round,pad=0.3'))
        y_position -= 0.04
        if wfg_deadlock_cycle:
            cycle_text = "Deadlock Cycle: " + " -> ".join(wfg_deadlock_cycle)
            involved_processes = sorted(set(wfg_deadlock_cycle[:-1]))
            involved_text = f" (Processes Involved: {', '.join(involved_processes)})"
            plt.figtext(0.5, y_position, cycle_text + involved_text, ha="center", fontsize=10, color='red', weight='bold', 
                        bbox=dict(facecolor='white', edgecolor='red', boxstyle='round,pad=0.3'))
            y_position -= 0.04
            for i, detail in enumerate(deadlock_details):
                plt.figtext(0.5, y_position - i * 0.04, detail, ha="center", fontsize=9, color='red', 
                            wrap=True, bbox=dict(facecolor='white', edgecolor='red', boxstyle='round,pad=0.3'))

    plt.tight_layout(rect=[0, 0.15, 1, 0.9])
    plt.show()

if __name__ == "__main__":
    # Example with no deadlock
    sample_rag = {
        "P1": ["R1"],
        "R1": ["P1"],
        "P2": ["R2"],
        "R2": []
    }
    sample_resources_held = {"P1": ["R1"], "P2": []}
    sample_resources_wanted = {"P1": [], "P2": ["R2"]}
    visualize_rag(sample_rag, sample_resources_held, sample_resources_wanted, total_resources=2)