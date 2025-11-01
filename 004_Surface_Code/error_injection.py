from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
import sys

# single data qubit error 'or' single measurement error
# error injection only round_idx=0

# e.g., d[5] bit flip at round=0
# round0: c_z[2] = 0 -> 1 (change!)
# round1: c_z[8] = 1 -> 1 (non-change!) [error_remain]
# round2: c_z[14] = 1 -> 1 (non-change!) [error_remain]
# result: c_z[2] single event -> correct only d[5] (apply bit-flip gate)

# e.g., sz[8] measurement error at round=0
# -> After AerSimulator!!!
# round0: sz[2] = 0 -> 1 (change!)
# round1: sz[8] = 1 -> 0 (change!)
# round2: sz[14] = 0 -> 0 (non-change!)
# result: sz[2], sz[8] double event -> no correction. shortest path is time-like measurement error

def error_injection_single_qubit_error_func(qc, flip_index, error_type='X'):
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

def error_injection_single_measurement_error_func(qc, flip_index, error_type='X'):
    sz = next(reg for reg in qc.cregs if reg.name == 'sz')
    sx = next(reg for reg in qc.cregs if reg.name == 'sx')
    if flip_index is None:
        return
    
    if error_type == 'X':
        qc.x(sx[flip_index])
    elif error_type == 'Z' or error_type == 'Y'
        qc.x(sz[flip_index])
    else:
        print("Wrong Error Type")
        sys.exit(1)

    return

def error_injection_logical_error_rate_func(qc, flip_index, error_type='X'):
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
