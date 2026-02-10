import stim
import pymatching
import random
import numpy as np
import time
from collections import Counter

# ==========================================
# 1. Simulation Parameters
# ==========================================
distance = 3
rounds = 3
shots = 1000 

# Error Rates (p=0.001)
p_1q = 0.001
p_2q = 0.001
p_meas = 0.001
p_reset = 0.001
p_idle = 0.001

output_file = f"baseline_memX_std_d{distance}_r{rounds}_s{shots}_p{p_2q}.txt"

# ==========================================
# 2. Setup Circuits & Decoder
# ==========================================
ideal_circuit = stim.Circuit.generated(
    "surface_code:rotated_memory_x",
    rounds=rounds,
    distance=distance,
    after_clifford_depolarization=0,
    after_reset_flip_probability=0,
    before_measure_flip_probability=0,
    before_round_data_depolarization=0
)

decoder_circuit = stim.Circuit.generated(
    "surface_code:rotated_memory_x",
    rounds=rounds,
    distance=distance,
    after_clifford_depolarization=p_2q,
    after_reset_flip_probability=p_reset,
    before_measure_flip_probability=p_meas,
    before_round_data_depolarization=p_idle
)

dem = decoder_circuit.detector_error_model(decompose_errors=True)
matcher = pymatching.Matching.from_detector_error_model(dem)

# ==========================================
# 3. [FIXED] Detector Classification (X vs Z)
# ==========================================
detector_coords = ideal_circuit.get_detector_coordinates()
x_det_indices = []
z_det_indices = []
time_coords = []

# Stim coordinates might be in units of 2 (0, 2, 4...), so divide by 2 to determine parity.
for k, v in detector_coords.items():
    x, y, t = v
    time_coords.append(t)
    
    # Distinguish by the parity of the sum of coordinates divided by 2 (Checkerboard pattern)
    # This method generally separates X/Z in Rotated Code.
    if int(x + y) // 2 % 2 == 0:
        z_det_indices.append(k)
    else:
        x_det_indices.append(k)

x_det_indices = np.array(sorted(x_det_indices), dtype=int)
z_det_indices = np.array(sorted(z_det_indices), dtype=int)

min_t = min(time_coords) if time_coords else 0
max_t = max(time_coords) if time_coords else 0

print(f"DEBUG: Split {len(detector_coords)} detectors into -> X: {len(x_det_indices)}, Z: {len(z_det_indices)}")

# ==========================================
# 4. Global Counters
# ==========================================
fault_counts = {
    "Data Idle": 0, "CNOT": 0, "Measure": 0, "1-Qubit": 0, "Reset": 0
}

hw_x_list = []
hw_z_list = []
total_logical_errors = 0

# ==========================================
# 5. Helper Functions
# ==========================================
def get_random_pauli_error_gate():
    r = random.random()
    if r < 0.333: return "X_ERROR"
    elif r < 0.666: return "Y_ERROR"
    else: return "Z_ERROR"

def inject_error(circuit, targets, p, type_key):
    if isinstance(targets, int): targets = [targets]
    injected = 0
    for q in targets:
        if random.random() < p:
            gate = get_random_pauli_error_gate()
            circuit.append(gate, [q], 1.0)
            fault_counts[type_key] += 1
            injected += 1
    return injected

# ==========================================
# 6. Main Simulation Loop
# ==========================================
print(f"Starting Simulation: d={distance}, r={rounds}, shots={shots}")
start_time = time.time()

flat_ideal_circuit = ideal_circuit.flattened()
num_qubits = ideal_circuit.num_qubits

