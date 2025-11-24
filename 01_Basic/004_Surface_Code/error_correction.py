import networkx as nx
import numpy as np
import itertools 

def get_stabilizer_and_decoding_maps():
    """
    Defines the stabilizer connectivity and the mapping for the decoding graph.
    This corresponds to a specific surface code layout (e.g., rotated surface code 13-qubit).
    """
    z_stabilizers = {
        'c_z[0]': ('d[0]', 'd[1]', 'd[3]'),
        'c_z[1]': ('d[1]', 'd[2]', 'd[4]'),
        'c_z[2]': ('d[3]', 'd[5]', 'd[6]', 'd[8]'),
        'c_z[3]': ('d[4]', 'd[6]', 'd[7]', 'd[9]'),
        'c_z[4]': ('d[8]', 'd[10]', 'd[11]'),
        'c_z[5]': ('d[9]', 'd[11]', 'd[12]')
    }
    x_stabilizers = {
        'c_x[0]': ('d[0]', 'd[3]', 'd[5]'),
        'c_x[1]': ('d[1]', 'd[3]', 'd[4]', 'd[6]'),
        'c_x[2]': ('d[2]', 'd[4]', 'd[7]'),
        'c_x[3]': ('d[5]', 'd[8]', 'd[10]'),
        'c_x[4]': ('d[6]', 'd[8]', 'd[9]', 'd[11]'),
        'c_x[5]': ('d[7]', 'd[9]', 'd[12]')
    }
    
    # Maps spatial edges (ancilla pairs) to the corresponding data qubit index for Z-graph (X-errors)
    z_spatial_map = {
        (0, 1): 1, (0, 2): 3, (1, 3): 4, (2, 3): 6, 
        (2, 4): 8, (3, 5): 9, (4, 5): 11
    }
    # Maps boundary ancilla indices to their corresponding data qubit index for Z-graph
    z_boundary_map = {0: 0, 1: 2, 2: 5, 3: 7, 4: 10, 5: 12}
    
    # Maps spatial edges (ancilla pairs) to the corresponding data qubit index for X-graph (Z-errors)
    x_spatial_map = {
        (0, 1): 3, (0, 3): 5, (1, 2): 4, (1, 4): 6, 
        (2, 5): 7, (3, 4): 8, (4, 5): 9
    }
    # Maps boundary ancilla indices to their corresponding data qubit index for X-graph
    x_boundary_map = {0: 0, 1: 1, 2: 2, 3: 10, 4: 11, 5: 12}

    return (
        z_stabilizers, x_stabilizers, 
        z_spatial_map, z_boundary_map, 
        x_spatial_map, x_boundary_map
    )

# --- Create Decoding Graph (with a single boundary node) ---
def create_decoding_graph(num_rounds, num_ancillas, spatial_edges, boundary_map, p_data, p_meas):
    """
    Creates the space-time decoding graph for MWPM.
    
    Args:
        num_rounds (int): Number of syndrome measurement rounds (T).
        num_ancillas (int): Number of ancilla qubits (N_a).
        spatial_edges (list): List of tuples (a_i, a_j) representing spatial connections.
        boundary_map (dict): Map from boundary ancilla index to data qubit index.
        p_data (float): Data qubit error probability.
        p_meas (float): Measurement error probability.
        
    Returns:
        nx.Graph: The decoding graph.
    """
    G = nx.Graph()
    w_spatial = -np.log(p_data) if p_data > 0 else float('inf')
    w_temporal = -np.log(p_meas) if p_meas > 0 else float('inf')
    w_boundary_edge = -np.log(p_data) if p_data > 0 else float('inf') # Boundary edge weight
    
    num_nodes_per_round = num_ancillas
    
    # 1. Spatial edges
    # Add edges within each time slice (round)
    ######################################
    ######################################


    ############# Fill the code ##########


    ######################################
    ######################################
            
    # 2. Temporal edges
    # Add edges connecting the same ancilla across different time slices
    ######################################
    ######################################


    ############# Fill the code ##########


    ######################################
    ######################################

    # 3. Boundary edges
    # Connect nodes in the final round to a single boundary node
    ######################################
    ######################################


    ############# Fill the code ##########


    ######################################
    ######################################
        
    return G

