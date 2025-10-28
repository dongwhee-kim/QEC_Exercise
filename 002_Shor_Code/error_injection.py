from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
import sys

def error_injection_func(qc, flip_index, error_type='X'):
    """
    Injects an error into one of the 9 data qubits (0-8) of the Shor code
    """
    
    # No Error
    if flip_index is None:
        return
    
    # Check if flip_index is within the 0-8 range
    if not (0 <= flip_index <= 8):
        print(f"Error: flip_index {flip_index} is out of range (0-8).")
        sys.exit(1)
        
    # Error Injection
    if error_type == 'X':
        qc.x(flip_index)
    elif error_type == 'Z':
        qc.z(flip_index)
    elif error_type == 'Y':
        qc.y(flip_index) # Y = XZ
    else:
        print("Wrong Error Type")
        sys.exit(1)

    return

