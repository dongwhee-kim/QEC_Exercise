from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister, transpile
from collections import Counter
from qiskit.circuit import Gate
from qiskit_aer import AerSimulator
import random
from encoding import *
from error_injection import *
from error_detection import *
from error_correction import *
from decoding import *

def main():
    Error_Cases = [None, 0, 1, 2] # No error / q0 error / q1 error / q2 error
    iters=1
    error_report = {'NE':0, 'CE':0, 'UE':0} # No Error (NE) / Correctable Error (CE) / Uncorrectable Error (UE)
    ################ Repetition Code (X Error) ################
    print("--- Repetition Code (X Error) ---")
    

    for iters_idx in range(1, iters):
        # 1. Encoding
        qc_main=encoding_func()
        qc_main.barrier()

        # 2. Error Injection
        error_injection_index = Error_Cases[random.randrange(1,5) - 1] # None, 0, 1, 2
        error_injection_func(qc_main,error_injection_index)
        qc_main.barrier()

        # 3. Error Detection
        error_detection_func(qc_main)
        qc_main.barrier()

        # 4. Error Correction (Using Syndrome)
        simulator = AerSimulator()
        trans_qc_main = transpile(qc_main, simulator)
        result = simulator.run(trans_qc_main, shots=1).result()
        counts=result.get_counts()
        measured_string = list(counts.keys())[0]
        syndrome = measured_string[-2] + measured_string[-1] # c1c0
        
        error_correction_func(qc_main, syndrome)

        qc_main.barrier()

        # 5. Decoding


        # 6. Result report

    print("Error Report (X Error):",error_report)
    ################ Repetition Code (Z Error) ################
    print("--- Repetition Code (Z Error) ---")
    # error report reset
    error_report['NE']=0
    error_report['CE']=0
    error_report['UE']=0




    print("Error Report (Z Error):",error_report)
    
if __name__ == '__main__':
    main()