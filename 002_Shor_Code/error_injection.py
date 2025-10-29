from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
import sys

# Injects an error into one of the 9 data qubits (0-8) of the Shor code
def error_injection_func(qc, flip_index, error_type='X'):
    if flip_index is None:
        return
    
    if error_type == 'X':
        qc.x(flip_index)
    elif error_type == 'Z':
        qc.z(flip_index)
    elif error_type == 'Y':
        qc.x(flip_index)
        qc.z(flip_index)
    else:
        print("Wrong Error Type")
        sys.exit(1)

    return