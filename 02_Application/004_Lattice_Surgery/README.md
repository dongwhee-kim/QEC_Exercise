# Lattice Surgery

[Introducing Lattice Surgery](https://pennylane.ai/demos/tutorial_lattice_surgery)

# Issues of Quantum Computing
- Scalability
- Fast Decoding
- Syndrome Extraction Fidelity
- Low Non-clifford operation overhead (Magic State Distillation is essential!!)

# Pauli-Based Computation (PBC)
- A framework to facilitate the mapping of quantum programs to surface codes.
- Conversion (Final Result): Quantum program (including **non-clifford gates**) -> Sequence consisting of **only pauli product measurements (PPMs) [1]**
- **Conclusion: PPMs are sufficient for universal computing**
- The Compilation Process
<img src="https://blog-assets.cloud.pennylane.ai/compilations/pauli-based-computation/overview.png?w=828" alt="Logical_X_Z_Operator_Merging" width="50%">

    - 🟧 **Clifford operators (angles $\pm\pi/4$)**: All such operators can be commuted to the right of the circuit and merged with PPMs. **Do not need to be executed on Hardware**.
    - 🟨 **T-gates / Non-Clifford operators (angles $\pm\pi/8$)**: All such operators can be realized with a magic state injection, leaving only classically controlled Clifford and Pauli operators that can be merged into PPMs again.
    - 🟦 **Blue boxes:** Terminal measurements at the very end of the circuit.
    - 1) **Input: Circuit (Clifford + T)** -> Any circuit can always be approximated to arbitrary precision with the (Clifford + T) gate set.
    - 2) **Intermediate representation** -> Quantum circuits are represented by a small set of building blocks, namely Pauli product measurements (PPMs) $\langle P \rangle$ and Pauli product rotations (PPRs) $e^{-i\phi P}$. The angle $\phi$ dictates how they are processed:
        - **Step 1: Decomposition**: The original (Clifford + T) gates are uniformly decomposed into a mixed sequence of Clifford (🟧) and non-Clifford (🟨) operations
        - **Step 2: Commutation**: All tractable Clifford operations (🟧) are **commuted** (**pushed**) to the far right of the circuit, mathematically updating the Pauli axes of the remaining non-Clifford operations (🟨) as they pass through.
        - **Step 3: Absorption**: The clustered Clifford operations (🟧) physically disappear from the circuit as they are absorbed into the terminal measurements (🟦).
        - **Step 4: Magic State Injection**: The remaining non-Clifford operations (🟨) are replaced by **magic state injections**.
    - 3) **Final Result (Output):** All non-Clifford PPRs are completely transformed, leaving the entire circuit as a sequence consisting of **only Pauli Product Measurements (PPMs)**.
- **Magic state injection is essential**! Injection of magic states from auxiliary qubits is neede! **Otherwise, we obtain a circuit containing PPMs + non-clifford PPRs**.

> 🔲 **Pauli ($\pi/2$)**: **Do not need to be executed on Hardware**. Tracking **sign ($\pm$) flips** $\rightarrow$ Hardware measures in the **original basis**
> 🆚 
> 🟧 **Clifford ($\pi/4$)**: **Do not need to be executed on Hardware**. Tracking **basis change** $\rightarrow$ Hardware measures in the **rotated basis**

![Non_Clifford_Conversion_Clifford_Magic_State](images/Non_Clifford_Conversion_Clifford_Magic_State.png)
- Non-Clifford PPRs = Magic State + PPMs (Figure 7 of **[1]**)
- Magic State $$|m\rangle = \frac{1}{\sqrt{2}} \left( |0\rangle + e^{i\pi/4}|1\rangle \right)$$

# Lattice Surgery [6]
- Why is it needed? To execute **transversal operations** on hardware. Because some hardware are constrained by **local physical connectivity** (e.g., superconducting qubits). Operating on distant, non-local logical qubits directly is physically restricted.
    - Previous Approach (Braiding)
        - Encoded logical qubits by creating holes (**defects**) in the surface code and moving them around via **continuous deformation** to perform operations.
        - Issue: Significantly **more physical qubits** are needed per logical qubit.