for shot_idx in range(shots):
    noisy_circuit = stim.Circuit()
    
    # === Manual Error Injection ===
    for instruction in flat_ideal_circuit:
        name = instruction.name
        targets = instruction.targets_copy()
        qubit_targets = [t.value for t in targets if t.is_qubit_target]

        # [Type 1] Measure (Before)
        if name in ["M", "MX", "MY", "MZ", "MR", "MRX", "MRY", "MRZ"]:
            inject_error(noisy_circuit, qubit_targets, p_meas, "Measure")
            noisy_circuit.append(instruction)
            if name.startswith("MR"):
                inject_error(noisy_circuit, qubit_targets, p_reset, "Reset")

        # [Type 2] Reset (After)
        elif name in ["R", "RX", "RY", "RZ"]:
            noisy_circuit.append(instruction)
            inject_error(noisy_circuit, qubit_targets, p_reset, "Reset")
        
        # [Type 3] Idle
        elif name == "TICK":
            noisy_circuit.append(instruction)
            for q in range(num_qubits):
                # Inject error with probability /4 (p_idle / 4) per tick
                if random.random() < (p_idle / 4):
                    noisy_circuit.append(get_random_pauli_error_gate(), [q], 1.0)
                    fault_counts["Data Idle"] += 1
        
        # [Type 4] Gates
        else:
            noisy_circuit.append(instruction)
            if name in ["CX", "CZ", "CNOT", "SWAP"]:
                inject_error(noisy_circuit, qubit_targets, p_2q, "CNOT")
            elif name in ["H", "H_XY", "H_YZ", "S", "S_DAG", "SQRT_X", "SQRT_Y", "SQRT_Z", "I"]:
                inject_error(noisy_circuit, qubit_targets, p_1q, "1-Qubit")

    # === Simulation ===
    sampler = noisy_circuit.compile_detector_sampler()
    detection_events, actual_flips = sampler.sample(shots=1, separate_observables=True)
    syndrome = detection_events[0]
    
    # === Separate Hamming Weights (X/Z) ===
    if len(x_det_indices) > 0:
        hw_x_list.append(np.sum(syndrome[x_det_indices]))
    else:
        hw_x_list.append(0)

    if len(z_det_indices) > 0:
        hw_z_list.append(np.sum(syndrome[z_det_indices]))
    else:
        hw_z_list.append(0)

    # === Decoding (PyMatching) ===
    predicted_flip = matcher.decode_batch(detection_events)[0][0]
    actual_flip = bool(actual_flips[0][0])
    
    if predicted_flip != actual_flip:
        total_logical_errors += 1

elapsed_time = time.time() - start_time

# ==========================================
# 7. Write Results
# ==========================================
total_faults = sum(fault_counts.values())
ler = total_logical_errors / shots

x_hw_counts = Counter(hw_x_list)
z_hw_counts = Counter(hw_z_list)

def format_hw_table(hw_counts, total_shots):
    lines = []
    # Sort by existing keys
    sorted_keys = sorted(hw_counts.keys())
    if not sorted_keys: return "No Data"
    
    for k in sorted_keys:
        count = hw_counts[k]
        perc = (count / total_shots) * 100
        lines.append(f"{k:<6}| {count:<11}| {perc:.4f}%")
    return "\n".join(lines)

with open(output_file, "w") as f:
    f.write(f"Total Fault Events: {total_faults:,}\n")
    f.write("-" * 40 + "\n")
    for key, val in fault_counts.items():
        ratio = (val / total_faults * 100) if total_faults > 0 else 0
        f.write(f"  {key:<10}: {val:,} ({ratio:.2f}%)\n")
    f.write("-" * 40 + "\n")
    f.write(f"  -> Max Time Coordinate: {float(max_t)}\n")
    f.write(f"  -> Filtering Time Range: {float(min_t)} <= t <= {float(max_t)}\n")
    f.write(f"  -> Extracted {len(x_det_indices)} X-bits and {len(z_det_indices)} Z-bits for analysis.\n")
    f.write(f"  -> Saving results to '{output_file}'\n")
    f.write(f"# Syndrome Analysis: d={distance}, r={rounds}, shots={shots}, p_idle={p_idle}\n")
    f.write("# Format: [X_Syndrome_Bits] [Z_Syndrome_Bits]\n")
    f.write("-" * 60 + "\n\n")
    
    f.write("=" * 40 + "\n")
    f.write("HAMMING WEIGHT DISTRIBUTION SUMMARY\n")
    f.write("=" * 40 + "\n\n")
    
    # X-Syndrome
    f.write(f"[X-Syndrome] Total Bits: {len(x_det_indices)}\n")
    f.write(f"{'HW':<6}| {'Count':<11}| {'Percentage'}\n")
    f.write("-" * 30 + "\n")
    f.write(format_hw_table(x_hw_counts, shots))
    f.write("\n\n")
    
    # Z-Syndrome
    f.write(f"[Z-Syndrome] Total Bits: {len(z_det_indices)}\n")
    f.write(f"{'HW':<6}| {'Count':<11}| {'Percentage'}\n")
    f.write("-" * 30 + "\n")
    f.write(format_hw_table(z_hw_counts, shots))
    f.write("\n\n")
    f.write("=" * 40 + "\n\n")
    
    f.write("=== FINAL QEC RESULTS (Sinter) ===\n")
    f.write(f"Model: Baseline (std)\n")
    f.write(f"Shots: {shots}\n")
    f.write(f"Logical Failures: {total_logical_errors}\n")
    f.write(f"Logical Error Rate (LER): {ler:.6e}\n")
    f.write(f"Time Taken: {elapsed_time:.2f}s\n")

print(f"Simulation Complete. Results saved to {output_file}")