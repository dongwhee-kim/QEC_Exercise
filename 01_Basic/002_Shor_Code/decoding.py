from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
import sys

# Inverse of the encoding function
def decoding_func(qc): 
    # 1. Inner code decoding (Phase-flip decoding)
    # Decode |+++> -> |+> and |---> -> |->
    
    ######################################
    ######################################


    ############# Fill the code ##########


    ######################################
    ######################################

    # 2. Outer code decoding (Bit-flip decoding)
    # Decode a|000> + b|111> -> a|0> + b|1> (on q0, q3, q6)
    
    ######################################
    ######################################


    ############# Fill the code ##########


    ######################################
    ######################################
    
    # Final logical state is restored to q0