- Solution: Lattice-Surgery can enable error-corrected logical operations with significantly lower space overhead and comparable time requirements **[1, 6, 7]**.

![Lattice_Surgery_Merge_Split](images/Lattice_Surgery_Merge_Split.png)
- Fundamental operations - **Lattice Merging and Lattice Splitting (Figure 3 of [9])**
- **Key point: By physically merging the boundaries of two logical qubit patches, we can extract the eigenvalue (parity) of their joint Pauli operators.**

## How Can Lattice Surgery Enable Universal Quantum Computing?
- Top-Down Perspective: Any quantum circuit -> Clifford + T (PPRs) circuit -> PPM + Magic State -> **Only PPMs**

## Homological Measurement**: "Measure the String"
<img src="https://blog-assets.cloud.pennylane.ai/demos/tutorial_lattice_surgery/main/_assets/images/logical_X_Z.png?w=828" alt="Logical_X_Z_Operator_Merging" width="50%">

- When measuring a logical qubit, we do not projectively measure every single physical qubit inside the patch.
- The Core Idea: We **only need to find and measure a single 'string' connecting one edge of the patch to the opposite edge**.
- Why homological? Topological Equivalence Class -> The exact path this string takes does not matter. As long as it connects the corresponding boundaries, any path yields the **identical logical information.**
- Yellow: X-stabilizer / White: Z-stabilizer

| Boundary Name | Inherit Stabilizers | Target Logical Operator | Bridge Initialization & Splitting Basis |
| :--- | :--- | :--- | :--- |
| **Z-edge** | X-arches (X-stabilizers) | Logical Z ($Z_L$) | X-basis ($|+\rangle$) |
| **X-edge** | Z-arches (Z-stabilizers) | Logical X ($X_L$) | Z-basis ($|0\rangle$) |

## Example - Measuring XL 'x' XL (Merge & Split two logical qubits on their X edges)
To measure the **$X_L \otimes X_L$** between two logical qubits, we merge and split them along their **X-edges**.

<img src="https://blog-assets.cloud.pennylane.ai/demos/tutorial_lattice_surgery/main/_assets/images/XX1.png?w=828" alt="Logical_X_Z_Operator_Merging" width="50%">

- **Step 1: Preparation (Initialization)**
- Alignment: Align the X-edges of the two patches to face each other, separated by a column of unused intermediate data qubits.
- Initialization: Initialize these intermediate qubits in the $|0\rangle$ (Z-basis) state.
- Why initialize in the **Z-basis ($|0\rangle$)**? When we want to measure X?
    - Preventing Error Explosions: If we initialized $q_i$ in $|+\rangle$, the new ⚪ Z-stabilizers would yield completely random results (since $Z|+\rangle$ is random), crashing the code. Initializing in $|0\rangle$ keeps the Z-stabilizers perfectly quiet ($Z|0\rangle = +1$).
    - The "Blank Slate" for X: To the 🟡 X-stabilizers, $|0\rangle$ is a superposition ($\frac{|+\rangle + |-\rangle}{\sqrt{2}}$). It acts as a transparent medium that absorbs no X-information of its own, allowing the pure X-strings from Patch A and Patch B to connect perfectly across the bridge.

```text
[Patch A (X-edge)]     [Intermediate Data Qubits]    [Patch B (X-edge)]
           (a_i)                        (q_i)                     (b_i)

        a1 ◯ ------------------------ ◯ q1 ------------------------ ◯ b1
           |      🟡 X-Patch (X)      |      ⚪ Z-Patch (Z)       |
        a2 ◯ ------------------------ ◯ q2 ------------------------ ◯ b2
           |      ⚪ Z-Patch (Z)      |      🟡 X-Patch (X)       |
        a3 ◯ ------------------------ ◯ q3 ------------------------ ◯ b3
           |      🟡 X-Patch (X)      |      ⚪ Z-Patch (Z)       |
        a4 ◯ ------------------------ ◯ q4 ------------------------ ◯ b4
           |      ⚪ Z-Patch (Z)      |      🟡 X-Patch (X)       |
        a5 ◯ ------------------------ ◯ q5 ------------------------ ◯ b5
```

