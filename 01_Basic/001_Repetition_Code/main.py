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
    Error_Cases = [None, 0, 1, 2] # No error / q0 error / q1 error / q2 error
    iters=1000
    error_report = {'NE':0, 'CE':0, 'UE':0} # No Error (NE) / Correctable Error (CE) / Uncorrectable Error (UE)
    simulator = AerSimulator()
    ################ Repetition Code (X Error) ################
    print("--- Repetition Code (X Error) ---")
    error_type = 'X'

    for iters_idx in tqdm(range(0, iters)):
        # 1. Encoding
        # initial value: q0 = |1>
        # initial value: q0q1q2 -> |111>
        initial_q0_value = '1'
        qc_main=encoding_func(error_type=error_type)

        # 2. Error Injection
        error_injection_index = random.choice(Error_Cases)
        error_injection_func(qc_main, error_injection_index, error_type=error_type)
        qc_main.barrier()

        # 3. Error Detection (store syndrome to c0, c1)
        error_detection_func(qc_main, error_type=error_type)
        qc_main.barrier()

        # 4. Error Correction
        error_correction_func(qc_main, error_type=error_type)
        qc_main.barrier()

        # 5. Decoding
        decoding_func(qc_main, error_type=error_type)
        qc_main.barrier()

        # 6. Result report
        qc_main.measure(0, 2) # q0 -> c2 (classical register)

        # Circuit Print
        # qc_main.draw()

        # 7. Run Simulator
        trans_qc_main = transpile(qc_main, simulator)
        result = simulator.run(trans_qc_main, shots=1).result() # one shot (ideal case)
        counts = result.get_counts()
        measured_string = list(counts.keys())[0]

        # 8. Error Report
        # Qiskit has reverse bitstring: c2 (q0) c1 c0 (syndrome 2bit)
        final_q0_value = measured_string[0] # c2 (q0)
        syndrome_s1 = measured_string[1]    # c1
        syndrome_s0 = measured_string[2]    # c0

        if error_injection_index is None: # No Error
            if final_q0_value == initial_q0_value:
                error_report['NE'] += 1 # NE
            else:
                error_report['UE'] += 1 # UE
        else: # Error Injection
            if final_q0_value == initial_q0_value:
                error_report['CE'] += 1 # CE
            else:
                error_report['UE'] += 1 # UE
        

    print("Error Report (X Error):",error_report)

    ################ Repetition Code (Z Error) ################
    print("--- Repetition Code (Z Error) ---")
    # error report reset
    error_report = {'NE':0, 'CE':0, 'UE':0}
    error_type = 'Z'

    for iters_idx in tqdm(range(0, iters)):
        # 1. Encoding
        initial_q0_value = '1'
        qc_main=encoding_func(error_type=error_type)

        # 2. Error Injection
        error_injection_index = random.choice(Error_Cases)
        error_injection_func(qc_main, error_injection_index, error_type=error_type)
        qc_main.barrier()

        # 3. Error Detection (store syndrome to c0, c1)
        error_detection_func(qc_main, error_type=error_type)
        qc_main.barrier()

        # 4. Error Correction
        error_correction_func(qc_main, error_type=error_type)
        qc_main.barrier()

        # 5. Decoding
        decoding_func(qc_main, error_type=error_type)
        qc_main.barrier()

        # 6. Result report
        qc_main.measure(0, 2) # q0 -> c2 (classical register)

        # Circuit Print
        # qc_main.draw()

        # 7. Run Simulator
        trans_qc_main = transpile(qc_main, simulator)
        result = simulator.run(trans_qc_main, shots=1).result() # one shot (ideal case)
        counts = result.get_counts()
        measured_string = list(counts.keys())[0]

        # 8. Error Report
        # Qiskit has reverse bitstring: c2 (q0) c1 c0 (syndrome 2bit)
        final_q0_value = measured_string[0] # c2 (q0)
        syndrome_s1 = measured_string[1]    # c1
        syndrome_s0 = measured_string[2]    # c0

        if error_injection_index is None: # No Error
            if final_q0_value == initial_q0_value:
                error_report['NE'] += 1 # NE
            else:
                error_report['UE'] += 1 # UE
        else: # Error Injection
            if final_q0_value == initial_q0_value:
                error_report['CE'] += 1 # CE
            else:
                error_report['UE'] += 1 # UE

    print("Error Report (Z Error):",error_report)
    
if __name__ == '__main__':
    main()