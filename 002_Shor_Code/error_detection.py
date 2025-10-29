from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
import sys

# Shor code syndrome measurement
# Uses 8 ancilla qubits (q9~q16) to measure 8 syndrome bits (c0~c7)
def error_detection_func(qc):   
    # --- 1. Detect bit-flip errors (ZZ) ---
    # Store syndromes in c0 ~ c5
    # Use ancilla qubits q9 ~ q14
    
    ######################################
    ######################################


    ############# Fill the code ##########


    ######################################
    ######################################
    
    # --- 2. Detect phase-flip errors (XX) ---
    # Store syndromes in c6 ~ c7
    # Use ancilla qubits q15 ~ q16
    
    ######################################
    ######################################


    ############# Fill the code ##########


    ######################################
    ######################################

    return