<img src="https://blog-assets.cloud.pennylane.ai/demos/tutorial_lattice_surgery/main/_assets/images/XX2.png?w=828" alt="Logical_X_Z_Operator_Merging" width="50%">

- **Step 2: Merging**
- Integration: Include the intermediate data qubits in the standard error correction cycles (measuring the new X and Z stabilizers).
- Extraction: The two patches temporarily become one. The product of the newly formed stabilizers along this boundary (indicated by the red dots) corresponds exactly to the eigenvalue of $X_L \otimes X_L$.

<img src="https://blog-assets.cloud.pennylane.ai/demos/tutorial_lattice_surgery/main/_assets/images/XX3.png?w=828" alt="Logical_X_Z_Operator_Merging" width="50%">

Now that we retrieved our measurement result $X_L \otimes X_L$, we want to restore the two qubits, which is achieved by lattice splitting. This, on the other hand, is done by measuring the intermediate data qubits in the **Z basis**.

<img src="https://blog-assets.cloud.pennylane.ai/demos/tutorial_lattice_surgery/main/_assets/images/XX4.png?w=828" alt="Logical_X_Z_Operator_Merging" width="50%">

- **Step 3: Splitting**
- Restoration: Measure the intermediate data qubits in the Z-basis.
- **Why Z-basis**? Measuring in the Z-basis projectively collapses the qubits back to their initialized state. This physical collapse cleanly "snaps" the connecting X-string without injecting random X-errors into the boundary Z-arches.
- **Correction**: If any Z-measurement yields a negative sign (due to physical errors during the merge), we track it classically and assign it to the logical operator signs to correct the final outcome.

## Y measurements
- Why is **Y measurement difficult**?
    - Logical $Y_L$ requires measuring **$X_L$ and $Z_L$ simultaneously** (**$Y = iXZ$**).
    - However, Pauli operators anti-commute ($XZ = -ZX$).
    - Attempting to apply X and Z measurement bases simultaneously on a standard boundary will break the stabilizer commutation rules, generating a $-1$ phase difference that the system will interpret as a fatal error.
- The Solution: We must topologically warp the patch to bypass this anti-commutation rule.
    - $X$ & $Z$ Measurements: Performed simply by merging identical, matching boundaries (e.g., X-edge to X-edge).
    - $Y$ Measurement (**Twist Defect**)
        - 1. Spatial Deformation: Extend the patch and re-orient its edges so that both X and Z edges co-exist on the same face 🟪.
        - 2. Twist Defect Generation: Merge this deformed patch with an auxiliary qubit. The mismatched boundaries force the creation of a topological Twist Defect.
        - 3. Parity Extraction: Inside this twisted space, the stabilizer operators become mixed (e.g., $Z \otimes X$). Measuring these mixed stabilizers allows us to safely extract the $Y$ eigenvalue.

<img src="https://blog-assets.cloud.pennylane.ai/demos/tutorial_lattice_surgery/main/_assets/images/extend1.png?w=828" alt="Logical_X_Z_Operator_Merging" width="50%">

<img src="https://blog-assets.cloud.pennylane.ai/demos/tutorial_lattice_surgery/main/_assets/images/extend2.png?w=828" alt="Logical_X_Z_Operator_Merging" width="50%">

<img src="https://blog-assets.cloud.pennylane.ai/demos/tutorial_lattice_surgery/main/_assets/images/extend3.png?w=828" alt="Logical_X_Z_Operator_Merging" width="50%">

- **Step 1: Patch Extension (Expanding the Qubit)**
- Concept: Increase the physical footprint of the logical qubit.
- Example (Extending Z-edge): Initialize an adjacent column of unused data qubits in $|0\rangle$ and run $d$ error correction cycles. The logical information now "slides" and encompasses this larger area.

<img src="https://blog-assets.cloud.pennylane.ai/demos/tutorial_lattice_surgery/main/_assets/images/corner_moving.png?w=828" alt="Logical_X_Z_Operator_Merging" width="50%">

