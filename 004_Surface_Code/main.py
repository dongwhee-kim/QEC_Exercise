from qiskit_aer.noise import NoiseModel
from qiskit_ibm_runtime.fake_provider import FakeManilaV2
from qiskit_aer import AerSimulator
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister

import numpy as np
import generate_circuit
import error_injection
import syndrome_extraction

def main():
    # 0. Setup (weight = -ln(p))
    d=3 # code distance
    num_data_qubits = 13
    num_x_ancillas = 6
    num_z_ancillas = 6
    num_trials = 1000
    num_rounds = 3  # syndrome extraction round
    # Error Model
    prob_data_x = 0.5  # For Z-Decoding Graph (Space)
    prob_data_z = 0.5  # For X-Decoding Graph (Space)
    prob_meas_z = 0.1  # For Z-Decoding Graph (Time)
    prob_meas_x = 0.1  # For X-Decoding Graph (Time)

    Error_Data_Cases = [None, 0, 1, 2, 3, 4, 5, 6]

    print("--- Surface Code Monte Carlo Test (d=3) ---")
    print(f"Running {num_trials} trials each for data and measurement errors.")
    print(f"Using {num_rounds} syndrome rounds.")

    print("--- Error Model (Probabilities) ---")
    print(f"Data X-Error (p_data_x):   {prob_data_x} (Weight: {-np.log(prob_data_x):.3f})")
    print(f"Data Z-Error (p_data_z):   {prob_data_z} (Weight: {-np.log(prob_data_z):.3f})")
    print(f"Z-Meas Error (p_meas_z):  {prob_meas_z} (Weight: {-np.log(prob_meas_z):.3f})")
    print(f"X-Meas Error (p_meas_x):  {prob_meas_x} (Weight: {-np.log(prob_meas_x):.3f})")
    

    # 1. Generate Surface Code Layout (Complete)
    qc_main = generate_circuit.generate_circuit_func()

    # 1-1. Generate Z_Decoding Graph (ZZ) with weight
    """
       start_index, end_index는 같은 node 기준이면 index가 작은 것에서 큰 순서
    d=3기준 round마다 7개 edge 있음
    -> start_index_z_graph = [0, 0, 1, 2, 2, 3, 4]
    -> end_index_z_graph   = [1, 2, 3, 3, 4, 5, 5]
    -> weight_z_graph 	    = [ln2, ln2, ln2, ln2, ln2, ln2, ln2]
    """

    # 1-2. Generate X_Decoding Graph (XX) with weight

    print("--- Test Correction Capabiliy (d=3 -> Single Data Qubit Error/Single Measurement Error) ---")


    # 2. Error Injection (Determine Error Type) - error injection은 round0에만 들어간다.
    # 모든 라운드에 독립적으로 들어감. 
    # 오류 전파 -> 이전 라운드에 data qubit 오류 있으면 수정되기 전까지 사라지지 않음. ->
    # 즉, round=0에서 d[5]에 X 오류 있으면 sz[2]=1, sz[8]=1, sz[14]=1 된다.
    # measurement error qc.measure 이후에 얻게 되는 classical bit를 뒤집는 방식으로 진행. 
    # 매 라운드마다 총 12개 syndome 측정 결과값 sz, sx들을 확률적으로 값을 뒤집는다.
    # classical 값이기에 bit flip만 적용하면 된다.

        # Determine Error Type (Data qubit error vs Measurement error)
        # Data qubit error
        # 1) Determine X/Z/Y error
        # 2) Determine error location (e.g., 0~12 (d=3))
        # 3) Error injection
        
        # Measurement error
        # 1) Determine X/Z ancilla
        # 2) Determine error location (e.g., 0~5 (d=3))
        # 3) Error Injection (After Error Detection)
    error_injection.error_injection_correction_capability_func(qc_main, flip)

    # 3. Error Detection (Multi Adjacent CNOTs)
    # Multi Round Syndrome Extraction
    for round_idx in range(num_rounds):
        syndrome_extraction.syndrome_extraction_func(qc_main, round_idx)

    # 4. Error Correction (MWPM, using Decoding Graph)

    # Extract ancilla qubits with '1' value and make decoding graph

    # 5. Decoding??

    # 6. Error Report

    print("--- Test Logical Error Rate (LER) (d=3) ---")
    
    # 2. Error Injection (Determine Error Type) - error injection은 모든 round에 랜덤하게 들어간다.

    error_injection.error_injection_logical_error_rate_func(qc_main, flip)

if __name__ == '__main__': 
    main()