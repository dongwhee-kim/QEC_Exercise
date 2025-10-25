from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from collections import Counter
from qiskit.circuit import Gate
import sys

# error_type='X' -> inject single X error (bit flip error)
# error_type='Z' -> inject single Z error (phase flip error)
def error_injection_func(qc, flip_index, error_type='X'):
    
    # No Error
    if flip_index==None:
        return
    
    # Error Injection
    if error_type=='X':
        qc.x(flip_index)
    elif error_type=='Z':
        qc.z(flip_index)
    else:
        print("Wrong Error Type")
        sys.exit(1)

    return