- **Step 2: Edge Reorientation (Changing Boundary Types)**
- Concept: Alter the property of the boundary without changing the logical bulk information.
- To measure Y, we need a patch that has both an X-edge and a Z-edge on the same side 🟪. We re-orient a segment of an X-edge into a Z-edge by introducing triangle-shaped stabilizers. This acts as a buffer zone, ensuring the neighboring X and Z edges commute smoothly by overlapping on exactly two data qubits.

<img src="https://blog-assets.cloud.pennylane.ai/demos/tutorial_lattice_surgery/main/_assets/images/y_measurement.png?w=828" alt="Logical_X_Z_Operator_Merging" width="50%">

- **Step 3: Y Measurement via Twist Defects**
- Setup: Create a re-oriented patch containing both X and Z edges on one face 🟪. Initialize an auxiliary qubit in $|0\rangle$ parallel to it.
- Lattice Merging: Merge the two patches. Because we are forcing a boundary mismatch (X-edges meeting Z-edges), the system generates a topological anomaly called a Twist Defect (highlighted in purple).
- Measure ($Y_L$): Inside this twist defect, the spatial geometry is warped, allowing mixed $Z \otimes X$ stabilizers to emerge without breaking commutation rules (e.g., $[ZZ, XY] = 0$). Measuring these mixed stabilizers effectively measures the **simultaneous $XZ$** parity, yielding the exact **$Y_L$ measurement result**.

<img src="https://blog-assets.cloud.pennylane.ai/demos/tutorial_lattice_surgery/main/_assets/images/twist_boundaries.png?w=828" alt="Logical_X_Z_Operator_Merging" width="50%">

## Terms

**Measurement**
- Readout information from a quantum state causes the superposition state to collapse/project to one of its basis states randomly.
    - Measurement along **x basis (Hadamard basis)**: |+>, |->
    - Measurement along **z basis (Standard basis 'or' Computational basis)**: |0>, |1>

**Joint Measurement [2]**
- Measures shared information of multiple entangled qubits at once without revealing their individual states, preserving delicate quantum information.
- **Bell State Measurement (BSM)**: One of the most representative examples. It identifies which of the four perfect entangled states two qubits share, acting as the core engine for quantum teleportation.
    - All quantum gates are **reversible**.
    - **We can know the input based on output**.
    - **We can know the information of entangled data qubits.**

[1. Entanglement Creation]             [2. Bell State Measurement]

```text
           ┌───┐                                 ┌───┐   ┌───┐   ┌─┐
Qubit A: ──┤ H ├───■─────────────────────────────┤ ■ ├───┤ H ├───┤M├── (Bit A)
           └───┘   │                             │ │ │   └───┘   └╥┘
Qubit B: ──────────⊕─────────────────────────────┤ ⊕ ├────────────╫─── (Bit B)
                                                 └───┘            ║
```

Note: The superposition states generated by the Hadamard gate are defined as:
- **$\vert+\rangle = \frac{1}{\sqrt{2}}(\vert0\rangle + \vert1\rangle)$**
- **$\vert-\rangle = \frac{1}{\sqrt{2}}(\vert0\rangle - \vert1\rangle)$**

