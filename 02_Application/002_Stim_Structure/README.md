# Stim - Inspection Surface Code Structure

This project generates and inspects the structure of an ideal (noise-free) rotated surface code circuit using Google's Stim library.

## 🔍 Qubit Mapping & Identification [ideal_surface_code.stim]

In the `rotated_memory_x` layout, qubits are placed on a 2D grid defined by `QUBIT_COORDS(r, c)`. You can distinguish their roles using the following rules:

### 1. Data Qubits (Data)
- **Coordinates**: Both row(`r`) and column(`c`) are **odd** numbers (e.g., `(1,1)`, `(3,1)`, `(5,1)`).
- **Role**: Store the logical quantum information.
- **In .stim file**: Initialized using `RX` (for X-basis memory) and are the targets of multiple CNOT gates.

### 2. Ancilla Qubits (Measurement)
These are located between data qubits and are used to detect errors without collapsing the data state.
- **Coordinates**: Located at **even** coordinates (e.g., `(2,2)`, `(2,0)`).
- **How to distinguish X vs Z**:
    - **X-Stabilizers**: Identified by the `H` (Hadamard) gate applied to them before and after the interaction with data qubits. In this file, they follow the rule: `(r + c) / 2` is **Odd** (e.g., `(2,0)`, `(4,2)`, `(2,4)`).
    - **Z-Stabilizers**: These interact with data qubits via CNOTs without Hadamard gates. They follow the rule: `(r + c) / 2` is **Even** (e.g., `(2,2)`, `(6,2)`, `(0,4)`).

# Contents [ideal_surface_code.stim]

The generated `.stim` file contains the full definition of a quantum error correction circuit. Its key components include:

- **QUBIT_COORDS**: Defines the 2D layout coordinates for each physical qubit, used for visualization.
- **R / RX (Reset)**: Initializes qubits into a specific state ($|0\rangle$ or $|+\rangle$).
- **TICK**: Represents a time step barrier. Operations between two TICKs are executed in parallel.
- **H / CX (Gates)**: Clifford gates (Hadamard and CNOT) used for syndrome extraction cycles.
- **M (Measure)**: Physical measurement of qubits at the end of a round or for syndrome extraction.
- **DETECTOR**: Defines parity constraints between measurement outcomes. In an ideal circuit, these help verify the stabilizer structure.
- **OBSERVABLE_INCLUDE**: Defines the logical observable (Logical X) for the memory experiment.

# Getting Started
- $ python Stim_Structure.py
- $ python Stim_Visualize.py