from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
import sys

# Shor code encoding function
# single logical qubit |φ> = a|0> + b|1> -> nine physical qubits
# q0 - q8: data qubits
# q9 - q16: ancilla qubits (for syndrome measurement)
# c0 - c7: syndrome classical bits
# c8: final result classical bit (decode original logical qubit q0)
def encoding_func(initial_value='0'):
    # 9 data qubits, 8 ancilla qubits = 17 qubits
    # 8 syndrome bits, 1 result bit = 9 classical bits
    qc = QuantumCircuit(17, 9)
    
    # 1. Set initial state (logical |1> or |0>)
    if initial_value == '1':
        qc.x(0) # initial value: q0 = |1>
    
    # 2. Outer code (Phase-flip encoding)
    # |φ> = a|0> + b|1>  ->  q0q3q6 = a|000> + b|111>
    qc.cx(0, 3)
    qc.cx(0, 6)
    
    # |φ> -> q0q3q6 = a|+++> + b|--->
    qc.h([0, 3, 6])
    
    # 3. Inner code (Bit-flip encoding)
    # Encode each |+> to |+++> and |-> to |--->
    # Block 1: q0 -> q0q1q2 = |+++> or |--->
    qc.cx(0, 1)
    qc.cx(0, 2)
    
    # Block 2: q3 -> q3q4q5 = |+++> or |--->
    qc.cx(3, 4)
    qc.cx(3, 5)
    
    # Block 3: q6 -> q6q7q8 = |+++> or |--->
    qc.cx(6, 7)
    qc.cx(6, 8)
    
    return qc