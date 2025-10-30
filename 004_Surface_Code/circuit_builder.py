import numpy as np
from qiskit import QuantumCircuit

def create_qec_circuit(error_type=None, error_qubit=None):
    """
    Creates the [[9, 1, 3]] syndrome measurement circuit.
    
    Qubit Layout:
    - Data: q[0] - q[8]
    - Ancilla (Z-stabs): q[9] - q[12]
    - Ancilla (X-stabs): q[13] - q[16]
    
    Syndrome Bit Layout:
    - c[0]-c[3]: Z-stabilizer syndromes (detect X errors)
    - c[4]-c[7]: X-stabilizer syndromes (detect Z errors)
    """
    
    # 9 data + 8 ancilla = 17 qubits
    # 8 syndrome bits (c[0]-c[7])
    qc = QuantumCircuit(17, 8)

    # --- 1. Encoding ---
    # The logical |0> state for this code is simply all qubits
    # in the |0> state. No encoding gates are needed.
    # We will test correction of the |0>_L state.
    
    qc.barrier()

    # --- 2. Error Injection ---
    if error_qubit is not None and error_type is not None:
        if 'X' in error_type:
            qc.x(error_qubit)
        if 'Z' in error_type:
            qc.z(error_qubit) # 'Y' error applies both
        
    qc.barrier()

    # --- 3. Error Detection (Syndrome Measurement) ---
    
    # --- Z-Stabilizers (Plaquettes) -> Detect X-errors ---
    # c[0]-c[3] : X-error syndrome
    # Ancillas: q[9]-q[12]
    
    # c[0] (q[9]): Z0 Z1 Z3 Z4
    qc.cx(0, 9)
    qc.cx(1, 9)
    qc.cx(3, 9)
    qc.cx(4, 9)
    
    # c[1] (q[10]): Z1 Z2 Z4 Z5
    qc.cx(1, 10)
    qc.cx(2, 10)
    qc.cx(4, 10)
    qc.cx(5, 10)
    
    # c[2] (q[11]): Z3 Z4 Z6 Z7
    qc.cx(3, 11)
    qc.cx(4, 11)
    qc.cx(6, 11)
    qc.cx(7, 11)
    
    # c[3] (q[12]): Z4 Z5 Z7 Z8
    qc.cx(4, 12)
    qc.cx(5, 12)
    qc.cx(7, 12)
    qc.cx(8, 12)

    # --- X-Stabilizers (Vertices) -> Detect Z-errors ---
    # c[4]-c[7] : Z-error syndrome
    # Ancillas: q[13]-q[16]
    
    qc.h([13, 14, 15, 16])
    
    # c[4] (q[13]): X0 X1 X3 X4
    qc.cx(13, 0)
    qc.cx(13, 1)
    qc.cx(13, 3)
    qc.cx(13, 4)

    # c[5] (q[14]): X1 X2 X4 Z5
    qc.cx(14, 1)
    qc.cx(14, 2)
    qc.cx(14, 4)
    qc.cx(14, 5)
    
    # c[6] (q[15]): X3 X4 X6 X7
    qc.cx(15, 3)
    qc.cx(15, 4)
    qc.cx(15, 6)
    qc.cx(15, 7)
    
    # c[7] (q[16]): X4 X5 X7 X8
    qc.cx(16, 4)
    qc.cx(16, 5)
    qc.cx(16, 7)
    qc.cx(16, 8)
    
    qc.h([13, 14, 15, 16])
    
    qc.barrier()
    
    # --- 4. Syndrome Measurement ---
    # Measure the 8 ancilla qubits into the 8 classical bits
    qc.measure(range(9, 17), range(0, 8))
    
    return qc
