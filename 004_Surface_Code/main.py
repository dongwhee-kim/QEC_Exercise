from qiskit_aer.noise import NoiseModel
from qiskit_ibm_runtime.fake_provider import FakeManilaV2
from qiskit_aer import AerSimulator
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister, transpile

import random
import numpy as np
import generate_circuit
import error_injection
import syndrome_extraction
import result_report
import error_correction

def main():
    # 0. Setup (weight = -ln(p))
    iters = 1
    d=3 # code distance
    error_report = {'NE':0, 'CE':0, 'UE':0} # No Error (NE) / Correctable Error (CE) / Uncorrectable Error (UE)
    simulator = AerSimulator()
    num_data_qubits = 13
    num_x_ancillas = 6
    num_z_ancillas = 6
    num_trials = 1000
    num_rounds = 3  # syndrome extraction round
    # Error Model
    prob_data_x = 0.001  # For Z-Decoding Graph (Space)
    prob_data_z = 0.001  # For X-Decoding Graph (Space)
    prob_meas_z = 0.01  # For Z-Decoding Graph (Time)
    prob_meas_x = 0.01  # For X-Decoding Graph (Time)

    Error_Data_Cases = [None, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
    Error_Ancilla_Cases = [None, 0, 1, 2, 3, 4, 5]
    Error_Group = ['Data', 'Measurement']
    Error_Types = ['X','Z','Y']

    print("--- Surface Code Monte Carlo Test (d=3) ---")
    print(f"Running {num_trials} trials each for data and measurement errors.")
    print(f"Using {num_rounds} syndrome rounds.")

    print("--- Error Model (Probabilities) ---")
    print(f"Data X-Error (p_data_x):   {prob_data_x} (Weight: {-np.log(prob_data_x):.3f})")
    print(f"Data Z-Error (p_data_z):   {prob_data_z} (Weight: {-np.log(prob_data_z):.3f})")
    print(f"Z-Meas Error (p_meas_z):  {prob_meas_z} (Weight: {-np.log(prob_meas_z):.3f})")
    print(f"X-Meas Error (p_meas_x):  {prob_meas_x} (Weight: {-np.log(prob_meas_x):.3f})")
    
    # Single Data Qubit Error/Single Measurement Error Test Start

    # 1. Generate Surface Code Layout (Complete)
    qc_main = generate_circuit.generate_circuit_func()
    # initialization: d register all '0's (|0...0>)
    qc_main.initialize([0]*num_data_qubits, qc_main.qregs[0])
    qc_main.barrier()

    # 1-1. Generate Z_Decoding Graph (ZZ) with weight
    # start_index = 0, end_index = 1 -> c_z[0] connected with c_z[1]
    # d=3 -> 7 edges per a round -> len(start_index_z_graph) = 7
    start_index_z_graph = [0, 0, 1, 2, 2, 3, 4]
    end_index_z_graph = [1, 2, 3, 3, 4, 5, 5]
    spatial_edges_z = list(zip(start_index_z_graph, end_index_z_graph))
    #weight_z_graph = [-np.log(prob_data_x),-np.log(prob_data_x),
    #                  -np.log(prob_data_x),-np.log(prob_data_x),
    #                  -np.log(prob_data_x),-np.log(prob_data_x),
    #                  -np.log(prob_data_x)] # edge weight: -ln(0.5)

    # 1-2. Generate X_Decoding Graph (XX) with weight
    start_index_x_graph = [0, 0, 1, 1, 2, 3, 4]
    end_index_x_graph = [1, 3, 2, 4, 5, 4, 5]
    spatial_edges_x = list(zip(start_index_x_graph, end_index_x_graph))
    #weight_x_graph = [-np.log(prob_data_z),-np.log(prob_data_z),
    #                  -np.log(prob_data_z),-np.log(prob_data_z),
    #                  -np.log(prob_data_z),-np.log(prob_data_z),
    #                  -np.log(prob_data_z)] # edge weight: -ln(0.5)
    
    # 2. Error Injection (Determine Error Type) - single data qubit error injection은 round0에만 들어간다.
    # error 누적: , round=0에서 d[5]에 X 오류 있으면 sz[2]=1, sz[8]=1, sz[14]=1 된다.
    # single measurement error는 error detection 이후에 들어감.
    print("--- Test Correction Capabiliy (d=3 -> Single Data Qubit Error/Single Measurement Error) ---")
    data_flip_index = random.choice(Error_Data_Cases) # None, 0, 1, ... 12
    ancilla_flip_index = random.choice(Error_Ancilla_Cases) # None, 0, 1, 2, 3, 4, 5
    error_group = random.choice(Error_Group) # Data, Measurement
    error_type = random.choice(Error_Types) # X, Z, Y
    # single data qubit error (error injected only round 0)
    if error_group == 'Data':
        error_injection.error_injection_single_qubit_error_func(qc_main, data_flip_index, error_type)

    # 3. Error Detection (Multi Adjacent CNOTs)
    # Multi Round Syndrome Extraction
    for round_idx in range(num_rounds):
        syndrome_extraction.syndrome_extraction_func(qc_main, round_idx)
        # measurement error injection (only round 0)
        # only apply bit flip (because it is a classical value)
        if error_group=='Measurement' and round_idx==0:
            error_injection.error_injection_single_measurement_error_func(qc_main, ancilla_flip_index, error_type)

    # 4. Error Correction (MWPM, using Decoding Graph)

    # Extract ancilla qubits with '1' value and make decoding graph

    # 5. Result report (13 data qubits)
    result_report.result_report_func(qc_main)

    # 6. Run Simulator
    trans_qc_main = transpile(qc_main, simulator)
    result = simulator.run(trans_qc_main, shots=1).result() # on sho
    counts = result.get_counts()
    measured_string = list(counts.keys())[0]

    # 7. Error Report using final data qubit (13bit) and syndromes


    # LER Test Start

    print("--- Test Logical Error Rate (LER) (d=3) ---")
    
    # 2. Error Injection (Determine Error Type) - error injection은 모든 round에 랜덤하게 들어간다.
    # 모든 라운드에 독립적으로 들어감. 

    error_injection.error_injection_logical_error_rate_func(qc_main, flip)

if __name__ == '__main__': 
    main()