# --- Calculate Syndrome from Final Result Bits ---
def calculate_syndrome_from_res(res_bits, stabilizers_map, num_ancillas):
    """
    Calculates the final syndrome by measuring stabilizers on the final data qubit state (res_bits).
    """
    final_syndrome = np.zeros(num_ancillas, dtype=int)
    
    ######################################
    ######################################


    ############# Fill the code ##########


    ######################################
    ######################################
        
    return final_syndrome

# --- Main Reporting Function ---
def run_error_correction_and_reporting(
    measured_string, num_rounds, num_data_qubits, num_x_ancillas, num_z_ancillas,
    spatial_edges_z, spatial_edges_x, prob_data_x, prob_data_z, prob_meas_z, prob_meas_x,
    injected_error_group, injected_data_flip_index, injected_ancilla_flip_index,
    enable_debug_printing=False): 
    
    (z_stabilizers, x_stabilizers, 
     z_spatial_map, z_boundary_map, 
     x_spatial_map, x_boundary_map) = get_stabilizer_and_decoding_maps()
    
    # --- 1. Parsing ---
    # Parse the long measurement string into separate arrays
    ######################################
    ######################################


    ############# Fill the code ##########


    ######################################
    ######################################

    # --- 2. 2D Transformation ---
    # Reshape the 1D syndrome arrays into 2D (round, ancilla_index)
    ######################################
    ######################################


    ############# Fill the code ##########


    ######################################
    ######################################
    
    # --- 3. Defect Calculation (Bulk) ---
    # Defects are the XOR between consecutive syndrome measurements
    ######################################
    ######################################


    ############# Fill the code ##########


    ######################################
    ######################################

    # --- 4. Boundary Defect Calculation ---
    ######################################
    ######################################


    ############# Fill the code ##########


    ######################################
    ######################################

    # --- 5. MWPM Graph Creation (Total Parity Check) ---
    
    # Z-Graph (for correcting X-errors)
    ######################################
    ######################################


    ############# Fill the code ##########


    ######################################
    ######################################
    
    # 1. Add bulk defects (from R0, R1, ..., R_T-1)
    ######################################
    ######################################


    ############# Fill the code ##########


    ######################################
    ######################################
    
    # 2. Add final boundary defects
    # (final_z_defects are the defects between R_T-1 and res_bits)
    ######################################
    ######################################


    ############# Fill the code ##########


    ######################################
    ######################################
            
    # Find the minimum weight perfect matching
    
    # Convert the matching on K_z back to a set of edges on the original z_graph
    ######################################
    ######################################


    ############# Fill the code ##########


    ######################################
    ######################################

    # X-Graph (for correcting Z-errors)
    ######################################
    ######################################


    ############# Fill the code ##########


    ######################################
    ######################################

    # 1. Add bulk defects (R0, R1, ...)
    ######################################
    ######################################


    ############# Fill the code ##########


    ######################################
    ######################################

    # 2. Add final boundary defects
    ######################################
    ######################################


    ############# Fill the code ##########


    ######################################
    ######################################
            
    # Check parity. If odd, pair one with the boundary.
    ######################################
    ######################################


    ############# Fill the code ##########


    ######################################
    ######################################)

    # Create the complete graph K_x for matching
    ######################################
    ######################################


    ############# Fill the code ##########


    ######################################
    ######################################
        
    # Find the minimum weight perfect matching
    
    # Convert the matching on K_x back to a set of edges on the original x_graph
    ######################################
    ######################################


    ############# Fill the code ##########


    ######################################
    ######################################

    # --- 6. Apply Correction ---
    # We apply Z-error corrections to the *syndrome* (or defect), not the res_bits
    
    # Z-Graph (X-Error) Correction -> Flips res_bits
    ######################################
    ######################################


    ############# Fill the code ##########


    ######################################
    ######################################

    # X-Graph (Z-Error) Correction -> Flips the final_x_syndrome
    # We are tracking the *logical* Z error, which is detected by the final X-stabilizers
    ######################################
    ######################################


    ############# Fill the code ##########


    ######################################
    ######################################

    # --- 7. Error Reporting ---
    
    ######################################
    ######################################


    ############# Fill the code ##########


    ######################################
    ######################################
    
    """
    # --- Debug Printing ---
    if enable_debug_printing and logical_error_detected:
        print("--- 🐞 DECODER INTERNAL DUMP (UE) 🐞 ---")
        
        injected_error_details = "None"
        if injected_error_group == 'Data' and injected_data_flip_index is not None:
            injected_error_details = f"Data d[{injected_data_flip_index}]"
        elif injected_error_group == 'Measurement' and injected_ancilla_flip_index is not None:
            # Assuming measurement error is always injected at R0 for this debug print
            injected_error_details = f"Meas (R0) Anc[{injected_ancilla_flip_index}]"
        print(f"DEBUG: Injected Error: {injected_error_details}")

        print(f"Parsed sx_bits (R0...R{num_rounds-1}): {sx_bits}")
        print(f"Parsed sz_bits (R0...R{num_rounds-1}): {sz_bits}")
        print(f"Parsed res_bits: {res_bits}")
        print(f"X-Defects (R0..R{num_rounds-1}): {x_defects.T}")
        print(f"Z-Defects (R0..R{num_rounds-1}): {z_defects.T}")
        print(f"Final X-Defects: {final_x_defects}")
        print(f"Final Z-Defects: {final_z_defects}")

        # Recalculate defect nodes for printing (as they were modified by parity check)
        debug_x_nodes = []
        for r in range(num_rounds):
            for a in range(num_x_ancillas):
                if x_defects[r, a] == 1: debug_x_nodes.append(r*num_x_ancillas+a)
        for a in range(num_x_ancillas):
            if final_x_defects[a] == 1: debug_x_nodes.append((num_rounds-1)*num_x_ancillas+a)
        if len(debug_x_nodes) % 2 == 1: debug_x_nodes.append(x_boundary_node)
        
        debug_z_nodes = []
        for r in range(num_rounds):
            for a in range(num_z_ancillas):
                if z_defects[r, a] == 1: debug_z_nodes.append(r*num_z_ancillas+a)
        for a in range(num_z_ancillas):
            if final_z_defects[a] == 1: debug_z_nodes.append((num_rounds-1)*num_z_ancillas+a)
        if len(debug_z_nodes) % 2 == 1: debug_z_nodes.append(z_boundary_node)

        print(f"X-Defect Nodes (for MWPM): {debug_x_nodes}")
        print(f"Z-Defect Nodes (for MWPM): {debug_z_nodes}")
        
        print(f"X-Matching (edges): {x_matching}")
        print(f"Z-Matching (edges): {z_matching}")
        print(f"Original res_bits: {np.array(res_bits)}")
        print(f"Corrected res_bits: {corrected_res_bits}")
        print(f"Corrected X-Syndrome: {corrected_final_x_syndrome} (Any={any(corrected_final_x_syndrome)})")
        print(f"Corrected Z-Syndrome: {corrected_final_z_syndrome} (Any={any(corrected_final_z_syndrome)})")
        print(f"Logical X Parity (Z_L): {logical_x_error_parity}")
        print(f"-> Result: logical_x_error: {logical_x_error_detected}, logical_z_error: {logical_z_error_detected}")
        print("---------------------------------------")
    # --- [END DEBUG] ---
    """
    
    if no_error_injected and not logical_error_detected:
        return 'NE' # No Error (No error injected, no logical error detected)
    elif not no_error_injected and not logical_error_detected:
        return 'CE' # Correctable Error (Error injected, no logical error detected)
    elif logical_error_detected:
        return 'UE' # Uncorrectable Error (Logical error detected, regardless of injection)
    else:
        # This case (no_error_injected and logical_error_detected) should be covered by 'UE'
        return 'UE' 
