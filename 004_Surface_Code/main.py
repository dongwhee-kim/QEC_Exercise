from qiskit_aer.noise import NoiseModel
from qiskit_ibm_runtime.fake_provider import FakeManilaV2
from qiskit_aer import AerSimulator
from qiskit import QuantumCircuit

import numpy as np
import layout
import decoding_graph
import correction

# Z-Graph (Data X-Error) test
def run_data_x_error_test(num_trials, num_rounds, z_graph, z_node_map):
    """
    (Z-Graph) Runs a simulation injecting a single, random data qubit X-error
    for each trial and checks if the decoder finds it.
    """
    print(f"\n--- Running {num_trials} trials of Single Data Qubit X-Errors (Z-Graph) ---")
    decoder_failures = 0

    data_to_z_ancillas = {}
    for ancilla, data_qubits in layout.z_stabilizers.items():
        for data in data_qubits:
            if data not in data_to_z_ancillas:
                data_to_z_ancillas[data] = []
            data_to_z_ancillas[data].append(ancilla)

    ancilla_names = list(layout.z_stabilizers.keys()) # Z-Ancilla name list
    data_qubit_names = list(layout.data_map.keys()) if hasattr(layout, 'data_map') else [f'd[{i}]' for i in range(layout.NUM_DATA_QUBITS)]

    for _ in range(num_trials):
        injected_data_qubit = np.random.choice(data_qubit_names)
        affected_ancillas = data_to_z_ancillas.get(injected_data_qubit, [])
        
        syndrome_list = []
        base_syndrome = np.zeros(layout.NUM_Z_ANCILLAS, dtype=int)

        for ancilla_name in affected_ancillas:
            ancilla_idx = ancilla_names.index(ancilla_name)
            base_syndrome[ancilla_idx] = 1

        for r in range(num_rounds):
            syndrome_str = "".join(map(str, base_syndrome))
            syndrome_list.append(syndrome_str)

        # ancilla_names transfer
        defect_nodes = correction.get_defects_from_syndromes(syndrome_list, ancilla_names)
        matching = correction.run_mwpm(z_graph, z_node_map, defect_nodes)

        if len(defect_nodes) == 2 and (matching is None or len(matching) != 1):
            decoder_failures += 1
        elif len(defect_nodes) != 2 and len(defect_nodes) != 0:
            decoder_failures += 1

    print(f"Data X-Error Test Complete. Decoder Failures: {decoder_failures}/{num_trials}")
    return decoder_failures

# Z-Graph (Meas Z-Error) test
def run_meas_z_error_test(num_trials, num_rounds, z_graph, z_node_map):
    """
    (Z-Graph) Runs a simulation injecting a single, random Z-ancilla measurement
    error for each trial and checks if the decoder finds it.
    """
    print(f"\n--- Running {num_trials} trials of Single Z-Measurement-Errors (Z-Graph) ---")
    decoder_failures = 0
    ancilla_names = list(layout.z_stabilizers.keys()) # Z-Ancilla name list

    for _ in range(num_trials):
        error_round = np.random.randint(0, num_rounds)
        error_ancilla_idx = np.random.randint(0, layout.NUM_Z_ANCILLAS)

        syndrome_list = []
        for r in range(num_rounds):
            round_syndrome = np.zeros(layout.NUM_Z_ANCILLAS, dtype=int)
            if r == error_round:
                round_syndrome[error_ancilla_idx] = 1
            
            syndrome_str = "".join(map(str, round_syndrome))
            syndrome_list.append(syndrome_str)

        # ancilla_names transfer
        defect_nodes = correction.get_defects_from_syndromes(syndrome_list, ancilla_names)
        matching = correction.run_mwpm(z_graph, z_node_map, defect_nodes)

        if len(defect_nodes) == 2 and (matching is None or len(matching) != 1):
            decoder_failures += 1
        elif len(defect_nodes) != 2 and len(defect_nodes) != 0:
            if error_round == num_rounds - 1:
                pass
            else:
                decoder_failures += 1

    print(f"Meas Z-Error Test Complete. Decoder Failures: {decoder_failures}/{num_trials}")
    return decoder_failures

