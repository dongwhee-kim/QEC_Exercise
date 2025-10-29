from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
import sys

# Steane code encoding function
def encoding_func(initial_value='0'):
    # 7 data qubits, 6 ancilla qubits = 13 qubits
    # 6 syndrome bits, 1 result bit = 7 classical bits
    qc = QuantumCircuit(13, 7)

    # 1. Set initial state (logical |1> or |0>)
    if initial_value == '1':
        qc.x(0) # initial value: q0 = |1>

    qc.barrier()

    # 2. Steane code encoding circuit
    qc.h(0)
    qc.h(1)
    qc.h(2)
    
    qc.cx(0, 3)
    qc.cx(0, 5)
    qc.cx(0, 6)
    
    qc.cx(1, 3)
    qc.cx(1, 4)
    qc.cx(1, 6)
    
    qc.cx(2, 4)
    qc.cx(2, 5)
    qc.cx(2, 6)
    
    qc.h(3)
    qc.h(5)
    qc.h(6)
    
    qc.barrier()

    return qc