# Background
- QEC Cycle / Round
- Syndrome Vector
- Logical Error
- Error Chain
- Pauli Tracking (referred to as working in the Pauli frame)
- 1us = Readout & State Discrimination (FPGA, 300ns~500ns) + Syndrome Transmission (tens of ns) + Decoding (e.g., MWPM, Union-Find) 200ns~400ns + Feedback Transmission (2bits (X,Z,Y) per a data qubit) + Frame Update (FPGA)

# Background: Real-Time Quantum Error Correction
This document outlines the fundamental architecture and timing constraints of real-time Quantum Error Correction (QEC), specifically focusing on Surface Codes implemented on superconducting qubit systems.

# 1. The 1µs Real-Time Decoding Cycle

Concept: In superconducting quantum systems, the syndrome extraction circuit typically has a latency of approximately 1µs (1000ns) [1, 2]. To prevent error accumulation (backlog), the entire decoding loop—from signal readout to frame update—must be completed within this strict deadline [2].

Timing Breakdown: A typical 1µs cycle consists of the following mandatory stages:
- 1) Readout & State Discrimination (300ns – 500ns): The FPGA (control hardware) converts analog microwave signals from the QPU into digital syndrome bits (0 or 1) [3].
- 2) Syndrome Transmission (tens of ns): The raw syndrome data is transmitted from the FPGA to the Decoder unit. Bandwidth must be sufficient to prevent transmission latency from eating into the decoding budget [2].
- Decoding (200ns – 400ns): Algorithms (e.g., MWPM, Union-Find) calculate the most likely error configuration based on the provided syndromes [1, 2].
- Feedback Transmission: The decoder sends correction information (typically 2 bits per data qubit indicating X/Z errors) back to the FPGA [5].
- Frame Update (Pauli Frame): The FPGA updates its internal error registers (Pauli Frame) using the received correction data [5, 6, 7].

**Description: A horizontal bar chart visualizing the 1000ns budget distribution: [Readout] -> [Tx] -> [Decoding] -> [Feedback] -> [Frame Update].**

# 2. Syndrome Vectors & Processing

Concept: Instead of processing a single round in isolation, decoders typically aggregate syndromes over $d$ rounds (where $d$ is the code distance) to construct a Spacetime Syndrome Graph. This vector contains both spatial (data qubit) and temporal (measurement) error information [2, 4].
- Syndrome Vector: A concatenated bitstring of syndromes collected over $d$ cycles.
- Batch Processing: The decoder processes this vector to match error chains that span across space and time.
**Note on Specific Implementations:**
 - 1) Astrea: Defines the "Syndrome Vector" explicitly and exploits its low Hamming weight for fast lookup [2].
 - 2) LILLIPUT: Uses a sliding window approach to process multiple rounds continuously [1].


# 3. Logical Errors & Error Chains

Error Chain: Physical errors on qubits form "chains" in the surface code lattice. A code of distance $d$ can correct chains of length up to $\lfloor (d-1)/2 \rfloor$ [2].

Logical Error: A logical error occurs when a chain of errors physically connects one boundary of the lattice to the opposite boundary (e.g., Top-to-Bottom for Z operators).

- Criterion: If the final logical readout differs from the initialized state (e.g., $|0\rangle_L \rightarrow |1\rangle_L$) after correction, a logical error has occurred [2, 4].
- Isolated Errors: Remaining physical errors that do not form a connecting chain are not considered logical errors as they do not flip the logical information.

**Description: A d=5 grid showing (A) a short, corrected chain and (B) a long chain connecting boundaries (Logical Failure).** 


# 4. Pauli Tracking (Virtual Correction)

Concept: Modern QEC systems do not physically correct data qubits during the cycle due to latency and noise concerns. Instead, they employ Pauli Tracking (also known as working in the Pauli Frame) [5, 6].

Mechanism:
- 1) No Physical Gates: The FPGA receives correction data but does not apply X or Z gates to the qubits.
- 2) Classical Record: The FPGA maintains a "Pauli Frame" register that tracks the cumulative error state of each data qubit.
- 3) Future Operations Update:
 - Gate Operations: When executing a new gate (e.g., Hadamard), the control processor modifies the instruction based on the tracked error (e.g., $Z \to X$) [2, 6].
 - Measurement: The final measurement result is flipped in software if the frame indicates an error.

**Description: Flowchart: [Decoder Output] -> [FPGA Register Update] -> [Next Gate Instruction Modified].**

# 5. Logical Measurement & Verification

Concept: To determine the final state of a logical qubit (e.g., at Round 5 for $d=5$), the system must perform a Transversal Measurement of all data qubits and apply the cumulative correction from all previous rounds [1, 4].

Calculation Formula: $$M_{final} = M_{raw} \oplus C_{accumulated}$$
- $M_{raw}$: The parity calculated from the raw measurement of the logical operator chain (e.g., measuring data qubits along a column).
- $C_{accumulated}$: The total error parity accumulated in the Pauli Frame from Round 1 to Round $d$.
- $\oplus$: XOR operation (Modulo 2 addition).


# References
**[1]** Das, Poulami, Aditya Locharla, and Cody Jones. "Lilliput: a lightweight low-latency lookup-table decoder for near-term quantum error correction." Proceedings of the 27th ACM International Conference on Architectural Support for Programming Languages and Operating Systems. 2022.

**[2]** Vittal, Suhas, Poulami Das, and Moinuddin Qureshi. "Astrea: Accurate quantum error-decoding via practical minimum-weight perfect-matching." Proceedings of the 50th Annual International Symposium on Computer Architecture. 2023.

**[3]** Ryan-Anderson, Ciaran, et al. "Realization of real-time fault-tolerant quantum error correction." Physical Review X 11.4 (2021): 041058.

**[4]** "Suppressing quantum errors by scaling a surface code logical qubit." Nature 614, no. 7949 (2023): 676-681.

**[5]** Paler, Alexandru, et al. "Software-based pauli tracking in fault-tolerant quantum circuits." 2014 Design, Automation & Test in Europe Conference & Exhibition (DATE). IEEE, 2014.

**[6]** Chamberland, Christopher, Pavithran Iyer, and David Poulin. "Fault-tolerant quantum computing in the Pauli or Clifford frame with slow error diagnostics." Quantum 2 (2018): 43.

**[7]** Knill, Emanuel. "Quantum computing with realistically noisy devices." Nature 434.7029 (2005): 39-44.
