from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit.circuit import Gate
import sys

# Applies correction operations (X, Z) based on the measured syndrome bits
def error_correction_func(qc):
    # Get the 7-bit classical register
    c_reg = qc.cregs[0]

    # --- X-Error Correction ---

    # syndrome table
    # c0 c1 c2
    # 000 -> no bit-flip error
    # 100 -> q0 flip
    # 010 -> q1 flip
    # 110 -> q2 flip
    # 001 -> q3 flip
    # 101 -> q4 flip
    # 011 -> q5 flip
    # 111 -> q6 flip

    # 100
    with qc.if_test((c_reg[0], 1)) as else_0:
        with qc.if_test((c_reg[1], 0)) as else_1:
            with qc.if_test((c_reg[2], 0)):
                qc.x(0)
    
    # 010
    with qc.if_test((c_reg[0], 0)) as else_2:
        with qc.if_test((c_reg[1], 1)) as else_3:
            with qc.if_test((c_reg[2], 0)):
                qc.x(1)

    # 110
    with qc.if_test((c_reg[0], 1)) as else_4:
        with qc.if_test((c_reg[1], 1)) as else_5:
            with qc.if_test((c_reg[2], 0)):
                qc.x(2)

    # 001
    with qc.if_test((c_reg[0], 0)) as else_6:
        with qc.if_test((c_reg[1], 0)) as else_7:
            with qc.if_test((c_reg[2], 1)):
                qc.x(3)

    # 101
    with qc.if_test((c_reg[0], 1)) as else_8:
        with qc.if_test((c_reg[1], 0)) as else_9:
            with qc.if_test((c_reg[2], 1)):
                qc.x(4)

    # 011
    with qc.if_test((c_reg[0], 0)) as else_10:
        with qc.if_test((c_reg[1], 1)) as else_11:
            with qc.if_test((c_reg[2], 1)):
                qc.x(5)

    # 111
    with qc.if_test((c_reg[0], 1)) as else_12:
        with qc.if_test((c_reg[1], 1)) as else_13:
            with qc.if_test((c_reg[2], 1)):
                qc.x(6)

    # --- Z-Error Correction ---
    
    # syndrome table
    # c3 c4 c5
    # 000 -> no phase-flip error
    # 100 -> q0 flip
    # 010 -> q1 flip
    # 110 -> q2 flip
    # 001 -> q3 flip
    # 101 -> q4 flip
    # 011 -> q5 flip
    # 111 -> q6 flip

    # 100
    with qc.if_test((c_reg[3], 1)) as else_14:
        with qc.if_test((c_reg[4], 0)) as else_15:
            with qc.if_test((c_reg[4], 0)):
                qc.z(0)
    
    # 010
    with qc.if_test((c_reg[3], 0)) as else_16:
        with qc.if_test((c_reg[4], 1)) as else_17:
            with qc.if_test((c_reg[5], 0)):
                qc.z(1)

    # 110
    with qc.if_test((c_reg[3], 1)) as else_18:
        with qc.if_test((c_reg[4], 1)) as else_19:
            with qc.if_test((c_reg[5], 0)):
                qc.z(2)

    # 001
    with qc.if_test((c_reg[3], 0)) as else_20:
        with qc.if_test((c_reg[4], 0)) as else_21:
            with qc.if_test((c_reg[5], 1)):
                qc.z(3)

    # 101
    with qc.if_test((c_reg[3], 1)) as else_22:
        with qc.if_test((c_reg[4], 0)) as else_23:
            with qc.if_test((c_reg[5], 1)):
                qc.z(4)

    # 011
    with qc.if_test((c_reg[3], 0)) as else_24:
        with qc.if_test((c_reg[4], 1)) as else_25:
            with qc.if_test((c_reg[5], 1)):
                qc.z(5)

    # 111
    with qc.if_test((c_reg[3], 1)) as else_26:
        with qc.if_test((c_reg[4], 1)) as else_27:
            with qc.if_test((c_reg[5], 1)):
                qc.z(6)
    
    return