import sinter
import stim
import matplotlib.pyplot as plt
import multiprocessing
import numpy as np
from typing import List

def generate_rotated_surface_code_circuit(d: int, p: float) -> stim.Circuit:
    # "surface_code:rotated_memory_z" creates a standard memory experiment in the Z-basis.
    return stim.Circuit.generated(
        "surface_code:rotated_memory_z",
        rounds=d,
        distance=d,
        after_clifford_depolarization=p,
        after_reset_flip_probability=p,
        before_measure_flip_probability=p,
        before_round_data_depolarization=p
    )

def main():
    # --- Configuration ---
    # 1. Sweep ranges
    distances = [3, 5, 7, 9]
    
    # Sweep physical error rates from 10^-4 to 10^-2
    physical_error_rates = np.geomspace(1e-4, 1e-2, 10)
    
    # 2. Simulation settings
    # FIX: Renamed variable to avoid confusion, though not strictly necessary
    target_shots = 1_000_000 
    
    # Use half of the available CPU cores
    num_workers = multiprocessing.cpu_count() // 2
    
    total_stats: List[sinter.TaskStats] = []

    print(f"Starting simulation with {num_workers} workers.")
    print(f"Physical Error Rates: {physical_error_rates[0]:.1e} ~ {physical_error_rates[-1]:.1e} ({len(physical_error_rates)} points)")
    print("-" * 60)

    # --- Simulation Loop ---
    for d in distances:
        print(f"distance={d} Simulation (sweeping p) ...", end=" ", flush=True)
        
        tasks = []
        for p in physical_error_rates:
            tasks.append(
                sinter.Task(
                    circuit=generate_rotated_surface_code_circuit(d, p),
                    json_metadata={'d': d, 'p': p}
                )
            )

        # Use sinter
        batch_stats = sinter.collect(
            num_workers=num_workers,
            tasks=tasks,
            max_shots=target_shots,
            decoders=['pymatching'],
            print_progress=False 
        )
        
        total_stats.extend(batch_stats)
        print("Done.")

    print("-" * 60)
    print("Simulation Complete.")

    # --- Plotting (Threshold Plot) ---
    try:
        plt.figure(figsize=(10, 7))
        
        for d in distances:
            d_stats = [s for s in total_stats if s.json_metadata['d'] == d]
            d_stats.sort(key=lambda s: s.json_metadata['p']) 
            
            x_p = [s.json_metadata['p'] for s in d_stats]
            y_logical = [s.errors / s.shots if s.shots > 0 else 0 for s in d_stats]
            
            plt.plot(x_p, y_logical, marker='o', label=f'd={d}')

        plt.xscale('log')
        plt.yscale('log')
        plt.xlabel("Physical Error Rate (p)")
        plt.ylabel("Logical Error Rate")
        plt.title("Surface Code Threshold Plot")
        plt.grid(True, which="both", ls="--", alpha=0.5)
        plt.legend()
        
        output_file = "surface_code_threshold.png"
        plt.savefig(output_file)
        print(f"Plot saved to '{output_file}'")
        
    except Exception as e:
        print(f"Could not generate plot: {e}")

if __name__ == '__main__':
    main()