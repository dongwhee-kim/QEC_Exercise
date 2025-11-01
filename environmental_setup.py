import sys
import subprocess

# --- Script Configuration ---

# 1. Target Python version that is compatible with Qiskit
PYTHON_VERSION = "3.12"

# 2. List of packages to install
PACKAGES = [
    "qiskit",
    "matplotlib",
    "pylatexenc",
    "qiskit-aer",
    "numpy",
    "qiskit-ibm-runtime", 
    "tqdm",
    "pymatching",
    "rustworkx",
    "networkx"
]

# --------------------------

def run_command(command_list):
    """
    Executes a shell command and checks for errors.
    """
    print(f"\n>>> Executing: {' '.join(command_list)}")
    try:
        # Run the command. check=True raises an error if the command fails.
        result = subprocess.run(command_list, check=True, text=True, encoding='utf-8')
        print(f"--- Success: {' '.join(command_list)} ---")
    except subprocess.CalledProcessError as e:
        print(f"\n\n--- 🚨 ERROR! ---")
        print(f"Command execution failed. (Exit Code: {e.returncode})")
        print(f"Command: {e.cmd}")
        print("Aborting script.")
        sys.exit(1)
    except FileNotFoundError:
        print(f"\n\n--- 🚨 ERROR! ---")
        print(f"Command 'conda' not found.")
        print("Please ensure Conda is installed and you are in a Conda environment.")
        print("Aborting script.")
        sys.exit(1)

def main():
    print("=========================================================")
    print("      Fixing the Current Conda Environment Script      ")
    print("=========================================================")
    print("This script will attempt to downgrade Python in the CURRENT")
    print(f"environment to {PYTHON_VERSION} and install all required packages.")
    print("This will resolve the Python 3.14 incompatibility issue.")
    
    # --- 1. Create the full install command ---
    # We combine Python downgrade and package install into ONE command
    # so the Conda solver can handle all constraints at once.
    
    install_cmd = (
        ['conda', 'install', '-c', 'conda-forge', f'python={PYTHON_VERSION}'] 
        + PACKAGES 
        + ['-y']
    )
    
    # --- 2. Execute the command ---
    run_command(install_cmd)

    # --- 3. Final success message ---
    print("\n\n================= ✅ Success! ===================")
    print(f"The current environment has been successfully updated.")
    print(f"Python is now downgraded to {PYTHON_VERSION} (or compatible).")
    print("All Qiskit packages should be installed correctly.")
    print("\nYou can now proceed with your work in this environment.")
    print("=========================================================")

if __name__ == "__main__":
    main()