| Initial Entangled State | Step 1: CNOT(A,B) | Step 2: H(A) (Fully Expanded) | Output |
| :--- | :--- | :--- | :--- |
| **$\vert\Phi^+\rangle$** = $\frac{1}{\sqrt{2}}(\vert00\rangle + \vert11\rangle)$ | $\frac{1}{\sqrt{2}}(\vert00\rangle + \vert10\rangle)$ | $\frac{1}{2}(\vert00\rangle + \vert10\rangle + \vert00\rangle - \vert10\rangle)$ | $\vert00\rangle$ |
| **$\vert\Psi^+\rangle$** = $\frac{1}{\sqrt{2}}(\vert01\rangle + \vert10\rangle)$ | $\frac{1}{\sqrt{2}}(\vert01\rangle + \vert11\rangle)$ | $\frac{1}{2}(\vert01\rangle + \vert11\rangle + \vert01\rangle - \vert11\rangle)$ | $\vert01\rangle$ |
| **$\vert\Phi^-\rangle$** = $\frac{1}{\sqrt{2}}(\vert00\rangle - \vert11\rangle)$ | $\frac{1}{\sqrt{2}}(\vert00\rangle - \vert10\rangle)$ | $\frac{1}{2}(\vert00\rangle + \vert10\rangle - \vert00\rangle + \vert10\rangle)$ | $\vert10\rangle$ |
| **$\vert\Psi^-\rangle$** = $\frac{1}{\sqrt{2}}(\vert01\rangle - \vert10\rangle)$ | $\frac{1}{\sqrt{2}}(\vert01\rangle - \vert11\rangle)$ | $\frac{1}{2}(\vert01\rangle + \vert11\rangle - \vert01\rangle + \vert11\rangle)$ | $\vert11\rangle$ |


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

**Pauli Product Measurements (PPM) [1]**
- A macroscopic **Joint Measurement** that checks the parity of a multi-qubit Pauli operator (e.g., $X \otimes Z \otimes Y$) across several logical qubits.
- A **physically executable** operation.
- The **only physical operation** that can be executed directly and fault-tolerantly on surface code hardware.

**Pauli Product Rotations (PPR) [1]**
- A quantum rotation that uses a Pauli operator as its axis to rotate qubits by a specific angle.
- **Clifford PPRs** (e.g., multiples of $\pi/4$ rotations, multipples of $\pi/2$ rotations) can be easily handled by classical bookkeeping without physical hardware operations.
- **Non-Clifford PPRs** (e.g., $\pi/8$ rotations) are physically impossible to execute directly on surface code hardware. 
- e.g., **T gate** (a representative non-Clifford operation) -> multiples of $\pi/8$ rotations. Can be realized with a magic state injection + clifford gate
- **Non-Clifford PPR = PPM + Magic State** (Figure 7 of **[4]**).
- So, if **magic states are available**, the only operations required for universal quantum computing are **Pauli product measurements**.

### Magic State [3]
- **Definition:** A specially prepared, pure quantum state (resource) injected from outside the system to achieve Universal Quantum Computation (UQC).
    - Typical examples include T-type and H-type magic states.
- **Why 'Magic'?**: They enable the execution of complex non-Clifford gates by using only simple Clifford gates and measurements. So, it is essential for the **universal quantum computing**
- They are precisely set at a specific angle.
    - e.g., $\pi/8$ rotated Pauli eigenstates $$|m\rangle = |0\rangle + e^{i\pi/4}|1\rangle$$
    - Normalized forma ($$|m\rangle$$ is a **eigenstate** of T-gate): $$|m\rangle = \frac{1}{\sqrt{2}} \left( |0\rangle + e^{i\pi/4}|1\rangle \right)$$
- **How?**: Lattice-Surgery Merge & Split -> Entangled data patch & magic state -> pauli measurement -> Same logical results
- **Purpose:** To bypass the physical limitations of surface codes. They are absolutely essential for **universal quantum computation**!

**Transversal T-gate**
- A logical T gate on the encoded logical qubit
- A physical T gate on very physical qubit corresponds to a logical t gate on the logical qubit

### Magic State Distillation [4]
- **Definition:** A protocol that takes multiple noisy, imperfect magic states and **purifies** them into a few **high-fidelity magic states**, using only fault-tolerant basic operations (Clifford gates and measurements).
- **Why is it needed?**: Due to realistic physical limitations, magic states prepared in external "factories" inevitably contain impurities/errors ($\rho$). Using these noisy states directly would ruin the computation.
- **The Threshold Rule (Crucial):** Distillation only works if the initial magic state's fidelity is above a certain threshold (e.g., > 91% for T-type). If the initial state is too noisy, the distillation fails and ruins the state completely.
- **How it works:** 
  1. Gather multiple imperfect magic states (e.g., 5 states for T-type, or 15-to-1 **[1]** for H-type distillation codes).
  2. Check for errors using reliable hardware operations (syndrome measurements).
  3. Discard the states entirely if any error signs are detected; keep only the ones that successfully pass the check.
  4. The surviving states are entangled to produce a single, higher-purity magic state with significantly reduced noise.
  5. Repeat this process (recursive iteration) to obtain magic states of the desired absolute purity.
