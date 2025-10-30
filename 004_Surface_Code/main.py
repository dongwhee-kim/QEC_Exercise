from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
from collections import Counter
import random # Re-importing for random distribution
from qiskit.circuit import Gate

from encoding import *
from error_injection import *
from error_detection import *
from error_correction import *
from decoding import *

# This main function is MODIFIED for the Surface Code exercise
# It will NOT correct errors, but will report the SYNDROME for each error
def run_simulation_observe_syndrome(simulator, error_type, error_index, initial_q0_value='0'):
    
    # 13 data + 12 ancilla = 25 qubits
    # 12 syndrome + 1 result = 13 classical bits
    qc = QuantumCircuit(25, 13)

    # 1. Encoding
    encoding_func(qc, initial_q0_value)
    qc.barrier()

    # 2. Error Injection
    error_injection_func(qc, error_index, error_type=error_type)
    qc.barrier()

    # 3. Error Detection
    # This is the function you will write
    error_detection_func(qc)
    qc.barrier()

    # 4. Error Correction - SKIPPED FOR THIS EXERCISE
    # error_correction_func(qc) 
    # qc.barrier()

    # 5. Decoding - Not necessary for observing syndromes
    # decoding_func(qc)
    # qc.barrier()
    
    # Measure the 12 SYNDROME bits (c[0]...c[11])
    # We measure them directly at the end for simplicity
    qc.measure(range(13, 25), range(0, 12)) 
    
    # Run simulation
    trans_qc = transpile(qc, simulator)
    result = simulator.run(trans_qc, shots=1).result()
    counts = result.get_counts()
    
    # Get the single shot result
    measured_string = list(counts.keys())[0]
    
    # Qiskit measures c[12]...c[0] from left to right
    # We reverse it to show c[0]c[1]...c[11]
    syndrome_string = measured_string[::-1] 
    
    # Format: "Z_S[5..0]  X_S[5..0]"
    # (c[5]c[4]c[3]c[2]c[1]c[0]) (c[11]c[10]c[9]c[8]c[7]c[6])
    z_syndrome = syndrome_string[0:6]
    x_syndrome = syndrome_string[6:12]

    print(f"Error: {error_type} on q[{error_index}]\t-> Syndrome (Z: {z_syndrome} | X: {x_syndrome})")


def main():
    # [[13, 1, 3]] Rotated Surface Code
    # 13 data qubits
    Error_Cases = [None, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12] 
    iters = 1 # We only run 1 shot for each case
    simulator = AerSimulator()
    initial_q0_value = '0' # The logical state to test

    print("--- Surface Code [[13, 1, 3]] Syndrome Observation ---")
    print("Goal: Observe which syndrome bits flip for each error.")
    print("Syndrome Format: (Z_Syndromes c[5]-c[0] | X_Syndromes c[11]-c[6])")
    print("-" * 60)

    # --- Run 'X' errors and observe Z-syndromes ---
    print("\n[Injecting X Errors (should flip Z-syndromes)]")
    for error_q in Error_Cases:
        run_simulation_observe_syndrome(simulator, 'X', error_q, initial_q0_value)

    # --- Run 'Z' errors and observe X-syndromes ---
    print("\n[Injecting Z Errors (should flip X-syndromes)]")
    for error_q in Error_Cases:
        run_simulation_observe_syndrome(simulator, 'Z', error_q, initial_q0_value)

if __name__ == '__main__':
    main()