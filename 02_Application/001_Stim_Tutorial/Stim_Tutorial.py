import stim
import numpy as np
import pymatching
import matplotlib.pyplot as plt
import sinter
from typing import List
import os
import scipy.stats

# Backend setting for drawing graphs in environments without a GUI (like Linux servers)
# Without this setting, plt.show() might cause an error.
plt.switch_backend('Agg')

def main():
    """
    Main execution function.
    All execution logic is encapsulated here to prevent multiprocessing errors.
    """
    
    print("=== 1. Basic Circuit Generation & Measurement (Bell Pair) ===")
    
    # Create an empty circuit
    circuit = stim.Circuit()

    # 1. Initialize Bell Pair
    # H gate: Put qubit 0 into superposition (|0> -> |+>)
    circuit.append("H", [0])
    # CNOT gate: Control(0), Target(1) -> Create entangled state (|00> + |11>)
    circuit.append("CNOT", [0, 1]) 

    # 2. Measurement
    # Measure both qubits in the Z basis (0 or 1)
    circuit.append("M", [0, 1])

    print("\n[Circuit Structure]")
    print(circuit)
    print("\n[Circuit Diagram]")
    print(circuit.diagram())

    # 3. Sampling (Run 10 times)
    # Since it's an entangled state, results should be 00 or 11.
    sampler = circuit.compile_sampler()
    print("\n[Sampling Results (10 shots)]")
    print(sampler.sample(shots=10)) 


    print("\n=== 2. Adding Detectors ===")

    # DETECTOR: Set conditions for error detection
    # This means rec[-1] (measurement of qubit 1) and rec[-2] (measurement of qubit 0) must be equal.
    # If measurements are equal -> Parity 0 (False, No error)
    # If measurements are different -> Parity 1 (True, Error detected)
    circuit.append("DETECTOR", [stim.target_rec(-1), stim.target_rec(-2)]) 
    
    print("\n[Circuit Diagram (With Detector)]")
    print(repr(circuit))

    # Detector Sampling
    # Samples 'whether an error was detected' rather than the raw measurement values.
    sampler = circuit.compile_detector_sampler()
    print("\n[Detector Sampling Results (5 shots)]")
    print(sampler.sample(shots=5)) # Ideally, all should be False


    print("\n=== 3. Error Injection ===")

    # Define a circuit with errors directly using text
    # X_ERROR(0.2): 20% probability of a bit flip error (0->1, 1->0)
    circuit = stim.Circuit("""
        H 0
        TICK

        CX 0 1
        X_ERROR(0.2) 0 1
        TICK

        M 0 1
        DETECTOR rec[-1] rec[-2]
    """)
    print("\n[Circuit Diagram (With Error)]")
    print(circuit.diagram())

    sampler = circuit.compile_detector_sampler()
    print("\n[Detector Sampling With Error (10 shots)]")
    print(sampler.sample(shots=10)) # True will appear mixed in due to errors

    # Statistical Estimation
    # Expected value calc: 20% error on each of 2 qubits.
    # Error detection prob = 0.2*(1-0.2) + (1-0.2)*0.2 = 0.32
    print("\n[Error Rate Estimation via Sampling (10^6 shots)]")
    print(f"Estimated: {np.sum(sampler.sample(shots=10**6)) / 10**6} (Theoretical Expected: 0.32)")


    print("\n=== 4. Repetition Code ===")

    # Generate Repetition Code circuit using Stim's built-in generator
    circuit = stim.Circuit.generated(
        "repetition_code:memory",
        rounds=25,     # Repeat error check for 25 rounds
        distance=9,    # Code distance 9
        before_round_data_depolarization=0.04, # Depolarization error on data qubits before round
        before_measure_flip_probability=0.01   # Bit flip error before measurement
        )

    print("\n[Repetition Code Circuit Structure]")
    print(circuit.diagram())

    # Measurement Sampling Visualization
    print("\n[Measurement Sampling Visualization (Partial)]")
    sampler = circuit.compile_sampler()
    one_sample = sampler.sample(shots=1)[0]
    # Print in chunks of 8 (Data change over time)
    for k in range(0, len(one_sample), 8):
        timeslice = one_sample[k:k+8]
        # 1 shown as '1', 0 as '_'. Without errors, it looks like stripes.
        print("".join("1" if e else "_" for e in timeslice))

    # Detector Sampling Visualization
    print("\n[Detector Sampling Visualization (Partial)]")
    detector_sampler = circuit.compile_detector_sampler()
    one_sample = detector_sampler.sample(shots=1)[0]
    for k in range(0, len(one_sample), 8):
        timeslice = one_sample[k:k+8]
        # Only error detection moments are shown as '!' (Sparse)
        print("".join("!" if e else "_" for e in timeslice))


    print("\n=== 5. Error Correction using PyMatching (Decoding) ===")

    # Create DEM (Detector Error Model)
    # Extracts the error mechanisms and their symptoms (Syndromes) in graph format from the circuit
    dem = circuit.detector_error_model() 
    print("\n[Detector Error Model (Partial)]")
    print(str(dem)[:500] + "...")

    # Define function to count logical errors
    def count_logical_errors(circuit: stim.Circuit, num_shots: int) -> int:
        # 1. Sampling: Collect detector events (symptoms) and actual answers (observables)
        sampler = circuit.compile_detector_sampler()
        detection_events, observable_flips = sampler.sample(num_shots, separate_observables=True)

        # 2. Decoder Setup: Extract error model from circuit and create PyMatching decoder
        detector_error_model = circuit.detector_error_model(decompose_errors=True)
        matcher = pymatching.Matching.from_detector_error_model(detector_error_model)

        # 3. Prediction: Predict if an error occurred based on detector events
        predictions = matcher.decode_batch(detection_events)

        # 4. Verification: If predicted value differs from actual, it's a 'Logical Error'
        num_errors = 0
        for shot in range(num_shots):
            actual_for_shot = observable_flips[shot]
            predicted_for_shot = predictions[shot]
            if not np.array_equal(actual_for_shot, predicted_for_shot):
                num_errors += 1
        return num_errors

    # Test Case 1: Low noise (0.03) -> Should have almost no errors
    circuit_low_noise = stim.Circuit.generated(
        "repetition_code:memory",
        rounds=100,
        distance=9,
        before_round_data_depolarization=0.03
        )
    num_shots = 10_000
    errors = count_logical_errors(circuit_low_noise, num_shots)
    print(f"\n[Low Noise Test] {errors} logical errors out of 10,000 shots")

    # Test Case 2: High noise (0.13) -> Should have many errors
    circuit_high_noise = stim.Circuit.generated(
        "repetition_code:memory",
        rounds=100,
        distance=9,
        before_round_data_depolarization=0.13,
        before_measure_flip_probability=0.01)
    errors = count_logical_errors(circuit_high_noise, num_shots)
    print(f"[High Noise Test] {errors} logical errors out of 10,000 shots")


    print("\n=== 6. Repetition Code Threshold Analysis (Monte-Carlo) ===")
    print("Generating graph... (1_repetition_threshold.png)")

    plt.figure(figsize=(10, 6))
    num_shots = 5_000 # Adjusted shots for speed
    for d in [3, 5, 7]: # Test with varying code distances (d)
        xs = []
        ys = []
        for noise in [0.1, 0.2, 0.3, 0.4, 0.5]: # Varying physical error rates
            circuit = stim.Circuit.generated(
                "repetition_code:memory",
                rounds=d * 3,
                distance=d,
                before_round_data_depolarization=noise)
            num_errors_sampled = count_logical_errors(circuit, num_shots)
            xs.append(noise)
            ys.append(num_errors_sampled / num_shots)
        plt.plot(xs, ys, label="d=" + str(d), marker='o')

    plt.loglog() # Log scale
    plt.xlabel("Physical Error Rate")
    plt.ylabel("Logical Error Rate per Shot")
    plt.title("Repetition Code Threshold")
    plt.legend()
    plt.grid(True, which="both", ls="--")
    plt.savefig("1_repetition_threshold.png") # Save to file
    plt.clf()


    print("\n=== 7. Large Scale Simulation & Plotting using Sinter ===")
    print("Collecting parallel tasks... (This may take a while)")

    # Define Sinter Tasks
    # Combine distance (d) and error rate (p) to create multiple cases
    tasks = [
        sinter.Task(
            circuit=stim.Circuit.generated(
                "repetition_code:memory",
                rounds=d * 3,
                distance=d,
                before_round_data_depolarization=noise,
            ),
            json_metadata={'d': d, 'p': noise},
        )
        for d in [3, 5, 7, 9]
        for noise in [0.05, 0.08, 0.1, 0.2, 0.3, 0.4, 0.5]
    ]

    # sinter.collect: Run parallel simulations (This is where the Multiprocessing error occurred)
    # Safe now as it is inside main() and called via if __name__ == "__main__"
    collected_stats: List[sinter.TaskStats] = sinter.collect(
        num_workers=4,          # Number of CPU cores to use
        tasks=tasks,            # List of tasks
        decoders=['pymatching'],# Decoder to use
        max_shots=100_000,      # Max shots
        max_errors=500,         # Early exit if 500 errors found
    )

    # Save Result Graph
    fig, ax = plt.subplots(1, 1)
    sinter.plot_error_rate(
        ax=ax,
        stats=collected_stats,
        x_func=lambda stats: stats.json_metadata['p'],
        group_func=lambda stats: stats.json_metadata['d'],
    )
    ax.set_ylim(1e-4, 1e-0)
    ax.set_xlim(5e-2, 5e-1)
    ax.loglog()
    ax.set_title("Repetition Code Error Rates (Phenomenological Noise)")
    ax.set_xlabel("Physical Error Rate")
    ax.set_ylabel("Logical Error Rate per Shot")
    ax.grid(which='major')
    ax.grid(which='minor')
    ax.legend()
    fig.set_dpi(120)
    plt.savefig("2_sinter_repetition_results.png")
    plt.clf()
    print("Graph saved: 2_sinter_repetition_results.png")


    print("\n=== 8. Surface Code Threshold & Footprint Analysis ===")

    # Define Surface Code Tasks
    surface_code_tasks = [
        sinter.Task(
            circuit = stim.Circuit.generated(
                "surface_code:rotated_memory_z",
                rounds=d * 3,
                distance=d,
                after_clifford_depolarization=noise,
                after_reset_flip_probability=noise,
                before_measure_flip_probability=noise,
                before_round_data_depolarization=noise,
            ),
            json_metadata={'d': d, 'r': d * 3, 'p': noise},
        )
        for d in [3, 5, 7]
        for noise in [0.008, 0.009, 0.01, 0.011, 0.012]
    ]

    print("Starting Surface Code simulation (This may take a while)...")
    
    collected_surface_code_stats: List[sinter.TaskStats] = sinter.collect(
        num_workers=os.cpu_count(), # Use all available CPU cores
        tasks=surface_code_tasks,
        decoders=['pymatching'],
        max_shots=1_000_000,
        max_errors=1_000,
        print_progress=True, # Print progress
    )

    # Save Result Graph
    fig, ax = plt.subplots(1, 1)
    sinter.plot_error_rate(
        ax=ax,
        stats=collected_surface_code_stats,
        x_func=lambda stat: stat.json_metadata['p'],
        group_func=lambda stat: stat.json_metadata['d'],
        failure_units_per_shot_func=lambda stat: stat.json_metadata['r'],
    )
    ax.set_ylim(5e-3, 5e-2)
    ax.set_xlim(0.008, 0.012)
    ax.loglog()
    ax.set_title("Surface Code Error Rates per Round")
    ax.set_xlabel("Physical Error Rate")
    ax.set_ylabel("Logical Error Rate per Round")
    ax.grid(which='major')
    ax.grid(which='minor')
    ax.legend()
    fig.set_dpi(120)
    plt.savefig("3_surface_code_threshold.png")
    plt.clf()
    print("Graph saved: 3_surface_code_threshold.png")


    print("\n=== 9. Predicting Code Distance for Target Logical Error Rate ===")

    noise = 1e-3
    print(f"Predicting required distance for noise level p={noise}...")

    # Collect data with increasing distance (d)
    surface_code_tasks = [
        sinter.Task(
            circuit = stim.Circuit.generated(
                "surface_code:rotated_memory_z",
                rounds=d * 3,
                distance=d,
                after_clifford_depolarization=noise,
                after_reset_flip_probability=noise,
                before_measure_flip_probability=noise,
                before_round_data_depolarization=noise,
            ),
            json_metadata={'d': d, 'r': d * 3, 'p': noise},
        )
        for d in [3, 5, 7, 9]
    ]

    collected_surface_code_stats = sinter.collect(
        num_workers=os.cpu_count(),
        tasks=surface_code_tasks,
        decoders=['pymatching'],
        max_shots=5_000_000,
        max_errors=100,
        print_progress=True,
    )

    # Linear Regression Prep (Assuming Log Error Rate decreases linearly with distance d)
    xs = []
    ys = []
    log_ys = []
    for stats in collected_surface_code_stats:
        d = stats.json_metadata['d']
        if not stats.errors:
            print(f"No errors observed for distance d={d}. Skipping statistics.")
            continue
        per_shot = stats.errors / stats.shots
        per_round = sinter.shot_error_rate_to_piece_error_rate(per_shot, pieces=stats.json_metadata['r'])
        xs.append(d)
        ys.append(per_round)
        log_ys.append(np.log(per_round))

    # Perform Linear Regression
    fit = scipy.stats.linregress(xs, log_ys)
    print(f"\n[Linear Regression Result]\n{fit}")

    # Save Projection Graph
    fig, ax = plt.subplots(1, 1)
    ax.scatter(xs, ys, label=f"Sampled Logical Error Rate (p={noise})")
    
    # Draw trend line from d=0 to d=25 (Future Projection)
    ax.plot([0, 25],
            [np.exp(fit.intercept), np.exp(fit.intercept + fit.slope * 25)],
            linestyle='--',
            label='Least Squares Line Fit')
            
    ax.set_ylim(1e-12, 1e-0)
    ax.set_xlim(0, 25)
    ax.semilogy() 
    ax.set_title("Projecting Distance Needed (Trillion Rounds Survival)")
    ax.set_xlabel("Code Distance")
    ax.set_ylabel("Logical Error Rate per Round")
    ax.grid(which='major')
    ax.grid(which='minor')
    ax.legend()
    fig.set_dpi(120)
    plt.savefig("4_distance_projection.png")
    plt.clf()
    print("Graph saved: 4_distance_projection.png")

    print("\n=== All Tasks Completed ===")

# [IMPORTANT] Core part for fixing Multiprocessing errors
# This block ensures child processes are not infinitely spawned, enabling safe parallel processing.
if __name__ == "__main__":
    main()
