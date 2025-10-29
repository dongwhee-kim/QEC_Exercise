from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister, transpile
from collections import Counter
from qiskit.circuit import Gate
from qiskit_aer import AerSimulator
from tqdm import tqdm
import random
from encoding import *
from error_injection import *
from error_detection import *
from error_correction import *
from decoding import *

def main():
    # Shor code uses 9 data qubits
    Error_Cases = [None, 0, 1, 2, 3, 4, 5, 6, 7, 8] # No error / q0 error / ... / q8 error
    iters = 1000 # Number of simulations
    error_report = {'NE':0, 'CE':0, 'UE':0} # No Error (NE) / Correctable Error (CE) / Uncorrectable Error (UE)
    simulator = AerSimulator()

    # Shor Code configuration
    # 17 qubits (9 data + 8 ancilla) / 9 classical bits (8 syndrome + 1 result)
    # 9 classical bits: c0-c5 (bit-flip syndromes), c6-c7 (phase-flip syndromes), c8 (final result)
    
    ################ Shor Code (X Error) ################
    print("--- Shor Code (X Error) ---")
    error_report = {'NE':0, 'CE':0, 'UE':0} # error report reset
    error_type = 'X'

    for iters_idx in tqdm(range(0, iters)):
        # 1. Encoding
        initial_q0_value = '1' # Test with logical |1>
        qc_main = encoding_func(initial_q0_value) # Create a 17-qubit, 9-classical-bit circuit

        # 2. Error Injection
        error_injection_index = random.choice(Error_Cases) # None, 0, 1, ... 8
        error_injection_func(qc_main, error_injection_index, error_type=error_type)
        qc_main.barrier()

        # 3. Error Detection (store syndrome to c0~c7)
        error_detection_func(qc_main)
        qc_main.barrier()

        # 4. Error Correction (Based on c0~c7 values)
        error_correction_func(qc_main)
        qc_main.barrier()

        # 5. Decoding (Restore logical state to q0)
        decoding_func(qc_main)
        qc_main.barrier()

        # 6. Result report
        qc_main.measure(0, 8) # Measure final logical qubit q0 -> c8

        # 7. Run Simulator
        trans_qc_main = transpile(qc_main, simulator)
        result = simulator.run(trans_qc_main, shots=1).result() # one shot
        counts = result.get_counts()
        measured_string = list(counts.keys())[0]

        # 8. Error Report
        # Qiskit bitstring order (reversed): c8 c7 c6 c5 c4 c3 c2 c1 c0
        final_q0_value = measured_string[0]    # c8 (final result)
        syndrome_bits = measured_string[1:]  # c7 ~ c0 (syndromes)

        if error_injection_index is None: # No Error
            if final_q0_value == initial_q0_value:
                error_report['NE'] += 1 # NE
            else:
                error_report['UE'] += 1 # UE
        else: # Error Injection
            if final_q0_value == initial_q0_value:
                error_report['CE'] += 1 # CE
            else:
                # Print error for debugging
                # print(f"UE: Error on q{error_injection_index}, Type: {error_type}, Syndromes: {syndrome_bits}, Result: {final_q0_value}")
                error_report['UE'] += 1 # UE
        

    print("Error Report (X Error):", error_report)

    ################ Shor Code (Z Error) ################
    print("--- Shor Code (Z Error) ---")
    error_report = {'NE':0, 'CE':0, 'UE':0} # error report reset
    error_type = 'Z'

    for iters_idx in tqdm(range(0, iters)):
        # 1. Encoding
        initial_q0_value = '1'
        qc_main = encoding_func(initial_q0_value)

        # 2. Error Injection
        error_injection_index = random.choice(Error_Cases)
        error_injection_func(qc_main, error_injection_index, error_type=error_type)
        qc_main.barrier()

        # 3. Error Detection
        error_detection_func(qc_main)
        qc_main.barrier()

        # 4. Error Correction
        error_correction_func(qc_main)
        qc_main.barrier()

        # 5. Decoding
        decoding_func(qc_main)
        qc_main.barrier()

        # 6. Result report
        qc_main.measure(0, 8) # q0 -> c8

        # 7. Run Simulator
        trans_qc_main = transpile(qc_main, simulator)
        result = simulator.run(trans_qc_main, shots=1).result()
        counts = result.get_counts()
        measured_string = list(counts.keys())[0]

        # 8. Error Report
        final_q0_value = measured_string[0] # c8
        syndrome_bits = measured_string[1:] # c7-c0

        if error_injection_index is None: # No Error
            if final_q0_value == initial_q0_value:
                error_report['NE'] += 1 # NE
            else:
                error_report['UE'] += 1 # UE
        else: # Error Injection
            if final_q0_value == initial_q0_value:
                error_report['CE'] += 1 # CE
            else:
                # print(f"UE: Error on q{error_injection_index}, Type: {error_type}, Syndromes: {syndrome_bits}, Result: {final_q0_value}")
                error_report['UE'] += 1 # UE

    print("Error Report (Z Error):", error_report)

    ################ Shor Code (Y Error) ################
    print("--- Shor Code (Y Error) ---")
    error_report = {'NE':0, 'CE':0, 'UE':0} # error report reset
    error_type = 'Y' # Y = XZ

    for iters_idx in tqdm(range(0, iters)):
        # 1. Encoding
        initial_q0_value = '1'
        qc_main = encoding_func(initial_q0_value)

        # 2. Error Injection
        error_injection_index = random.choice(Error_Cases)
        error_injection_func(qc_main, error_injection_index, error_type=error_type)
        qc_main.barrier()

        # 3. Error Detection
        error_detection_func(qc_main)
        qc_main.barrier()

        # 4. Error Correction
        error_correction_func(qc_main)
        qc_main.barrier()

        # 5. Decoding
        decoding_func(qc_main)
        qc_main.barrier()

        # 6. Result report
        qc_main.measure(0, 8) # q0 -> c8

        # 7. Run Simulator
        trans_qc_main = transpile(qc_main, simulator)
        result = simulator.run(trans_qc_main, shots=1).result()
        counts = result.get_counts()
        measured_string = list(counts.keys())[0]

        # 8. Error Report
        final_q0_value = measured_string[0] # c8
        syndrome_bits = measured_string[1:] # c7-c0

        if error_injection_index is None: # No Error
            if final_q0_value == initial_q0_value:
                error_report['NE'] += 1 # NE
            else:
                error_report['UE'] += 1 # UE
        else: # Error Injection
            if final_q0_value == initial_q0_value:
                error_report['CE'] += 1 # CE
            else:
                # print(f"UE: Error on q{error_injection_index}, Type: {error_type}, Syndromes: {syndrome_bits}, Result: {final_q0_value}")
                error_report['UE'] += 1 # UE

    print("Error Report (Y Error):", error_report)


if __name__ == '__main__':
    main()

