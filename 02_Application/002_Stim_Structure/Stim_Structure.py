import stim

# 1. Set parameters for the surface code
rounds = 3
distance = 3

# 2. Generate an ideal surface code circuit (noise-free)
# All error probabilities are set to 0 to inspect the clean structure
ideal_circuit = stim.Circuit.generated(
    "surface_code:rotated_memory_x",
    rounds=rounds,
    distance=distance,
    after_clifford_depolarization=0,
    after_reset_flip_probability=0,
    before_measure_flip_probability=0,
    before_round_data_depolarization=0
)

# 3. Define the file name and save to a .stim file
file_name = "ideal_surface_code.stim"
with open(file_name, "w") as f:
    # Convert the circuit object to its string representation
    f.write(str(ideal_circuit))

print(f"Success: The circuit has been saved to '{file_name}'")

# 4. Optional: Print the first 20 lines to inspect components
print("\n--- Circuit Component Preview (Top 20 lines) ---")
circuit_lines = str(ideal_circuit).splitlines()
for line in circuit_lines[:20]:
    print(line)