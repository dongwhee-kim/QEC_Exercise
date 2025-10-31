# error_injector.py
from qiskit import QuantumCircuit

def inject_data_qubit_error(qc, error_type, qubit_index):
    """
    Injects a data qubit error at the very beginning (Round 0)
    of the circuit for testing.
    
    Args:
        qc (QuantumCircuit): The full circuit.
        error_type (str): 'X', 'Z', or 'Y'.
        qubit_index (int): Index of the data qubit to apply the error to.
    """
    
    # We create a new circuit for the error and compose it
    # to ensure it's at the beginning.
    error_qc = QuantumCircuit(qc.qregs[0], qc.qregs[1], qc.qregs[2]) # Assumes data, cx, cz order

    if error_type == 'X':
        error_qc.x(qubit_index)
    elif error_type == 'Z':
        error_qc.z(qubit_index)
    elif error_type == 'Y':
        error_qc.y(qubit_index)
    error_qc.barrier()
    
    print(f"Injecting {error_type} error on data qubit {qubit_index} at round 0.")

    # Compose the error circuit before the main circuit
    # Note: Qubits must be in the same order
    full_circuit = error_qc.compose(qc, qubits=range(qc.num_qubits), front=True)

    return full_circuit