- **Specific Distillation Protocols [1]**
    - **15-to-1 Distillation** (Fig. 15 in **[1]**)
        - Summary: The most widely used standard T-gate magic state distillation protocol, based on the Reed-Muller code **[10]**.
        - Motivation/Why needed: Offers a balanced trade-off (T-gate consumption speed <-> hardware resources).
        - Input: 15 noisy states ('p' error probability each)
        - Output: 1 pure state ($35p^3$ error probability)
        - Concept: By removing redundancy (**Shortening [11]**) from the 15 qubits, the circuit can be ultimately optimized down to a compact 5-data-qubit module.
    - **7-to-1 Distillation** (Appendix D in **[1]**)
        - Summary: A protocol for distilling $|Y\rangle$ magic states, based on the **Steane Code**.
        - Motivation/Why needed: Although not necessary in this paper's framework (since Y-measurements are handled via Twist defects), it is analyzed for benchmarking against older braiding-based techniques.
        - Input: 7 noisy states.
        - Output: 1 pure $|Y\rangle$ state.
    - **Triorthogonal Codes & 20-to-4** (Fig. 16 in [1])
        - Summary: An expanded family of protocols based on large mathematical matrices (Triorthogonal matrices) that guarantee **Transversal T-gates**.
        - Motivation/Why needed: Used to maximize distillation block (factory) throughput by producing multiple magic states in a single batch, rather than extracting them one by one.
            - 15-to-1 method: 4 magic states in isolated parallel requires **44 tiles** (4 blocks $\times$ 11 tiles)
            - 20-to-4 method: Achieves the same output simultaneously using only **14 tiles** in a single batch, saving space by roughly 3x without sequential latency.
        - Input: 20 noisy states.
        - Output: 4 pure states.
        - Concept: Through Puncturing (or Shortening)—which removes specific columns from the matrix—various variant codes like 15-to-1 or 14-to-2 can be algorithmically generated. Some codes with relaxed constraints (Semi-triorthogonal) require an additional Clifford correction.
- **Surface-code Implementation (Fig. 17 in [1])**
    - Summary: The hardware implementation strategy that maps magic state distillation circuits onto 2D Surface Code Tiles and discrete **Time steps ($1\circlearrowright$)**.
    - Motivation/Why needed: Designed to **prevent the latency** caused by probabilistic Clifford corrections during T-gate injection.
    - Concept: "Auto-corrected rotation". It utilizes an ancilla qubit to perform error correction simultaneously without consuming extra time steps, simply by choosing the measurement basis (X or Z). This is the core of **Latency Hiding**, which even masks constant-time delays using an alternating ping-pong strategy with two ancilla blocks (Fig. 18 in [1]).
- **Benchmarking (Table 1 in [1])**
    - Summary: Proves the extreme **space-time cost reduction** of the Tile-based lattice surgery strategy.
    - Motivation/Why needed: Demonstrates that intelligent scheduling and architectural layout optimization alone can **reduce resource consumption** by up to 90% ($2344d^3 \rightarrow 238d^3$).
    - Result: For the 20-to-4 protocol, the space-time cost drops drastically from $2344d^3$ (old hole braiding) to $238d^3$.
    - Concept? (e.g., single bit/phase error correction)
- **Higher-fidelity Protocols & Concatenation (Fig. 19 in [1])**
    - Summary: Multi-level distillation architectures designed to achieve **extremely low error rates ($\sim 10^{-21}$)**.
    - Motivation/Why needed: Using a **piplined approach is better for hardware scheduling** than simply using a massive code with a high output-to-input ratio ($k/n$).
    - **Concatenation** (Better!) vs. Higher-distance:
        - Concatenation (e.g., 225-to-1): Operates as a **pipeline** where multiple Level-1 factories feed a Level-2 factory. Upon a partial failure, the scheduler **only needs to skip a single time step (relative small time penalty)**, making it highly robust for dynamic scheduling. Furthermore, lower-level factories can operate at a **reduced Code Distance ($d$)** to save significant physical resources.
        - Massive Codes (e.g., 912-to-112): High theoretical yield, but a single error ruins the entire massive batch (Stochastic failure). **The time penalty for restarting is severe**.

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