# X-Graph (Data Z-Error) test ---
def run_data_z_error_test(num_trials, num_rounds, x_graph, x_node_map):
    """
    (X-Graph) Runs a simulation injecting a single, random data qubit Z-error
    for each trial and checks if the decoder finds it.
    """
    print(f"\n--- Running {num_trials} trials of Single Data Qubit Z-Errors (X-Graph) ---")
    decoder_failures = 0

    data_to_x_ancillas = {}
    for ancilla, data_qubits in layout.x_stabilizers.items(): # x_stabilizers
        for data in data_qubits:
            if data not in data_to_x_ancillas:
                data_to_x_ancillas[data] = []
            data_to_x_ancillas[data].append(ancilla)

    ancilla_names = list(layout.x_stabilizers.keys()) # X-Ancilla name list
    data_qubit_names = list(layout.data_map.keys()) if hasattr(layout, 'data_map') else [f'd[{i}]' for i in range(layout.NUM_DATA_QUBITS)]

    for _ in range(num_trials):
        injected_data_qubit = np.random.choice(data_qubit_names)
        affected_ancillas = data_to_x_ancillas.get(injected_data_qubit, [])
        
        syndrome_list = []
        base_syndrome = np.zeros(layout.NUM_X_ANCILLAS, dtype=int) # [!!] NUM_X_ANCILLAS

        for ancilla_name in affected_ancillas:
            ancilla_idx = ancilla_names.index(ancilla_name)
            base_syndrome[ancilla_idx] = 1

        for r in range(num_rounds):
            syndrome_str = "".join(map(str, base_syndrome))
            syndrome_list.append(syndrome_str)

        # x ancilla_names transfer
        defect_nodes = correction.get_defects_from_syndromes(syndrome_list, ancilla_names)
        matching = correction.run_mwpm(x_graph, x_node_map, defect_nodes)

        if len(defect_nodes) == 2 and (matching is None or len(matching) != 1):
            decoder_failures += 1
        elif len(defect_nodes) != 2 and len(defect_nodes) != 0:
            decoder_failures += 1

    print(f"Data Z-Error Test Complete. Decoder Failures: {decoder_failures}/{num_trials}")
    return decoder_failures

# X-Graph (Meas X-Error) test
def run_meas_x_error_test(num_trials, num_rounds, x_graph, x_node_map):
    """
    (X-Graph) Runs a simulation injecting a single, random X-ancilla measurement
    error for each trial and checks if the decoder finds it.
    """
    print(f"\n--- Running {num_trials} trials of Single X-Measurement-Errors (X-Graph) ---")
    decoder_failures = 0
    ancilla_names = list(layout.x_stabilizers.keys()) # X-Ancilla name list

    for _ in range(num_trials):
        error_round = np.random.randint(0, num_rounds)
        error_ancilla_idx = np.random.randint(0, layout.NUM_X_ANCILLAS) # [!!] NUM_X_ANCILLAS

        syndrome_list = []
        for r in range(num_rounds):
            round_syndrome = np.zeros(layout.NUM_X_ANCILLAS, dtype=int) # [!!] NUM_X_ANCILLAS
            if r == error_round:
                round_syndrome[error_ancilla_idx] = 1
            
            syndrome_str = "".join(map(str, round_syndrome))
            syndrome_list.append(syndrome_str)

        # x ancilla_names transfer
        defect_nodes = correction.get_defects_from_syndromes(syndrome_list, ancilla_names)
        matching = correction.run_mwpm(x_graph, x_node_map, defect_nodes)

        if len(defect_nodes) == 2 and (matching is None or len(matching) != 1):
            decoder_failures += 1
        elif len(defect_nodes) != 2 and len(defect_nodes) != 0:
            if error_round == num_rounds - 1:
                pass
            else:
                decoder_failures += 1

    print(f"Meas X-Error Test Complete. Decoder Failures: {decoder_failures}/{num_trials}")
    return decoder_failures

