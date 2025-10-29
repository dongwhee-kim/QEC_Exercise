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
    qc.h(4)
    qc.h(5)
    qc.h(6)
    
    qc.cx(0, 1)
    qc.cx(0, 2)
    
    qc.cx(6, 0)
    qc.cx(6, 1)
    qc.cx(6, 3)
    
    qc.cx(5, 0)
    qc.cx(5, 2)
    qc.cx(5, 3)
    
    qc.cx(4,1)
    qc.cx(4,2)
    qc.cx(4,3)
    
    qc.barrier()

    return qc