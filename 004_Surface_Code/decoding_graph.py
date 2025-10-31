import rustworkx as rx
import numpy as np
import layout

def build_z_decoding_graph(rounds, data_x_prob=0.5, meas_z_prob=0.1):
    """
    Builds the Z-Decoding Graph (for X-errors).
    """
    graph = rx.PyGraph()
    weight_space = -np.log(data_x_prob) # 0.693
    weight_time = -np.log(meas_z_prob)  # 2.303
    
    node_map = {} # Map (ancilla_name, round) -> node_index
    
    # 1. Create nodes (Ancilla * Rounds)
    ancilla_names = list(layout.z_stabilizers.keys())
    for r in range(rounds):
        for name in ancilla_names:
            node_idx = graph.add_node((name, r))
            node_map[(name, r)] = node_idx

    # 2. Connect Time edges
    if rounds > 1:
        for r in range(rounds - 1):
            for name in ancilla_names:
                node1 = node_map[(name, r)]
                node2 = node_map[(name, r + 1)]
                graph.add_edge(node1, node2, weight_time)

    # 3. Connect Space edges
    # Find pairs of ancillas that share a data qubit
    data_to_ancilla_map = {}
    for ancilla, data_qubits in layout.z_stabilizers.items():
        for data in data_qubits:
            if data not in data_to_ancilla_map:
                data_to_ancilla_map[data] = []
            data_to_ancilla_map[data].append(ancilla)

    for data, ancillas in data_to_ancilla_map.items():
        # If a data qubit is shared by two ancillas, add a space edge
        if len(ancillas) == 2:
            a1, a2 = ancillas
            for r in range(rounds):
                node1 = node_map[(a1, r)]
                node2 = node_map[(a2, r)]
                graph.add_edge(node1, node2, weight_space)
    
    return graph, node_map

def build_x_decoding_graph(rounds, data_z_prob=0.5, meas_x_prob=0.1):
    """
    Builds the X-Decoding Graph (for Z-errors).
    """
    graph = rx.PyGraph()
    weight_space = -np.log(data_z_prob) # 0.693
    weight_time = -np.log(meas_x_prob)  # 2.303
    
    node_map = {} # Map (ancilla_name, round) -> node_index
    
    # 1. Create nodes (Ancilla * Rounds)
    ancilla_names = list(layout.x_stabilizers.keys())
    for r in range(rounds):
        for name in ancilla_names:
            node_idx = graph.add_node((name, r))
            node_map[(name, r)] = node_idx

    # 2. Connect Time edges
    if rounds > 1:
        for r in range(rounds - 1):
            for name in ancilla_names:
                node1 = node_map[(name, r)]
                node2 = node_map[(name, r + 1)]
                graph.add_edge(node1, node2, weight_time)

    # 3. Connect Space edges
    # Find pairs of ancillas that share a data qubit
    data_to_ancilla_map = {}
    for ancilla, data_qubits in layout.x_stabilizers.items():
        for data in data_qubits:
            if data not in data_to_ancilla_map:
                data_to_ancilla_map[data] = []
            data_to_ancilla_map[data].append(ancilla)

    for data, ancillas in data_to_ancilla_map.items():
        # If a data qubit is shared by two ancillas, add a space edge
        if len(ancillas) == 2:
            a1, a2 = ancillas
            for r in range(rounds):
                node1 = node_map[(a1, r)]
                node2 = node_map[(a2, r)]
                graph.add_edge(node1, node2, weight_space)
    
    return graph, node_map