def main():
    # 0. Setup (weight = -ln(p))
    NUM_TRIALS = 1000
    NUM_ROUNDS = 3  # syndrome extraction round
    # Error Model
    prob_data_x = 0.5  # For Z-Decoding Graph (Space)
    prob_data_z = 0.5  # For X-Decoding Graph (Space)
    prob_meas_z = 0.1  # For Z-Decoding Graph (Time)
    prob_meas_x = 0.1  # For X-Decoding Graph (Time)

    print("--- Surface Code Monte Carlo Test (d=3) ---")
    print(f"Running {NUM_TRIALS} trials each for data and measurement errors.")
    print(f"Using {NUM_ROUNDS} syndrome rounds.")

    print("--- Error Model (Probabilities) ---")
    print(f"Data X-Error (p_data_x):   {prob_data_x} (Weight: {-np.log(prob_data_x):.3f})")
    print(f"Data Z-Error (p_data_z):   {prob_data_z} (Weight: {-np.log(prob_data_z):.3f})")
    print(f"Z-Meas Error (p_meas_z):  {prob_meas_z} (Weight: {-np.log(prob_meas_z):.3f})")
    print(f"X-Meas Error (p_meas_x):  {prob_meas_x} (Weight: {-np.log(prob_meas_x):.3f})")
    
    # 1. Build the Z-Decoding Graph (for X-errors)
    print("\nBuilding Z-Decoding Graph (for Data-X and Meas-Z errors)...")
    z_graph, z_node_map = decoding_graph.build_z_decoding_graph(
        NUM_ROUNDS,
        prob_data_x,  # Pass the specific prob
        prob_meas_z   # Pass the specific prob
    )
    print(f"Graph built with {z_graph.num_nodes()} nodes and {z_graph.num_edges()} edges.")
    
    # Build the Z-Decoding Graph (for X-errors)
    print("\nBuilding X-Decoding Graph (for Data-Z and Meas-X errors)...")
    x_graph, x_node_map = decoding_graph.build_x_decoding_graph(
        NUM_ROUNDS,
        prob_data_z, 
        prob_meas_x  
    )
    print(f"Graph built with {x_graph.num_nodes()} nodes and {x_graph.num_edges()} edges.")

# --- Run Simulation 1: Data Qubit Errors (tests Z-Graph) ---
    data_x_errors = run_data_x_error_test(NUM_TRIALS, NUM_ROUNDS, z_graph, z_node_map)

    # --- Run Simulation 2: Measurement Errors (tests Z-Graph) ---
    meas_z_errors = run_meas_z_error_test(NUM_TRIALS, NUM_ROUNDS, z_graph, z_node_map)
 
    # --- Run Simulation 3: Data Qubit Errors (tests X-Graph) ---
    data_z_errors = run_data_z_error_test(NUM_TRIALS, NUM_ROUNDS, x_graph, x_node_map)

    # --- Run Simulation 4: Measurement Errors (tests X-Graph) ---
    meas_x_errors = run_meas_x_error_test(NUM_TRIALS, NUM_ROUNDS, x_graph, x_node_map)

    print("\n--- Simulation Summary ---")
    print(f"Total Data-X Error Decoder Failures (Z-Graph): {data_x_errors}")
    print(f"Total Meas-Z Error Decoder Failures (Z-Graph): {meas_z_errors}")
    print(f"Total Data-Z Error Decoder Failures (X-Graph): {data_z_errors}")
    print(f"Total Meas-X Error Decoder Failures (X-Graph): {meas_x_errors}")

    # 1. Generate Surface Code Layout (Complete)

    # 1-1. Generate Z_Decoding Graph (ZZ) with weight

    # 1-2. Generate X_Decoding Graph (XX) with weight

    # 2. Error Injection (Determine Error Type)

        # Determine Error Type (Data qubit error vs Measurement error)
        # Data qubit error
        # 1) Determine X/Z/Y error
        # 2) Determine error location (e.g., 0~12 (d=3))
        # 3) Error injection
        
        # Measurement error
        # 1) Determine X/Z ancilla
        # 2) Determine error location (e.g., 0~5 (d=3))
        # 3) Error Injection (After Error Detection)

    # 3. Error Detection (Multi Adjacent CNOTs)
    # Multi Round Syndrome Extraction

    # 4. Error Correction (MWPM, using Decoding Graph)

    # Extract ancilla qubits with '1' value and make decoding graph

    # 5. Decoding??

    # 6. Error Report


if __name__ == '__main__':
    main()