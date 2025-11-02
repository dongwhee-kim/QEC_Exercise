from qiskit_aer.noise import NoiseModel
from qiskit_ibm_runtime.fake_provider import FakeManilaV2
from qiskit_aer import AerSimulator
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister, transpile

from tqdm import tqdm
import random
import numpy as np
import generate_circuit
import error_injection
import syndrome_extraction
import result_report
import error_correction

def main():
    # 0. Setup (weight = -ln(p))
    d=3 # code distance
    error_report = {'NE':0, 'CE':0, 'UE':0} # No Error (NE) / Correctable Error (CE) / Uncorrectable Error (UE)
    simulator = AerSimulator()
    num_data_qubits = 13
    num_x_ancillas = 6
    num_z_ancillas = 6
    num_trials = 100 # Monte-Carlo Simulation
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
    print(f"Using {num_rounds} syndrome rounds.")

    print("--- Error Model (Probabilities) ---")
    print(f"Data X-Error (p_data_x):   {prob_data_x} (Weight: {-np.log(prob_data_x):.3f})")
    print(f"Data Z-Error (p_data_z):   {prob_data_z} (Weight: {-np.log(prob_data_z):.3f})")
    print(f"Z-Meas Error (p_meas_z):  {prob_meas_z} (Weight: {-np.log(prob_meas_z):.3f})")
    print(f"X-Meas Error (p_meas_x):  {prob_meas_x} (Weight: {-np.log(prob_meas_x):.3f})")
    
    # 1-1. Generate Z_Decoding Graph (ZZ) with weight (Constant setup)
    start_index_z_graph = [0, 0, 1, 2, 2, 3, 4]
    end_index_z_graph = [1, 2, 3, 3, 4, 5, 5]
    spatial_edges_z = list(zip(start_index_z_graph, end_index_z_graph))

    # 1-2. Generate X_Decoding Graph (XX) with weight (Constant setup)
    start_index_x_graph = [0, 0, 1, 1, 2, 3, 4]
    end_index_x_graph = [1, 3, 2, 4, 5, 4, 5]
    spatial_edges_x = list(zip(start_index_x_graph, end_index_x_graph))
    
    print(f"\n--- Test Correction Capabiliy (Single Error Injection) ---")
    print(f"Running {num_trials} trials for single error correction capability.")

    # Monte-Carlo Start (Single Error Test)
    for trial_num in tqdm(range(num_trials), desc="Running Single Error Test"):
        
        # 1. Generate Surface Code Layout (Fresh circuit for each trial)
        qc_main = generate_circuit.generate_circuit_func()
        qc_main.initialize(0, qc_main.qregs[0])
        qc_main.barrier()

        # 2. Error Injection (Single specific error)
        data_flip_index = random.choice(Error_Data_Cases) 
        ancilla_flip_index = random.choice(Error_Ancilla_Cases)
        error_group = random.choice(Error_Group) 
        error_type = random.choice(Error_Types) 

        if error_group == 'Data':
            error_injection.error_injection_single_qubit_error_func(qc_main, data_flip_index, error_type)

        # 3. Error Detection
        for round_idx in range(num_rounds):
            syndrome_extraction.syndrome_extraction_func(qc_main, round_idx)

        # 4. Result report
        result_report.result_report_func(qc_main)

        # 5. Run Simulator
        trans_qc_main = transpile(qc_main, simulator)
        result = simulator.run(trans_qc_main, shots=1).result() 
        counts = result.get_counts()
        measured_string = list(counts.keys())[0]

        # 6. Post-Process -> Measurement Error Injection (Single specific error)
        if error_group == 'Measurement':
            measured_string = error_injection.post_process_measurement_error_func(
                measured_string, ancilla_flip_index, error_type, 
                round_idx=0, # Single error test only injects at R0
                num_z_ancillas=num_z_ancillas, 
                num_x_ancillas=num_x_ancillas
            )

        # 7. Error Correction (MWPM, using Decoding Graph) and Reporting
        status = error_correction.run_error_correction_and_reporting(
            measured_string=measured_string,
            num_rounds=num_rounds,
            num_data_qubits=num_data_qubits,
            num_x_ancillas=num_x_ancillas,
            num_z_ancillas=num_z_ancillas,
            spatial_edges_z=spatial_edges_z,
            spatial_edges_x=spatial_edges_x,
            prob_data_x=prob_data_x,
            prob_data_z=prob_data_z,
            prob_meas_z=prob_meas_z,
            prob_meas_x=prob_meas_x,
            injected_error_group=error_group,
            injected_data_flip_index=data_flip_index,
            injected_ancilla_flip_index=ancilla_flip_index
        )

        error_report[status] += 1
    # Monte-Carlo End (Single Error Test)

    print("\n--- Final Correction Report (Single Error Test) ---")
    print(f"Total Trials: {num_trials}")
    print(f"Results: {error_report}")
    success_rate = (error_report['NE'] + error_report['CE']) / num_trials * 100
    failure_rate = error_report['UE'] / num_trials * 100
    print(f"Success Rate (NE + CE): {success_rate:.2f}%")
    print(f"Failure Rate (UE): {failure_rate:.2f}%")


    # --- [LER Test Start] ---
    print("\n--- Test Logical Error Rate (LER) (d=3) ---")
    print(f"Running {num_trials} trials with probabilistic errors.")
    print(f"Using {num_rounds} syndrome rounds.")
    
    error_report_ler = {'NE':0, 'CE':0, 'UE':0} # Reset report for LER test

    for trial_num in tqdm(range(num_trials), desc="Running LER Test"):
        
        # 1. Generate Surface Code Layout (Fresh circuit)
        qc_ler = generate_circuit.generate_circuit_func()
        # Initialize in |0_L> state
        qc_ler.initialize(0, qc_ler.qregs[0]) 
        qc_ler.barrier()

        # 2. Error Injection & Detection (Per Round)
        for round_idx in range(num_rounds):
            # Inject probabilistic data qubit errors (X, Z) BEFORE syndrome measurement
            error_injection.error_injection_logical_error_rate_func(
                qc_ler, 
                num_data_qubits, 
                prob_data_x, 
                prob_data_z
            )
            
            # Run syndrome extraction circuit for this round
            syndrome_extraction.syndrome_extraction_func(qc_ler, round_idx)
            
            # Note: Measurement errors are injected *after* simulation

        # 3. Final data qubit measurement
        result_report.result_report_func(qc_ler)

        # 4. Run Simulator
        trans_qc_ler = transpile(qc_ler, simulator)
        result_ler = simulator.run(trans_qc_ler, shots=1).result() 
        counts_ler = result_ler.get_counts()
        measured_string_ler = list(counts_ler.keys())[0]

        # 5. Post-Process -> Inject Probabilistic Measurement Errors (All rounds)
        measured_string_with_meas_errors = error_injection.post_process_ler_measurement_errors(
            measured_string_ler,
            num_rounds,
            num_x_ancillas,
            num_z_ancillas,
            prob_meas_x,
            prob_meas_z
        )

        # 6. Error Correction (MWPM) and Reporting
        # For LER test, we don't have a *single* known injected error,
        # so we pass 'None' for the injection details.
        status_ler = error_correction.run_error_correction_and_reporting(
            measured_string=measured_string_with_meas_errors,
            num_rounds=num_rounds,
            num_data_qubits=num_data_qubits,
            num_x_ancillas=num_x_ancillas,
            num_z_ancillas=num_z_ancillas,
            spatial_edges_z=spatial_edges_z,
            spatial_edges_x=spatial_edges_x,
            prob_data_x=prob_data_x,
            prob_data_z=prob_data_z,
            prob_meas_z=prob_meas_z,
            prob_meas_x=prob_meas_x,
            injected_error_group=None, # Not tracking a single injected error
            injected_data_flip_index=None,
            injected_ancilla_flip_index=None
        )

        error_report_ler[status_ler] += 1
    # LER Monte-Carlo End

    print("\n--- LER Test Final Report ---")
    print(f"Total Trials: {num_trials}")
    print(f"Results: {error_report_ler}")
    
    # Calculate LER
    # LER is the probability that an uncorrectable error (UE) occurred.
    ler = error_report_ler['UE'] / num_trials
    print(f"Logical Error Rate (LER) (UE / Trials): {ler:.6f}")
    
    success_rate_ler = (error_report_ler['NE'] + error_report_ler['CE']) / num_trials * 100
    print(f"Success Rate (NE + CE): {success_rate_ler:.2f}%")
    print(f"Failure Rate (UE): {100.0 - success_rate_ler:.2f}%")
    # --- [⭐️ LER Test End ⭐️] ---


if __name__ == '__main__': 
    main()