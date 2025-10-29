from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit.circuit import Gate
import sys

def error_correction_func(qc):
    """
    Applies correction operations (X, Z) based on the measured syndrome bits
    c[0]...c[5], using classically controlled gates (if_test).
    
    Syndrome-to-Error-Location Mapping:
    
    Z-Error Syndrome (c[2]c[1]c[0]):
    001 (1) -> Z error on q[0]
    010 (2) -> Z error on q[1]
    100 (4) -> Z error on q[2]
    011 (3) -> Z error on q[3]
    110 (6) -> Z error on q[4]
    101 (5) -> Z error on q[5]
    111 (7) -> Z error on q[6]
    
    X-Error Syndrome (c[5]c[4]c[3]):
    001 (1) -> X error on q[0]
    010 (2) -> X error on q[1]
    100 (4) -> X error on q[2]
    011 (3) -> X error on q[3]
    110 (6) -> X error on q[4]
    101 (5) -> X error on q[5]
    111 (7) -> X error on q[6]
    
    A Y error (Y = iXZ) will trigger both syndromes simultaneously,
    and both an X and Z gate will be correctly applied.
    """
    
    # Get the 7-bit classical register
    c_reg = qc.cregs[0]

    # --- Z-Error Correction (based on c[0], c[1], c[2]) ---
    # Syndrome (c[2], c[1], c[0])
    
    # Case 001 (1) -> Z(0)
    with qc.if_test((c_reg[2], 0)) as else_0:
        with qc.if_test((c_reg[1], 0)) as else_1:
            with qc.if_test((c_reg[0], 1)):
                qc.z(0)
    
    # Case 010 (2) -> Z(1)
    with qc.if_test((c_reg[2], 0)) as else_2:
        with qc.if_test((c_reg[1], 1)) as else_3:
            with qc.if_test((c_reg[0], 0)):
                qc.z(1)

    # Case 100 (4) -> Z(2)
    with qc.if_test((c_reg[2], 1)) as else_4:
        with qc.if_test((c_reg[1], 0)) as else_5:
            with qc.if_test((c_reg[0], 0)):
                qc.z(2)

    # Case 011 (3) -> Z(3)
    with qc.if_test((c_reg[2], 0)) as else_6:
        with qc.if_test((c_reg[1], 1)) as else_7:
            with qc.if_test((c_reg[0], 1)):
                qc.z(3)

    # Case 110 (6) -> Z(4)
    with qc.if_test((c_reg[2], 1)) as else_8:
        with qc.if_test((c_reg[1], 1)) as else_9:
            with qc.if_test((c_reg[0], 0)):
                qc.z(4)

    # Case 101 (5) -> Z(5)
    with qc.if_test((c_reg[2], 1)) as else_10:
        with qc.if_test((c_reg[1], 0)) as else_11:
            with qc.if_test((c_reg[0], 1)):
                qc.z(5)

    # Case 111 (7) -> Z(6)
    with qc.if_test((c_reg[2], 1)) as else_12:
        with qc.if_test((c_reg[1], 1)) as else_13:
            with qc.if_test((c_reg[0], 1)):
                qc.z(6)


    # --- X-Error Correction (based on c[3], c[4], c[5]) ---
    # Syndrome (c[5], c[4], c[3])
    
    # Case 001 (1) -> X(0)
    with qc.if_test((c_reg[5], 0)) as else_14:
        with qc.if_test((c_reg[4], 0)) as else_15:
            with qc.if_test((c_reg[3], 1)):
                qc.x(0)
    
    # Case 010 (2) -> X(1)
    with qc.if_test((c_reg[5], 0)) as else_16:
        with qc.if_test((c_reg[4], 1)) as else_17:
            with qc.if_test((c_reg[3], 0)):
                qc.x(1)

    # Case 100 (4) -> X(2)
    with qc.if_test((c_reg[5], 1)) as else_18:
        with qc.if_test((c_reg[4], 0)) as else_19:
            with qc.if_test((c_reg[3], 0)):
                qc.x(2)

    # Case 011 (3) -> X(3)
    with qc.if_test((c_reg[5], 0)) as else_20:
        with qc.if_test((c_reg[4], 1)) as else_21:
            with qc.if_test((c_reg[3], 1)):
                qc.x(3)

    # Case 110 (6) -> X(4)
    with qc.if_test((c_reg[5], 1)) as else_22:
        with qc.if_test((c_reg[4], 1)) as else_23:
            with qc.if_test((c_reg[3], 0)):
                qc.x(4)

    # Case 101 (5) -> X(5)
    with qc.if_test((c_reg[5], 1)) as else_24:
        with qc.if_test((c_reg[4], 0)) as else_25:
            with qc.if_test((c_reg[3], 1)):
                qc.x(5)

    # Case 111 (7) -> X(6)
    with qc.if_test((c_reg[5], 1)) as else_26:
        with qc.if_test((c_reg[4], 1)) as else_27:
            with qc.if_test((c_reg[3], 1)):
                qc.x(6)
    
    return