# Lattice Surgery

![Introducing Lattice Surgery](https://pennylane.ai/demos/tutorial_lattice_surgery)

# Issues of Quantum Computing
- Scalability
- Fast Decoding
- Syndrome Extraction Fidelity
- Low Non-clifford operation overhead (Magic State Distillation is essential!!)

# Pauli-Based Computation (PBC)
- A framework to facilitate the mapping of quantum programs to surface codes.
-

1) Pauli Product Measurements (PPM)
- 


![A Game of Surface Codes](https://pennylane.ai/demos/tutorial_game_of_surface_codes)
- Paper **[1]**

## Terms

**Measurement**
- Readout information from a quantum state causes the superposition state to collapse/project to one of its basis states randomly.
    - Measurement along **x basis (Hadamard basis)**: |+>, |->
    - Measurement along **z basis (Standard basis 'or' Computational basis)**: |0>, |1>

**Joint Measurement [2]**
- Measures shared information of multiple entangled qubits at once without revealing their individual states, preserving delicate quantum information.
- **Bell State Measurement (BSM)**: One of the most representative examples. It identifies which of the four perfect entangled states two qubits share, acting as the core engine for quantum teleportation.
- **Syndrome Extraction**: A process in superconducting systems -> Quantum Error Correction (QEC) relies on parity qubits to periodically extract information from data qubits via Z- or X-type stabilizer circuits (Surface Code has **degree-4**, four data qubits mapped to one parity qubit).
  - **What you do**: Perform standard single-qubit measurements on many individual ancilla (parity) qubits simultaneously.
  - **What it means**: Because each ancilla is entangled with its neighboring data qubits via stabilizer circuits (e.g., degree-4 in surface codes), these parallel single measurements effectively execute numerous **joint measurements** on the data qubits at once.
- **Examples:**
  - Performing a BSM on two qubits to read out their shared quantum correlation rather than their individual 0 or 1 values.
  - Measuring $Z \otimes Z \otimes Z \otimes Z$ parity in a surface code to detect if an error occurred, without ever asking if the individual qubits are $|0\rangle$ or $|1\rangle$.

**Codespace**
- A strictly defined "safe zone" (mathematical subspace) where valid, error-free quantum information is allowed to exist.
- Forces the system to only accept specific states, making errors stand out.
- **E.g.,** In a 2-qubit system, artificially restricting the valid states to only even parity ($a|00\rangle + b|11\rangle$) and treating odd parity ($|01\rangle, |10\rangle$) as errors.

**Encoding**
- The process of mapping fragile quantum information into the protected **Codespace**.
- Achieved by entangling multiple physical qubits together to form a single logical unit.
- If a physical error occurs, the state is kicked *out* of the codespace, triggering detection.
- **E.g.,** Translating a single logical $|0\rangle_L$ into a complex, entangled grid of many physical qubits on a surface code patch.

**Pauli Product Measurements (PPM)**
- A macroscopic **Joint Measurement** that checks the parity of a multi-qubit Pauli operator (e.g., $X \otimes Z \otimes Y$) across several logical qubits.
- A **physically executable** operation.
- The **only physical operation** that can be executed directly and fault-tolerantly on surface code hardware.

**Pauli Product Rotations (PPR)**
- A quantum rotation that uses a Pauli operator as its axis to rotate qubits by a specific angle.
- **Clifford PPRs** (e.g., $\pi/4$ rotations) can be easily handled by classical bookkeeping without physical hardware operations.
- **Non-Clifford PPRs** (e.g., $\pi/8$ rotations) are physically impossible to execute directly on surface code hardware. 
- e.g., **T gate** (a representative non-Clifford operation).
- **Non-Clifford PPR = PPM + Magic State** (Figure 7 of **[4]**).
- So, if **magic states are available**, the only operations required for universal quantum computing are **Pauli product measurements**.

**Magic State [3]**
- **Definition:** A specially prepared, pure quantum state (resource) injected from outside the system to achieve Universal Quantum Computation (UQC).
    - Typical examples include T-type and H-type magic states.
- **Why 'Magic'?**: They enable the execution of complex non-Clifford gates by using only simple Clifford gates and measurements. 
- They are precisely set at a specific angle.
    - e.g., $\pi/8$ rotated Pauli eigenstates $$|m\rangle = |0\rangle + e^{i\pi/4}|1\rangle$$
    - Normalized format: $$|m\rangle = \frac{1}{\sqrt{2}} \left( |0\rangle + e^{i\pi/4}|1\rangle \right)$$
- **Purpose:** To bypass the physical limitations of surface codes. They are absolutely essential for **universal quantum computation**!

**Magic State Distillation [4]**
- **Definition:** A protocol that takes multiple noisy, imperfect magic states and **purifies** them into a few **high-fidelity magic states**, using only fault-tolerant basic operations (Clifford gates and measurements).
- **Why is it needed?**: Due to realistic physical limitations, magic states prepared in external "factories" inevitably contain impurities/errors ($\rho$). Using these noisy states directly would ruin the computation.
- **The Threshold Rule (Crucial):** Distillation only works if the initial magic state's fidelity is above a certain threshold (e.g., > 91% for T-type). If the initial state is too noisy, the distillation fails and ruins the state completely.
- **How it works:** 
  1. Gather multiple imperfect magic states (e.g., 5 states for T-type, or 15 states for H-type distillation codes).
  2. Check for errors using reliable hardware operations (syndrome measurements).
  3. Discard the states entirely if any error signs are detected; keep only the ones that successfully pass the check.
  4. The surviving states are entangled to produce a single, higher-purity magic state with significantly reduced noise.
  5. Repeat this process (recursive iteration) to obtain magic states of the desired absolute purity.

**Non-clifford opearation**
- **Gottesman-Knill theorem**
    - All the gates (X, Y, Z, H, S, CNOT ...) are members of a special gorup of gates known as the Clifford group.
    - These gates can be simulated efficiently on a classical computer.
    - So, **the Clifford group is not universal on its own.**
- e.g., (T Gate, Toffoli gate, )
    - **T Gate**: A single-qubit gate that applies a **$\pi$/4 phase rotation ($\pi/8$ physical rotation)**. It **breaks the symmetry of the Clifford group** (does not map Puali operators back to Pauli operators) and enables **universal quantum computation** by allowing circuits to reach arbitrary states on the Bloch sphere.
    - **Why is a $\pi/4$ rotation called a $\pi/8$ gate?**
    - $$|\psi\rangle = \cos\left(\frac{\theta}{2}\right)|0\rangle + e^{i\phi}\sin\left(\frac{\theta}{2}\right)|1\rangle$$
    - **Actual Rotation ($\pi/4$)**: In the standard qubit state equation $|\psi\rangle = \cos\left(\frac{\theta}{2}\right)|0\rangle + e^{i\phi}\sin\left(\frac{\theta}{2}\right)|1\rangle$, the phase $\phi$ physically rotates by exactly **$\pi/4$ (45 degrees)**.
    - **Mathematical Expression ($\pi/8$)**: The standard formula for a Z-axis rotation matrix incorporates a half-angle ($\alpha/2$) in its exponents. When we plug in our actual rotation angle $\alpha = \pi/4$, the fraction **$\pi/8$** appears in the matrix elements, which is why it is conventionally called the $\pi/8$ gate.
        ```math
          R_z\left(\frac{\pi}{4}\right) = \begin{pmatrix} e^{-i\frac{\pi}{8}} & 0 \\ 0 & e^{i\frac{\pi}{8}} \end{pmatrix}
        ```

### Comparison Table: Clifford vs. Non-Clifford Gates

| Feature | Clifford Gates | Non-Clifford Gates (e.g., T, Toffoli) |
| --- | --- | --- |
| **Classical Simulation** | Efficient (Polynomial time) | Inefficient (Exponential time) |
| **Mathematical Role** | Maps Pauli to Pauli | "Escapes" the Pauli group |
| **Common Examples** | H, S, CNOT, Pauli X, Y, Z | T, Toffoli (CCNOT) |
| **Error Correction** | Easy to implement via stabilizer codes | Difficult; requires magic state distillation |
| **Universality** | Not universal on their own | Required for a universal gate set |

## References
**[1]** Litinski, Daniel. "A game of surface codes: Large-scale quantum computing with lattice surgery." Quantum 3 (2019): 128.

**[2]** Ding, Y. (2025). Lecture 6: Quantum Measurements [Lecture notes, CPSC 4470/5470]. Department of Computer Science, Yale University. https://www.yongshanding.com/cpsc447-f25/Lec6-f25.pdf

**[3]** Bravyi, Sergey, and Alexei Kitaev. "Universal quantum computation with ideal Clifford gates and noisy ancillas." Physical Review A—Atomic, Molecular, and Optical Physics 71.2 (2005): 022316.

**[4]** Litinski, Daniel. "A game of surface codes: Large-scale quantum computing with lattice surgery." Quantum 3 (2019): 128.