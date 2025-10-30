import numpy as np
import pymatching
from qiskit import transpile
from qiskit_aer import AerSimulator

# Import the circuit-building function
from circuit_builder import create_qec_circuit

def get_parity_check_matrices():
    """
    Defines the Parity-Check Matrix (H) for the [[9, 1, 3]] code.
    This H matrix is the "graph" that MWPM uses.
    """
    # H_z: Z-stabilizers (4 stabs x 9 qubits)
    # This matrix detects X-errors
    H_z = np.array([
        [1, 1, 0, 1, 1, 0, 0, 0, 0], # c[0]: Z0 Z1 Z3 Z4
        [0, 1, 1, 0, 1, 1, 0, 0, 0], # c[1]: Z1 Z2 Z4 Z5
        [0, 0, 0, 1, 1, 0, 1, 1, 0], # c[2]: Z3 Z4 Z6 Z7
        [0, 0, 0, 0, 1, 1, 0, 1, 1]  # c[3]: Z4 Z5 Z7 Z8
    ], dtype=np.uint8)

    # H_x: X-stabilizers (4 stabs x 9 qubits)
    # This matrix detects Z-errors
    # For this specific code, H_x is identical to H_z
    H_x = np.array([
        [1, 1, 0, 1, 1, 0, 0, 0, 0], # c[4]: X0 X1 X3 X4
        [0, 1, 1, 0, 1, 1, 0, 0, 0], # c[5]: X1 X2 X4 X5
        [0, 0, 0, 1, 1, 0, 1, 1, 0], # c[6]: X3 X4 X6 X7
        [0, 0, 0, 0, 1, 1, 0, 1, 1]  # c[7]: X4 X5 X7 X8
    ], dtype=np.uint8)
    
    return H_z, H_x

def get_logical_operators():
    """
    Defines the Logical Operators for the [[9, 1, 3]] code.
    We need these to check if a logical error occurred.
    """
    # Z_L = Z0 * Z3 * Z6 (any vertical column)
    Z_logical = np.array([1, 0, 0, 1, 0, 0, 1, 0, 0], dtype=np.uint8)
    
    # X_L = X0 * X1 * X2 (any horizontal row)
    X_logical = np.array([1, 1, 1, 0, 0, 0, 0, 0, 0], dtype=np.uint8)
    
    return Z_logical, X_logical

def main():
    print("--- [[9, 1, 3]] Surface Code Simulation with MWPM Decoder ---")

    # 1. Setup Simulator and Classical Code Definitions
    simulator = AerSimulator()
    H_z, H_x = get_parity_check_matrices()
    Z_L, X_L = get_logical_operators()

    # 2. Initialize the MWPM "Matcher" objects from Pymatching
    # This creates the graph object from the H matrix
    
    # *** FIXED HERE ***
    z_error_matcher = pymatching.Matching(H_z)
    x_error_matcher = pymatching.Matching(H_x)
    # *** FIXED HERE ***

    # 3. Define Test Cases
    # (Error Type, Qubit Index)
    test_cases = [
        ('X', 4),  # X-error on q[4] (center) -> flips all 4 Z-syndromes
        ('X', 1),  # X-error on q[1] -> flips c[0], c[1]
        ('Z', 7),  # Z-error on q[7] -> flips c[6], c[7]
        ('Y', 8),  # Y-error on q[8] -> flips c[3] (Z-stab) and c[7] (X-stab)
        ('X', 0),  # X-error on q[0] (boundary)
        ('Z', 2),  # Z-error on q[2] (boundary)
        (None, None) # No error
    ]
    
    print(f"Testing {len(test_cases)} single-qubit error cases...")
    print("-" * 60)
    
    num_logical_errors = 0

    for error_type, error_qubit in test_cases:
        
        # 4. Create and Run the Quantum Circuit
        qc = create_qec_circuit(error_type, error_qubit)
        trans_qc = transpile(qc, simulator)
        # We run 1 shot and get the 'memory' (the classical bit string)
        result = simulator.run(trans_qc, shots=1, memory=True).result()
        syndrome_str = result.get_memory(0)[0] # e.g., '00001100'
        
        # Qiskit measures c[7]...c[0], so we reverse it
        syndrome_str = syndrome_str[::-1] # Now c[0]...c[7]
        
        # 5. Classical Post-processing: Parse Syndromes
        syndrome_bits = np.array([int(s) for s in syndrome_str], dtype=np.uint8)
        
        z_syndrome = syndrome_bits[0:4] # For X-errors (c[0]-c[3])
        x_syndrome = syndrome_bits[4:8] # For Z-errors (c[4]-c[7])

        # 6. Classical Post-processing: MWPM Decoding
        # Feed the syndrome to the matcher to get the predicted error
        predicted_x_error_vec = z_error_matcher.decode(z_syndrome)
        predicted_z_error_vec = x_error_matcher.decode(x_syndrome)

        # 7. Classical Post-processing: Verification
        # Create a vector for the error we actually injected
        injected_x_error_vec = np.zeros(9, dtype=np.uint8)
        injected_z_error_vec = np.zeros(9, dtype=np.uint8)
        
        if error_type:
            if 'X' in error_type:
                injected_x_error_vec[error_qubit] = 1
            if 'Z' in error_type:
                injected_z_error_vec[error_qubit] = 1

        # The final error is (injected + predicted) mod 2
        final_x_error = (injected_x_error_vec + predicted_x_error_vec) % 2
        final_z_error = (injected_z_error_vec + predicted_z_error_vec) % 2

        # 8. Check for Logical Error
        # A logical error occurs if the *final* error flips the logical state.
        # This happens if (final_x_error) anti-commutes with (Z_L)
        # OR (final_z_error) anti-commutes with (X_L).
        # We check this with a dot product modulo 2.
        
        is_x_logical_error = (final_x_error @ Z_L) % 2 != 0
        is_z_logical_error = (final_z_error @ X_L) % 2 != 0
        
        status = "SUCCESS"
        if is_x_logical_error or is_z_logical_error:
            status = "FAILURE (Logical Error)"
            num_logical_errors += 1

        print(f"Test: {str(error_type)} on q[{str(error_qubit)}] | Syndrome (Z|X): {z_syndrome} | {x_syndrome}")
        print(f"  -> Predicted X Error: {predicted_x_error_vec}")
        print(f"  -> Predicted Z Error: {predicted_z_error_vec}")
        print(f"  -> Result: {status}\n")

    print("-" * 60)
    print(f"Simulation Complete. Total Logical Errors: {num_logical_errors}")

if __name__ == '__main__':
    main()