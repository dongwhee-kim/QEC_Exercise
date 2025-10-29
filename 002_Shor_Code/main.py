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

# Simulates by randomly distributing the total 'iters' among the Error_Cases.
def run_simulation_hybrid(simulator, error_type, iters, Error_Cases, initial_q0_value='1'):
    print(f"--- Shor Code ({error_type} Error) [Hybrid Random Sampling] ---")
    error_report = {'NE':0, 'CE':0, 'UE':0}
    
    # 1. Randomly pick from the 10 error cases 'iters' number of times.
    print(f"Generating random distribution for {iters} total trials...")
    # (e.g., make 1000 picks)
    trial_picks = random.choices(Error_Cases, k=iters)
    
    # 2. Count how many times each case was picked.
    # (e.g., {None: 98, 0: 105, 1: 95, 2: 101, ...})
    case_shot_counts = Counter(trial_picks)
    print(f"Random distribution (Total {sum(case_shot_counts.values())} shots): {dict(case_shot_counts)}")

    # 3. Pre-generate and transpile the 10 base circuits.
    # (Prepare them in advance to avoid creating them in a loop)
    print("Preparing and transpiling 10 base circuits...")
    transpiled_circuits_map = {}
    for error_index in Error_Cases:
        qc = encoding_func(initial_q0_value)
        error_injection_func(qc, error_index, error_type=error_type)
        qc.barrier()
        error_detection_func(qc)
        qc.barrier()
        error_correction_func(qc)
        qc.barrier()
        decoding_func(qc)
        qc.barrier()
        qc.measure(0, 8) # q0 -> c8
        
        # Store the transpiled circuit in a dictionary
        transpiled_circuits_map[error_index] = transpile(qc, simulator)

    # 4. Run 'individual' simulations for each case with its 'randomly assigned shot count'
    print("Running simulations with random shot counts...")
    for error_index, shots_for_this_case in case_shot_counts.items():
        # Skip if this case was picked 0 times (e.g., if iters < 10)
        if shots_for_this_case == 0:
            continue
            
        trans_qc = transpiled_circuits_map[error_index]
        # Run only for the number of shots assigned to this case (e.g., 98 shots)
        result = simulator.run(trans_qc, shots=shots_for_this_case).result()
        counts = result.get_counts()
        
        # 5. Aggregate results (same logic as before)
        for measured_string, count in counts.items():
            final_q0_value = measured_string[0] # c8
            
            if error_index is None: # 'No Error' case
                if final_q0_value == initial_q0_value:
                    error_report['NE'] += count
                else:
                    error_report['UE'] += count
            else: # 'Error Injected' case
                if final_q0_value == initial_q0_value:
                    error_report['CE'] += count
                else:
                    error_report['UE'] += count
                        
    print(f"Error Report ({error_type} Error):", error_report)
    return error_report

def main():
    # Shor code uses 9 data qubits
    Error_Cases = [None, 0, 1, 2, 3, 4, 5, 6, 7, 8] # No error / q0 error / ... / q8 error
    iters = 1000 # Total number of simulation iterations
    simulator = AerSimulator()
    initial_q0_value = '1' # The logical state to test

    # --- Run 'hybrid' simulation for each error type ---
    run_simulation_hybrid(simulator, 'X', iters, Error_Cases, initial_q0_value)
    run_simulation_hybrid(simulator, 'Z', iters, Error_Cases, initial_q0_value)
    run_simulation_hybrid(simulator, 'Y', iters, Error_Cases, initial_q0_value)


if __name__ == '__main__':
    main()