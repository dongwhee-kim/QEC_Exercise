# Stim - Inspection Surface Code Structure

This project generates and inspects the structure of an ideal (noise-free) rotated surface code circuit using Google's Stim library.

# Contents [ideal_surface_code.stim]

The generated `.stim` file contains the full definition of a quantum error correction circuit. Its key components include:

- **QUBIT_COORDS**: Defines the 2D layout coordinates for each physical qubit, used for visualization.
- **R / RX (Reset)**: Initializes qubits into a specific state ($|0\rangle$ or $|+\rangle$).
- **TICK**: Represents a time step barrier. Operations between two TICKs are executed in parallel.
- **H / CX (Gates)**: Clifford gates (Hadamard and CNOT) used for syndrome extraction cycles.
- **M (Measure)**: Physical measurement of qubits at the end of a round or for syndrome extraction.
- **DETECTOR**: Defines XOR parity constraints for measurements. If a constraint is violated, it triggers a **Detection Event** that decoders use to track down physical errors.
- **OBSERVABLE_INCLUDE**: Defines the logical observable (Logical X) for the memory experiment (**Logical Error or not**).

# Output Files
- **circuit_timeline.png**: A visual gate-level representation showing the chronological **sequence** of quantum operations and measurements.
- **qubit_layout.png**: A 2D spatial map visualizing the grid arrangement and coordinate-based positions of all qubits.

## Qubit Mapping & Identification [ideal_surface_code.stim]
![Qubit_Layout](images/Qubit_Layout.png)

In the `rotated_memory_x` layout, qubits are placed on a 2D grid defined by `QUBIT_COORDS(r, c)`. You can distinguish their roles using the following rules:

### 1. Data Qubits (Data)
- **Coordinates**: Both row(`r`) and column(`c`) are **odd** numbers (e.g., `(1,1)`, `(3,1)`, `(5,1)`).
- **Role**: Store the physical qubit information.
- **In .stim file**: Initialized using `RX` (for X-basis memory) and are the targets of multiple CNOT gates.
- **Index**: 1, 3, 5, 8, 10, 12, 15, 17, 19

### 2. Ancilla Qubits (Measurement)
These are located between data qubits and are used to detect errors (Measurement errors can happen).
- **Coordinates**: Located at **even** coordinates (e.g., `(2,2)`, `(2,0)`).
- **How to distinguish X vs Z**:
    - **X-Stabilizers**: Identified by the `H` (Hadamard) gate applied to them before and after the interaction with data qubits. In this file, they follow the rule: `(r + c) / 2` is **Odd** (e.g., `(2,0)`, `(4,2)`, `(2,4)`).
        - **Index**: 2, 11, 16, 25
    - **Z-Stabilizers**: These interact with data qubits via CNOTs without Hadamard gates. They follow the rule: `(r + c) / 2` is **Even** (e.g., `(2,2)`, `(6,2)`, `(0,4)`).
        - **Index**: 9, 13, 14, 18

### 3. Interaction Sequence (4 CNOTs) in Syndrome Extraction - Based on data qubit location
The directions in the 2nd and 3rd CX steps are reversed
 - **Why?** To ensure mathematical commutativity between X and Z measurements and to suppress **Hook errors**, preventing single-qubit flips from propagating into fatal logical error chains.

| Step | Z-Stabilizer Position | X-Stabilizer Position |
| :---: | :--- | :--- |
| **1st CX** | **Top-Left** (TL) | **Top-Left** (TL) <br> *(e.g., `CX 2 3`, `CX 16 17`, `CX 11 12`)* |
| **2nd CX** | **Top-Right** (TR) | **Bottom-Left** (BL) |
| **3rd CX** | **Bottom-Left** (BL) | **Top-Right** (TR) |
| **4th CX** | **Bottom-Right** (BR) | **Bottom-Right** (BR) |

### 4. Detector
| Stage | Stim Logic (XOR Sum) | Purpose |
| :--- | :--- | :--- |
| **1. Initial** | $rec[-n] = 0$ | **Initialization Check**: Verifies X-stabilizers return 0 after $|+\rangle$ setup. |
| **2. Repeat** | $rec[-n] \oplus rec[-m] = 0$ | **Stability Check**: Compares the current syndrome to the previous round. |
| **3. Final** | $Data \oplus Ancilla = 0$ | **Readout Check**: Matches final data parity against the last syndrome. |
| **4. Logical** | `OBSERVABLE_INCLUDE` | **Success Criterion**: Final parity of the **Logical X** operator. |

# Getting Started
- $ python Stim_Structure.py
- $ python Stim_Visualize.py