$$
R_z(\alpha) = \left[ \begin{array}{cc}
e^{-i\frac{\alpha}{2}} & 0 \\
0 & e^{i\frac{\alpha}{2}}
\end{array} \right]
$$

$$
R_z\left(\frac{\pi}{4}\right) = \left[ \begin{array}{cc}
e^{-i\frac{\pi}{8}} & 0 \\
0 & e^{i\frac{\pi}{8}}
\end{array} \right]
$$

### Comparison Table: Clifford vs. Non-Clifford Gates

| Feature | Clifford Gates | Non-Clifford Gates (e.g., T, Toffoli) |
| --- | --- | --- |
| **Classical Simulation** | Efficient (Polynomial time) | Inefficient (Exponential time) |
| **Mathematical Role** | Maps Pauli to Pauli | "Escapes" the Pauli group |
| **Common Examples** | H, S, CNOT, Pauli X, Y, Z | T, Toffoli (CCNOT) |
| **Error Correction** | Easy to implement via stabilizer codes | Difficult; requires magic state distillation |
| **Universality** | Not universal on their own | Required for a universal gate set |

**Transversal Gate [5]**
- A logical gate that doesn't propagate errors within each code block (e.g., don't propagate errors within each surface codes)
![Transversal Gates (CNOTs between corresponding qubits on two code blocks)](https://arthurpesah.me/assets/img/blog/transversal-gates/transversal-cnot.png)
- Logical CNOTs between two logical qubits (surface code blocks) do not propagate errors within the each surface code block.

## References
**[1]** Litinski, Daniel. "A game of surface codes: Large-scale quantum computing with lattice surgery." Quantum 3 (2019): 128.

**[2]** Ding, Y. (2025). Lecture 6: Quantum Measurements [Lecture notes, CPSC 4470/5470]. Department of Computer Science, Yale University. https://www.yongshanding.com/cpsc447-f25/Lec6-f25.pdf

**[3]** Bravyi, Sergey, and Alexei Kitaev. "Universal quantum computation with ideal Clifford gates and noisy ancillas." Physical Review A—Atomic, Molecular, and Optical Physics 71.2 (2005): 022316.

**[4]** Litinski, Daniel. "A game of surface codes: Large-scale quantum computing with lattice surgery." Quantum 3 (2019): 128.

**[5]** Pesah, A. (2023, December 25). Computing with quantum codes using transversal gates. https://arthurpesah.me/blog/2023-12-25-transversal-gates/

**[6]** (1,2) Dominic Horsman, Austin G. Fowler, Simon Devitt, Rodney Van Meter, “Surface code quantum computing by lattice surgery”, arXiv:1111.4022, 2011

**[7]** (1,2) Christopher Chamberland, Earl T. Campbell “Universal quantum computing with twist-free and temporally encoded lattice surgery”, arXiv:2109.02746, 2021

**[8]** Austin G. Fowler, Craig Gidney “Low overhead quantum computation using lattice surgery” arXiv:1808.06709, 2018.

**[9]** Vuillot, Christophe, et al. "Code deformation and lattice surgery are gauge fixing." New Journal of Physics 21.3 (2019): 033028.

**[10]** Bravyi, Sergey, and Alexei Kitaev. "Universal quantum computation with ideal Clifford gates and noisy ancillas." Physical Review A—Atomic, Molecular, and Optical Physics 71.2 (2005): 022316.

**[11]** J. I. Hall, Notes on Coding Theory Chapter 6: Modifying Codes, https://users.math.msu.edu/users/jhall/classes/codenotes/Mod.pdf, accessed: 2019-01-30.